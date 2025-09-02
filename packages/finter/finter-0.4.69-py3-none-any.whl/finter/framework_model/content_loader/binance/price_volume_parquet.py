from finter.framework_model.content import Loader
import pandas as pd
from finter.settings import logger
import gc
from finter.rest import ApiException

def to_end(dt):
    if dt.minute != 0:
        end_dt = dt.replace(second=59, microsecond=999999)
    elif dt.hour != 0:
        end_dt = dt.replace(minute=59, second=59, microsecond=999999)
    else:
        end_dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    return end_dt

class BinancePriceVolumeLoader(Loader):   
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = '1T' # daily production, 1T index

    def get_df(self, start: int, end: int, fill_nan=True, columns=None, *args, **kwargs):
        start_dt = pd.to_datetime(str(start))
        end_dt = pd.to_datetime(str(end))
        cm_name = self.__CM_NAME

        raw = self._load_cache(
            cm_name,
            start,
            end,
            universe="binance-all-spot",
            freq=self.__FREQ,
            fill_nan=fill_nan,
            columns=columns,
            *args,
            **kwargs
        )

        return raw.loc[start_dt:to_end(end_dt)].dropna(how="all")
