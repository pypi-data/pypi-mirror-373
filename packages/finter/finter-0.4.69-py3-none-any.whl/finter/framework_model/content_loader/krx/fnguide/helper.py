from finter.data.symbol import Mapper
import pandas as pd
from time import time


def fnguide_ccid_to_dataguide_ccid(cm):
    """
    Convert column of cm; fnguide_ccid -> dataguide_ccid(quantit_ccid)
    convert 되지 않으면 drop
    """
    mapper = Mapper.get_ccid_to_short_code_mapper()
    cm.columns = cm.columns.astype(str)
    convert_cm = cm[[col for col in mapper.keys() if col in cm.columns]]
    convert_cm = convert_cm.rename(mapper, axis=1)
    return convert_cm


def fnguide_entity_id_to_dataguide_ccid(cm):
    """
    Convert column of cm; fnguide_entity -> dataguide_ccid(quantit_ccid)
    entity_id는 기업 기준으로, ccid로 변환할 땐 보통주와 우선주가 있을 땐 컬럼 n개로 변환함
    """
    start = time()
    convert = {}
    mapper = Mapper.get_entity_id_to_ccid_mapper()
    cm.columns = cm.columns.astype(str)
    for col, values in mapper.items():
        if col not in cm.columns:
            continue
        if isinstance(values, list):
            for value in values:
                convert[value] = cm[col]
        else:
            convert[values] = cm[col]

    ccid_cm = pd.DataFrame(convert)
    return fnguide_ccid_to_dataguide_ccid(ccid_cm)
