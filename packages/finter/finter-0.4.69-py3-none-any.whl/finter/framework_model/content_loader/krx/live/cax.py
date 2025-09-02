import re

import numpy as np

from finter.framework_model.content import Loader
from finter.settings import logger


class StockEventLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]

    @staticmethod
    def event_pattern(string, parsing_type):
        if (not string) or (type(string) != str):
            return []
        string = string.rstrip(")")
        l = re.split("[(]|[)]", string)

        if parsing_type == "event_code":
            l = set(i for i in l if l.index(i) % 2 == 0)
        elif parsing_type == "event_reason":
            l = set(i for i in l if l.index(i) % 2 == 1)
        else:
            raise ValueError("Choose in event_code or event_reason")

        return l

    def get_df(
        self,
        start: int,
        end: int,
        get_raw=False,
        filter_event_code=None,
        filter_event_reason=None,
        info=False,
        fill_nan=True,
        *args,
        **kwargs
    ):
        if info:
            event_info = {
                "01": "Trading Halt",
                "02": "Oversight Issues",
                "03": "Unfaithful Disclosure",
                "04": "Liquidation Trade",
                "05": "Backdoor Listing",
                "06": "Abeyance of Collateralized Security",
                "07": "Superior Corporate Governance",
                "08": "Covered Short Selling Not Allowed",
                "09": "Regulation S",
                "10": "Venture Company Designation",
                "11": "Investment Caution Issues",
                "12": "Short-term feverish issues",
                "13": "Trading Closure",
                "14": "Super Low Liquidity Issues",
                "15": "Investment precaution bond",
                "16": "Abnormal rise issues",
                "17": "Overheated short-selling issues",
                "18": "Optional LP system",
                "19": "Investment Precaution Issue",
                "20": "Preferred Stocks with lesser shares",
            }
            return event_info

        raw = self._load_cache(
            self.__CM_NAME,
            start,
            end,
            universe="krx-kospi-stock",
            freq=self.__FREQ,
            cache_t="hdf",
            fill_nan=fill_nan,
        )
        if get_raw:
            return raw

        # Setting default
        if not filter_event_code:
            logger.warning(
                "filter_event_code is not set. Default value: 01, 02, 03, 04, 20\n"
                "Use info=True to see event code descriptions\n"
                "Use get_raw=True to see raw data"
            )
            filter_event_code = ["01", "02", "03", "04", "20"]

        filter_raw_code = (
            (
                raw.applymap(
                    lambda x: any(
                        i
                        in StockEventLoader.event_pattern(
                            string=x, parsing_type="event_code"
                        )
                        for i in filter_event_code
                    )
                )
                * 1.0
            )
            .replace(0, np.nan)
            .dropna(how="all", axis=1)
        )

        # Todo: If reason filtering need
        # if filter_event_reason:
        #     filter_raw_reason = raw.applymap(
        #         lambda x: any(
        #             i in StockEventLoader.event_pattern(
        #                 string=x,
        #                 parsing_type='event_reason'
        #             ) for i in filter_event_code
        #         )
        #     )

        return filter_raw_code


"""
"Event Type Code 
01: Trading Halt 
02: Oversight Issues 
03: Unfaithful Disclosure 
04: Liquidation Trade 
05: Backdoor Listing 
06: Abeyance of Collateralized Security 
07: Superior Corporate Governance 
08: Covered Short Selling Not Allowed 
09: Regulation S
10: Venture Company Designation 
11: Investment Caution Issues 
12: Short-term feverish issues 
13: Trading Closure 
14: Super Low Liquidity Issues 
15: Investment precaution bond 
16: Abnormal rise issues 
17: Overheated short-selling issues 
18: Optional LP system
19: Investment Precaution Issue
20: Preferred Stocks with lesser shares


When Event Type Code is 01(Trading Halt), 02(Oversight Issues), 05(Backdoor Listing), please refer to the below for more details. ""0000"" is N/A. 
01: (Designation Alert) Application for restoration prodecure 
02: (Designation Alert) Trigger Clause for listed bond 
03: (Designation Alert) Holding a meeting of bondholders 
04: (Designation Alert) Resolution of meeting of bondholders
11: (Designation) All capital impaired 
12: (Designation) No submission of regular report
13: (Designation) No submission of quarterly/a half-term report
14: (Designation) Denial or Inappropriate opinion about a review 
15: (Designation) Denial or Inappropriate auditing opinion 
16: (Designation) Restrictive limit of scope of auditing opinion 
17: (Designation) Restrictive limit of scope of auditing opinion for two consecutive years 
18: (Designation) 
99: Designation"
"""
