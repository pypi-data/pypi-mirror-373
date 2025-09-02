from abc import ABCMeta, abstractmethod

import pandas as pd

from finter.framework_model import ContentModelLoader


class BaseAlpha(metaclass=ABCMeta):
    __CM_LOADER = ContentModelLoader()
    __cm_set = set()

    start, end, universe, data_handler = None, None, None, None

    @abstractmethod
    def get(self, start, end):
        pass

    @classmethod
    def get_cm(cls, key):
        if key.startswith("content."):
            cls.__cm_set.add(key)
        else:
            cls.__cm_set.add("content." + key)
        return cls.__CM_LOADER.load(key)

    def depends(self):
        return self.__cm_set

    @staticmethod
    def cleanup_position(position: pd.DataFrame):
        df_cleaned = position.loc[:, ~((position == 0) | (position.isna())).all(axis=0)]
        if df_cleaned.empty:
            df_cleaned = position

        return df_cleaned.fillna(0)

    def backtest(self, universe=None, start=None, end=None, data_handler=None):
        """
        Backtest the alpha.

        Parameters:
        ----------
        universe : str, optional
            Universe to use (defaults to self.universe or raises error)
        start, end : int
            Date range for backtesting
        data_handler : DataHandler, optional
            Data handler to use (defaults to self.data_handler or raises error)

        Returns:
        -------
        pd.DataFrame
            Summary DataFrame with the backtest results
        """
        from finter.backtest.__legacy_support.main import Simulator

        if universe is not None:
            self.universe = universe
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end
        if data_handler is not None:
            self.data_handler = data_handler

        # Collect missing attributes in a list comprehension
        missing_attrs = [
            attr
            for attr in [
                "start",
                "end",
                "universe",
            ]
            if getattr(self, attr) is None
        ]
        if missing_attrs:
            # Raise a ValueError with a concise message
            raise ValueError(
                f"Missing required attributes: {', '.join(missing_attrs)}. Please set them before calling backtest(). or backtest(start, end, universe)"
            )

        simulator = Simulator(self.start, self.end, data_handler=self.data_handler)
        simulator = simulator.run(
            universe=self.universe, position=self.get(self.start, self.end)
        )
        return simulator.summary

    def analyze_parameters(self, params, universe, start, end, n_jobs=4, dry_run=False):
        """
        Analyze different parameter combinations for this alpha.

        Parameters:
        ----------
        params : dict
            Dictionary with parameter names as keys and lists of values to test
        start, end : int
            Date range for backtesting
        universe : str, optional
            Universe to use (defaults to self.universe or raises error)
        n_jobs : int, default=4
            Number of parallel workers
        dry_run : bool, default=False
            If True, only shows execution plan without running

        Returns:
        -------
        pd.DataFrame
            Results with metrics and parameter combinations
        """
        from finter.backtest import Simulator
        from finter.backtest.parameter_analyzer import ParameterAnalyzer

        # Create simulator
        simulator = Simulator(universe)

        # Create analyzer and run analysis
        analyzer = ParameterAnalyzer(self.__class__, simulator)
        return analyzer.analyze_all(params, start, end, n_jobs=n_jobs, dry_run=dry_run)


"""
from finter import BaseAlpha
from finter.data import ContentFactory


class Alpha(BaseAlpha):
    universe = "id_stock"

    def get(self, start, end):
        cf = ContentFactory(self.universe, start, end)
        df = cf.get_df("price_close")
        return df


if __name__ == "__main__":
    alpha = Alpha()
    res = alpha.backtest(universe=alpha.universe, start=20230101, end=20240101)
"""
