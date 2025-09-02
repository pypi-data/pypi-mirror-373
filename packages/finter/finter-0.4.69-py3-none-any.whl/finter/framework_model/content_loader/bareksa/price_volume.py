from finter.framework_model.content import Loader


class BareksaLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]

    def get_df(self, start: int, end: int, fill_nan=True, *args, **kwargs):
        raw = self._load_cache(
            self.__CM_NAME,
            start,
            end,
            universe="id-bareksa-fund",
            freq=self.__FREQ,
            cache_t="hdf",
            fill_nan=fill_nan,
        )
        return raw
