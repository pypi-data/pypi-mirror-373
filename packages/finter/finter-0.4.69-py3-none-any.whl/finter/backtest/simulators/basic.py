from finter.backtest.base.main import BaseBacktestor
from finter.backtest.core import (
    calculate_capital_gain_tax,
    calculate_target_buy_sell_volume,
    execute_buy_transactions,
    execute_sell_transactions,
    prepare_data,
    update_aum,
    update_target_volume,
    update_valuation_and_cash,
)


class BasicBacktestor(BaseBacktestor):
    def run(self):
        for i in range(1, self.frame.shape[0]):
            self.run_step(i)

        if not self.optional.debug:
            self._clear_all_variables(clear_attrs=True)
        else:
            self._clear_all_variables(clear_attrs=False)

    def run_step(self, i: int):
        (
            prev_adj_price,
            volume_adjustment_ratio,
            rebalancing_mask_current,
            target_volume_limit_current,
            redistribute_max_iter,
            lot_size,
            capital_gain_tax_mask_current,
            capital_gain_tax_mask_prev,
        ) = prepare_data(
            i,
            self.vars.input.price,
            self.vars.input.adjustment_ratio,
            self.execution.rebalancing_method,
            self.vars.input.rebalancing_mask,
            self.cost.capital_gain_tax,
            self.vars.input.capital_gain_tax_mask,
            self.vars.input.target_volume_limit,
            self.trade.target_volume_limit_args,
            self.trade.lot_args,
        )

        self.vars.position.target_volume[i] = update_target_volume(
            self.vars.input.weight[i],
            self.vars.result.aum[i - 1, 0],
            self.vars.input.weight[i - 1],
            self.vars.position.target_volume[i - 1],
            i == 1,
            self.execution.rebalancing_method,
            rebalancing_mask_current,
            target_volume_limit=target_volume_limit_current,
            redistribute_max_iter=redistribute_max_iter,
            adjustment_ratio=self.vars.input.adjustment_ratio[i],
            prev_adj_price=prev_adj_price,
        )

        (
            self.vars.buy.target_buy_volume[i],
            self.vars.sell.target_sell_volume[i],
            self.vars.sell.target_short_sell_volume[i],
            self.vars.buy.target_short_cover_volume[i],
        ) = calculate_target_buy_sell_volume(
            self.vars.position.target_volume[i],
            self.vars.position.actual_holding_volume[i - 1],
            self.vars.input.weight[i],
            volume_capacity=self.vars.input.volume_capacity[i],
            volume_adjustment_ratio=volume_adjustment_ratio,
        )

        (
            self.vars.sell.actual_sell_volume[i],
            self.vars.sell.actual_sell_amount[i],
            self.vars.sell.actual_short_sell_volume[i],
            self.vars.sell.actual_short_sell_amount[i],
        ) = execute_sell_transactions(
            self.vars.sell.target_sell_volume[i],
            self.vars.sell.target_short_sell_volume[i],
            self.vars.input.sell_price[i],
            self.cost.sell_fee_tax,
            actual_holding_volume=self.vars.position.actual_holding_volume[i - 1],
            actual_buy_volume=self.vars.buy.actual_buy_volume,
            adjustment_ratio=self.vars.input.adjustment_ratio,
            i=i,
            settlement_days=0,
            lot_size=lot_size,
            volume_adjustment_ratio=volume_adjustment_ratio,
        )

        (
            self.vars.buy.available_buy_amount[i],
            self.vars.buy.actual_buy_volume[i],
            self.vars.buy.actual_buy_amount[i],
            self.vars.buy.actual_short_cover_volume[i],
            self.vars.buy.actual_short_cover_amount[i],
        ) = execute_buy_transactions(
            self.vars.input.buy_price[i],
            self.cost.buy_fee_tax,
            self.vars.result.cash[i - 1, 0],
            self.vars.buy.target_buy_volume[i],
            self.vars.buy.target_short_cover_volume[i],
            self.vars.position.actual_holding_volume[i - 1],
            self.vars.sell.actual_sell_amount,
            self.vars.sell.actual_short_sell_amount,
            settlement_days=0,
            current_index=i,
            lot_size=lot_size,
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
            self.vars.sell.actual_short_sell_volume[i],
            self.vars.buy.actual_short_cover_volume[i],
            self.vars.input.price[i],
            self.vars.buy.available_buy_amount[i, 0],
            self.vars.buy.actual_buy_amount[i],
            self.vars.buy.actual_short_cover_amount[i],
            self.vars.input.dividend_ratio[i],
            self.execution.drip,
            self.cost.dividend_tax,
            volume_adjustment_ratio,
        )

        (
            self.vars.buy.cummulative_buy_amount[i],
            self.vars.buy.average_buy_price[i],
            self.vars.result.cummulative_realized_pnl[i],
            self.vars.result.capital_gain_tax[i],
        ) = calculate_capital_gain_tax(
            self.vars.input.sell_price[i],
            self.vars.buy.cummulative_buy_amount[i - 1],
            self.vars.buy.average_buy_price[i - 1],
            self.vars.result.cummulative_realized_pnl[i - 1],
            self.vars.buy.actual_buy_volume[i],
            self.vars.input.buy_price[i],
            self.vars.sell.actual_sell_volume[i],
            self.vars.position.actual_holding_volume[i],
            capital_gain_tax_mask_prev,
            capital_gain_tax_mask_current,
            self.cost.capital_gain_tax,
        )

        (
            self.vars.result.cash[i, 0],
            self.vars.result.aum[i, 0],
        ) = update_aum(
            self.vars.result.cash[i, 0],
            self.vars.result.valuation[i],
            self.vars.input.money_flow[i],
            self.vars.result.capital_gain_tax[i],
            self.trade.deposit_interest_rate,
        )
