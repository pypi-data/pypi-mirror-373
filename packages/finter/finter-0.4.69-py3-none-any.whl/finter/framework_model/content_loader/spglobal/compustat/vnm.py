import warnings

import pandas as pd

from finter.framework_model.alpha import BaseAlpha
from finter.framework_model.content import Loader


class CompustatLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]
        self.__UNIV = None
        self.__INST = cm_name.split(".")[-2].split("-")[1]
        self.__ITEM = cm_name.split(".")[-2].split("-")[2]
        self.__CATEGORY = cm_name.split(".")[-3]

    def get_df(
        self,
        start: int,
        end: int,
        adj=True,
        adj_div=False,
        fill_nan=True,
        currency=None,
        *args,
        **kwargs,
    ) -> pd.DataFrame:
        base_args = {
            "start": start,
            "end": end,
            "universe": f"vnm-vnm-{self.__INST}",
            "freq": self.__FREQ,
            "cache_t": "hdf",
            "fill_nan": fill_nan,
        }
        BaseAlpha.get_cm(self.__CM_NAME)

        raw = self._load_cache(self.__CM_NAME, **base_args)
        raw_col = raw.columns

        if self.__ITEM in ("indicated_annual_dividend", "eps"):
            return raw

        if self.__CATEGORY in ("universe", "cax", "classification"):
            return raw

        if adj:
            adj_cm_name = (
                f"content.spglobal.compustat.cax.vnm-{self.__INST}-adjust_factor.1d"
            )

            BaseAlpha.get_cm(adj_cm_name)
            adj_factor = (
                self._load_cache(adj_cm_name, **base_args)
                .reindex(columns=raw_col)
                .fillna(1)
            )

            if adj_div:
                BaseAlpha.get_cm(
                    f"content.spglobal.compustat.cax.vnm-{self.__INST}-total_return_factor.1d"
                )
                total_return_factor = (
                    self._load_cache(
                        f"content.spglobal.compustat.cax.vnm-{self.__INST}-total_return_factor.1d",
                        start,
                        end,
                        universe=f"vnm-vnm-{self.__INST}",
                        freq=self.__FREQ,
                        cache_t="hdf",
                        fill_nan=fill_nan,
                    )
                    .reindex(columns=raw_col)
                    .fillna(1)
                )
                adj_factor /= total_return_factor

            if self.__ITEM in ["shares_outstanding", "trading_volume"]:
                raw = raw * adj_factor
            elif self.__ITEM in [
                "price_open",
                "price_high",
                "price_low",
                "price_close",
            ]:
                raw = raw / adj_factor
            else:
                raise ValueError(
                    "This item is not support adjusted value or not supported. Try adj=False or check the item name"
                )

            warnings.warn(
                f"\n{self.__CM_NAME.split('.')[-2]} has been adjusted. Use adj=False if you want unadjusted values"
            )
        return raw
