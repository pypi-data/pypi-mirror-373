from datetime import datetime, timedelta

import pandas as pd

from finter.framework_model.calendar import iter_trading_days, iter_us_trading_days
from finter.utils.market_time import FutureMarketTimeV2, StockMarketTimeV2


def outsample_end_date(now: datetime, n_week=104, n_seconds=None) -> datetime:
    if n_seconds is not None and n_seconds >= 0:
        return now - pd.Timedelta(seconds=n_seconds)
    return pd.date_range(end=now, periods=n_week, freq="1W-SAT", normalize=True)[0].to_pydatetime()


def convert_to_int(x):
    return int(str(x.date()).replace("-", ""))


class Indexer:
    def __init__(self, start, end, freq):
        self.__START = start
        self.__END = end
        self.__FREQ = freq
        self.__START_DATETM, self.__END_DATETM = IndexUtil.convert_start_end_to_datetm(
            self.__START, self.__END
        )

    def get_index(self, exchange, universe, instrument_type):
        # TODO: as universe / instrument_type / irregurar open close time
        if exchange == "us" and self.__FREQ == "1d":
            return pd.DatetimeIndex(
                list(iter_us_trading_days(self.__START_DATETM, self.__END_DATETM))
            )

        elif exchange == "vnm" and self.__FREQ == "1d":
            return pd.DatetimeIndex(
                list(
                    iter_trading_days(
                        self.__START_DATETM, self.__END_DATETM, exchange="vnm"
                    )
                )
            )

        elif exchange == "id" and self.__FREQ == "1d":
            return pd.DatetimeIndex(
                list(
                    iter_trading_days(
                        self.__START_DATETM, self.__END_DATETM, exchange="id"
                    )
                )
            )

        elif exchange != "krx":
            return pd.date_range(
                self.__START_DATETM, self.__END_DATETM, freq=self.__FREQ
            )

        if "W" in self.__FREQ or "M" in self.__FREQ or "Q" in self.__FREQ:
            return pd.date_range(
                self.__START_DATETM.date(), self.__END_DATETM.date(), freq=self.__FREQ
            )
        elif self.__FREQ == "1d":
            return pd.Index(
                [
                    pd.to_datetime(str(date))
                    for date in iter_trading_days(
                        self.__START_DATETM, self.__END_DATETM
                    )
                ]
            )
        else:
            daily = pd.DatetimeIndex([]).union_many(
                [
                    IndexUtil.get_daily_index(
                        date, self.__FREQ, exchange, universe, instrument_type
                    )
                    for date in iter_trading_days(
                        self.__START_DATETM, self.__END_DATETM
                    )
                ]
            )
            return daily[(daily >= self.__START_DATETM) & (daily <= self.__END_DATETM)]

    def convert(
        self,
        df,
        exchange="krx",
        universe="kospi",
        instrument_type="stock",
        valid_from=20171219,
    ):
        start = self.set_if_none(self.__START, valid_from)
        end = self.set_if_none(self.__END, datetime.today())
        start_datetm, end_datetm = IndexUtil.convert_start_end_to_datetm(start, end)
        df = IndexUtil.convert_index_to_datetime(df)
        datetm_idx = self.get_index(exchange, universe, instrument_type)
        return df.reindex(index=datetm_idx).loc[start_datetm:end_datetm, :]

    @staticmethod
    def set_if_none(x, default):
        if x is None:
            return int(str(default.date()).replace("-", ""))
        else:
            return x


class IndexUtil:
    __DT_FORMAT = "%Y%m%d%H%M%S"
    __DT_STR_LEN = 14

    @classmethod
    def convert_index_to_datetime(cls, df):
        if df.index.is_numeric():
            df.index = df.index.astype("str").str.pad(cls.__DT_STR_LEN, "right", "0")
            df.index = pd.to_datetime(df.index, format=cls.__DT_FORMAT)
        return df

    @staticmethod
    def get_start_end_time(date, freq, universe, instrument_type):
        if isinstance(date, int):
            date = str(date)
        datetm = datetime.strptime(date, "%Y%m%d")

        if universe in ["stock", "index", "bond", "currency", "commodity"]:
            start = FutureMarketTimeV2.start(datetm, freq)
            end = FutureMarketTimeV2.end(datetm, freq)
        else:
            start = StockMarketTimeV2.start(datetm, freq)
            end = StockMarketTimeV2.end(datetm, freq)
        return date + str(start.hour).rjust(2, "0") + str(start.minute).rjust(
            2, "0"
        ), date + str(end.hour).rjust(2, "0") + str(end.minute).rjust(2, "0")

    @classmethod
    def get_daily_index(cls, date, freq, exchange, universe, instrument_type):
        return pd.date_range(
            *cls.get_start_end_time(str(date), freq, universe, instrument_type),
            freq=freq,
        )

    @classmethod
    def convert_start_end_to_datetm(cls, start, end):
        assert isinstance(start, int)
        assert isinstance(end, int)

        start = datetime.strptime(
            str(start).ljust(cls.__DT_STR_LEN, "0"), cls.__DT_FORMAT
        )
        end = str(end)
        end_fill = cls.__DT_STR_LEN - len(end)

        if end_fill % 2 == 1:
            end_fill -= 1
            end += "0"

        if end_fill == 0:
            end = datetime.strptime(end, cls.__DT_FORMAT)
        elif end_fill == 2:
            end = datetime.strptime(end + "00", cls.__DT_FORMAT)
        elif end_fill == 4:
            end = datetime.strptime(end + "5900", cls.__DT_FORMAT)
        elif end_fill == 6:
            end = datetime.strptime(end + "235900", cls.__DT_FORMAT)
        else:
            raise ValueError("invalid end: %s" % end)
        return start, end

    @staticmethod
    def get_date_range(start: int, end: int, freq: str):
        str_end = str(end)
        assert (
            8 <= len(str(start)) <= 14 or 8 <= len(str_end) <= 14
        ), f"Value Error: only support 8 ~ 14 length, {str(start)}, {str_end}"
        start, end = sort_start_end_to_left(start, end)
        freq_unit = freq[-1]
        end = get_max_end_point(end, str_end)
        if not end:
            assert False, f"not supported freq_unit {freq_unit}"
        return pd.date_range(start, end, freq=freq)

    @staticmethod
    def get_start_end_points(start: int, end: int):
        d = "%Y%m%d%H%M%S"
        str_end = str(end)
        start, end = sort_start_end_to_left(start, end)
        end = get_max_end_point(end, str_end)
        start = int(datetime.strftime(start, d))
        end = int(datetime.strftime(end, d))
        return start, end


def sort_start_end_to_left(start: int, end: int):
    d = "%Y%m%d%H%M%S"
    str_start = str(start)
    str_end = str(end)
    start = datetime.strptime(str_start.ljust(14, "0"), d)
    end = datetime.strptime(str_end.ljust(14, "0"), d)
    return start, end


def get_max_end_point(end: datetime, str_end: str):
    if len(str_end) == 8:
        end += timedelta(hours=23, minutes=59, seconds=59)
    elif len(str_end) == 10:
        end += timedelta(minutes=59, seconds=59)
    elif len(str_end) == 12:
        end += timedelta(seconds=59)
    elif len(str_end) == 14:
        pass
    else:
        assert (
            False
        ), f"Not supported unit. Enter only within the range of yyyymmdd ~ yyyymmddHHMMSS"
    return end
