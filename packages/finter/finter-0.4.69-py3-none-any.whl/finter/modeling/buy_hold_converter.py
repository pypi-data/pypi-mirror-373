import pandas as pd

from finter.data.data_handler.main import DataHandler
from finter.settings import logger


class BuyHoldConverter:
    """
    A class to convert buy-and-hold data with different rebalancing periods.
    """

    def __init__(self):
        pass

    def _get_price_data(self, universe, start, end, columns):
        """
        Retrieve price data for a given universe and date range.

        Parameters:
        - universe (str): The universe to retrieve data from (e.g., 'kr_stock').
        - start (int): The start date in YYYYMMDD format.
        - end (int): The end date in YYYYMMDD format.
        - columns (list): List of columns to retrieve.

        Returns:
        - DataFrame: The price data.
        """
        data_handler = DataHandler(start, end, cache_timeout=300)
        prc = data_handler.universe(universe).price()[columns]

        return prc

    def _get_date_range(self, df: pd.DataFrame) -> tuple:
        """
        Calculate the start and end dates based on the DataFrame index.

        Parameters:
        - df (DataFrame): The input DataFrame with a date index.

        Returns:
        - tuple: The start and end dates in YYYYMMDD format.
        """
        start, end = df.index[0], df.index[-1]
        start = (
            (start.year * 10000 + 101)
            if start.month == 1
            else ((start.year - 1) * 10000 + 1201)
        )
        end = end.year * 10000 + end.month * 100 + end.day
        return start, end

    def basic_converter(self, df: pd.DataFrame, universe: str) -> pd.DataFrame:
        """
        Convert the DataFrame using a basic buy-and-hold strategy.

        Parameters:
        - df (DataFrame): The input DataFrame with positions.
        - universe (str): The universe to retrieve price data from.

        Returns:
        - DataFrame: The transformed DataFrame.
        """
        start, end = self._get_date_range(df)

        # Keep only columns with non-zero sum
        df = df.loc[:, df.sum() != 0]

        # Retrieve price data for the given universe
        self.prc = self._get_price_data(universe, start, end, df.columns)

        # Copy the original and transformed DataFrames
        df_transformed = df.copy()
        prc_change = self.prc.pct_change(1, fill_method="pad").fillna(0).loc[df.index]

        # Apply transformation
        for i in range(1, df.shape[0]):
            if (df.iloc[i] == df.iloc[i - 1]).all():
                df_transformed.iloc[i] = df_transformed.iloc[i - 1] * (
                    1 + prc_change.iloc[i - 1]
                )
                df_transformed.iloc[i] /= (
                    df_transformed.iloc[i].sum() / df.iloc[i].sum()
                )
            else:
                df_transformed.iloc[i] = df.iloc[i]

        return df_transformed

    def fixed_converter(
        self, df: pd.DataFrame, universe: str, rebalancing_period: str
    ) -> pd.DataFrame:
        """
        Convert the DataFrame using a fixed rebalancing period.

        Parameters:
        - df (DataFrame): The input DataFrame with positions.
        - universe (str): The universe to retrieve price data from.
        - rebalancing_period (str): The rebalancing period (e.g., 'weekly', 'monthly', 'quarterly', or an integer for custom periods).

        Returns:
        - DataFrame: The transformed DataFrame.
        """
        start, end = self._get_date_range(df)

        # Keep only columns with non-zero sum
        df = df.loc[:, df.sum() != 0]

        # Retrieve price data for the given universe
        self.prc = self._get_price_data(universe, start, end, df.columns)

        df_transformed = df.copy()
        prc_change = self.prc.pct_change(1, fill_method="pad").fillna(0).loc[df.index]

        # Determine rebalancing dates
        if isinstance(rebalancing_period, int):
            rebalancing_dates = df.index[::rebalancing_period]
        else:
            if rebalancing_period == "weekly":
                freq = "W-MON"
            elif rebalancing_period == "monthly":
                freq = "MS"
            elif rebalancing_period == "quarterly":
                freq = "QS"
            else:
                raise ValueError(
                    "Invalid rebalancing_period. Use integer or one of ['weekly', 'monthly', 'quarterly']"
                )

            # Find the first valid trading day for each period
            potential_rebalancing_dates = df.resample(freq).first().index
            rebalancing_dates = []
            for date in potential_rebalancing_dates:
                valid_dates = df.index[df.index >= date]
                if len(valid_dates) > 0:
                    rebalancing_dates.append(valid_dates[0])
            rebalancing_dates = pd.DatetimeIndex(rebalancing_dates)

        # Apply rebalancing and maintain positions
        for i in range(1, df.shape[0]):
            if df.index[i] in rebalancing_dates:
                df_transformed.iloc[i] = df.iloc[i]
            else:
                df_transformed.iloc[i] = df_transformed.iloc[i - 1] * (
                    1 + prc_change.iloc[i - 1]
                )
                df_transformed.iloc[i] /= (
                    df_transformed.iloc[i].sum() / df.iloc[i].sum()
                )

        logger.info(
            f"The first rebalancing day is {rebalancing_dates[0]}. It should be earlier than the position start date of the get function."
        )

        return df_transformed
