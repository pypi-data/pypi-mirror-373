from typing import Any, Dict, Optional, Tuple

import numpy as np
from numba import njit

from finter.backtest.config.config import AVAILABLE_REBALANCING_METHODS


@njit(cache=True)
def calculate_volume_adjustment_ratio(
    adjustment_ratio: np.ndarray,
    prev_adjustment_ratio: np.ndarray,
) -> np.ndarray:
    return adjustment_ratio / prev_adjustment_ratio


def prepare_data(
    current_index: int,
    price: np.ndarray,
    adjustment_ratio: np.ndarray,
    rebalancing_method: AVAILABLE_REBALANCING_METHODS,
    rebalancing_mask: np.ndarray,
    capital_gain_tax: float,
    capital_gain_tax_mask: np.ndarray,
    target_volume_limit: np.ndarray,
    target_volume_limit_args: Optional[Dict[str, Any]],
    lot_args: Optional[Dict[str, Any]] = None,
) -> Tuple[np.ndarray, np.ndarray, int, Optional[np.ndarray], int, int, int, int]:
    prev_adj_price = price[current_index - 1] * adjustment_ratio[current_index - 1]
    volume_adjustment_ratio = calculate_volume_adjustment_ratio(
        adjustment_ratio[current_index], adjustment_ratio[current_index - 1]
    )

    if rebalancing_method in ["W", "M", "Q"]:
        rebalancing_mask_current = rebalancing_mask[current_index]
    else:
        rebalancing_mask_current = 0

    if capital_gain_tax != 0:
        capital_gain_tax_mask_current = capital_gain_tax_mask[current_index]
        capital_gain_tax_mask_prev = capital_gain_tax_mask[current_index - 1]
    else:
        capital_gain_tax_mask_current = 0
        capital_gain_tax_mask_prev = 0

    if target_volume_limit_args is not None:
        target_volume_limit_current = target_volume_limit[current_index - 1]
        redistribute_max_iter = target_volume_limit_args.get("redistribute_max_iter", 0)
    else:
        target_volume_limit_current = None
        redistribute_max_iter = 0

    if lot_args is not None:
        lot_size = lot_args.get("size", 0)
    else:
        lot_size = 0

    return (
        prev_adj_price,
        volume_adjustment_ratio,
        rebalancing_mask_current,
        target_volume_limit_current,
        redistribute_max_iter,
        lot_size,
        capital_gain_tax_mask_current,
        capital_gain_tax_mask_prev,
    )
