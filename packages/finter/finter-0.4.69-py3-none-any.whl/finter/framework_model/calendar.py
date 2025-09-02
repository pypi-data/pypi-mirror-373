from __future__ import print_function

import pandas as pd
from datetime import datetime
from typing import Iterator, Dict, Union
from enum import Enum

import finter
from finter.rest import ApiException
from finter.utils.convert import datetime_to_string, string_to_datetime
from finter.utils.testing.format import is_valid_date_string
from finter.settings import get_api_client, logger

d_form_func = lambda x, y: datetime_to_string(x, y)


class Code(Enum):
    ALL_DAY = 0
    TRADING_DAY = 1
    HOLIDAY = 2
    WEEKENDS = 3

    @classmethod
    def get_all_by_dict(cls):
        return {getattr(Code, x): getattr(Code, x).value for x in list(Code.__members__.keys())}

    @classmethod
    def get_all_values(cls):
        return list(cls.get_all_by_dict().values())


def iter_days(start, end, exchange="krx", date_type=0) -> Iterator[datetime]:
    """
    return iter days
    :param start: datetime.date
    :param end: datetime.date
    :param date_type: int | 0:all day 1: trading day, 2: closed day, 3: weekends (optional, default: 0)
    :param exchange: str |  'krx', 'us' (optional)
    """

    try:
        try:
            client = finter.CalendarApi(
                get_api_client()
            )
        except ValueError:  # Permission is not required on CalendarApi
            client = finter.CalendarApi()

        api_response = client.calendar_retrieve(
            start_date=d_form_func(start, "%Y%m%d"),
            end_date=d_form_func(end, "%Y%m%d"),
            exchange=exchange,
            date_type=date_type
        )

        # Not use calendar DB
        if (exchange == 'crypto') and date_type in (Code.ALL_DAY.value, Code.TRADING_DAY.value):
            api_response.dates = pd.date_range(string_to_datetime(start), string_to_datetime(end)).strftime("%Y%m%d").to_list()

        return iter(
            [
                datetime.strptime(str(d_int), "%Y%m%d") for d_int in api_response.dates
            ]
        )

    except ApiException as e:
        logger.error("Exception when calling CalendarApi->calendar_retrieve: %s\n" % e)


def iter_trading_days(
        start: Union[datetime.date, str, int],
        end: Union[datetime.date, str, int],
        exchange='krx'
):
    return iter_days(
        start, end, exchange=exchange, date_type=Code.TRADING_DAY.value
    )


def iter_us_trading_days(start: datetime.date, end: datetime.date):
    return iter_trading_days(start, end, exchange="us")


def iter_holidays(
        start: Union[datetime.date, str, int],
        end: Union[datetime.date, str, int],
        exchange='krx'
):
    return iter_days(
        start, end, exchange=exchange, date_type=Code.HOLIDAY.value
    )
    
def iter_trading_times(start, end, exchange="crypto", date_type=0, freq='10T') -> Iterator[datetime]:
    """
    return iter times
    :param start: Union[datetime.date, str, int]
    :param end: Union[datetime.date, str, int]
    :param date_type: int | 0:all times 1: trading times, 2: closed times, 3: weekends times (optional, default: 0)
    :param exchange: str |  'crypto' (optional)
    """
    
    if (exchange != 'crypto') and (freq != '1d'):
        logger.warning(f"iter_trading_times only support crypto now ({freq} != 1d)")
        return iter_trading_days(start, end, exchange)
        
    elif freq == '1d':
        return iter_trading_days(start, end, exchange)
    
    else:   
        return iter(
                pd.date_range(
                    string_to_datetime(start),
                    string_to_datetime(end),
                    freq=freq
                    ).to_list()
                )


class TradingDay:
    @staticmethod
    def func_tday(dt_str="%Y%m%d", **kwargs):
        try:
            try:
                client = finter.CalendarApi(
                    get_api_client()
                )
            except ValueError:  # Permission is not required on CalendarApi
                client = finter.CalendarApi()

            d = d_form_func(kwargs["date"], dt_str)
            kwargs["date"] = d

            assert is_valid_date_string(d, date_format=dt_str), f"'{dt_str}' format is required"

            api_response = client.trading_day_retrieve(**kwargs)

            return datetime.strptime(api_response._date, "%Y%m%d")

        except ApiException as e:
            logger.error("Exception when calling CalendarApi->trading_day_retrieve: %s\n" % e)

    @staticmethod
    def last_close(date: Union[datetime, str, int], exchange="krx") -> datetime:
        params = {
            "date": date,
            "exchange": exchange,
            "func": "close_last"
        }
        return TradingDay.func_tday(dt_str="%Y%m%d%H%M%S", **params)

    @staticmethod
    def upcoming_close(date: Union[datetime, str, int], exchange="krx") -> datetime:
        params = {
            "date": date,
            "exchange": exchange,
            "func": "close_upcoming"
        }
        return TradingDay.func_tday(dt_str="%Y%m%d%H%M%S", **params)

    @staticmethod
    def prev(date: Union[datetime, str, int], exchange="krx") -> datetime:
        params = {
            "date": date,
            "exchange": exchange,
            "func": "prev"
        }
        return TradingDay.func_tday(dt_str="%Y%m%d", **params)

    @staticmethod
    def next(date: Union[datetime, str, int], exchange="krx") -> datetime:
        params = {
            "date": date,
            "exchange": exchange,
            "func": "next"
        }
        return TradingDay.func_tday(dt_str="%Y%m%d", **params)

    @staticmethod
    def day_delta(date: Union[datetime, str, int], n: int, exchange="krx") -> int:
        """
            Returns the trading day that is n business days away from the given date.
            If n = -1, the result is the same as using TradingDay.prev.
            If n = 1, the result is the same as using TradingDay.next.

            Args:
                date: The reference date (does not need to be a trading day)
                n: The number of business days from the date
                exchange: Can be either "us" or "krx". Any other value will be treated as "krx".
        """

        params = {
            "date": date,
            "exchange": exchange,
            "func": "day_delta",
            "n": n
        }
        return TradingDay.func_tday(dt_str="%Y%m%d", **params)
