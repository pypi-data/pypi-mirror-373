from typing import Optional, Tuple

import numpy as np
from numba import njit
from typing_extensions import Literal


@njit
def redistribute(
    target: np.ndarray,
    max_limit: np.ndarray,
    weight: np.ndarray,
    max_iter: int,
) -> np.ndarray:
    it = 0
    adjusted = np.minimum(target, max_limit)

    excess = np.sum(target - adjusted)

    while excess > 1e-10 and it < max_iter:
        room_left = max_limit - adjusted
        can_add = room_left > 0

        if not np.any(can_add):
            break

        available_weights = weight * can_add
        weight_sum = available_weights.sum()

        if weight_sum <= 1e-10:
            break
        else:
            distribution = available_weights / weight_sum

        to_add = distribution * excess
        to_add = np.minimum(to_add, room_left)
        adjusted = adjusted + to_add

        excess = np.sum(target - adjusted)
        it += 1
    return adjusted


@njit
def apply_target_volume_constraint(
    prev_price: np.ndarray,
    target_volume: np.ndarray,
    target_volume_limit: Optional[np.ndarray],
    weight: np.ndarray,
    redistribute_max_iter: int = 0,
) -> np.ndarray:
    if target_volume_limit is None:
        return target_volume

    target_value = target_volume * prev_price
    target_value_limit = target_volume_limit * prev_price

    target_value = redistribute(
        target_value, target_value_limit, weight, redistribute_max_iter
    )
    return np.nan_to_num(target_value / prev_price)


@njit
def apply_turnover_volume_constraint(
    target_volume: np.ndarray,
    volume_capacity: np.ndarray,
    weight: np.ndarray,
) -> np.ndarray:
    # Notice: Redistribute in turnover constraint leads big difference in result.
    redistributed_target_volume = redistribute(
        target_volume, volume_capacity, weight, max_iter=0
    )
    return np.nan_to_num(redistributed_target_volume)


@njit
def update_target_volume(
    weight: np.ndarray,
    prev_aum: float,
    prev_price: np.ndarray,
    weight_before: np.ndarray,
    target_volume_before: np.ndarray,
    is_first_day: bool = False,
    rebalancing_method: Literal["auto", "W", "M", "Q", "by_position"] = "auto",
    rebalancing_mask: int = 0,
    target_volume_limit: Optional[np.ndarray] = None,
    redistribute_max_iter: int = 0,
) -> np.ndarray:
    if is_first_day or rebalancing_method == "auto":
        target_volume = np.nan_to_num(weight * prev_aum / prev_price)

    elif rebalancing_method == "by_position":
        # ISSUE
        if (np.abs(weight_before - weight) > 1e-10).any():
            target_volume = np.nan_to_num(weight * prev_aum / prev_price)
        else:
            target_volume = target_volume_before

    elif rebalancing_method in ["W", "M", "Q"]:
        if rebalancing_mask:
            target_volume = np.nan_to_num(weight * prev_aum / prev_price)
        else:
            target_volume = target_volume_before

    else:
        raise ValueError(f"Invalid rebalancing method: {rebalancing_method}")

    return apply_target_volume_constraint(
        prev_price,
        target_volume,
        target_volume_limit,
        weight,
        redistribute_max_iter,
    )


@njit
def calculate_buy_sell_volumes(
    target_volume: np.ndarray,
    prev_actual_holding_volume: np.ndarray,
    weight: np.ndarray,
    available_sell_volume: Optional[np.ndarray] = None,
    volume_capacity: Optional[np.ndarray] = None,
) -> tuple:
    target_buy_volume = np.maximum(target_volume - prev_actual_holding_volume, 0)
    target_sell_volume = np.maximum(prev_actual_holding_volume - target_volume, 0)

    if volume_capacity is not None:
        target_buy_volume = apply_turnover_volume_constraint(
            target_buy_volume, volume_capacity, weight
        )
        target_sell_volume = apply_turnover_volume_constraint(
            target_sell_volume, volume_capacity, weight
        )

    if available_sell_volume is not None:
        actual_sell_volume = np.minimum(available_sell_volume, target_sell_volume)
    else:
        actual_sell_volume = target_sell_volume

    return target_buy_volume, target_sell_volume, actual_sell_volume


