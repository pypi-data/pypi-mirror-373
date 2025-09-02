from finter.framework_model.calendar import iter_us_trading_days

from abc import ABCMeta, abstractmethod
from datetime import datetime
import json


# Simplified version of the load_config function.
def load_config(config_name: str):
    with open(config_name, "r") as file:
        return json.load(file)


class HourMinute(object):
    def __init__(self, hour: int, minute: int):
        self.hour = hour
        self.minute = minute


class IMarketTime(metaclass=ABCMeta):
    @property
    @abstractmethod
    def start(self) -> HourMinute:
        return HourMinute()

    @property
    @abstractmethod
    def end(self) -> HourMinute:
        return HourMinute()


class MarketTime(IMarketTime):
    def before_open(self, dt: datetime):
        if dt.hour < self.start.hour:
            return True
        elif dt.hour == self.start.hour and dt.minute < self.start.minute:
            return True
        else:
            return False

    def after_close(self, dt: datetime):
        if dt.hour > self.end.hour:
            return True
        elif dt.hour == self.end.hour and dt.minute >= self.end.minute:
            return True
        else:
            return False

    @staticmethod
    def of(instrument_type):
        if isinstance(instrument_type, str):
            if "future" in instrument_type:
                return FutureMarketTime
            elif instrument_type == "stock":
                return StockMarketTime
        else:
            return None


class FutureMarketTime(MarketTime):
    start = HourMinute(9, 0)
    end = HourMinute(15, 50)


class StockMarketTime(MarketTime):
    start = HourMinute(9, 0)
    end = HourMinute(15, 40)


