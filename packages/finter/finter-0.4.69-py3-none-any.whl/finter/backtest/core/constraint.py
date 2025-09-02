from typing import Optional

import numpy as np
from numba import njit


@njit(cache=True)
def apply_target_volume_constraint(
    prev_price: np.ndarray,
    target_volume: np.ndarray,
    target_volume_limit: Optional[np.ndarray],
    weight: np.ndarray,
    redistribute_max_iter: int,
) -> np.ndarray:
    if target_volume_limit is None:
        return target_volume

    target_value = target_volume * prev_price
    target_value_limit = target_volume_limit * prev_price

    target_value = redistribute(
        target_value, target_value_limit, weight, redistribute_max_iter
    )
    return np.nan_to_num(target_value / prev_price)


@njit(cache=True)
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


@njit(cache=True)
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
