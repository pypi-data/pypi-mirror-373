from datetime import datetime, timedelta
from typing import Tuple, Union, List

from pydantic import Field

from finter.data import ContentFactory
from finter.modeling.metamodel.base import BaseMetaAlpha


class MomentumMetaAlpha(BaseMetaAlpha):
    momentum_period_days: int
    resample_days: int
    top_rank: float
    bottom_rank: float
    middle_rank: Tuple[float, float]
    filter_ids: List[Union[int, str]]

    class Parameters(BaseMetaAlpha.Parameters):
        momentum_period_days: int
        resample_days: int = Field(
            0,
            description="the number of days over which the momentum ranks are averaged or smoothed. Default is 0.",
        )
        top_rank: float = Field(
            ...,
            description="A float value between 0 and 1, where represents the top n percent rank. For example, 0.2 corresponds to the top 20%. 0 means no selection. The top_rank, bottom_rank, and middle_rank are used in union.",
        )  # 0~1
        bottom_rank: float = Field(
            0,
            description="A float value between 0 and 1, where represents the bottom n percent rank. For example, 0.2 corresponds to the bottom 20%. 0 means no selection. Default is 0. The top_rank, bottom_rank, and middle_rank are used in union.",
        )
        middle_rank: Tuple[float, float] = Field(
            (0, 0),
            description="Represents the ranks between a and b, where a and b are float values between 0 and 1. Default is (0,0) which means no selection.",
        )
        filter_ids: List[Union[int, str]] = Field(
            [],
            description="A list of IDs used to filter. If this list is empty (default is an empty list), no filtering is applied.",
        )

    @staticmethod
    def calculate_previous_start_date(start_date: int, lookback_days: int):
        start = datetime.strptime(str(start_date), "%Y%m%d")
        previous_start = start - timedelta(days=lookback_days)
        return int(previous_start.strftime("%Y%m%d"))

    def get(self, start, end):
        pre_start = self.calculate_previous_start_date(
            start, max(self.momentum_period_days, self.resample_days) * 5
        )

        cf = ContentFactory(self.universe.get_content_base_name(), pre_start, end)
        close = cf.get_df("price_close")

        assert close is not None

        if self.filter_ids:
            close = close[self.filter_ids]

        momentum = close.pct_change(self.momentum_period_days, fill_method=None)

        stock_rank = momentum.rank(pct=True, axis=1)

        selected_ranks = stock_rank[
            (stock_rank <= self.top_rank)
            | (stock_rank >= (1 - self.bottom_rank))
            | (
                (stock_rank >= self.middle_rank[0])
                & (stock_rank <= self.middle_rank[1])
            )
        ]

        if self.resample_days > 0:
            selected_ranks = selected_ranks.rolling(self.resample_days).mean()

        stock_ratio = selected_ranks.div(selected_ranks.sum(axis=1), axis=0)
        position = stock_ratio * 1e8

        alpha = position.shift(1)
        alpha = alpha.loc[str(start) : str(end)]

        return self.cleanup_position(alpha)
