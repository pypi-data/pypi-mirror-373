import numpy as np

from finter.framework_model.content import Loader


class BloombergLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]
        self.__ITEM_NAME = cm_name.split(".")[-2]

    def get_df(self, start: int, end: int, adj=True, fill_nan=True, *args, **kwargs):
        raw = self._load_cache(
            self.__CM_NAME,
            start,
            end,
            universe="us-us-stock",
            freq=self.__FREQ,
            cache_t="hdf",
            fill_nan=fill_nan,
        )

        if not adj:
            return raw
        else:
            adj_rollover = self._load_cache(
                "content.bloomberg.api.future.adj_rollover.1d",
                20000101,
                end,
                universe="us-us-stock",
                freq=self.__FREQ,
                cache_t="hdf",
                fill_nan=fill_nan,
            )

            if self.__ITEM_NAME == "px_last":
                adj_factor = adj_rollover.apply(np.exp).cumprod()
                raw = raw * adj_factor.reindex(raw.index)
                raw = raw.dropna(how="all", axis=1)
                raw = raw.loc[raw.index]

        return raw
