from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from finter.backtest.result.calculators import (
    BasicCalculator,
    ContributionCalculator,
    PnLCalculator,
    StatisticsCalculator,
    SummaryCalculator,
)
from finter.backtest.result.report import BacktestReporter

if TYPE_CHECKING:
    from finter.backtest.base.main import BaseBacktestor


class BacktestResult:
    def __init__(self, simulator: "BaseBacktestor") -> None:
        self.simulator = simulator
        self.vars = simulator.vars
        self.frame = simulator.frame

        # 컴포지션 패턴으로 계산기 객체들 초기화
        self._basic_calculator = BasicCalculator(self)
        self._pnl_calculator = PnLCalculator(self)
        self._contribution_calculator = ContributionCalculator(self)
        self._summary_calculator = SummaryCalculator(self)
        self._statistics_calculator = StatisticsCalculator(self)
        self._report_calculator = BacktestReporter

    def _create_df(
        self, data: np.ndarray, index: list[str], columns: list[str]
    ) -> pd.DataFrame:
        if data.size == 0:
            return pd.DataFrame(index=index, columns=columns)
        return pd.DataFrame(data, index=index, columns=columns)

    # 기본 속성들은 BasicCalculator에서 위임
    @property
    def aum(self) -> pd.DataFrame:
        return self._basic_calculator.aum

    @property
    def cash(self) -> pd.DataFrame:
        return self._basic_calculator.cash

    @property
    def valuation(self) -> pd.DataFrame:
        return self._basic_calculator.valuation

    @property
    def cost(self) -> pd.DataFrame:
        return self._basic_calculator.cost

    @property
    def slippage(self) -> pd.DataFrame:
        return self._basic_calculator.slippage

    @property
    def exchange_rate(self) -> pd.DataFrame:
        return self._basic_calculator.exchange_rate

    @property
    def dividend(self) -> pd.DataFrame:
        return self._basic_calculator.dividend

    @property
    def money_flow(self) -> pd.DataFrame:
        return self._basic_calculator.money_flow

    # 요약 정보는 SummaryCalculator에서 위임
    @property
    def summary(self) -> pd.DataFrame:
        return self._summary_calculator.calculate_summary()

    # PnL 관련 계산은 PnLCalculator에서 위임
    @property
    def average_buy_price(self) -> pd.DataFrame:
        return self._pnl_calculator.calculate_average_buy_price()

    @property
    def realized_pnl(self) -> pd.DataFrame:
        return self._pnl_calculator.calculate_realized_pnl()

    @property
    def unrealized_pnl(self) -> pd.DataFrame:
        return self._pnl_calculator.calculate_unrealized_pnl()

    @property
    def target_weight(self) -> pd.DataFrame:
        return self._basic_calculator.target_weight

    @property
    def position(self) -> pd.DataFrame:
        return self._basic_calculator.position

    # 기여도 관련 계산은 ContributionCalculator에서 위임
    @property
    def contribution(self) -> pd.DataFrame:
        return self._contribution_calculator.calculate_contribution()

    @property
    def contribution_summary(self) -> pd.DataFrame:
        return self._contribution_calculator.calculate_contribution_summary()

    # 통계 정보는 StatisticsCalculator에서 위임
    @property
    def statistics(self) -> pd.Series:
        return self._statistics_calculator.calculate_statistics()

    @property
    def performance(self) -> pd.DataFrame:
        return self._statistics_calculator.calculate_performance()

    # Turnover 관련 계산은 SummaryCalculator에서 위임
    @property
    def target_turnover(self) -> pd.DataFrame:
        return self._summary_calculator.calculate_target_turnover()

    @property
    def actual_turnover(self) -> pd.DataFrame:
        return self._summary_calculator.calculate_actual_turnover()

    @property
    def report(self) -> BacktestReporter:
        return self._report_calculator(self.summary, self.statistics)
