from datetime import datetime
from typing import cast

import numpy as np
import pandas as pd
from typing_extensions import Unpack

from finter.backtest.config.simulator import SimulatorInputConfig
from finter.backtest.config.templates import (
    AVAILABLE_MARKETS,
    MarketTemplates,
)
from finter.data.data_handler.main import DataHandler
from finter.log import PromtailLogger


class Simulator:
    # Class-level caching for DataHandler (existing)
    _data_handler_instance = None
    _cached_start = None
    _cached_end = None

    # Class-level caching for Simulator instances - one per market_type (갈아끼우기 방식)
    _cached_simulators = {}  # {market_type: (cache_key, simulator_instance)}

    def __init__(
        self,
        market_type: AVAILABLE_MARKETS | list[AVAILABLE_MARKETS],
        start: int = 20000101,
        end: int = int(datetime.now().strftime("%Y%m%d")),
        _handler_cls=DataHandler,
    ):
        self.market_type = market_type

        # If market_type is a list, use MultiMarketSimulator
        if isinstance(market_type, list):
            # Lazy import to avoid circular dependency
            from finter.backtest.simulators.multi_market.main import (
                MultiMarketSimulator,
            )

            self._multi_market_simulator = MultiMarketSimulator(
                start=start, end=end, market_types=market_type
            )

            return

        # Single market case - check cache first
        cache_key = (market_type, start, end, _handler_cls)
        if market_type in self.__class__._cached_simulators:
            cached_key, cached_instance = self.__class__._cached_simulators[market_type]
            if cached_key == cache_key:
                # Copy attributes from cached instance and return
                self.__dict__.update(cached_instance.__dict__)
                return

        # No cache or different parameters - initialize normally
        self.data_handler = self._get_cached_data_handler(
            _handler_cls=_handler_cls,
            start=start,
            end=end,
            cache_timeout=300,
        )

        self.builder = MarketTemplates.create_simulator(
            cast(AVAILABLE_MARKETS, self.market_type)
        )
        self.set_market_builder()

        # Configuration attributes initialized later
        self.use_currency = None
        self.use_volume_capacity_ratio = None
        self.use_target_volume_limit = None
        self.use_sub_universe = None
        self.use_drip = None

    @classmethod
    def get_cached_instance(
        cls,
        market_type: AVAILABLE_MARKETS | list[AVAILABLE_MARKETS],
        start: int = 20000101,
        end: int = int(datetime.now().strftime("%Y%m%d")),
        _handler_cls=DataHandler,
    ):
        """Get or refresh a single cached Simulator per market_type.

        - Only one simulator is cached per market_type.
        - If start/end differ from the cached key, refresh the cached instance instead of creating multiple.
        """
        if isinstance(market_type, list):
            # For multi-market, do not cache wrapper here; return a fresh one
            return cls(
                market_type=market_type,
                start=start,
                end=end,
                _handler_cls=_handler_cls,
            )

        cache_key = (market_type, start, end, _handler_cls)

        # If an instance exists for this market_type
        if market_type in cls._cached_simulators:
            prev_key, instance = cls._cached_simulators[market_type]
            if prev_key == cache_key:
                return instance
            # Refresh existing instance for new period
            instance.data_handler = cls._get_cached_data_handler(
                _handler_cls=_handler_cls,
                start=start,
                end=end,
                cache_timeout=300,
            )
            instance.set_market_builder()
            cls._cached_simulators[market_type] = (cache_key, instance)
            return instance

        # No cached instance yet: create and cache
        instance = cls(
            market_type=market_type,
            start=start,
            end=end,
            _handler_cls=_handler_cls,
        )
        cls._cached_simulators[market_type] = (cache_key, instance)
        return instance

    def build(self, position: pd.DataFrame, **kwargs: Unpack[SimulatorInputConfig]):
        # Configure runtime settings
        kwargs = self._configure_settings(**kwargs)

        # Initialize additional data if needed
        self._load_additional_data()

        # Update builder with kwargs
        self.builder.update(**kwargs)

        # Create a copy of position and truncate values
        position_copy = position.copy()
        position_copy.iloc[:, :] = np.trunc(position_copy.values / 1e4) * 1e4

        # Build simulator
        return self.builder.build(position_copy)

    def run(self, position: pd.DataFrame, **kwargs: Unpack[SimulatorInputConfig]):
        if isinstance(self.market_type, list):
            for market_type in self.market_type:
                self._multi_market_simulator.update_market_config(market_type, **kwargs)
            summary = self._multi_market_simulator.run(position, **kwargs)
            self._multi_market_simulator.summary = summary
            return self._multi_market_simulator

        simulator = self.build(position, **kwargs)

        # Run simulator with logging
        return self._execute_simulation(simulator)

    def _configure_settings(self, **kwargs: Unpack[SimulatorInputConfig]):
        """Configure simulator settings from provided arguments."""
        self.use_currency = kwargs.pop("currency", None)

        self.use_volume_capacity_ratio = kwargs.get(
            "volume_capacity_ratio",
            getattr(self.builder.trade, "volume_capacity_ratio", None),
        )

        self._configure_volume_limit(
            kwargs.get(
                "target_volume_limit_args",
                getattr(self.builder.trade, "target_volume_limit_args", None),
            )
        )

        self.use_drip = kwargs.get(
            "drip",
            getattr(self.builder.execution, "drip", None),
        )
        return kwargs

    def _configure_volume_limit(self, target_volume_limit_args):
        """Configure volume limit settings."""
        if target_volume_limit_args is None:
            self.use_target_volume_limit = None
            self.use_sub_universe = None
            return

        processor_configs = target_volume_limit_args.get("processors", None)
        if not processor_configs:
            self.use_target_volume_limit = None
            self.use_sub_universe = None
            return

        types = [p.get("type") for p in processor_configs]
        if None in types:
            raise ValueError("Each processor config must include a 'type' key")
        if len(set(types)) != len(types):
            raise ValueError("Processor 'type' must be unique")

        # Extract universes if universe processor exists
        self.use_sub_universe = None
        if "universe" in types:
            self.use_sub_universe = processor_configs[types.index("universe")].get(
                "sub_universe", None
            )

        # Set target volume limit if trading_volume processor exists
        self.use_target_volume_limit = (
            target_volume_limit_args if "trading_volume" in types else None
        )

    def _execute_simulation(self, simulator):
        """Execute simulation with error handling and logging."""
        try:
            simulator.run()
            status = "success"
        except Exception as e:
            status = "error"
            raise e
        finally:
            try:
                PromtailLogger.send_log(
                    level="INFO",
                    message=f"{self.market_type}",
                    service="finterlabs-jupyterhub",
                    user_id=PromtailLogger.get_user_info(),
                    operation="simulation",
                    status=status,
                )
            except Exception:
                # Avoid masking original exceptions due to logging failures
                pass

        return simulator

    def _load_additional_data(self):
        """Load additional data based on configuration settings."""
        self._load_drip_data()
        self._load_currency_data()
        self._load_volume_data()
        self._load_universe_data()

    def _load_drip_data(self):
        """Load dividend data if drip is enabled."""
        if self.use_drip:
            self.builder.update_data(
                dividend_ratio=self.data_handler.universe(cast(str, self.market_type))
                .dividend_factor()
                .dropna(how="all")
            )

    def _load_currency_data(self):
        """Load currency exchange rate data if needed."""
        if self.use_currency is None:
            return

        base_currency = MarketTemplates.get_config_value(
            cast(AVAILABLE_MARKETS, self.market_type),
            "base_currency",
        )

        if base_currency == self.use_currency:
            self.builder.update_data(exchange_rate=pd.DataFrame())

        currency_data = self.data_handler.common.currency()
        if (
            self.use_currency in currency_data.columns
            and base_currency in currency_data.columns
        ):
            exchange_rate = (
                currency_data[self.use_currency] / currency_data[base_currency]
            )
            exchange_rate = exchange_rate.ffill()
            self.builder.update_data(exchange_rate=exchange_rate)
        else:
            raise ValueError(
                f"No exchange rate found for conversion from {base_currency} to {self.use_currency}"
            )

    def _load_volume_data(self):
        """Load volume data if needed for capacity calculations."""
        needs_volume = (
            self.use_volume_capacity_ratio is not None
            and 0 < self.use_volume_capacity_ratio <= 1
        ) or (self.use_target_volume_limit is not None)

        if needs_volume:
            self.builder.update_data(
                volume=self.data_handler.universe(cast(str, self.market_type)).volume(),
            )

    def _load_universe_data(self):
        """Load constituent data for sub-universes."""
        if self.use_sub_universe is None:
            return

        constituent = pd.concat(
            [
                self.data_handler.common.constituent(sub_universe=sub_universe)
                for sub_universe in self.use_sub_universe
            ],
            axis=1,
        )
        constituent = constituent.groupby(level=0, axis=1).sum()
        constituent = (constituent > 0).astype(int) * np.inf
        self.builder.update_data(constituent=constituent.fillna(0))

    @classmethod
    def _get_cached_data_handler(cls, _handler_cls, **kwargs):
        """Get or create a cached data handler instance."""
        start = kwargs.get("start")
        end = kwargs.get("end")

        if (
            cls._data_handler_instance is None
            or start != cls._cached_start
            or end != cls._cached_end
            or not isinstance(cls._data_handler_instance, _handler_cls)
        ):
            cls._data_handler_instance = _handler_cls(**kwargs)
            cls._cached_start = start
            cls._cached_end = end
        return cls._data_handler_instance

    def set_market_builder(self):
        """Initialize market builder with price and adjustment data."""
        price = (
            self.data_handler.universe(cast(str, self.market_type))
            .price(adj=False)
            .dropna(how="all")
        )
        if self.market_type in ("us_stock", "us_etf", "id_bond"):
            price = price.ffill()
        elif self.market_type == "btcusdt_spot_binance":
            # Vectorized and safer numeric conversion
            price = price.apply(pd.to_numeric, errors="coerce")

        adjustment_ratio = self.data_handler.universe(
            cast(str, self.market_type)
        ).adjustment_ratio()

        self.builder.update_data(price=price, adjustment_ratio=adjustment_ratio)

    def post_init(self):
        """Legacy method, now replaced by _load_additional_data."""
        self._load_additional_data()
