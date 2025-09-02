from finter import BaseAlpha
from finter.data import ContentFactory
from pydantic import Field

from typing import Optional, Tuple, List, Union
from finter.framework_model.submission.config import (
    ModelTypeConfig,
    ModelUniverseConfig,
)
from finter.modeling.metamodel.base import BaseMetaAlpha

from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def get_us_factors():
    return ContentFactory("us_stock", 20240101, 20240131).cm_dict[
        "content.quantit.compustat_cm.factor.us-stock_pit-*.1d"
    ]


# Alpha class inheriting from BaseAlpha
class UsFactorLongOnlyAlpha(BaseMetaAlpha):
    factor: str
    min_rank: float
    ascending: bool = True
    filter_ids: List[str]

    class Parameters(BaseMetaAlpha.Parameters):
        factor: str = Field(..., description="Factor to use for alpha generation")
        min_rank: float = Field(
            ...,
            description="The value is a float, and it indicates selecting only those with ranks greater than or equal to this value. For example, if the value is 0.7, only those with ranks of 0.7 or higher will be selected.",
        )  # 0~1
        ascending: bool = Field(
            True,
            description="The default value is True, meaning that items with higher factor values will be selected. If false, low factor values will be selected.",
        )
        filter_ids: List[str] = Field(
            [],
            description="A list of IDs used to filter. If this list is empty (default is an empty list), no filtering is applied.",
        )

    def get_factor(self, start, end):
        return ContentFactory(self.universe.get_content_base_name(), start, end).get_df(
            self.factor
        )

    # Function to calculate the previous start date based on a given lookback period
    @staticmethod
    def calculate_previous_start_date(start_date, lookback_days):
        start = datetime.strptime(
            str(start_date), "%Y%m%d"
        )  # Convert start_date to datetime object
        previous_start = start - timedelta(
            days=lookback_days
        )  # Calculate previous start date
        return int(
            previous_start.strftime("%Y%m%d")
        )  # Return previous start date in yyyyMMdd format

    @staticmethod
    def retain_first_of_month(x):
        tmp = x.index[-2:-1]
        tmp = tmp.append(x.index[0:-1])
        mask = x.index.to_period("M") != tmp.to_period("M")
        return x[mask]

    @staticmethod
    def entity_df_to_stock_df(entity_df: pd.DataFrame, price: pd.DataFrame):
        def entity_id(stock_id):
            return stock_id[:6]

        entity2stocks = {}
        for stock_id in price.columns:
            eid = entity_id(stock_id)
            entity2stocks[eid] = entity2stocks.get(eid, []) + [stock_id]

        # select all stocks per entity
        # TODO: support other selection method
        # entity2stock = {eid: min(stock_ids) for eid, stock_ids in entity2stocks.items()}
        new_df = pd.DataFrame()
        for eid in entity_df.columns:
            sids = entity2stocks.get(eid)
            if sids:
                for sid in sids:
                    new_df[sid] = entity_df[eid]

        return new_df

    # Function to safely apply a transformation to the data
    def get_signal(self, factor, price):
        # Function to scale the DataFrame
        def scale_df(df):
            row_sums = df.sum(axis=1)
            scaling_factors = np.where(row_sums != 0, row_sums, 1)
            return df.div(scaling_factors, axis=0)

        rank = factor.rank(
            axis=1, pct=True, ascending=self.ascending
        )  # Calculate cross-sectional factor rank

        selected = rank[rank >= self.min_rank]

        if len(factor.columns[0]) == 6:  # entity factor
            selected = self.entity_df_to_stock_df(selected, price)

        selected = selected[selected.columns.intersection(price.columns)]
        selected = selected.reindex(index=price.index)

        # long_df = long_df.rename(columns=entity2stock)
        # remove columns with no stock_id
        selected = selected[selected.columns.intersection(price.columns)]
        selected = selected.reindex(index=price.index)

        selected = selected[price > 0].ffill(limit=60)  # forward fill nan values
        selected = scale_df(selected) * 1e8

        return selected

    # Method to generate alpha
    def get(self, start, end):
        pre_start = self.calculate_previous_start_date(
            start, 365
        )  # Calculate start date for data retrieval

        price = self.get_default_price(pre_start, end)
        factor = self.get_factor(pre_start, end)

        alpha = self.get_signal(factor, price)

        alpha = alpha.shift(1)  # Shift positions to avoid look-ahead bias
        alpha = self.retain_first_of_month(alpha).fillna(0).reindex(price.index).ffill()

        return self.cleanup_position(
            alpha.loc[str(start) : str(end)]
        )  # Return alpha values for the given period
