import requests

from finter.ai.gpt.config import URL_NAME


def summary_strategy(input_text):
    url = f"http://{URL_NAME}:8282/summary_strategy"
    data = {"input": input_text}

    response = requests.post(url, json=data)
    return response.json()["result"]


if __name__ == "__main__":
    input_text = """
from finter import BaseAlpha
from datetime import datetime, timedelta


def calculate_previous_start_date(start_date, lookback_days):
    start = datetime.strptime(str(start_date), "%Y%m%d")
    previous_start = start - timedelta(days=lookback_days)
    return int(previous_start.strftime("%Y%m%d"))

LOOKBACK_DAYS = 365

# Alpha class inheriting from BaseAlpha
class Alpha(BaseAlpha):
    def get(self, start, end):
        pre_start = calculate_previous_start_date(start, LOOKBACK_DAYS)
        self.close = self.get_cm(
            "content.fnguide.ftp.price_volume.price_close.1d"
        ).get_df(pre_start, end)
        momentum_21d = self.close.pct_change(21, fill_method=None)
        stock_rank = momentum_21d.rank(pct=True, axis=1)
        stock_top10 = stock_rank[stock_rank<=0.1]
        stock_top10_rolling = stock_top10.rolling(21).apply(lambda x: x.mean())
        stock_ratio = stock_top10_rolling.div(stock_top10_rolling.sum(axis=1), axis=0)
        position = stock_ratio * 1e8
        alpha = position.shift(1)
        return alpha.loc[str(start): str(end)]
"""
    rel = summary_strategy(input_text)