@njit
def calculate_available_buy_amount(
    prev_cash: float,
    actual_sell_amount: np.ndarray,
    settlement_days: int,
    current_index: int,
) -> float:
    if current_index < settlement_days:
        return prev_cash

    settled_cash = prev_cash
    for i in range(settlement_days - 1, 0, -1):
        settled_cash -= actual_sell_amount[current_index - i].sum()
    return settled_cash


@njit
def execute_transactions(
    actual_sell_volume: np.ndarray,
    buy_price: np.ndarray,
    buy_fee_tax: float,
    sell_price: np.ndarray,
    sell_fee_tax: float,
    prev_cash: float,
    target_buy_volume: np.ndarray,
    actual_sell_amount: Optional[np.ndarray] = None,
    settlement_days: int = 0,
    current_index: int = 0,
) -> Tuple:
    actual_sell_amount_current = np.nan_to_num(
        actual_sell_volume * sell_price * (1 - sell_fee_tax)
    )
    available_buy_amount_non_settled = prev_cash + actual_sell_amount_current.sum()
    if actual_sell_amount is None:
        available_buy_amount = available_buy_amount_non_settled
    else:
        available_buy_amount = calculate_available_buy_amount(
            prev_cash,
            actual_sell_amount,
            settlement_days,
            current_index,
        )

    target_buy_amount = np.nan_to_num(target_buy_volume * buy_price * (1 + buy_fee_tax))
    target_buy_amount_sum = target_buy_amount.sum()
    if target_buy_amount_sum > 0:
        available_buy_volume = np.nan_to_num(
            (target_buy_amount / target_buy_amount_sum)
            * (available_buy_amount / (buy_price * (1 + buy_fee_tax)))
        )
        actual_buy_volume = np.minimum(available_buy_volume, target_buy_volume)
        actual_buy_amount = np.nan_to_num(
            actual_buy_volume * buy_price * (1 + buy_fee_tax)
        )
    else:
        actual_buy_volume = np.zeros_like(target_buy_volume)
        actual_buy_amount = np.zeros_like(target_buy_volume)
    return (
        actual_sell_amount_current,
        available_buy_amount_non_settled,
        actual_buy_volume,
        actual_buy_amount,
    )


@njit
def update_valuation_and_cash(
    prev_actual_holding_volume: np.ndarray,
    prev_valuation: np.ndarray,
    actual_buy_volume: np.ndarray,
    actual_sell_volume: np.ndarray,
    price: np.ndarray,
    available_buy_amount: float,
    actual_buy_amount: np.ndarray,
    dividend_ratio: Optional[np.ndarray] = None,
    drip: Literal[None, "cash", "reinvest", "coupon"] = None,
    dividend_tax: float = 0.0,
) -> tuple:
    # TODO: settle dividend

    actual_holding_volume = (
        prev_actual_holding_volume + actual_buy_volume - actual_sell_volume
    )

    if drip in ["cash", "reinvest"]:
        dividend = np.nan_to_num(prev_valuation * dividend_ratio) * (1 - dividend_tax)
    elif drip == "coupon":
        dividend = np.nan_to_num(actual_holding_volume * dividend_ratio) * (
            1 - dividend_tax
        )
    else:
        dividend = np.zeros_like(prev_valuation)

    if drip == "reinvest":
        cash = available_buy_amount - actual_buy_amount.sum() + dividend.sum()
    elif drip in ["cash", "coupon"]:
        cash = available_buy_amount - actual_buy_amount.sum()
    else:
        cash = available_buy_amount - actual_buy_amount.sum()

    valuation = np.nan_to_num(actual_holding_volume * price)
    return actual_holding_volume, valuation, cash, dividend


@njit
def update_aum(
    cash: float,
    valuation: np.ndarray,
    money_flow: float = 0.0,
) -> Tuple[float, float]:
    cash = cash + money_flow
    return cash, cash + valuation.sum()
