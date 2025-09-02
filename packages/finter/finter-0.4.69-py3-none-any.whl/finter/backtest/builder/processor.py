import typing
from typing import Literal

import numpy as np

from finter.backtest.builder.volume_limit_processors import VolumeLimitProcessorFactory
from finter.backtest.config.config import DataConfig, SimulatorConfig
from finter.modeling.utils import daily2period, get_rebalancing_mask

POSITION_SCALAR = 1e8
BASIS_POINT_SCALAR = 10000


class DataProcessor:
    def __init__(self):
        pass

    @staticmethod
    def preprocess_position(config: SimulatorConfig, data: DataConfig):
        if config.execution.resample_period:
            position = daily2period(
                data.position,
                config.execution.resample_period,
                keep_index=True,
            )
        else:
            position = data.position

        return (
            np.nan_to_num((position / POSITION_SCALAR).to_numpy()),
            data.price.to_numpy(),
        )

    @staticmethod
    def preprocess_rebalancing_mask(config: SimulatorConfig, data: DataConfig):
        period = config.execution.rebalancing_method
        if period in ("W", "M", "Q"):
            casted_period = typing.cast(Literal["W", "M", "Q"], period)
            return np.array(
                [
                    d in get_rebalancing_mask(data.position, casted_period)
                    for d in config.frame.common_index
                ],
                dtype=int,
            )
        else:
            return np.array([])

    @staticmethod
    def preprocess_capital_gain_tax_mask(config: SimulatorConfig, data: DataConfig):
        if config.cost.capital_gain_tax != 0:
            return np.array(
                [
                    d in get_rebalancing_mask(data.position, "Y")
                    for d in config.frame.common_index
                ],
                dtype=int,
            )
        else:
            return np.array([])

    @staticmethod
    def preprocess_dividend_ratio(config: SimulatorConfig, data: DataConfig):
        if data.dividend_ratio.empty:
            return np.full(
                (len(config.frame.common_index), len(config.frame.common_columns)),
                0,
            )
        else:
            return data.dividend_ratio.to_numpy()

    @staticmethod
    def preprocess_exchange_rate(config: SimulatorConfig, data: DataConfig):
        if data.exchange_rate.empty:
            return np.full(
                (len(config.frame.common_index), 1),
                1,
            )
        else:
            return data.exchange_rate.to_numpy()

    @staticmethod
    def preprocess_money_flow(config: SimulatorConfig, data: DataConfig):
        if data.money_flow.empty:
            return np.full(
                (len(config.frame.common_index), 1),
                0,
            )
        else:
            return np.nan_to_num(data.money_flow.to_numpy())

    @staticmethod
    def preprocess_target_volume_limit(config: SimulatorConfig, data: DataConfig):
        volume_limit = VolumeLimitProcessorFactory.process(config, data)
        return volume_limit

    @staticmethod
    def preprocess_volume_capacity(config: SimulatorConfig, data: DataConfig):
        if config.trade.volume_capacity_ratio == 0:
            return np.full(
                (len(config.frame.common_index), len(config.frame.common_columns)),
                np.inf,
            )
        else:
            volume = data.volume.reindex(
                config.frame.common_index,
                columns=config.frame.common_columns,
            )
            adjustment_ratio = data.adjustment_ratio.reindex(
                config.frame.common_index,
                columns=config.frame.common_columns,
            )
            return (
                volume.fillna(0).to_numpy()
                * config.trade.volume_capacity_ratio
                * adjustment_ratio.ffill().to_numpy()
            )

    @staticmethod
    def preprocess_adjustment_ratio(config: SimulatorConfig, data: DataConfig):
        if data.adjustment_ratio.empty:
            return np.full(
                (len(config.frame.common_index), len(config.frame.common_columns)),
                1.0,
            )
        else:
            adjustment_ratio = data.adjustment_ratio.reindex(
                config.frame.common_index,
                columns=config.frame.common_columns,
            )
            return adjustment_ratio.ffill().to_numpy()
