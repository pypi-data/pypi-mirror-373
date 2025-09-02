from typing import Optional, Tuple

import numpy as np
from numba import njit

from finter.backtest.config.config import AVAILABLE_DIVIDEND_TYPES


@njit(cache=True)
def update_valuation_and_cash(
    prev_actual_holding_volume: np.ndarray,
    prev_valuation: np.ndarray,
    actual_buy_volume: np.ndarray,
    actual_sell_volume: np.ndarray,
    actual_short_sell_volume: np.ndarray,
    actual_short_cover_volume: np.ndarray,
    price: np.ndarray,
    available_buy_amount: float,
    actual_buy_amount: np.ndarray,
    actual_short_cover_amount: np.ndarray,
    dividend_ratio: Optional[np.ndarray],
    drip: AVAILABLE_DIVIDEND_TYPES,
    dividend_tax: float,
    volume_adjustment_ratio: np.ndarray,
) -> tuple:
    # TODO: settle dividend
    actual_holding_volume = (
        prev_actual_holding_volume * volume_adjustment_ratio
        + actual_buy_volume
        + actual_short_cover_volume
        - actual_sell_volume
        - actual_short_sell_volume
    )
    valuation = np.nan_to_num(actual_holding_volume * price)

    dividend = calculate_dividend(
        prev_valuation,
        actual_holding_volume,
        dividend_ratio,
        drip,
        dividend_tax,
    )

    cash = transfer_dividend(
        available_buy_amount,
        actual_buy_amount,
        actual_short_cover_amount,
        dividend,
        drip,
    )

    return actual_holding_volume, valuation, cash, dividend


@njit(cache=True)
def calculate_dividend(
    prev_valuation: np.ndarray,
    actual_holding_volume: np.ndarray,
    dividend_ratio: Optional[np.ndarray],
    drip: AVAILABLE_DIVIDEND_TYPES,
    dividend_tax: float,
) -> np.ndarray:
    if drip in ["cash", "reinvest"]:
        dividend = np.nan_to_num(prev_valuation * dividend_ratio) * (1 - dividend_tax)
    elif drip == "coupon":
        dividend = np.nan_to_num(actual_holding_volume * dividend_ratio) * (
            1 - dividend_tax
        )
    else:
        dividend = np.zeros_like(prev_valuation)
    return dividend


@njit(cache=True)
def transfer_dividend(
    available_buy_amount: float,
    actual_buy_amount: np.ndarray,
    actual_short_cover_amount: np.ndarray,
    dividend: np.ndarray,
    drip: AVAILABLE_DIVIDEND_TYPES,
) -> float:
    if drip == "reinvest":
        cash = (
            available_buy_amount
            - actual_buy_amount.sum()
            - actual_short_cover_amount.sum()
            + dividend.sum()
        )
    elif drip in ["cash", "coupon"]:
        cash = (
            available_buy_amount
            - actual_buy_amount.sum()
            - actual_short_cover_amount.sum()
        )
    else:
        cash = (
            available_buy_amount
            - actual_buy_amount.sum()
            - actual_short_cover_amount.sum()
        )
    return np.nan_to_num(cash)


@njit(cache=True)
def update_aum(
    cash: float,
    valuation: np.ndarray,
    money_flow: float,
    capital_gain_tax: float,
    deposit_interest_rate: float,
) -> Tuple[float, float]:
    cash = cash * (1 + deposit_interest_rate)
    cash = cash + money_flow
    cash = cash - capital_gain_tax
    return np.nan_to_num(cash), np.nan_to_num(cash + valuation.sum())
