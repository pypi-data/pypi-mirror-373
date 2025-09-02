from typing import Tuple

import numpy as np
from numba import njit


@njit(cache=True)
def execute_sell_transactions(
    target_sell_volume: np.ndarray,
    target_short_sell_volume: np.ndarray,
    sell_price: np.ndarray,
    sell_fee_tax: float,
    actual_holding_volume: np.ndarray,
    actual_buy_volume: np.ndarray,
    adjustment_ratio: np.ndarray,
    i: int,
    settlement_days: int,
    lot_size: int,
    volume_adjustment_ratio: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    actual_sell_volume = target_sell_volume.copy()

    if lot_size > 0:
        raw_remaining_sell_volume = (
            actual_holding_volume * volume_adjustment_ratio
            - np.trunc(actual_holding_volume * volume_adjustment_ratio / lot_size)
            * lot_size
        )
        # Apply remainder only when there is a positive holding and a positive sell target
        remaining_sell_volume = np.where(
            (actual_holding_volume > 0) & (target_sell_volume > 0),
            raw_remaining_sell_volume,
            0.0,
        )
        normal_sell_volume = np.trunc(target_sell_volume / lot_size) * lot_size
        actual_sell_volume = normal_sell_volume + remaining_sell_volume

    available_sell_volume = calculate_available_sell_volume(
        actual_holding_volume,
        actual_buy_volume,
        adjustment_ratio,
        i,
        settlement_days,
    )
    available_sell_volume = np.maximum(available_sell_volume, 0)
    actual_sell_volume = np.minimum(available_sell_volume, actual_sell_volume)
    actual_sell_volume = np.maximum(actual_sell_volume, 0)

    actual_sell_amount = np.nan_to_num(
        actual_sell_volume * sell_price * (1 - sell_fee_tax)
    )

    # Handle short sell (no constraints, can short any amount)
    if target_short_sell_volume is not None:
        actual_short_sell_volume = target_short_sell_volume.copy()

        if lot_size > 0:
            actual_short_sell_volume = (
                np.trunc(target_short_sell_volume / lot_size) * lot_size
            )

        actual_short_sell_amount = np.nan_to_num(
            actual_short_sell_volume * sell_price * (1 - sell_fee_tax)
        )
    else:
        actual_short_sell_volume = np.zeros_like(target_sell_volume)
        actual_short_sell_amount = np.zeros_like(target_sell_volume)

    return (
        np.nan_to_num(actual_sell_volume),
        np.nan_to_num(actual_sell_amount),
        np.nan_to_num(actual_short_sell_volume),
        np.nan_to_num(actual_short_sell_amount),
    )


@njit(cache=True)
def calculate_available_sell_volume(
    actual_holding_volume: np.ndarray,
    actual_buy_volume: np.ndarray,
    adjustment_ratio: np.ndarray,
    i: int,
    settlement_days: int,
) -> np.ndarray:
    if i < settlement_days:
        return np.zeros_like(actual_holding_volume)
    else:
        available_sell_volume = actual_holding_volume / adjustment_ratio[i - 1]
        for j in range(settlement_days - 1, 0, -1):
            available_sell_volume -= actual_buy_volume[i - j] / adjustment_ratio[i - j]
        available_sell_volume = np.maximum(available_sell_volume, 0)

    return np.maximum(available_sell_volume * adjustment_ratio[i], 0)


@njit(cache=True)
def execute_buy_transactions(
    buy_price: np.ndarray,
    buy_fee_tax: float,
    prev_cash: float,
    target_buy_volume: np.ndarray,
    target_short_cover_volume: np.ndarray,
    actual_holding_volume: np.ndarray,
    actual_sell_amount: np.ndarray,
    actual_short_sell_amount: np.ndarray,
    settlement_days: int,
    current_index: int,
    lot_size: int = 0,
) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    available_buy_amount = (
        prev_cash
        + actual_sell_amount[current_index].sum()
        + actual_short_sell_amount[current_index].sum()
    )

    available_buy_amount_settled = calculate_available_buy_amount(
        prev_cash,
        available_buy_amount,
        settlement_days,
        actual_sell_amount,
        current_index,
    )

    target_buy_amount = np.nan_to_num(target_buy_volume * buy_price * (1 + buy_fee_tax))
    target_buy_amount_sum = target_buy_amount.sum()
    if target_buy_amount_sum > 0:
        available_buy_volume = np.nan_to_num(
            (target_buy_amount / target_buy_amount_sum)
            * (available_buy_amount_settled / (buy_price * (1 + buy_fee_tax)))
        )
        actual_buy_volume = np.minimum(available_buy_volume, target_buy_volume)

        if lot_size > 0:
            actual_buy_volume = np.trunc(actual_buy_volume / lot_size) * lot_size

        actual_buy_amount = np.nan_to_num(
            actual_buy_volume * buy_price * (1 + buy_fee_tax)
        )
    else:
        actual_buy_volume = np.zeros_like(target_buy_volume)
        actual_buy_amount = np.zeros_like(target_buy_volume)

    target_short_cover_amount = np.nan_to_num(
        target_short_cover_volume * buy_price * (1 + buy_fee_tax)
    )
    target_short_cover_amount_sum = target_short_cover_amount.sum()

    if target_short_cover_amount_sum > 0:
        remaining_cash_after_buy = available_buy_amount_settled - (
            actual_buy_amount.sum() if target_buy_amount_sum > 0 else 0
        )
        available_short_cover_volume = np.nan_to_num(
            (target_short_cover_amount / target_short_cover_amount_sum)
            * (remaining_cash_after_buy / (buy_price * (1 + buy_fee_tax)))
        )
        actual_short_cover_volume = np.minimum(
            available_short_cover_volume, target_short_cover_volume
        )
    else:
        actual_short_cover_volume = target_short_cover_volume.copy()

    short_mask = actual_holding_volume < 0
    actual_short_cover_volume = np.where(
        short_mask, np.minimum(actual_short_cover_volume, -actual_holding_volume), 0
    )

    if lot_size > 0:
        actual_short_cover_volume = (
            np.trunc(actual_short_cover_volume / lot_size) * lot_size
        )

    actual_short_cover_amount = np.nan_to_num(
        actual_short_cover_volume * buy_price * (1 + buy_fee_tax)
    )

    return (
        available_buy_amount,
        actual_buy_volume,
        actual_buy_amount,
        actual_short_cover_volume,
        actual_short_cover_amount,
    )


@njit(cache=True)
def calculate_available_buy_amount(
    prev_cash: float,
    available_buy_amount: float,
    settlement_days: int,
    actual_sell_amount: np.ndarray,
    current_index: int,
) -> float:
    if current_index < settlement_days:
        available_buy_amount_settled = prev_cash
    else:
        available_buy_amount_settled = available_buy_amount
        for i in range(settlement_days - 1, -1, -1):
            available_buy_amount_settled -= actual_sell_amount[current_index - i].sum()
    return available_buy_amount_settled
