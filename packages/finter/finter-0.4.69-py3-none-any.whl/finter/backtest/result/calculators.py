from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from finter.performance.stats import PortfolioAnalyzer

if TYPE_CHECKING:
    from finter.backtest.result.main import BacktestResult


class BasicCalculator:
    """기본적인 백테스트 결과 계산을 담당하는 클래스"""

    def __init__(self, result: "BacktestResult") -> None:
        self.result = result
        self.simulator = result.simulator
        self.vars = result.vars
        self.frame = result.frame

    @property
    def aum(self) -> pd.DataFrame:
        return self.result._create_df(
            self.vars.result.aum, self.frame.common_index, ["aum"]
        )

    @property
    def cash(self) -> pd.DataFrame:
        return self.result._create_df(
            self.vars.result.cash, self.frame.common_index, ["cash"]
        )

    @property
    def valuation(self) -> pd.DataFrame:
        return self.result._create_df(
            self.vars.result.valuation,
            self.frame.common_index,
            self.frame.common_columns,
        )

    @property
    def cost(self) -> pd.DataFrame:
        cost = self._calculate_cost_array()
        return self.result._create_df(
            np.nan_to_num(cost),
            index=self.frame.common_index,
            columns=self.frame.common_columns,
        )

    def _calculate_cost_array(self) -> np.ndarray:
        """거래 비용 계산 로직"""
        return (
            self.vars.buy.actual_buy_volume
            * self.vars.input.buy_price
            * self.simulator.cost.buy_fee_tax
        ) + (
            self.vars.sell.actual_sell_volume
            * self.vars.input.sell_price
            * self.simulator.cost.sell_fee_tax
        )

    @property
    def slippage(self) -> pd.DataFrame:
        slippage = self._calculate_slippage_array()
        return self.result._create_df(
            np.nan_to_num(slippage),
            index=self.frame.common_index,
            columns=self.frame.common_columns,
        )

    def _calculate_slippage_array(self) -> np.ndarray:
        """슬리피지 계산 로직"""
        return (
            self.vars.buy.actual_buy_volume
            * self.vars.input.buy_price
            * (self.simulator.cost.slippage / (1 + self.simulator.cost.slippage))
        ) + (
            self.vars.sell.actual_sell_volume
            * self.vars.input.sell_price
            * (self.simulator.cost.slippage / (1 - self.simulator.cost.slippage))
        )

    @property
    def exchange_rate(self) -> pd.DataFrame:
        return self.result._create_df(
            self.vars.input.exchange_rate,
            self.frame.common_index,
            ["exchange_rate"],
        )

    @property
    def dividend(self) -> pd.DataFrame:
        return self.result._create_df(
            self.vars.result.dividend,
            self.frame.common_index,
            self.frame.common_columns,
        )

    @property
    def money_flow(self) -> pd.DataFrame:
        return self.result._create_df(
            self.vars.input.money_flow,
            self.frame.common_index,
            ["money_flow"],
        )

    @property
    def target_weight(self) -> pd.DataFrame:
        return self.result._create_df(
            self.vars.input.weight,
            index=self.frame.common_index,
            columns=self.frame.common_columns,
        )

    @property
    def position(self) -> pd.DataFrame:
        return self.result._create_df(
            self.vars.input.weight * 1e8,
            index=self.frame.common_index,
            columns=self.frame.common_columns,
        )


