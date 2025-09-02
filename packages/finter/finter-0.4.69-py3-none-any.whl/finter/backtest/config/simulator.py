from typing import Any, Dict, Optional

import pandas as pd
from typing_extensions import TypedDict

from finter.backtest.config.config import (
    AVAILABLE_BASE_CURRENCY,
    AVAILABLE_CORE_TYPES,
    AVAILABLE_DIVIDEND_TYPES,
    AVAILABLE_REBALANCING_METHODS,
    AVAILABLE_RESAMPLE_PERIODS,
)


class SimulatorInputConfig(TypedDict, total=False):
    # date
    start: int
    end: int

    # data
    money_flow: pd.DataFrame

    # cost
    buy_fee_tax: float
    sell_fee_tax: float
    slippage: float
    dividend_tax: float

    capital_gain_tax: float

    # trade
    deposit_interest_rate: float

    initial_cash: float
    volume_capacity_ratio: float
    target_volume_limit_args: Optional[Dict[str, Any]]
    lot_args: Optional[Dict[str, Any]]

    # execution
    resample_period: AVAILABLE_RESAMPLE_PERIODS
    rebalancing_method: AVAILABLE_REBALANCING_METHODS
    core_type: AVAILABLE_CORE_TYPES
    drip: AVAILABLE_DIVIDEND_TYPES

    # optional
    debug: bool
    results: list[str]

    # external
    currency: AVAILABLE_BASE_CURRENCY
