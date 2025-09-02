from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Tuple

import pandas as pd

from finter.backtest.base.main import BaseBacktestor
from finter.backtest.base.variables import InputVars
from finter.backtest.builder.processor import DataProcessor
from finter.backtest.config.config import (
    CacheConfig,
    CostConfig,
    DataConfig,
    DateConfig,
    ExecutionConfig,
    FrameConfig,
    OptionalConfig,
    SimulatorConfig,
    TradeConfig,
)
from finter.backtest.simulators.basic import BasicBacktestor
from finter.backtest.simulators.id_fund import IDFundBacktestor
from finter.backtest.simulators.vn import VNBacktestor
from finter.settings import logger

POSITION_SCALAR = 1e8
BASIS_POINT_SCALAR = 10000


@dataclass
class SimulatorBuilder:
    data: DataConfig = field(default_factory=DataConfig)

    date: DateConfig = field(default_factory=DateConfig)
    cost: CostConfig = field(default_factory=CostConfig)
    trade: TradeConfig = field(default_factory=TradeConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    optional: OptionalConfig = field(default_factory=OptionalConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    frame: FrameConfig = field(default_factory=FrameConfig)

    def __repr__(self) -> str:
        return (
            "SimulatorBuilder(\n"
            f"    data={self.data},\n"
            f"    date={self.date},\n"
            f"    trade={self.trade},\n"
            f"    cost={self.cost},\n"
            f"    execution={self.execution},\n"
            f"    optional={self.optional},\n"
            f"    cache={self.cache},\n"
            f"    frame={self.frame}\n"
            ")"
        )

    def strptime_with_length(self, date_str):
        if len(date_str) == 8:
            return datetime.strptime(date_str, "%Y%m%d")
        elif len(date_str) == 12:
            return datetime.strptime(date_str, "%Y%m%d%H%M")
        else:
            raise ValueError(f"{date_str} format is not supported")

    def build(self, position: pd.DataFrame) -> BaseBacktestor:
        start_date = self.strptime_with_length(str(self.date.start))
        end_date = self.strptime_with_length(str(self.date.end))
        position = position.loc[start_date:end_date]

        if position.empty or self.data.price.empty:
            raise ValueError("Both position and price data are required")

        self.__validate_config()
        data_config = self.__build_data(position)
        self.frame = self.__build_frame(data_config)
        config = self.__build_config()
        input_vars = self.__build_input_vars(config, data_config)

        if self.execution.core_type == "basic":
            return BasicBacktestor(config, input_vars, results=self.optional.results)
        elif self.execution.core_type == "id_fund":
            return IDFundBacktestor(config, input_vars, results=self.optional.results)
        elif self.execution.core_type == "vn":
            return VNBacktestor(config, input_vars, results=self.optional.results)
        else:
            raise ValueError(f"Unknown core type: {self.execution.core_type}")

    def __validate_config(self):
        """Validate configuration settings and their combinations."""
        # if self.execution.drip is None and self.cost.dividend_tax != 0:
        # raise ValueError("Dividend tax cannot be applied when DRIP is not set")

        if self.execution.drip and self.data.dividend_ratio.empty:
            raise ValueError("Dividend ratio is required for drip")

        # if not self.data.money_flow.empty and self.trade.initial_cash != 0:
        #     raise ValueError("Initial cash must be 0 when money flow is provided")

        if self.trade.volume_capacity_ratio != 0 and self.data.volume.empty:
            raise ValueError("Volume data is required when volume_capacity_ratio > 0")

        if not (0 <= self.trade.volume_capacity_ratio <= 1):
            raise ValueError("Volume capacity ratio must be between 0 and 1")

        if self.date.start >= self.date.end:
            raise ValueError("Start date must be earlier than end date")

    def __build_input_vars(
        self, config: SimulatorConfig, data_config: DataConfig
    ) -> InputVars:
        weight, price = DataProcessor.preprocess_position(config, data_config)

        adjustment_ratio = DataProcessor.preprocess_adjustment_ratio(
            config, data_config
        )

        rebalancing_mask = DataProcessor.preprocess_rebalancing_mask(
            config, data_config
        )
        capital_gain_tax_mask = DataProcessor.preprocess_capital_gain_tax_mask(
            config, data_config
        )

        target_volume_limit = DataProcessor.preprocess_target_volume_limit(
            config, data_config
        )
        volume_capacity = DataProcessor.preprocess_volume_capacity(config, data_config)

        dividend_ratio = DataProcessor.preprocess_dividend_ratio(config, data_config)
        exchange_rate = DataProcessor.preprocess_exchange_rate(config, data_config)
        money_flow = DataProcessor.preprocess_money_flow(config, data_config)

        buy_price = price * (1 + self.cost.slippage)
        sell_price = price * (1 - self.cost.slippage)

        input_vars = InputVars(
            weight=weight,
            price=price,
            adjustment_ratio=adjustment_ratio,
            buy_price=buy_price,
            sell_price=sell_price,
            volume_capacity=volume_capacity,
            target_volume_limit=target_volume_limit,
            rebalancing_mask=rebalancing_mask,
            capital_gain_tax_mask=capital_gain_tax_mask,
            dividend_ratio=dividend_ratio,
            exchange_rate=exchange_rate,
            money_flow=money_flow,
        )
        return input_vars

    def __build_frame(self, data_config: DataConfig) -> FrameConfig:
        return FrameConfig(
            shape=data_config.price.shape,
            common_columns=data_config.position.columns.intersection(
                data_config.price.columns
            ).tolist(),
            common_index=data_config.price.index.tolist(),
        )

    def __build_config(self) -> SimulatorConfig:
        return SimulatorConfig(
            date=self.date,
            cost=self.cost,
            trade=self.trade,
            execution=self.execution,
            optional=self.optional,
            cache=self.cache,
            frame=self.frame,
        )

    def __build_data(self, position: pd.DataFrame) -> DataConfig:
        def _filter_nonzero_and_common_columns(
            position: pd.DataFrame, price: pd.DataFrame
        ) -> Tuple[pd.DataFrame, pd.DataFrame]:
            non_zero_columns = position.columns[position.sum() != 0]

            missing_columns = set(non_zero_columns) - set(price.columns)
            if missing_columns:
                logger.warning(
                    f"Missing price data for positions with non-zero values: {missing_columns}"
                )
                # raise ValueError(
                #     f"Missing price data for positions with non-zero values: {missing_columns}"
                # )

            position = position[non_zero_columns]
            price = price[non_zero_columns]

            common_columns = position.columns.intersection(price.columns)
            if len(common_columns) == 0:
                raise ValueError("No overlapping columns between position and price")

            position = position[common_columns]
            price = price[common_columns]

            return position, price

        def _align_index_with_price(
            position: pd.DataFrame, price: pd.DataFrame
        ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
            start_date = (
                (position.reindex_like(price).shift(-1).notna() * price.notna())
                .any(axis=1)
                .idxmax()
            )

            position = position.loc[start_date:]
            price = price.loc[start_date:]
            position_start_date = position.index.min()

            if price.loc[:position_start_date].empty:
                logger.warning(
                    "No price data before position start date. "
                    "Position data will be trimmed to match available price data.",
                )
                price_start_date = price.index[0]
            else:
                price_start_date = price.loc[:position_start_date].index[-1]

            common_end_date = min(position.index[-1], price.index[-1])
            price = price.loc[price_start_date:common_end_date]
            position = position.reindex(price.index)

            return position, price, price_start_date

        def _align_data_with_position(
            df: pd.DataFrame,
            price_start_date: pd.Timestamp,
            position: pd.DataFrame,
            align_columns: bool = True,
            union_ffill: bool = False,
        ) -> pd.DataFrame:
            if df.empty:
                return df

            df = df.loc[price_start_date:]

            if union_ffill:
                union_index = df.index.union(position.index)
                df = df.reindex(union_index).sort_index().ffill()

            if align_columns:
                df = df.reindex(index=position.index, columns=position.columns)
            else:
                df = df.reindex(index=position.index)
            return df.loc[: position.index[-1]]

        price = self.data.price
        adjustment_ratio = self.data.adjustment_ratio

        volume = self.data.volume
        constituent = self.data.constituent

        dividend_ratio = self.data.dividend_ratio
        exchange_rate = self.data.exchange_rate
        money_flow = self.data.money_flow

        if not position.empty and not price.empty:
            position, price = _filter_nonzero_and_common_columns(position, price)
            position, price, price_start_date = _align_index_with_price(position, price)

            adjustment_ratio = _align_data_with_position(
                adjustment_ratio, price_start_date, position
            )

            volume = _align_data_with_position(volume, price_start_date, position)
            constituent = _align_data_with_position(
                constituent, price_start_date, position
            )

            dividend_ratio = _align_data_with_position(
                dividend_ratio, price_start_date, position
            )
            exchange_rate = _align_data_with_position(
                exchange_rate, price_start_date, position, align_columns=False
            )

            # Todo: aum != money_flow.cumsum()
            # need assert ..?
            aum = _align_data_with_position(
                money_flow.cumsum(),
                price_start_date,
                position,
                align_columns=False,
                union_ffill=True,
            ).fillna(0)
            if not aum.empty:
                money_flow = aum.diff().fillna(aum.iloc[0])
                self.trade.initial_cash = float(money_flow.values[0])
                logger.info(
                    f"Initial cash is set to the first value of money flow: {self.trade.initial_cash}",
                )

        return DataConfig(
            position=position,
            price=price,
            adjustment_ratio=adjustment_ratio,
            volume=volume,
            constituent=constituent,
            dividend_ratio=dividend_ratio,
            exchange_rate=exchange_rate,
            money_flow=money_flow,
        )

    def update_data(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(DataConfig))
        if invalid_params:
            raise ValueError(f"Invalid parameters for DataConfig: {invalid_params}")

        data_params = {
            slot: kwargs.get(slot, getattr(self.data, slot))
            for slot in slots(DataConfig)
        }

        self.data = DataConfig(**data_params)
        return self

    def update_date(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(DateConfig))
        if invalid_params:
            raise ValueError(f"Invalid parameters for DateConfig: {invalid_params}")

        date_params = {
            slot: kwargs.get(slot, getattr(self.date, slot))
            for slot in slots(DateConfig)
        }

        self.date = DateConfig(**date_params)
        return self

    def update_cost(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(CostConfig))
        if invalid_params:
            raise ValueError(f"Invalid parameters for CostConfig: {invalid_params}")

        # Convert basis points to decimal if provided
        for param in [
            "buy_fee_tax",
            "sell_fee_tax",
            "slippage",
            "dividend_tax",
            "capital_gain_tax",
        ]:
            if param in kwargs:
                kwargs[param] = kwargs[param] / BASIS_POINT_SCALAR

        cost_params = {
            slot: kwargs.get(slot, getattr(self.cost, slot))
            for slot in slots(CostConfig)
        }

        self.cost = CostConfig(**cost_params)
        return self

    def update_trade(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(TradeConfig))
        if invalid_params:
            raise ValueError(f"Invalid parameters for TradeConfig: {invalid_params}")

        for param in ["deposit_interest_rate"]:
            if param in kwargs:
                if param == "deposit_interest_rate":
                    kwargs[param] = kwargs[param] / (252 * BASIS_POINT_SCALAR)

        trade_params = {
            slot: kwargs.get(slot, getattr(self.trade, slot))
            for slot in slots(TradeConfig)
        }

        self.trade = TradeConfig(**trade_params)
        return self

    def update_execution(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(ExecutionConfig))
        if invalid_params:
            raise ValueError(
                f"Invalid parameters for ExecutionConfig: {invalid_params}"
            )

        execution_params = {
            slot: kwargs.get(slot, getattr(self.execution, slot))
            for slot in slots(ExecutionConfig)
        }

        self.execution = ExecutionConfig(**execution_params)
        return self

    def update_optional(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(OptionalConfig))
        if invalid_params:
            raise ValueError(f"Invalid parameters for OptionalConfig: {invalid_params}")

        optional_params = {
            slot: kwargs.get(slot, getattr(self.optional, slot))
            for slot in slots(OptionalConfig)
        }

        self.optional = OptionalConfig(**optional_params)
        return self

    def update_cache(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(CacheConfig))
        if invalid_params:
            raise ValueError(f"Invalid parameters for CacheConfig: {invalid_params}")

        cache_params = {
            slot: kwargs.get(slot, getattr(self.cache, slot))
            for slot in slots(CacheConfig)
        }

        self.cache = CacheConfig(**cache_params)
        return self

    def update(self, **kwargs) -> "SimulatorBuilder":
        """
        Update any configuration options in a single call.
        Uses __slots__ from Config classes to determine which parameters belong where.

        Raises:
            ValueError: If an unknown parameter is provided
        """
        updates = {
            "data": {},
            "date": {},
            "cost": {},
            "trade": {},
            "execution": {},
            "optional": {},
            "cache": {},
        }

        # Track unknown parameters
        unknown_params = []

        # Sort parameters into their respective config updates
        for key, value in kwargs.items():
            if key in slots(DataConfig):
                updates["data"][key] = value
            elif key in slots(DateConfig):
                updates["date"][key] = value
            elif key in slots(CostConfig):
                updates["cost"][key] = value
            elif key in slots(TradeConfig):
                updates["trade"][key] = value
            elif key in slots(ExecutionConfig):
                updates["execution"][key] = value
            elif key in slots(OptionalConfig):
                updates["optional"][key] = value
            elif key in slots(CacheConfig):
                updates["cache"][key] = value
            else:
                unknown_params.append(key)

        # Raise error if unknown parameters were provided
        if unknown_params:
            raise ValueError(
                f"Unknown parameter(s): {', '.join(unknown_params)}. "
                "Please check the parameter names and try again."
            )

        if updates["data"]:
            self.update_data(**updates["data"])
        if updates["date"]:
            self.update_date(**updates["date"])
        if updates["cost"]:
            self.update_cost(**updates["cost"])
        if updates["trade"]:
            self.update_trade(**updates["trade"])
        if updates["execution"]:
            self.update_execution(**updates["execution"])
        if updates["optional"]:
            self.update_optional(**updates["optional"])
        if updates["cache"]:
            self.update_cache(**updates["cache"])

        return self


def slots(cls):
    return [f.name for f in fields(cls)]
