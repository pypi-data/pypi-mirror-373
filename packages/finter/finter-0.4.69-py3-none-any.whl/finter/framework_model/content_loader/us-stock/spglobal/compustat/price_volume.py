from datetime import datetime

import numpy as np
import pandas as pd

from finter.framework_model.alpha import BaseAlpha
from finter.framework_model.content import Loader
from finter.settings import get_api_client


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
        quantit_universe=True,
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
                19980401,  # to avoid start dependency in dataset
                end,
                universe="us-compustat-stock",
                freq=self.__FREQ,
                fill_nan=fill_nan,
                *args,
                **kwargs,
            )
            self.raw_price = raw
            self.fill_nan = fill_nan
        if is_filter_column:
            raw = raw.filter(filter_columns)

        if self.__ITEM in (
            "us-stock-indicated_annual_dividend",
            "us-stock-eps",
            "us-stock-mkt_cap",
            "us-stock-amount",
            "us-stock-adr_ratio",
        ):
            adj = False

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
                    "content.spglobal.compustat.cax.us-stock-adjust_factor.1d",
                    19980401,  # to avoid start dependency in dataset
                    end,
                    universe="us-compustat-stock",
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
                        "content.spglobal.compustat.cax.us-stock-total_return_factor.1d",
                        19980401,  # to avoid start dependency in dataset
                        end,
                        universe="us-compustat-stock",
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
                "us-stock-trading_volume",
                "us-stock-shares_outstanding",
            ]:
                raw = raw * adj_factor

            elif self.__ITEM in [
                "us-stock-price_open",
                "us-stock-price_high",
                "us-stock-price_low",
                "us-stock-price_close",
                "us-stock-eps",
            ]:
                raw = raw / adj_factor
                vol = self._load_cache(
                    "content.spglobal.compustat.price_volume.us-stock-trading_volume.1d",
                    19980401,  # to avoid start dependency in dataset
                    end,
                    universe="us-compustat-stock",
                    freq=self.__FREQ,
                    fill_nan=fill_nan,
                    *args,
                    **kwargs,
                )
                vol = vol.reindex(columns=raw.columns)
                raw[vol == 0] = np.nan
                raw.ffill(inplace=True, limit=3)

            else:
                raise ValueError(f"Unknown item: {self.__ITEM}")

        if quantit_universe:
            univ = self._load_cache(
                "content.spglobal.compustat.universe.us-stock-constituent.1d",
                19980401,  # to avoid start dependency in dataset
                end,
                universe="us-compustat-stock",
                freq=self.__FREQ,
                fill_nan=fill_nan,
                *args,
                **kwargs,
            )
            univ = univ.reindex(columns=raw.columns)
            raw *= univ
        else:
            self.client = get_api_client()
            if self.client.user_group != "quantit":
                raise AssertionError("Only quantit user group can use all universe")
            else:
                raw.iloc[-1] *= 0
        raw = raw.replace(0, np.nan)
        return raw.loc[datetime.strptime(str(start), "%Y%m%d") :]
