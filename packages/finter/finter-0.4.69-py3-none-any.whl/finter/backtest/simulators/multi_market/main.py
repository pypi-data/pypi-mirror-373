from datetime import datetime
from functools import reduce
from typing import Dict, Unpack

import numpy as np
import pandas as pd

from finter.backtest.base.main import BaseBacktestor
from finter.backtest.config.simulator import SimulatorInputConfig
from finter.backtest.config.templates import AVAILABLE_MARKETS
from finter.backtest.simulator import Simulator


class MultiMarketSimulator:
    """
    multi market simulator
    """

    # No more caching needed - individual Simulators are cached

    # 같은 시장을 공유하는 시장 조합들
    SINGLE_MARKET_COMBINATIONS = {
        frozenset(['us_etf', 'us_stock']),  # 미국 통합 시장
    }

    def __init__(
        self,
        start: int = 20000101,
        end: int = int(datetime.now().strftime("%Y%m%d")),
        *,
        market_types: list[AVAILABLE_MARKETS],
    ):
        self.start = start
        self.end = end
        self.market_types = sorted(market_types)  # Sort for consistent behavior

        # 특정 조합인지 확인
        market_set = frozenset(self.market_types)
        if market_set in self.SINGLE_MARKET_COMBINATIONS:
            self.single_market_mode = True
        else:
            self.single_market_mode = False

        self.union_index: list = []

        self.simulators: Dict[str, Simulator] = {}
        self.positions: Dict[str, pd.DataFrame] = {}
        self.configs: Dict[str, SimulatorInputConfig] = {}
        self.backtestors: Dict[str, BaseBacktestor] = {}

        self.results: dict[str, np.ndarray] = {}

        for market_type in market_types:
            # Use cached Simulator instances
            simulator = Simulator.get_cached_instance(
                market_type=market_type,
                start=self.start,
                end=self.end,
            )
            self.simulators[market_type] = simulator
            self.configs[market_type] = {}

            simulator.builder.data.price.columns

    def seperate_positions(self, position: pd.DataFrame):
        original_position_columns = set(position.columns)
        remaining_columns = set(str(col) for col in position.columns)  # 모든 columns를 문자열로 변환

        for market_type in self.market_types:
            price_cols = self.simulators[market_type].builder.data.price.columns
            position_copy = position.copy()
            
            if market_type == 'kr_stock':
                # kr_stock인 경우에만 숫자로 된 columns를 int로 변환
                numeric_cols = [col for col in position_copy.columns if str(col).isdigit()]
                if numeric_cols:
                    position_copy_int = position_copy[numeric_cols].copy()
                    position_copy_int.columns = position_copy_int.columns.astype(int)
                    price_cols = price_cols.astype(int)
                    self.positions[market_type] = position_copy_int.reindex(columns=price_cols)
                    remaining_columns -= set(str(col) for col in numeric_cols)
            else:
                # 다른 시장은 문자열 그대로 처리
                price_cols = price_cols.astype(str)
                self.positions[market_type] = position_copy.reindex(columns=price_cols)
                remaining_columns -= set(str(col) for col in self.positions[market_type].columns)

        assert len(remaining_columns) == 0, f"Unmatched columns: {remaining_columns}"
        return self

    def update_market_config(
        self,
        market_type: AVAILABLE_MARKETS,
        **kwargs: Unpack[SimulatorInputConfig],
    ):
        assert set(kwargs.keys()) <= set(SimulatorInputConfig.__annotations__.keys()), (
            f"Invalid keys: {set(kwargs.keys()) - set(SimulatorInputConfig.__annotations__.keys())}\n"
            f"Available keys: {SimulatorInputConfig.__annotations__.keys()}"
        )

        self.configs[market_type] = kwargs

        return self

    def build(self):
        price_indices = [
            simulator.builder.data.price.index for simulator in self.simulators.values()
        ]
        max_price_start = max(idx[0] for idx in price_indices)
        min_price_end = min(idx[-1] for idx in price_indices)

        position_indices = [position.index for position in self.positions.values()]
        min_position_start = max(idx[0] for idx in position_indices)
        min_position_end = min(idx[-1] for idx in position_indices)

        max_start = max(max_price_start, min_position_start)
        min_end = min(min_price_end, min_position_end)

        all_indices = pd.DatetimeIndex(
            sorted(reduce(lambda x, y: x.union(y), price_indices))
        )
        all_indices = all_indices[all_indices.slice_indexer(max_start, min_end)]

        for market_type, simulator in self.simulators.items():
            simulator.builder.update(
                price=simulator.builder.data.price.fillna(0)
                .reindex(all_indices)
                .ffill()
                .replace(0, np.nan)
                .fillna(0),
            )
            self.backtestors[market_type] = simulator.build(
                position=self.positions[market_type]
                .fillna(np.inf)
                .reindex(all_indices)
                .ffill()
                .replace(np.inf, np.nan)
                .fillna(0),
                **self.configs[market_type],
            )
        common_indexes = {
            market_type: backtestor.frame.common_index
            for market_type, backtestor in self.backtestors.items()
        }
        self.union_index = sorted(common_indexes.values())[0]

        assert len(set([len(c) for c in list(common_indexes.values())])), (
            "All backtestors must have the same number of rows"
        )
        assert not self.union_index == 0, "Union index is 0"
        self.results["cash"] = np.full(
            (len(self.union_index), 1), np.nan, dtype=np.float64
        )

        # Create market_type to index mapping
        self.market_order = {
            market_type: idx for idx, market_type in enumerate(self.backtestors.keys())
        }

    def run(self, position: pd.DataFrame, **kwargs):
        if hasattr(self, 'single_market_mode') and self.single_market_mode:
            # 단일 시장 모드로 실행
            return self.run_single_market_mode(position, **kwargs)
        else:
            # 기존 다중 시장 모드로 실행
            return self._run_multi_market(position)

    def run_single_market_mode(self, position: pd.DataFrame, **kwargs):
        """단일 시장 모드로 실행"""
        # 1. 통합된 시뮬레이터 생성
        unified_simulator = self._create_unified_simulator()
        
        # 2. 포지션 그대로 사용 (분리하지 않음)
        # 3. 단일 시뮬레이션 실행
        result = unified_simulator.run(position, **kwargs)
        
        # 4. 결과를 MultiMarketSimulator 형식으로 래핑
        self._single_market_result = result
        return self

    @property
    def summary(self):
        """통합된 summary 반환"""
        if hasattr(self, '_single_market_result'):
            return self._single_market_result.summary
        elif hasattr(self, '_summary'):
            return self._summary
        else:
            return None
    
    @summary.setter
    def summary(self, value):
        """summary setter - 다중 시장 모드용"""
        self._summary = value
    
    def _get_summary(self):
        """다중 시장 모드에서 summary를 가져오는 메서드"""
        if hasattr(self, '_summary'):
            return self._summary
        else:
            return None

    def _run_multi_market(self, position: pd.DataFrame):
        self.seperate_positions(position)
        self.build()

        # 환율맞추기, 오더링

        total_cash = sum(
            backtestor.vars.result.cash[0, 0]
            for backtestor in self.backtestors.values()
        )

        self.results["cash"][0, 0] = total_cash

        for i in range(1, len(self.union_index)):
            total_weight = sum(
                backtestor.vars.input.weight[i].sum()
                for backtestor in self.backtestors.values()
            )
            total_aum = (
                sum(
                    backtestor.vars.result.aum[i - 1]
                    for backtestor in self.backtestors.values()
                )
                + total_cash
            )

            for market_type, backtestor in self.backtestors.items():
                target_aum = total_aum * (
                    backtestor.vars.input.weight[i].sum() / total_weight
                )

                backtestor.vars.result.cash[i - 1] = total_cash
                backtestor.vars.result.aum[i - 1] = target_aum

                backtestor.run_step(i)

                total_cash = backtestor.vars.result.cash[i, 0]

                backtestor.vars.result.cash[i] = 0
                backtestor.vars.result.aum[i] -= total_cash

            self.results["cash"][i, 0] = total_cash

        for backtestor in self.backtestors.values():
            if not backtestor.optional.debug:
                backtestor._clear_all_variables(clear_attrs=True)
            else:
                backtestor._clear_all_variables(clear_attrs=False)

        sorted_backtestors = sorted(
            self.backtestors.items(), key=lambda x: self.market_order[x[0]]
        )

        # 데이터 추출 및 병합
        markets, backtestors = zip(*sorted_backtestors)
        backtestors = list(backtestors)

        # DataFrame 생성
        result = pd.concat(
            [
                *[bt.summary.valuation for bt in backtestors],
                *[bt.summary.cost for bt in backtestors],
                *[bt.summary.slippage for bt in backtestors],
                pd.DataFrame(self.results["cash"], index=self.union_index),
            ],
            axis=1,
        )

        # 컬럼 설정 및 계산
        val_cols = [f"{m}_valuation" for m in markets]
        cost_cols = [f"{m}_cost" for m in markets]
        slippage_cols = [f"{m}_slippage" for m in markets]

        result.columns = val_cols + cost_cols + slippage_cols + ["cash"]
        result["valuation"] = result[val_cols].sum(axis=1)
        result["cost"] = result[cost_cols].sum(axis=1)
        result["slippage"] = result[slippage_cols].sum(axis=1)

        result["aum"] = result["valuation"] + result["cash"]
        result["nav"] = (result["aum"] / result["aum"].iloc[0]) * 1000

        # 최종 정렬
        return result[
            ["nav", "aum", "cash", "valuation", "cost", "slippage"]
            + val_cols
            + cost_cols
            + slippage_cols
        ]

    def _create_unified_simulator(self):
        """통합된 시뮬레이터 생성"""
        # 1. 모든 시장의 인덱스 교집합 찾기
        all_price_indices = [sim.builder.data.price.index for sim in self.simulators.values()]
        
        # 가격 인덱스만 사용하여 통일
        common_price_index = all_price_indices[0].intersection(all_price_indices[1])
        unified_index = common_price_index
        
        # 2. 가격 데이터 통합 및 정렬
        unified_price = pd.concat([
            sim.builder.data.price.reindex(unified_index) for sim in self.simulators.values()
        ], axis=1).ffill()

        # 3. 배당 데이터 통합 및 정렬
        unified_dividend = pd.concat([
            sim.data_handler.universe(market_type).dividend_factor().reindex(unified_index)
            for sim, market_type in zip(self.simulators.values(), self.market_types)
        ], axis=1).ffill()

        # 4. adjustment_ratio를 price와 정확히 같은 크기로 생성
        unified_adjustment_ratio = pd.DataFrame(
            1.0, 
            index=unified_price.index, 
            columns=unified_price.columns
        )
        
        # 5. 누락값 처리
        unified_price = unified_price.fillna(method='ffill').fillna(0)
        unified_dividend = unified_dividend.fillna(0)
        
        # 6. 완전히 새로운 시뮬레이터 생성 (캐시 사용하지 않음)
        base_market_type = self.market_types[0]
        unified_simulator = Simulator(
            market_type=base_market_type,
            start=self.start,
            end=self.end
        )
        
        # 7. 기존 데이터 완전히 초기화
        from finter.backtest.builder.main import SimulatorBuilder
        unified_simulator.builder = SimulatorBuilder()
        
        # 8. 모든 데이터가 동일한 크기인지 확인
        assert unified_price.shape[0] == unified_dividend.shape[0] == unified_adjustment_ratio.shape[0], \
            f"Data shapes don't match: price={unified_price.shape}, dividend={unified_dividend.shape}, adj={unified_adjustment_ratio.shape}"
        
        # 9. 통합된 데이터로 업데이트
        unified_simulator.builder.update_data(
            price=unified_price,
            dividend_ratio=unified_dividend,
            adjustment_ratio=unified_adjustment_ratio
        )
        
        # 10. data_handler도 초기화
        unified_simulator.data_handler = list(self.simulators.values())[0].data_handler
        
        # 11. market_type을 통합된 것으로 설정
        unified_simulator.market_type = base_market_type
        
        # 12. 기존 설정 속성들 초기화
        unified_simulator.use_currency = None
        unified_simulator.use_volume_capacity_ratio = None
        unified_simulator.use_target_volume_limit = None
        unified_simulator.use_sub_universe = None
        unified_simulator.use_drip = None

        return unified_simulator
