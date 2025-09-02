from finter.framework_model.content import Loader
import pandas as pd
from finter.settings import logger


class QuandaFlowLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]

    def get_df(self, start: int, end: int, fill_nan=True, columns=None, *args, **kwargs):
        raw = self._load_cache(
            self.__CM_NAME,
            start,
            end,
            freq=self.__FREQ,
            fill_nan=fill_nan,
            columns=columns,
            *args,
            **kwargs
        )

        return raw
        