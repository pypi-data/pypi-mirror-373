from finter.framework_model.content import Loader


class DescriptorLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]
        self.__ITEM = cm_name.split(".")[-2]

    def get_df(self, start: int, end: int, fill_nan=True, *args, **kwargs):

        raw = self._load_cache(
            self.__CM_NAME,
            start,
            end,
            freq=self.__FREQ,
            fill_nan=fill_nan,
        )

        return raw