class IMarketTimeV2(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def start(dt: datetime, freq) -> HourMinute:
        return HourMinute(0, 0)

    @staticmethod
    @abstractmethod
    def end(dt: datetime, freq) -> HourMinute:
        return HourMinute(0, 0)


class OpenCloseCheckable:
    @classmethod
    def before_open(cls: IMarketTimeV2, dt: datetime, freq=None):
        if dt.hour < cls.start(dt, freq).hour:
            return True
        elif (
            dt.hour == cls.start(dt, freq).hour
            and dt.minute < cls.start(dt, freq).minute
        ):
            return True
        else:
            return False

    @classmethod
    def after_close(cls: IMarketTimeV2, dt: datetime, freq=None):
        if dt.hour > cls.end(dt, freq).hour:
            return True
        elif dt.hour == cls.end(dt, freq).hour and dt.minute > cls.end(dt, freq).minute:
            return True
        elif (
            dt.hour == cls.end(dt, freq).hour
            and dt.minute == cls.end(dt, freq).minute
            and dt.second > 0
        ):
            return True
        else:
            return False

    @staticmethod
    def of(instrument_type, exchange=None):
        if "us" == exchange:
            return NYSEMarketTime
        if isinstance(instrument_type, str):
            if "future" in instrument_type:
                return FutureMarketTimeV2
            elif instrument_type == "stock":
                return StockMarketTimeV2
            elif "option" in instrument_type:
                return OptionMarketTime
        else:
            return None


class FutureMarketTimeV2(IMarketTimeV2, OpenCloseCheckable):
    @staticmethod
    def start(dt: datetime, freq):
        if _is_exceptional_date(dt, "open"):
            if freq == "10T":
                return HourMinute(10, 10)
            elif freq == "1T":
                return HourMinute(10, 1)
            else:
                return HourMinute(10, 0)
        else:
            if freq == "10T":
                return HourMinute(9, 10)
            elif freq == "1T":
                return HourMinute(9, 1)
            else:
                return HourMinute(9, 0)

    @staticmethod
    def end(dt: datetime, freq):
        if _is_exceptional_date(dt, "close"):
            if freq == "10T":
                return HourMinute(16, 50)
            else:
                return HourMinute(16, 45)
        else:
            if freq == "10T":
                return HourMinute(15, 50)
            else:
                return HourMinute(15, 45)


class OptionMarketTime(IMarketTimeV2, OpenCloseCheckable):
    @staticmethod
    def start(dt: datetime, freq):
        if _is_exceptional_date(dt, "open"):
            if freq == "10T":
                return HourMinute(10, 10)
            elif freq == "1T":
                return HourMinute(10, 1)
            else:
                return HourMinute(10, 0)
        else:
            if freq == "10T":
                return HourMinute(9, 10)
            elif freq == "1T":
                return HourMinute(9, 1)
            else:
                return HourMinute(9, 0)

    @staticmethod
    def end(dt: datetime, freq):
        # todo: 최종결제일 9:00~15:20
        if _is_exceptional_date(dt, "close"):
            if freq == "10T":
                return HourMinute(16, 50)
            else:
                return HourMinute(16, 45)
        else:
            if freq == "10T":
                return HourMinute(15, 50)
            else:
                return HourMinute(15, 45)


class StockMarketTimeV2(IMarketTimeV2, OpenCloseCheckable):
    @staticmethod
    def start(dt: datetime, freq):
        if _is_exceptional_date(dt, "open"):
            if freq == "10T":
                return HourMinute(10, 10)
            elif freq == "1T":
                return HourMinute(10, 1)
            else:
                return HourMinute(10, 0)
        else:
            if freq == "10T":
                return HourMinute(9, 10)
            elif freq == "1T":
                return HourMinute(9, 1)
            else:
                return HourMinute(9, 0)

    @staticmethod
    def end(dt: datetime, freq):
        if _is_exceptional_date(dt, "close"):
            if freq == "10T":
                return HourMinute(16, 40)
            elif freq == "1T":
                return HourMinute(16, 40)
            else:
                return HourMinute(15, 30)
        else:
            if freq == "10T":
                return HourMinute(15, 40)
            elif freq == "1T":
                return HourMinute(15, 40)
            else:
                return HourMinute(15, 30)


class StockCoMarketTime(IMarketTimeV2, OpenCloseCheckable):
    @staticmethod
    def start(dt: datetime, freq):
        if _is_exceptional_date(dt, "open"):
            if freq == "10T":
                return HourMinute(10, 10)
            elif freq == "1T":
                return HourMinute(10, 1)
            else:
                return HourMinute(10, 0)
        else:
            if freq == "10T":
                return HourMinute(9, 10)
            elif freq == "1T":
                return HourMinute(9, 1)
            else:
                return HourMinute(9, 0)

    @staticmethod
    def end(dt: datetime, freq):
        if _is_exceptional_date(dt, "close"):
            return HourMinute(16, 20)
        else:
            return HourMinute(15, 20)


def get_offset_from_freq(freq):  # 10T +10, 1T +1, 1d +0
    try:
        return (
            int(freq.replace("T", "")) if freq and freq.endswith("T") else 0
        )  # freq can be None
    except ValueError:
        print(f"wrong freq {freq}")
        return 0


class NYSEMarketTime(IMarketTimeV2, OpenCloseCheckable):
    MARKET_OPEN = "open"
    MARKET_CLOSE = "close"

    @staticmethod
    def start(dt: datetime, freq):
        open_hour, open_minute = NYSEMarketTime.get_nyse_open_close_time(
            dt, time_type=NYSEMarketTime.MARKET_OPEN
        )
        return HourMinute(
            open_hour, open_minute + get_offset_from_freq(freq)
        )  # 10T +10, 1T +1, 1d +0

    @staticmethod
    def end(dt: datetime, freq):
        hour, minute = NYSEMarketTime.get_nyse_open_close_time(
            dt, time_type=NYSEMarketTime.MARKET_CLOSE
        )
        return HourMinute(
            hour, minute + get_offset_from_freq(freq)
        )  # 10T +10, 1T +1, 1d +0

    @staticmethod
    def get_default_open_close_time(time_type):
        if time_type == NYSEMarketTime.MARKET_OPEN:
            hour, minute = 9, 30
        else:
            hour, minute = 16, 0
        return hour, minute

    @staticmethod
    def get_nyse_open_close_time(dt: datetime, time_type: str):  # dt is EST
        if (time_type == NYSEMarketTime.MARKET_CLOSE) and _is_exceptional_date(
            dt, time_type, exchange="us"
        ):
            return 13, 00
        else:
            return NYSEMarketTime.get_default_open_close_time(time_type)

    @staticmethod
    def get_schedule(start_date, end_date):  # date is EST

        return iter_us_trading_days(start_date, end_date)


def _is_exceptional_date(dt: datetime, open_close: str, exchange: str = "krx") -> bool:
    assert exchange in ["krx", "us"]
    return int(dt.strftime("%Y%m%d")) in _exceptional_dates(open_close, exchange)


def _exceptional_dates(open_close, exchange):
    exceptional_dates = load_config("exceptional_dates")[exchange]
    if exchange == "krx":
        return exceptional_dates["delay_%s_an_hour" % open_close]
    elif exchange == "us":
        # TODO: open delay not yet...
        # close at 13:00,
        return exceptional_dates["advance_%s_time" % open_close]
