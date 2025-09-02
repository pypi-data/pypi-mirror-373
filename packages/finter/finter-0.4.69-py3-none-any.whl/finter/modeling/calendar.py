from datetime import datetime, timedelta

from finter.calendar import TradingDay


class DateConverter:
    @staticmethod
    def get_pre_start(start, lookback_days, trading_day=False):
        """
        Returns the pre-start date based on the given start date and lookback days.

        Parameters:
            start (int, str, datetime): The start date. It can be an integer in the format YYYYMMDD, a string in the format 'YYYYMMDD', or a datetime object.
            lookback_days (int): The number of days to look back.
            trading_day (bool, optional): If True, considers trading days only. Defaults to False.

        Returns:
            int or datetime: The pre-start date. If the start parameter is an integer or a string, the pre-start date will be returned as an integer in the format YYYYMMDD. If the start parameter is a datetime object, the pre-start date will be returned as a datetime object.

        Raises:
            ValueError: If the start parameter is not of type int, str, or datetime.

        Example:
            get_pre_start(20220101, 5)  # Returns 20211227
            get_pre_start('20220101', 5)  # Returns 20211227
            get_pre_start(datetime(2022, 1, 1), 5)  # Returns datetime(2021, 12, 27)
        """
        if isinstance(start, int):
            start = str(start)

        if isinstance(start, str):
            start = datetime.strptime(start, "%Y%m%d")
            if trading_day:
                pre_start = TradingDay.day_delta(start, n=-lookback_days)
            else:
                pre_start = start - timedelta(days=lookback_days)
            return int(pre_start.strftime("%Y%m%d"))

        elif isinstance(start, datetime):
            if trading_day:
                pre_start = TradingDay.day_delta(start, n=-lookback_days)
            else:
                pre_start = start - timedelta(days=lookback_days)
            return pre_start

        else:
            raise ValueError("start must be either int, str, or datetime")
