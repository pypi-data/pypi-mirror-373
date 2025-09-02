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
        self.__FREQ = cm_name.split(".")[-1]

    def get_df(self, start: int, end: int, fill_nan=True, columns=None, *args, **kwargs):
        start_dt = pd.to_datetime(str(start))
        end_dt = pd.to_datetime(str(end))
        cm_name = self.__CM_NAME
        
        # select cm_name
        if cm_name.split(".")[-2].split("_")[-1].isdigit():
            logger.info("Load yearly cm")
            raw = self._load_cache(
                self.__CM_NAME,
                start,
                end,
                universe="binance-all-spot",
                freq=self.__FREQ,
                fill_nan=fill_nan,
                columns=columns,
                *args,
                **kwargs
            )
        
        # single cm
        elif start_dt.year == end_dt.year:
            y = start_dt.year
            raw = self._load_cache(
                cm_name.replace(".1T", f"_{y}.1T"),
                start,
                end,
                universe="binance-all-spot",
                freq=self.__FREQ,
                fill_nan=fill_nan,
                columns=columns,
                *args,
                **kwargs
            )

        # Over 1 year; needs columns params
        elif bool(columns):
            temp_list = []
            for y in range(start_dt.year, end_dt.year + 1):
                try:
                    current_cm_name = cm_name.replace(".1T", f"_{y}.1T")
                    
                    temp_raw = self._load_cache(
                        current_cm_name,
                        int(f"{y}0101"),
                        int(f"{y}1231"),
                        universe="binance-all-spot",
                        freq=self.__FREQ,
                        fill_nan=fill_nan,
                        columns=columns,
                        *args,
                        **kwargs
                    ).dropna(how="all")
                    temp_list.append(temp_raw)
                except ApiException as e:
                    logger.warning(f"Skipped : there is no data for {y}")
            raw = pd.concat(temp_list)
            del temp_list
            gc.collect()
        else:
            raise "Please choose the columns when requesting data for more than one year."

        return raw.loc[start_dt:to_end(end_dt)].dropna(how="all")