class PnLCalculator:
    """손익 계산 관련 로직을 담당하는 클래스"""

    def __init__(self, result: "BacktestResult") -> None:
        self.result = result
        self.simulator = result.simulator
        self.vars = result.vars
        self.frame = result.frame

    def calculate_average_buy_price(self) -> pd.DataFrame:
        """평균 매수 가격 계산"""
        average_buy_price, _ = self._compute_average_buy_price()

        return self.result._create_df(
            average_buy_price,
            index=self.simulator.frame.common_index,
            columns=self.simulator.frame.common_columns,
        )

    def _compute_average_buy_price(self) -> tuple[np.ndarray, np.ndarray]:
        """평균 매수 가격 및 누적 매수 금액 계산"""
        cummulative_buy_amount = np.full(
            self.simulator.frame.shape, np.nan, dtype=np.float64
        )
        average_buy_price = np.full(
            self.simulator.frame.shape, np.nan, dtype=np.float64
        )

        cummulative_buy_amount[0] = 0
        average_buy_price[0] = 0

        for i in range(1, self.simulator.frame.shape[0]):
            cummulative_buy_amount[i] = (
                cummulative_buy_amount[i - 1]
                + (
                    self.simulator.vars.buy.actual_buy_volume[i]
                    * np.nan_to_num(self.simulator.vars.input.buy_price[i])
                )
                - (
                    self.simulator.vars.sell.actual_sell_volume[i]
                    * average_buy_price[i - 1]
                )
            )

            average_buy_price[i] = np.nan_to_num(
                cummulative_buy_amount[i]
                / self.simulator.vars.position.actual_holding_volume[i]
            )

        return average_buy_price, cummulative_buy_amount

    def calculate_realized_pnl(self) -> pd.DataFrame:
        """실현 손익 계산"""
        average_buy_price = self.calculate_average_buy_price()

        return self.result._create_df(
            (
                np.nan_to_num(self.simulator.vars.input.sell_price)
                - average_buy_price.shift()
            )
            * self.simulator.vars.sell.actual_sell_volume,
            index=self.frame.common_index,
            columns=self.frame.common_columns,
        ).fillna(0)

    def calculate_unrealized_pnl(self) -> pd.DataFrame:
        """미실현 손익 계산"""
        average_buy_price = self.calculate_average_buy_price()

        return self.result._create_df(
            (np.nan_to_num(self.simulator.vars.input.price) - average_buy_price)
            * self.simulator.vars.position.actual_holding_volume,
            index=self.frame.common_index,
            columns=self.frame.common_columns,
        ).fillna(0)


class ContributionCalculator:
    """기여도 계산 관련 로직을 담당하는 클래스"""

    def __init__(self, result: "BacktestResult") -> None:
        self.result = result

    def calculate_contribution(self) -> pd.DataFrame:
        """포트폴리오 기여도 계산"""
        pnl = (
            self.result.realized_pnl
            + self.result.unrealized_pnl.diff()
            - self.result.cost
        )
        return pnl.div(self.result.aum.shift()["aum"], axis=0) * 100

    def calculate_contribution_summary(self) -> pd.DataFrame:
        """기여도 요약 보고서 생성"""
        realized_pnl = self.result.realized_pnl
        unrealized_pnl = self.result.unrealized_pnl.diff()
        cost = self.result.cost
        aum = self.result.aum

        pnl = realized_pnl + unrealized_pnl - cost
        contribution = pnl.div(aum.shift()["aum"], axis=0)
        prev_weight = self.result.valuation.shift().div(aum.shift()["aum"], axis=0)
        weight = self.result.valuation.div(aum["aum"], axis=0)

        # 멀티칼럼 DataFrame 생성
        result = pd.concat(
            {
                "pnl": pnl,
                "contribution": contribution * 100,
                "prev_weight": prev_weight * 100,
                "weight": weight * 100,
                "target": self.result.target_weight * 100,
            },
            axis=1,
        )
        result = result.swaplevel(0, 1, axis=1)
        result = result.sort_index(axis=1)
        result = result.reindex(
            columns=[
                "pnl",
                "contribution",
                "prev_weight",
                "weight",
                "target",
            ],
            level=1,
        )
        return result


