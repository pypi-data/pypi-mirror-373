from finter.framework_model.content import Loader

from datetime import datetime
import pandas as pd


class PriceVolumeLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]
        self.__ITEM = cm_name.split(".")[-2]

        self.raw_price = pd.DataFrame()
        self.adj_factor = pd.DataFrame()
        self.div_adj_factor = pd.DataFrame()
        self.clearance = pd.DataFrame()
        self.fill_nan = False

    def get_df(
        self,
        start: int,
        end: int,
        adj=True,
        adj_div=False,
        fill_nan=True,
        *args,
        **kwargs,
    ):
        assert not (
            (adj is False) & (adj_div is True)
        ), f"Only dividend adjust is not available"

        filter_columns = kwargs.get("filter_columns", None)
        is_filter_column = filter_columns is not None and not filter_columns.empty

        if (
            not self.raw_price.empty
            and self.raw_price.index[0] == datetime.strptime(str(start), "%Y%m%d")
            and self.raw_price.index[-1] == datetime.strptime(str(end), "%Y%m%d")
            and fill_nan == self.fill_nan
        ):
            raw = self.raw_price
        else:
            raw = self._load_cache(
                self.__CM_NAME,
                start,
                end,
                universe="us-compustat-etf",
                freq=self.__FREQ,
                fill_nan=fill_nan,
                *args,
                **kwargs,
            )
            self.raw_price = raw
            self.fill_nan = fill_nan
        if is_filter_column:
            raw = raw.filter(filter_columns)

        if adj:
            if (
                not self.adj_factor.empty
                and self.adj_factor.index[0] == datetime.strptime(str(start), "%Y%m%d")
                and self.adj_factor.index[-1] == datetime.strptime(str(end), "%Y%m%d")
                and fill_nan == self.fill_nan
            ):
                adj_factor = self.adj_factor
            else:
                adj_factor = self._load_cache(
                    "content.spglobal.compustat.cax.us-etf-adjust_factor.1d",
                    start,
                    end,
                    universe="us-compustat-etf",
                    freq=self.__FREQ,
                    fill_nan=fill_nan,
                    *args,
                    **kwargs,
                )
                self.adj_factor = adj_factor
                self.fill_nan = fill_nan
            if is_filter_column:
                adj_factor = adj_factor.filter(filter_columns).fillna(1)
            adj_factor = adj_factor.reindex(columns=raw.columns)
            if adj_div:
                assert "price" in self.__ITEM

                if (
                    not self.div_adj_factor.empty
                    and self.div_adj_factor.index[0]
                    == datetime.strptime(str(start), "%Y%m%d")
                    and self.div_adj_factor.index[-1]
                    == datetime.strptime(str(end), "%Y%m%d")
                    and fill_nan == self.fill_nan
                ):
                    div_adj_factor = self.div_adj_factor
                else:
                    div_adj_factor = self._load_cache(
                        "content.spglobal.compustat.cax.us-etf-total_return_factor.1d",
                        start,
                        end,
                        universe="us-compustat-etf",
                        freq=self.__FREQ,
                        fill_nan=fill_nan,
                        *args,
                        **kwargs,
                    )
                    self.div_adj_factor = div_adj_factor
                    self.fill_nan = fill_nan
                if is_filter_column:
                    div_adj_factor = div_adj_factor.filter(filter_columns)
                div_adj_factor = div_adj_factor.reindex(columns=raw.columns).fillna(1)

                adj_factor /= div_adj_factor

            if self.__ITEM in [
                "us-etf-trading_volume",
                "us-etf-shares_outstanding",
            ]:
                raw = raw * adj_factor
            elif self.__ITEM in [
                "us-etf-price_open",
                "us-etf-price_high",
                "us-etf-price_low",
                "us-etf-price_close",
                "us-etf-eps",
            ]:
                raw = raw / adj_factor
        return raw
