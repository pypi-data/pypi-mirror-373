from datetime import datetime

import numpy as np
import pandas as pd
from finter.framework_model.content import Loader

initial_date = 19820131


class CompustatFinancialLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]

    @staticmethod
    def _unpivot_df(raw):
        unpivot_df = raw.unstack().dropna().reset_index()
        unpivot_df.columns = ["id", "pit", "val"]
        m = (
            pd.DataFrame([*unpivot_df["val"]], unpivot_df.index)
            .stack()
            .rename_axis([None, "fiscal"])
            .reset_index(1, name="value")
        )
        result = unpivot_df[["id", "pit"]].join(m)
        return result.dropna(subset=["fiscal", "value"])

    def get_df(
        self,
        start: int,
        end: int,
        fill_nan=True,
        unpivot: bool = False,
        delay: int = 90,
        quantit_universe=True,
        *args,
        **kwargs
    ):
        """
        unpivot : bool
        delay : raw index에서 며칠의 딜레이를 줄지. period end의 경우는 90일보다 딜레이가 적으면 raise
        """
        raw = self._load_cache(
            self.__CM_NAME,
            initial_date,
            end,
            freq=self.__FREQ,
            fill_nan=fill_nan,
            cache_t="hdf",
        ).dropna(how="all")

        if not self.__CM_NAME.split(".")[-2] in ['us-stock-filedate']:
            assert delay >= 90
            raw.index = raw.index + pd.DateOffset(days=delay)
        
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
            univ.columns = [col[:6] for col in univ.columns]
            univ = univ.T.groupby(univ.columns).any().T
            univ = univ.reindex(pd.date_range(start=univ.index[0], end=univ.index[-1], freq='D')).fillna(method='ffill')

            raw = raw.where(univ, np.nan)

        raw = raw.dropna(how="all").loc[
            datetime.strptime(str(start), "%Y%m%d") : datetime.strptime(
                str(end), "%Y%m%d"
            )
        ]
        
        if unpivot:
            raw = CompustatFinancialLoader._unpivot_df(raw)
        return raw
