from dataclasses import dataclass, field
from typing import Tuple

import numpy as np


@dataclass
class InputVars:
    weight: np.ndarray
    price: np.ndarray

    adjustment_ratio: np.ndarray

    buy_price: np.ndarray
    sell_price: np.ndarray
    volume_capacity: np.ndarray
    target_volume_limit: np.ndarray

    rebalancing_mask: np.ndarray
    capital_gain_tax_mask: np.ndarray

    dividend_ratio: np.ndarray
    exchange_rate: np.ndarray
    money_flow: np.ndarray


@dataclass
class PositionVars:
    actual_holding_volume: np.ndarray
    target_volume: np.ndarray


@dataclass
class BuyVars:
    target_buy_volume: np.ndarray
    target_short_cover_volume: np.ndarray
    available_buy_volume: np.ndarray
    actual_buy_volume: np.ndarray
    actual_buy_amount: np.ndarray
    actual_short_cover_volume: np.ndarray
    actual_short_cover_amount: np.ndarray
    available_buy_amount: np.ndarray
    target_buy_amount: np.ndarray

    cummulative_buy_amount: np.ndarray
    average_buy_price: np.ndarray


@dataclass
class SellVars:
    target_sell_volume: np.ndarray
    target_short_sell_volume: np.ndarray
    actual_sell_volume: np.ndarray
    actual_sell_amount: np.ndarray
    actual_short_sell_volume: np.ndarray
    actual_short_sell_amount: np.ndarray


@dataclass
class ResultVars:
    valuation: np.ndarray
    cash: np.ndarray
    aum: np.ndarray
    dividend: np.ndarray

    cummulative_realized_pnl: np.ndarray
    capital_gain_tax: np.ndarray


@dataclass
class SimulationVariables:
    input: InputVars

    shape: Tuple[int, int]
    shape_1d: Tuple[int, int] = field(init=False)

    position: PositionVars = field(init=False)
    buy: BuyVars = field(init=False)
    sell: SellVars = field(init=False)
    result: ResultVars = field(init=False)

    def __post_init__(self):
        self.shape_1d = (self.shape[0], 1)

        # Initialize sub-dataclasses
        self.position = PositionVars(
            actual_holding_volume=np.full(self.shape, np.nan, dtype=np.float64),
            target_volume=np.full(self.shape, np.nan, dtype=np.float64),
        )

        self.buy = BuyVars(
            target_buy_volume=np.full(self.shape, np.nan, dtype=np.float64),
            target_short_cover_volume=np.full(self.shape, np.nan, dtype=np.float64),
            actual_short_cover_volume=np.full(self.shape, np.nan, dtype=np.float64),
            actual_short_cover_amount=np.full(self.shape, np.nan, dtype=np.float64),
            available_buy_volume=np.full(self.shape, np.nan, dtype=np.float64),
            available_buy_amount=np.full(self.shape_1d, np.nan, dtype=np.float64),
            actual_buy_volume=np.full(self.shape, np.nan, dtype=np.float64),
            actual_buy_amount=np.full(self.shape, np.nan, dtype=np.float64),
            target_buy_amount=np.full(self.shape, np.nan, dtype=np.float64),
            cummulative_buy_amount=np.full(self.shape, np.nan, dtype=np.float64),
            average_buy_price=np.full(self.shape, np.nan, dtype=np.float64),
        )

        self.sell = SellVars(
            target_sell_volume=np.full(self.shape, np.nan, dtype=np.float64),
            target_short_sell_volume=np.full(self.shape, np.nan, dtype=np.float64),
            actual_sell_volume=np.full(self.shape, np.nan, dtype=np.float64),
            actual_sell_amount=np.full(self.shape, np.nan, dtype=np.float64),
            actual_short_sell_volume=np.full(self.shape, np.nan, dtype=np.float64),
            actual_short_sell_amount=np.full(self.shape, np.nan, dtype=np.float64),
        )

        self.result = ResultVars(
            valuation=np.full(self.shape, np.nan, dtype=np.float64),
            cash=np.full(self.shape_1d, np.nan, dtype=np.float64),
            aum=np.full(self.shape_1d, np.nan, dtype=np.float64),
            dividend=np.full(self.shape, np.nan, dtype=np.float64),
            cummulative_realized_pnl=np.full(self.shape, np.nan, dtype=np.float64),
            capital_gain_tax=np.full(self.shape_1d, np.nan, dtype=np.float64),
        )

    def initialize(self, initial_cash: float):
        self.position.actual_holding_volume[0] = 0
        self.sell.actual_sell_amount[0] = 0

        self.result.cash[0] = initial_cash
        self.result.aum[0] = initial_cash
        self.result.valuation[0] = 0
        self.result.dividend[0] = 0
        self.result.cummulative_realized_pnl[0] = 0
        self.result.capital_gain_tax[0] = 0

        self.buy.cummulative_buy_amount[0] = 0
        self.buy.average_buy_price[0] = 0