class SummaryCalculator:
    """요약 정보 계산을 담당하는 클래스"""

    def __init__(self, result: "BacktestResult") -> None:
        self.result = result
        self.simulator = result.simulator

    def calculate_target_turnover(self) -> pd.DataFrame:
        """목표 비중 변화에 기반한 turnover 계산"""
        target_weight = self.result.target_weight
        target_weight_change = target_weight.diff().abs()
        target_turnover = target_weight_change.sum(axis=1) / 2  # 양방향 turnover의 반

        return pd.DataFrame(
            target_turnover,
            index=self.result.frame.common_index,
            columns=["target_turnover"],
        )

    def calculate_actual_turnover(self) -> pd.DataFrame:
        """실제 거래 금액에 기반한 turnover 계산"""
        # 실제 매수/매도 금액 계산
        actual_buy_amount = self.simulator.vars.buy.actual_buy_amount.sum(axis=1)
        actual_sell_amount = self.simulator.vars.sell.actual_sell_amount.sum(axis=1)

        # 총 거래 금액 (매수 + 매도)
        total_trade_amount = np.nan_to_num(actual_buy_amount) + np.nan_to_num(
            actual_sell_amount
        )

        # AUM 대비 turnover 계산 (0 division 방지)
        aum = self.result.aum["aum"].values
        actual_turnover = np.where(
            np.array(aum) > 0,
            total_trade_amount / np.array(aum) / 2,  # 양방향 turnover의 반
            0,
        )

        return pd.DataFrame(
            actual_turnover,
            index=self.result.frame.common_index,
            columns=["actual_turnover"],
        )

    def calculate_summary(self) -> pd.DataFrame:
        """백테스트 결과 요약 정보 계산"""
        if self.simulator.execution.drip == "reinvest":
            cash = self.result.cash
            aum = self.result.aum
        elif self.simulator.execution.drip in ["cash", "coupon"]:
            cash = self.result.cash.add(
                self.result.dividend.sum(axis=1).cumsum(), axis=0
            )
            aum = self.result.aum.add(self.result.dividend.sum(axis=1).cumsum(), axis=0)
        else:
            cash = self.result.cash
            aum = self.result.aum

        # 기본 정보 계산
        result = pd.concat(
            [
                aum,
                cash,
                self.result.valuation.sum(axis=1).rename("valuation"),
                self.result.money_flow,
                self.result.cost.sum(axis=1).rename("cost"),
                self.result.slippage.sum(axis=1).rename("slippage"),
                self.result.exchange_rate,
                self.result.dividend.sum(axis=1).rename("dividend"),
            ],
            axis=1,
        )
        result["daily_return"] = (
            (result["aum"] - result["money_flow"]) / result["aum"].shift()
        ).fillna(1)
        result["nav"] = result["daily_return"].cumprod() * 1000

        aum_in_currency = result["aum"] * result["exchange_rate"]
        daily_return_in_currency = (
            (aum_in_currency - result["money_flow"] * result["exchange_rate"])
            / aum_in_currency.shift()
        ).fillna(1)
        result["nav_in_currency"] = daily_return_in_currency.cumprod() * 1000

        # Turnover 계산 및 추가
        target_turnover = self.calculate_target_turnover()
        actual_turnover = self.calculate_actual_turnover()

        result = pd.concat([result, target_turnover, actual_turnover], axis=1)

        result = result.reindex(
            columns=[
                "nav",
                "aum",
                "cash",
                "valuation",
                "money_flow",
                "dividend",
                "cost",
                "slippage",
                "daily_return",
                "target_turnover",
                "actual_turnover",
                "exchange_rate",
                "nav_in_currency",
            ]
        )

        return result


class StatisticsCalculator:
    """통계 계산 관련 로직을 담당하는 클래스"""

    def __init__(self, result: "BacktestResult") -> None:
        self.result = result

    def calculate_statistics(self) -> pd.Series:
        """NAV를 기반으로 통계 지표 계산"""
        summary = self.result.summary

        if "nav" not in summary.columns:
            raise ValueError(
                "Summary must contain 'nav' column for statistics calculation"
            )

        nav = summary["nav"]

        stats = PortfolioAnalyzer._nav_to_stats(nav)

        return stats

    def calculate_performance(self) -> pd.DataFrame:
        """NAV를 기반으로 성과 지표 계산"""
        summary = self.result.summary

        if "nav" not in summary.columns:
            raise ValueError(
                "Summary must contain 'nav' column for statistics calculation"
            )

        position = self.result.position
        nav = summary["nav"]
        return PortfolioAnalyzer.stats(nav, position)
