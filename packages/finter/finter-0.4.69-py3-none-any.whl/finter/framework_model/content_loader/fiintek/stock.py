import warnings

import pandas as pd

from finter.framework_model.alpha import BaseAlpha
from finter.framework_model.content import Loader

CM_PREFIX = "content.fiintek.api.%s.%s.1d"


class FiintekLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]
        self.__ITEM = cm_name.split(".")[-2]
        self.__CATEGORY = cm_name.split(".")[-3]

    def get_df(
        self,
        start: int,
        end: int,
        adj=True,
        adj_div=False,
        fill_nan=True,
        *args,
        **kwargs,
    ) -> pd.DataFrame:
        base_args = {
            "start": start,
            "end": end,
            "universe": "vnm-vnm-stock",
            "freq": self.__FREQ,
            "cache_t": "hdf",
            "fill_nan": fill_nan,
        }
        BaseAlpha.get_cm(self.__CM_NAME)

        raw = self._load_cache(self.__CM_NAME, **base_args)
        raw_col = raw.columns

        if self.__CATEGORY in [
            "ratio",
            "classification",
            "cax",
            "income_statement",
            "cash_flow",
            "balance_sheet",
        ]:
            return raw

        if self.__ITEM in ("indicated_annual_dividend", "eps"):
            return raw

        if adj:
            if self.__ITEM in ["ForeignTotalRoom", "ForeignCurrentRoom"]:
                return raw

            adj_cm_name = f"{CM_PREFIX % ('cax', 'RateAdjusted')}"
            print(adj_cm_name)

            BaseAlpha.get_cm(adj_cm_name)
            adj_factor = (
                self._load_cache(adj_cm_name, **base_args)
                .reindex(columns=raw_col)
                .fillna(1)
            )

            # if adj_div:
            #     BaseAlpha.get_cm(f"spglobal.compustat.cax.vnm-{self.__INST}-total_return_factor.1d")
            #     total_return_factor = self._load_cache(
            #         f"spglobal.compustat.cax.vnm-{self.__INST}-total_return_factor.1d",
            #         start,
            #         end,
            #         universe=f"vnm-vnm-{self.__INST}",
            #         freq=self.__FREQ,
            #         cache_t="hdf",
            #         fill_nan=fill_nan
            #     ).reindex(columns=raw_col).fillna(1)
            #     adj_factor /= total_return_factor

            if "Volume" in self.__ITEM:
                raw = raw / adj_factor
            elif "Price" in self.__ITEM:
                raw = raw * adj_factor
            else:
                warnings.warn(
                    f"\n{self.__CM_NAME.split('.')[-2]} not available for adjustment. Use adj=False if you want unadjusted values"
                )
                raise ValueError

            warnings.warn(
                f"\n{self.__CM_NAME.split('.')[-2]} has been adjusted. Use adj=False if you want unadjusted values"
            )
        return raw
