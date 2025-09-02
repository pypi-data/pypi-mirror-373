from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
import pandas as pd


import pandas as pd

from finter.framework_model import ContentModelLoader
from finter.framework_model.portfolio_loader import PortfolioPositionLoader
from finter.framework_model.alpha_loader import AlphaPositionLoader


def datestr(date_int: int):
    date_str = str(date_int)
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"


def signal(func):
    """
    A decorator to wrap a method to be a signal method.
    """
    func._is_signal = True
    return func


class BaseFlexibleFund(ABC):
    __cm_set = set()

    class AlphaLoader:
        """to support legacy portfolio"""

        def __init__(self, start: int, end: int):
            self.start = datestr(start)
            self.end = datestr(end)
            self._cache = {}

        def get_alpha(self, alpha):
            from finter.data import ModelData

            if alpha not in self._cache:
                self._cache[alpha] = ModelData.load(alpha)
            return self._cache[alpha].loc[self.start : self.end]

    class PortfolioLoader:
        """to support legacy portfolio"""

        def __init__(self, start: int, end: int):
            self.start = datestr(start)
            self.end = datestr(end)
            self._cache = {}

        def get_portfolio(self, portfolio):
            from finter.data import ModelData

            if portfolio not in self._cache:
                self._cache[portfolio] = ModelData.load(portfolio)
            return self._cache[portfolio].loc[self.start : self.end]

    class FlexibleFundLoader:
        """to support legacy portfolio"""

        def __init__(self, start: int, end: int):
            self.start = datestr(start)
            self.end = datestr(end)
            self._cache = {}

        def get_flexible_fund(self, flexible_fund):
            from finter.data import ModelData

            if flexible_fund not in self._cache:
                self._cache[flexible_fund] = ModelData.load(flexible_fund)
            return self._cache[flexible_fund].loc[self.start : self.end]

    @property
    def alphas(self):
        return None

    @property
    @abstractmethod
    def portfolios(self):
        pass

    @property
    def flexible_funds(self):
        return None

    def depends(self):
        result = set(self.portfolios) | self.__cm_set
        if hasattr(self, "alphas") and self.alphas:
            result |= set(self.alphas)
        if hasattr(self, "flexible_funds") and self.flexible_funds:
            result |= set(self.flexible_funds)
        return result

    def alpha_loader(self, start: int, end: int):
        return BaseFlexibleFund.AlphaLoader(start, end)

    def portfolio_loader(self, start: int, end: int):
        return BaseFlexibleFund.PortfolioLoader(start, end)

    def flexible_fund_loader(self, start: int, end: int):
        return BaseFlexibleFund.FlexibleFundLoader(start, end)

    @classmethod
    def _protected_methods(cls):
        return {
            "alpha_loader",
            "portfolio_loader",
            "flexible_fund_loader",
            "depends",
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

    @classmethod
    def get_cm(cls, key):
        if key.startswith("content."):
            cls.__cm_set.add(key)
        else:
            cls.__cm_set.add("content." + key)
        return ContentModelLoader.load(key)

    def get_portfolio_position_loader(
        self, start, end, exchange, universe, instrument_type, freq, position_type
    ):
        return PortfolioPositionLoader(
            start,
            end,
            exchange,
            universe,
            instrument_type,
            freq,
            position_type,
            self.portfolios,
        )

    def get(self, start, end):
        alpha_loader = self.alpha_loader(start, end)
        portfolio_loader = self.portfolio_loader(start, end)
        flexible_fund_loader = self.flexible_fund_loader(start, end)

        strategy_dict: dict[str, pd.DataFrame] = {}
        weights = self.weight(start, end)

        assert weights is not None
        portfolio_strategies = [
            col for col in weights.columns if col.startswith("portfolio.")
        ]
        alpha_strategies = [col for col in weights.columns if col.startswith("alpha.")]
        flexible_fund_strategies = [
            col for col in weights.columns if col.startswith("flexible_fund.")
        ]

        for portfolio_strategy in portfolio_strategies:
            portfolio = portfolio_loader.get_portfolio(portfolio_strategy)
            portfolio.replace(0, np.nan, inplace=True)
            portfolio.dropna(axis=1, how="all", inplace=True)
            portfolio = portfolio.fillna(0)

            # adjust wrong alpha position whose sum of row is greater than 1e8
            row_sums = portfolio.sum(axis=1)
            scaling_factors = np.where(row_sums > 1e8, 1e8 / row_sums, 1)
            portfolio = portfolio.mul(scaling_factors, axis=0)

            strategy_dict[portfolio_strategy] = portfolio.fillna(0)

        for alpha_strategy in alpha_strategies:
            alpha = alpha_loader.get_alpha(alpha_strategy)
            alpha.replace(0, np.nan, inplace=True)
            alpha.dropna(axis=1, how="all", inplace=True)
            alpha = alpha.fillna(0)

            # adjust wrong alpha position whose sum of row is greater than 1e8
            row_sums = alpha.sum(axis=1)
            scaling_factors = np.where(row_sums > 1e8, 1e8 / row_sums, 1)
            alpha = alpha.mul(scaling_factors, axis=0)

            strategy_dict[alpha_strategy] = alpha.fillna(0)

        for flexible_fund_strategy in flexible_fund_strategies:
            flexible_fund = flexible_fund_loader.get_flexible_fund(
                flexible_fund_strategy
            )
            flexible_fund.replace(0, np.nan, inplace=True)
            flexible_fund.dropna(axis=1, how="all", inplace=True)
            flexible_fund = flexible_fund.fillna(0)

            # adjust wrong alpha position whose sum of row is greater than 1e8
            row_sums = flexible_fund.sum(axis=1)
            scaling_factors = np.where(row_sums > 1e8, 1e8 / row_sums, 1)
            flexible_fund = flexible_fund.mul(scaling_factors, axis=0)

            strategy_dict[flexible_fund_strategy] = flexible_fund.fillna(0)

        # union all indexes
        all_indices = None
        for df in strategy_dict.values():
            if all_indices is None:
                all_indices = df.index
            else:
                all_indices = all_indices.union(df.index)
        all_indices = all_indices.sort_values()

        # resample all alphas and forward fill
        for strategy in strategy_dict:
            strategy_dict[strategy] = (
                strategy_dict[strategy].reindex(all_indices).ffill()
            )

        weights = weights.reindex(all_indices).ffill()

        # 모든 알파들의 컬럼들을 합침
        all_columns = pd.Index([])
        for df in strategy_dict.values():
            all_columns = all_columns.union(df.columns)

        # 각 알파에 대해 없는 컬럼은 0으로 채움
        for strategy in strategy_dict:
            strategy_dict[strategy] = strategy_dict[strategy].reindex(
                columns=all_columns, fill_value=0
            )

        pf = sum(
            strategy_dict[strategy] * weights[strategy].values[:, None]
            for strategy in strategy_dict
        )

        return self.cleanup_position(pf.fillna(0)).loc[str(start) : str(end)]

    @signal
    def weight(self, start, end) -> Optional[pd.DataFrame]:
        """base weight of portfolio is equal weight"""
        strategy_list = self.portfolios.copy()
        sub_strategies = [
            self.portfolio_loader(start, end).get_portfolio(portfolio)
            for portfolio in self.portfolios
        ]
        if hasattr(self, "alphas") and self.alphas:
            strategy_list.extend(self.alphas)
            sub_strategies.extend(
                [
                    self.alpha_loader(start, end).get_alpha(alpha)
                    for alpha in self.alphas
                ]
            )
        if hasattr(self, "flexible_funds") and self.flexible_funds:
            strategy_list.extend(self.flexible_funds)
            sub_strategies.extend(
                [
                    self.flexible_fund_loader(start, end).get_flexible_fund(
                        flexible_fund
                    )
                    for flexible_fund in self.flexible_funds
                ]
            )

        all_indices = None
        for sub_strategy in sub_strategies:
            if all_indices is None:
                all_indices = sub_strategy.index
            else:
                all_indices = all_indices.union(sub_strategy.index)
        all_indices = all_indices.sort_values()
        weight_df = pd.DataFrame(
            1 / len(strategy_list), index=all_indices, columns=strategy_list
        )
        return weight_df.loc[str(start) : str(end)]

    @staticmethod
    def cleanup_position(position: pd.DataFrame):
        df_cleaned = position.loc[:, ~((position == 0) | (position.isna())).all(axis=0)]
        if df_cleaned.empty:
            df_cleaned = position

        return df_cleaned.fillna(0)
