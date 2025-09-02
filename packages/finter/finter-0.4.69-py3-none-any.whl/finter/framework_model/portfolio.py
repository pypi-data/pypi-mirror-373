from abc import ABC
from typing import Optional

from datetime import datetime
import numpy as np
import pandas as pd

from finter.framework_model import ContentModelLoader
from finter.framework_model.alpha_loader import AlphaPositionLoader


def datestr(date_int: int):
    date_str = str(date_int)
    
    length = len(date_str)
    if length == 8:
        fmt = "%Y%m%d"
    elif length == 10:
        fmt = "%Y%m%d%H"
    elif length == 12:
        fmt = "%Y%m%d%H%M"
    elif length == 14:
        fmt = "%Y%m%d%H%M%S"
        
    return datetime.strptime(date_str, fmt)


def signal(func):
    """
    A decorator to wrap a method to be a signal method.
    """
    func._is_signal = True
    return func


class BasePortfolio(ABC):
    __cm_set = set()
    alpha_list = []
    alpha_set = {}

    class AlphaLoader:
        """to support legacy portfolio"""

        def __init__(self, start: int, end: int):
            self.start = datestr(start)
            self.end = datestr(end)
            self._cache = {}

        def get_alpha(self, alpha):
            from finter.data import ModelData

            if alpha not in self._cache:
                self._cache[alpha] = ModelData.load("alpha." + alpha)
            return self._cache[alpha].loc[self.start : self.end]

    def alpha_loader_v2(self, start: int, end: int):
        if (
            not hasattr(self, "_BasePortfolio__alpha_loader")
            or self.__alpha_loader is None
        ):
            self.__alpha_loader = BasePortfolio.AlphaLoader(start, end)
        if self.__alpha_loader.start != datestr(
            start
        ) or self.__alpha_loader.end != datestr(end):
            self.__alpha_loader = BasePortfolio.AlphaLoader(start, end)
        return self.__alpha_loader

    @classmethod
    def _protected_methods(cls):
        return {
            "alpha_loader_v2",
            "get_signal_names",
            "get_signals",
            "depends",
            "get_alpha_position_loader",
        }

    def __setattr__(self, name, value):
        """Prevent overriding specific methods with instance variables"""
        if name in self._protected_methods():
            raise AttributeError(
                f"Cannot override method '{name}' with an instance variable"
            )
        super().__setattr__(name, value)

    def __init_subclass__(cls, **kwargs):
        """Prevent overriding specific methods in child classes"""
        super().__init_subclass__(**kwargs)
        for method in cls._protected_methods():
            if method in cls.__dict__:
                raise TypeError(
                    f"Class {cls.__name__} cannot override method '{method}'"
                )

    def _get_signal_methods(self):
        """Identify all methods marked with the `signal` decorator"""
        signal_methods = {}
        for base in reversed(self.__class__.__mro__[:-1]):  # object 클래스 제외
            for name, method in vars(base).items():
                if callable(method) and getattr(method, "_is_signal", False):
                    signal_methods[name] = getattr(
                        self, name
                    )  # base class 에 signal이 붙어 있으면 상속받은 클래스 method를 추가

        return signal_methods

    def get_signal_names(self):
        signal_methods = self._get_signal_methods()
        return signal_methods.keys()

    def get_signals(self, start, end):
        signal_methods = self._get_signal_methods()
        for name, method in signal_methods.items():
            yield name, method(start, end)

    def depends(self):
        if self.__class__.alpha_list:
            return set("alpha." + i for i in self.__class__.alpha_list) | self.__cm_set
        else:
            return set("alpha." + i for i in self.__class__.alpha_set) | self.__cm_set

    @classmethod
    def get_cm(cls, key):
        if key.startswith("content."):
            cls.__cm_set.add(key)
        else:
            cls.__cm_set.add("content." + key)
        return ContentModelLoader.load(key)

    def get_alpha_position_loader(
        self, start, end, exchange, universe, instrument_type, freq, position_type
    ):
        return AlphaPositionLoader(
            start,
            end,
            exchange,
            universe,
            instrument_type,
            freq,
            position_type,
            self.alpha_set,
        )

    def get(self, start, end):
        alpha_loader = self.alpha_loader_v2(start, end)

        alpha_dict: dict[str, pd.DataFrame] = {}
        weights = self.weight(start, end)

        assert weights is not None

        for alpha_idn in weights.columns:
            alpha = alpha_loader.get_alpha(alpha_idn)
            alpha.replace(0, np.nan, inplace=True)
            alpha.dropna(axis=1, how="all", inplace=True)
            alpha = alpha.fillna(0)

            # adjust wrong alpha position whose sum of row is greater than 1e8
            row_sums = alpha.sum(axis=1)
            scaling_factors = np.where(row_sums > 1e8, 1e8 / row_sums, 1)
            alpha = alpha.mul(scaling_factors, axis=0)

            alpha_dict[alpha_idn] = alpha.fillna(0)

        # union all indexes
        all_indices = None
        for df in alpha_dict.values():
            if all_indices is None:
                all_indices = df.index
            else:
                all_indices = all_indices.union(df.index)
        all_indices = all_indices.sort_values()

        # resample all alphas and forward fill
        for alpha_id in alpha_dict:
            alpha_dict[alpha_id] = alpha_dict[alpha_id].reindex(all_indices).ffill()

        weights = weights.reindex(all_indices).ffill()

        # 모든 알파들의 컬럼들을 합침
        all_columns = pd.Index([])
        for df in alpha_dict.values():
            all_columns = all_columns.union(df.columns)

        # 각 알파에 대해 없는 컬럼은 0으로 채움
        for alpha_id in alpha_dict:
            alpha_dict[alpha_id] = alpha_dict[alpha_id].reindex(
                columns=all_columns, fill_value=0
            )

        pf = sum(
            alpha_dict[alpha] * weights[alpha].values[:, None] for alpha in alpha_dict
        )

        return self.cleanup_position(pf.fillna(0)).loc[str(start) : str(end)]

    @signal
    def weight(self, start, end) -> Optional[pd.DataFrame]:
        """base weight of portfolio is equal weight"""

        alphas = [
            self.alpha_loader_v2(start, end).get_alpha(alpha)
            for alpha in self.alpha_list
        ]

        all_indices = None
        for alpha in alphas:
            if all_indices is None:
                all_indices = alpha.index
            else:
                all_indices = all_indices.union(alpha.index)
        all_indices = all_indices.sort_values()
        weight_df = pd.DataFrame(
            1 / len(self.alpha_list), index=all_indices, columns=self.alpha_list
        )
        return weight_df.loc[str(start) : str(end)]

    @staticmethod
    def cleanup_position(position: pd.DataFrame):
        df_cleaned = position.loc[:, ~((position == 0) | (position.isna())).all(axis=0)]
        if df_cleaned.empty:
            df_cleaned = position

        return df_cleaned.fillna(0)
        
    def get_alpha_dict(self, start: int, end: int):
        return {alpha: self.alpha_loader_v2(start, end).get_alpha(alpha) for alpha in self.alpha_list}
    
    def alpha_return_dict(self, universe: str, start: int, end: int):
        from finter.backtest.simulator import Simulator
        return_dict = self.get_alpha_dict(start, end)
        sim = Simulator(universe, start, end)
        for alpha, alpha_df in return_dict.items():
            res = sim.run(alpha_df.fillna(0), start = start, end = end, volume_capacity_ratio=0, target_volume_limit_args=None, rebalancing_method='auto')
            return_dict[alpha] = res.summary.daily_return
        return return_dict