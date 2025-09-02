import re

import pandas as pd
from finter.framework_model.content import Loader


class ThemeLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]

    def get_df(
            self, start: int, end: int, search=None, fill_nan=True, meaningful=True, *args, **kwargs
    ):
        raw = self._load_cache(
            self.__CM_NAME,
            start,
            end,
            freq=self.__FREQ,
            fill_nan=fill_nan,
            cache_t="hdf",
            **kwargs
        )

        if search is not None:
            search = search.replace("(", "\(").replace(")", "\)")
            raw = raw.filter(regex=f".*{search}.*")

        raw = raw.dropna(how="all")
        if meaningful:
            return raw.loc[:, ~raw.iloc[-1].isna()]
        return raw

    @staticmethod
    def filter_columns_name(raw):
        # theme
        if raw.columns.nlevels == 1:
            raw.columns = [
                re.sub(r"\s*\([^()]*\)$", '', str(keyword))
                for keyword in raw.columns
            ]

        # company_keyword
        else:
            new_col = [
                (ccid, re.sub(r"\s*\([^()]*\)$", '', str(keyword)))
                for ccid, keyword in raw.columns.values
            ]
            raw.columns = pd.MultiIndex.from_tuples(new_col)

        return raw
