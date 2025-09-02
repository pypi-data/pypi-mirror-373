import numpy as np
from numba import njit


@njit(cache=True)
def calculate_capital_gain_tax(
    sell_price: np.ndarray,
    prev_cummulative_buy_amount: np.ndarray,
    prev_average_buy_price: np.ndarray,
    prev_cummulative_realized_pnl: np.ndarray,
    actual_buy_volume: np.ndarray,
    buy_price: np.ndarray,
    actual_sell_volume: np.ndarray,
    actual_holding_volume: np.ndarray,
    capital_gain_tax_mask_prev: int,
    capital_gain_tax_mask_current: int,
    capital_gain_tax_rate: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    cummulative_buy_amount = (
        prev_cummulative_buy_amount
        + (actual_buy_volume * np.nan_to_num(buy_price))
        - (actual_sell_volume * prev_average_buy_price)
    )

    average_buy_price = np.nan_to_num(cummulative_buy_amount / actual_holding_volume)

    realized_pnl = (
        np.nan_to_num(sell_price) - prev_average_buy_price
    ) * actual_sell_volume

    if capital_gain_tax_mask_current:
        capital_gain_tax = (
            capital_gain_tax_mask_current
            * capital_gain_tax_rate
            * prev_cummulative_realized_pnl.sum()
        )
        cummulative_realized_pnl = realized_pnl
    else:
        cummulative_realized_pnl = prev_cummulative_realized_pnl + realized_pnl
        capital_gain_tax = 0

    return (
        cummulative_buy_amount,
        average_buy_price,
        cummulative_realized_pnl,
        capital_gain_tax,
    )
