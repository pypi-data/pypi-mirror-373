import numpy as np
import pandas as pd
import json
from datetime import datetime

from finter.settings import logger


def str_to_type(type_str):
    if type_str == "str":
        return str
    elif type_str == "int":
        return int
    elif type_str == "float":
        return float
    else:
        return str


def to_dataframe(json_response, column_types=None):
    try:
        df = pd.DataFrame.from_dict(json.loads(json_response), orient="index")
        df.index = pd.to_datetime(df.index.astype(int), unit="ms")
        df = df.sort_index()
        df = df.replace({None: np.nan})
        if column_types:
            if isinstance(column_types, str):
                column_types = json.loads(column_types)
            response_column_types = pd.Series(column_types)
            df.columns = df.columns.to_series().apply(
                lambda x: str_to_type(response_column_types.loc[str(x)])(x)
            )
        return df
    except Exception as e:
        logger.error(e, exc_info=True)
        return pd.read_json(json_response, orient="index")


def get_json_with_columns_from_dataframe(df):
    # get df json, column types json from df
    df_json = df.to_json(orient="index")
    original_column_types = df.columns.to_series().apply(
        lambda x: str(type(x).__name__)
    )
    column_types_json = json.dumps(original_column_types.to_dict())

    return df_json, column_types_json


def datetime_to_string(d, format="%Y%m%d"):
    if format == "%Y%m%d":
        fl = 8
    elif format == "%Y%m%d%H%M%S":
        fl = 14
    else:
        raise ValueError("Now '%Y%m%d' and '%Y%m%d%H%M%S' are supported")

    if isinstance(d, int) or isinstance(d, str):
        return str(d)[:fl]
    elif isinstance(d, datetime):
        return d.strftime(format)

def string_to_datetime(d):
    formats = {
        8: "%Y%m%d",           # YYYYMMDD
        10: "%Y%m%d%H",        # YYYYMMDDHH
        12: "%Y%m%d%H%M",      # YYYYMMDDHHMM
        14: "%Y%m%d%H%M%S",    # YYYYMMDDHHMMSS
    }
    
    if isinstance(d, int) or isinstance(d, str):
        return datetime.strptime(str(d), formats[len(str(d))])
    else:
        return d
    
    