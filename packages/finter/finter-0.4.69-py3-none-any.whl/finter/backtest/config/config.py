from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import pandas as pd
from typing_extensions import Literal

from finter.data.data_handler.main import DataHandler

AVAILABLE_RESAMPLE_PERIODS = Literal[None, "W", "M", "Q"]
AVAILABLE_REBALANCING_METHODS = Literal["auto", "W", "M", "Q", "by_position"]
AVAILABLE_CORE_TYPES = Literal["basic", "id_fund", "vn"]
AVAILABLE_DIVIDEND_TYPES = Literal[None, "cash", "reinvest", "coupon"]
AVAILABLE_MARKETS = Literal[
    "kr_stock",
    "us_stock",
    "us_etf",
    "us_future",
    "id_stock",
    "id_bond",
    "id_fund",
    #########################################################
    "vn_stock",
    "btcusdt_spot_binance",
]
AVAILABLE_BASE_CURRENCY = Literal["KRW", "IDR", "USD", "VND"]
AVAILABLE_DEFAULT_BENCHMARK = Literal[
    "KOSPI200", "S&P500", "JCI", "HO_CHI_MINH_STOCK_INDEX", "US_DOLLAR_INDEX"
]


@dataclass
class DataConfig:
    position: pd.DataFrame = field(default_factory=pd.DataFrame)

    price: pd.DataFrame = field(default_factory=pd.DataFrame)
    adjustment_ratio: pd.DataFrame = field(default_factory=pd.DataFrame)

    volume: pd.DataFrame = field(default_factory=pd.DataFrame)

    constituent: pd.DataFrame = field(default_factory=pd.DataFrame)

    dividend_ratio: pd.DataFrame = field(default_factory=pd.DataFrame)
    exchange_rate: pd.DataFrame = field(default_factory=pd.DataFrame)
    money_flow: pd.DataFrame = field(default_factory=pd.DataFrame)

    def __repr__(self) -> str:
        summaries = {
            "position": f"DataFrame(shape={self.position.shape})"
            if not self.position.empty
            else "Empty",
            "price": f"DataFrame(shape={self.price.shape})"
            if not self.price.empty
            else "Empty",
            "volume": f"DataFrame(shape={self.volume.shape})"
            if not self.volume.empty
            else "Empty",
            "adjustment_ratio": f"DataFrame(shape={self.adjustment_ratio.shape})"
            if not self.adjustment_ratio.empty
            else "Empty",
            "dividend_ratio": f"DataFrame(shape={self.dividend_ratio.shape})"
            if not self.dividend_ratio.empty
            else "Empty",
            "exchange_rate": f"DataFrame(shape={self.exchange_rate.shape})"
            if not self.exchange_rate.empty
            else "Empty",
            "money_flow": f"DataFrame(shape={self.money_flow.shape})"
            if not self.money_flow.empty
            else "Empty",
            "constituent": f"DataFrame(shape={self.constituent.shape})"
            if not self.constituent.empty
            else "Empty",
        }
        fields = [f"{k}={v}" for k, v in summaries.items()]
        return f"DataConfig({', '.join(fields)})"


@dataclass
class DateConfig:
    start: int = 20150101  # e.g. 20200101
    end: int = int(datetime.now().strftime("%Y%m%d"))  # e.g. 20201231


@dataclass
class CostConfig:
    # unit: basis point
    buy_fee_tax: float = 0.0
    sell_fee_tax: float = 0.0
    slippage: float = 0.0
    dividend_tax: float = 0.0

    capital_gain_tax: float = 0.0


@dataclass
class TradeConfig:
    initial_cash: float = 1e8
    volume_capacity_ratio: float = 0.0

    deposit_interest_rate: float = 0.0  # unit: basis point

    target_volume_limit_args: Optional[Dict[str, Any]] = (
        None  # 항상 아래 형식으로 사용:
        # {"processors": [
        #    {"type": "trading_volume", "rolling_window": 20, "limit_ratio": 0.1},
        #    {"type": "universe", "sub_universe": "spx"}
        # ], "redistribute_max_iter": 0}
        #
        # 단일 프로세서인 경우:
        # {"processors": [
        #    {"type": "trading_volume", "rolling_window": 20, "limit_ratio": 0.1}
        # ], "redistribute_max_iter": 0}
    )
    lot_args: Optional[Dict[str, Any]] = None  # e.g. {"size": 100}


@dataclass
class ExecutionConfig:
    resample_period: AVAILABLE_RESAMPLE_PERIODS = None
    rebalancing_method: AVAILABLE_REBALANCING_METHODS = "auto"

    core_type: AVAILABLE_CORE_TYPES = "basic"

    drip: AVAILABLE_DIVIDEND_TYPES = None


@dataclass
class OptionalConfig:
    debug: bool = False
    results: list[str] = field(
        default_factory=lambda: [
            "summary",
            "statistics",
            "report",
            "performance",
        ]
    )


@dataclass
class CacheConfig:
    data_handler: Optional[DataHandler] = None
    timeout: int = 300
    maxsize: int = 5


@dataclass
class FrameConfig:
    shape: Tuple[int, int] = field(default_factory=tuple)
    common_columns: list[str] = field(default_factory=list)
    common_index: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        summaries = {
            "shape": self.shape,
            "common_columns": f"{len(self.common_columns)} columns",
            "common_index": f"{len(self.common_index)} dates",
        }
        fields = [f"{k}={v}" for k, v in summaries.items()]
        return f"FrameConfig({', '.join(fields)})"


@dataclass
class SimulatorConfig:
    date: DateConfig
    cost: CostConfig
    trade: TradeConfig
    execution: ExecutionConfig
    optional: OptionalConfig
    cache: CacheConfig
    frame: FrameConfig

    def __repr__(self) -> str:
        date_info = f"Date: {self.date.start} -> {self.date.end}"
        cost_info = "Cost: " + ", ".join(
            f"{slot}: {getattr(self.cost, slot) * 10000:.1f}bp"
            for slot in slots(self.cost)
        )
        trade_info = "Trade: " + ", ".join(
            f"{slot}: {getattr(self.trade, slot)}" for slot in slots(self.trade)
        )
        execution_info = "Execution: " + ", ".join(
            f"{slot}: {getattr(self.execution, slot)}" for slot in slots(self.execution)
        )
        frame_info = f"Frame: {self.frame.shape}"

        return (
            "┌─────────────────────────────────────\n"
            f"│ {date_info}\n"
            f"│ {cost_info}\n"
            f"│ {trade_info}\n"
            f"│ {execution_info}\n"
            f"│ {frame_info}\n"
            "└─────────────────────────────────────"
        )


def slots(cls):
    return [f.name for f in fields(cls)]
