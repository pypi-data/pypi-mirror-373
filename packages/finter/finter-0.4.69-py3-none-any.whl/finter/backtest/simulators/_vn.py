import numpy as np
import pandas as pd
from numba import njit

from finter.backtest.__legacy_core.core import (
    calculate_buy_sell_volumes,
    update_aum,
    update_target_volume,
    update_valuation_and_cash,
)
from finter.backtest.base.main import BaseBacktestor
from finter.backtest.core.execution import calculate_available_sell_volume
from finter.backtest.result.main import BacktestResult


class VNBacktestor(BaseBacktestor):
    settlement_days = 3
    future_fee_tax = 5 / 10000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._results = VietnamResult(self)

    def run(self):
        for i in range(1, self.frame.shape[0]):
            # Todo: delete
            short = False
            if self.vars.input.weight[i].sum() < 0:
                short = True

            self.vars.position.target_volume[i] = update_target_volume(
                self.vars.input.weight[i],
                self.vars.result.aum[i - 1, 0],
                self.vars.input.price[i - 1],
                self.vars.input.weight[i - 1],
                self.vars.position.target_volume[i - 1],
                i == 1,
                self.execution.rebalancing_method,
                self.vars.input.rebalancing_mask[i]
                if self.execution.rebalancing_method in ["W", "M", "Q"]
                else 0,
            )

            available_sell_volume = calculate_available_sell_volume(
                self.vars.position.actual_holding_volume,
                self.vars.sell.actual_sell_volume,
                self.vars.input.adjustment_ratio,
                i,
                self.settlement_days,
            )

            (
                self.vars.buy.target_buy_volume[i],
                self.vars.sell.target_sell_volume[i],
                self.vars.sell.actual_sell_volume[i],
            ) = calculate_buy_sell_volumes(
                self.vars.position.target_volume[i],
                self.vars.position.actual_holding_volume[i - 1],
                self.vars.input.weight[i],
                available_sell_volume=available_sell_volume
                if not short
                else None,  # Todo: should be deleted
                volume_capacity=self.vars.input.volume_capacity[i],
            )

            (
                self.vars.sell.actual_sell_amount[i],
                self.vars.buy.available_buy_amount[i, 0],
                self.vars.buy.actual_buy_volume[i],
                self.vars.buy.actual_buy_amount[i],
            ) = execute_transactions(
                self.vars.sell.actual_sell_volume[i],
                self.vars.input.buy_price[i],
                self.cost.buy_fee_tax,
                self.vars.input.sell_price[i],
                self.cost.sell_fee_tax,
                self.vars.result.cash[i - 1, 0],
                self.vars.buy.target_buy_volume[i],
                self.vars.position.actual_holding_volume[i - 1],
                self.future_fee_tax,
            )

            (
                self.vars.position.actual_holding_volume[i],
                self.vars.result.valuation[i],
                self.vars.result.cash[i, 0],
                self.vars.result.dividend[i],
            ) = update_valuation_and_cash(
                self.vars.position.actual_holding_volume[i - 1],
                self.vars.result.valuation[i - 1],
                self.vars.buy.actual_buy_volume[i],
                self.vars.sell.actual_sell_volume[i],
                self.vars.input.price[i],
                self.vars.buy.available_buy_amount[i, 0],
                self.vars.buy.actual_buy_amount[i],
                self.vars.input.dividend_ratio[i],
                self.execution.drip,
                self.cost.dividend_tax,
            )

            (
                self.vars.result.cash[i, 0],
                self.vars.result.aum[i, 0],
            ) = update_aum(
                self.vars.result.cash[i, 0],
                self.vars.result.valuation[i],
                self.vars.input.money_flow[i],
            )

        if not self.optional.debug:
            self._clear_all_variables(clear_attrs=True)
        else:
            self._clear_all_variables(clear_attrs=False)


@njit(cache=True)
def execute_transactions(
    actual_sell_volume: np.ndarray,
    buy_price: np.ndarray,
    buy_fee_tax: float,
    sell_price: np.ndarray,
    sell_fee_tax: float,
    prev_cash: float,
    target_buy_volume: np.ndarray,
    prev_actual_holding_volume: np.ndarray,
    future_fee_tax: float,
) -> tuple:
    sell_spot_volume = np.minimum(actual_sell_volume, prev_actual_holding_volume)
    sell_spot_volume[sell_spot_volume < 0] = 0
    sell_future_volume = actual_sell_volume - sell_spot_volume

    actual_sell_amount = np.nan_to_num(
        sell_spot_volume * sell_price * (1 - sell_fee_tax)
        + sell_future_volume * sell_price * (1 - future_fee_tax)
    )
    available_buy_amount = prev_cash + actual_sell_amount.sum()

    buy_future_volume = np.where(
        prev_actual_holding_volume < 0,
        -1 * prev_actual_holding_volume,
        np.zeros_like(prev_actual_holding_volume),
    )
    buy_spot_volume = target_buy_volume - buy_future_volume

    target_buy_amount = np.nan_to_num(
        buy_spot_volume * buy_price * (1 + buy_fee_tax)
        + buy_future_volume * buy_price * (1 + future_fee_tax)
    )

    target_buy_amount_sum = target_buy_amount.sum()
    if target_buy_amount_sum > 0:
        available_buy_volume = (
            np.floor(
                np.nan_to_num(
                    (target_buy_amount / target_buy_amount_sum)
                    * (available_buy_amount / (buy_price * (1 + buy_fee_tax) * 100))
                )
            )
            * 100
        )
        actual_buy_volume = np.minimum(available_buy_volume, target_buy_volume)

        actual_buy_amount = np.nan_to_num(
            actual_buy_volume * buy_price * (1 + buy_fee_tax)
        )
    else:
        actual_buy_volume = np.zeros_like(target_buy_volume)
        actual_buy_amount = np.zeros_like(target_buy_volume)
    return (
        actual_sell_amount,
        available_buy_amount,
        actual_buy_volume,
        actual_buy_amount,
    )


class VietnamResult(BacktestResult):
    @property
    def cost(self) -> pd.DataFrame:
        # 이전 시점의 보유 수량 계산
        prev_holding = np.roll(
            self.simulator.vars.position.actual_holding_volume, 1, axis=0
        )
        prev_holding[0] = 0  # 첫날의 이전 포지션은 0으로 설정

        # 매도 비용 계산
        sell_spot_volume = np.minimum(
            self.simulator.vars.sell.actual_sell_volume, prev_holding
        )
        sell_spot_volume[sell_spot_volume < 0] = 0
        sell_future_volume = (
            self.simulator.vars.sell.actual_sell_volume - sell_spot_volume
        )

        sell_cost = (
            sell_spot_volume
            * self.simulator.vars.input.sell_price
            * self.simulator.cost.sell_fee_tax
        ) + (
            sell_future_volume
            * self.simulator.vars.input.sell_price
            * self.simulator.future_fee_tax
        )

        # 매수 비용 계산
        buy_future_volume = np.minimum(
            np.abs(prev_holding), self.simulator.vars.buy.actual_buy_volume
        )
        buy_spot_volume = self.simulator.vars.buy.actual_buy_volume - buy_future_volume

        buy_cost = (
            buy_spot_volume
            * self.simulator.vars.input.buy_price
            * self.simulator.cost.buy_fee_tax
        ) + (
            buy_future_volume
            * self.simulator.vars.input.buy_price
            * self.simulator.future_fee_tax
        )

        total_cost = buy_cost + sell_cost
        return pd.DataFrame(
            total_cost,
            index=self.simulator.frame.common_index,
            columns=self.simulator.frame.common_columns,
        )
