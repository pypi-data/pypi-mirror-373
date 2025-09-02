from finter.framework_model.content import Loader


class DILoader(Loader):
    def __init__(self, cm_name: str):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]

    def get_df(self, start: int, end: int, fill_nan=True, *args, **kwargs):

        raw = self._load_cache(
            self.__CM_NAME,
            start,
            end,
            universe="krx-krx-stock",
            freq=self.__FREQ,
            fill_nan=fill_nan,
            *args,
            **kwargs
        )

        return raw
