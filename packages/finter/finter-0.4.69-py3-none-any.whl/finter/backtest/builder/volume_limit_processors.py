from abc import ABC, abstractmethod
from typing import Any, Dict, Type

import numpy as np

from finter.backtest.config.config import DataConfig, SimulatorConfig


class VolumeLimitProcessor(ABC):
    @abstractmethod
    def process(
        self, config: SimulatorConfig, data: DataConfig, proc_config: Dict[str, Any]
    ) -> np.ndarray:
        pass


class TradingVolumeProcessor(VolumeLimitProcessor):
    def process(
        self, config: SimulatorConfig, data: DataConfig, proc_config: Dict[str, Any]
    ) -> np.ndarray:
        if proc_config is None:
            return np.array([])

        return np.nan_to_num(
            (
                data.volume.fillna(0)
                .rolling(
                    proc_config["rolling_window"],
                    min_periods=1,
                )
                .mean()
                * proc_config["limit_ratio"]
            ).to_numpy()
        )


class UniverseProcessor(VolumeLimitProcessor):
    def process(
        self, config: SimulatorConfig, data: DataConfig, proc_config: Dict[str, Any]
    ) -> np.ndarray:
        if proc_config is None:
            return np.array([])

        return np.nan_to_num((data.constituent).fillna(0).to_numpy())


class VolumeLimitProcessorFactory:
    _processors: Dict[str, Type[VolumeLimitProcessor]] = {
        "trading_volume": TradingVolumeProcessor,
        "universe": UniverseProcessor,
    }

    @classmethod
    def register_processor(
        cls, type_name: str, processor_class: Type[VolumeLimitProcessor]
    ) -> None:
        cls._processors[type_name] = processor_class

    @classmethod
    def get_processor(cls, type_name: str) -> VolumeLimitProcessor:
        processor_class = cls._processors.get(type_name)
        if processor_class is None:
            raise ValueError(f"Unknown volume limit processor type: {type_name}")
        return processor_class()

    @classmethod
    def process(cls, config: SimulatorConfig, data: DataConfig) -> np.ndarray:
        if config.trade.target_volume_limit_args is None:
            return np.array([])

        args = config.trade.target_volume_limit_args

        if "processors" not in args:
            raise ValueError(
                "target_volume_limit_args must contain a 'processors' key with a list of processor configurations"
            )

        processor_configs = args["processors"]
        results = []

        for proc_config in processor_configs:
            type_name = proc_config["type"]
            processor = cls.get_processor(type_name)
            result = processor.process(config, data, proc_config)
            results.append(result)
        if not results:
            return np.array([])

        if len(results) == 1:
            result = results[0]
        else:
            result = np.minimum.reduce(results)

        # combined_result = results[0]
        # for result in results[1:]:
        # if result.size > 0 and combined_result.size > 0:
        # combined_result = np.minimum(combined_result, result)

        return result
