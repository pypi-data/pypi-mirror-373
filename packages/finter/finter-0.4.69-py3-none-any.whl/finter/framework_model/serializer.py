import pickle
import re

DART_CM_LIST = [
    'content.dart.api.disclosure.bonus_issue.1d',
    'content.dart.api.disclosure.br_issue.1d',
    'content.dart.api.disclosure.buyback.1d',
    'content.dart.api.disclosure.buyback_disposal.1d',
    'content.dart.api.disclosure.buyback_trust.1d',
    'content.dart.api.disclosure.bw.1d',
    'content.dart.api.disclosure.cb.1d',
    'content.dart.api.disclosure.coco.1d',
    'content.dart.api.disclosure.division.1d',
    'content.dart.api.disclosure.division_merge.1d',
    'content.dart.api.disclosure.eb.1d',
    'content.dart.api.disclosure.major_stock.1d',
    'content.dart.api.disclosure.merge.1d',
    'content.dart.api.disclosure.reduction.1d',
    'content.dart.api.disclosure.rights_issue.1d'
]

IPO_CM_LIST = [
    'content.38comm.crawl.ipo.lockup_table.1d',
    'content.38comm.crawl.ipo.schedule.1d'
]

MIXED_STRUCTURE_CM_LIST = [
    "content.vaiv.api.somemoney.recommend-n-kospi_l1.1d",
    "content.vaiv.api.somemoney.recommend-n-kospi_m1.1d",
    "content.vaiv.api.somemoney.recommend-n-kosdaq_l1.1d",
    "content.vaiv.api.somemoney.recommend-n-kosdaq_m1.1d",
    "content.vaiv.api.somemoney.recommend-n-kosdaq_s1.1d"
]

NOT_RECOGNIZE_PYTHON_VALUE = [
    'content.quantit.api.marketregime.k200_ms4.1d'
]

MULTI_DIMENSION_ARRAY = [
    'content.quantit.api.marketregime.oecd_usa.1d',
    'content.quantit.api.marketregime.oecd_world.1d',
    'content.quantit.api.marketregime.oecd_china.1d'
]

SERIALIZE_PATTERN = [
    "content.fnguide.ftp.financial*",
    "content.fred.api.economy*",
    "content\.fnguide\.ftp\.consensus\.krx-spot-[\w]+_[aq]\.1d",
    "content.spglobal.compustat.financial*"
]

SERIALIZE_CM_LIST = DART_CM_LIST + IPO_CM_LIST + MIXED_STRUCTURE_CM_LIST + NOT_RECOGNIZE_PYTHON_VALUE + MULTI_DIMENSION_ARRAY

COMPILED_PATTERN = re.compile("|".join(SERIALIZE_PATTERN + SERIALIZE_CM_LIST))


def is_serializer_target(identity_name):
    return bool(COMPILED_PATTERN.match(identity_name))


def deserialize_bytes(value):
    if not isinstance(value, bytes):
        return value
    try:
        return pickle.loads(value)
    except:
        return value


def apply_deserialization(df):
    for column in df.columns:
        df[column] = df[column].apply(deserialize_bytes)
    return df
