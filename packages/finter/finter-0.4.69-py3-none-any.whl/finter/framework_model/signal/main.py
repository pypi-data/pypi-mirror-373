import bisect
from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional, cast

import numpy as np
import pandas as pd
from tqdm import tqdm

from finter.backtest import Simulator
from finter.backtest.config.config import AVAILABLE_MARKETS
from finter.data.manager.adaptor import DataAdapter
from finter.data.manager.type import DataType
from finter.framework_model.alpha import BaseAlpha
from finter.framework_model.signal.explore import (
    generate_param_combinations,
    greedy_select,
    run_param_exploration,
)
from finter.framework_model.signal.plot import quick_plot_stats, quick_plot_two_way
from finter.framework_model.signal.process import normalize_signal
from finter.framework_model.signal.schemas import SignalConfig, SignalParams
from finter.framework_model.signal.timeout import timeout


class BaseSignal(BaseAlpha):
    POSITION_SCALE_FACTOR = 1e8
    SIGNAL_SUM_TOLERANCE = 1.01
    TIMEOUT_SECONDS = 1000

    # 글로벌 캐시 클래스 변수
    _global_cache: Optional[Dict[str, Any]] = None

    def __init__(self, use_cache: bool = False):
        super().__init__()

        self._initialized = False
        self._disable_tqdm = False  # tqdm 비활성화 플래그
        self.last_date: int = int(datetime.now().strftime("%Y%m%d"))

        self.params: SignalParams
        self.configs: SignalConfig
        self.adapter: DataAdapter
        self.simulator: Simulator
        self.signal: pd.DataFrame
        self.position: pd.DataFrame

        self.setup(use_cache=use_cache)

    def setup(self, use_cache: bool = False):
        self.set_params()  # params 먼저 설정
        self.set_config()  # params 사용해서 config 설정

        if use_cache and self._global_cache:
            # 캐시된 데이터 사용
            self.adapter = self._global_cache["adapter"]
            self.simulator = self._global_cache["simulator"]
            self._cache_adapter_data()
        else:
            # 새로 생성 및 캐시에 저장
            self.adapter = DataAdapter(
                self.configs.universe,
                self.configs.first_date,
                self.last_date,
            )
            self.adapter.add(self.configs.data_list)
            self.adapter.info()
            self._cache_adapter_data()

            self.simulator = Simulator(
                cast(AVAILABLE_MARKETS, self.configs.universe),
                start=self.configs.first_date,
                end=self.last_date,
            )

            # 글로벌 캐시에 저장
            self._store_to_cache()

        self._initialized = True

    @abstractmethod
    def set_params(self):
        """
        파라미터 설정 - self.params = SignalParams(...)
        """
        pass

    @abstractmethod
    def set_config(self):
        """
        설정 - self.configs = SignalConfig(...)
        params 값을 사용하여 설정
        """
        pass

    @abstractmethod
    def step(self, t: datetime) -> np.ndarray:  # (N)
        pass

    @abstractmethod
    def post_process(self, position: pd.DataFrame) -> pd.DataFrame:
        pass

    @timeout(TIMEOUT_SECONDS)
    def run_step(self, t: datetime, idx: int, first_date_idx: int) -> np.ndarray:
        """
        Rebalancing logic을 적용한 step 실행
        first_date를 anchor로 하여 rebalance 주기에 맞춰 신호를 계산하거나 이전 신호를 재사용
        """

        # first_date 이전이면 NaN 배열 반환
        if idx < first_date_idx:
            return self._get_nan_signal()

        return self.step(t)

    def update_params(self, **kwargs) -> "BaseSignal":
        """
        파라미터 업데이트 후 config 재설정
        파라메트릭 서치에서 사용
        """
        self.params.update(**kwargs)
        self.set_config()

        return self

    def reset_params(self):
        self.params.update(**self.params.default)
        self.set_config()

        return self

    def _store_to_cache(self):
        """어댑터와 시뮬레이터를 글로벌 캐시에 저장"""
        if hasattr(self, "adapter") and hasattr(self, "simulator"):
            self.__class__._global_cache = {
                "adapter": self.adapter,
                "simulator": self.simulator,
            }

    @classmethod
    def clear_cache(cls):
        """글로벌 캐시 클리어"""
        cls._global_cache = None

    def get(self, start: int, end: int) -> pd.DataFrame:
        start_date = self._parse_date(start)
        end_date = self._parse_date(end)

        # start, end 날짜의 인덱스 찾기
        start_pos = bisect.bisect_left(self.stock_data.T, start_date)
        end_pos = bisect.bisect_right(self.stock_data.T, end_date)

        # shift를 위해 하루 전부터 + signal_lookback만큼 더 앞서서 계산
        signal_start_pos = (
            start_pos - 1 - self.configs.signal_lookback if start_pos > 0 else start_pos
        )

        # 날짜 범위 검증 및 조정
        start, start_pos, signal_start_pos = self._validate_and_adjust_dates(
            start, start_pos, signal_start_pos
        )

        # 신호 계산을 위한 최적화된 배치 처리
        signal_list, date_index = self._calculate_signals_batch(
            signal_start_pos, end_pos, start, end
        )

        # DataFrame 생성 및 검증
        self.signal = self._create_signal_dataframe(signal_list, date_index)
        self.position = self._create_position_dataframe(self.signal, start, end)

        self.position = self.post_process(self.position)

        self.position = (
            self.position.shift()
            .replace(0, np.nan)
            .dropna(how="all", axis=1)[str(start) : str(end)]
        )

        return self.position

    def backtest(self, start: int, end: int, fee: bool = True, worker=False) -> Any:
        # worker 모드에서는 tqdm 비활성화
        if worker:
            self._disable_tqdm = True
        position = self.get(start, end)
        if worker:
            self._disable_tqdm = False

        if not fee:
            simulator = self.simulator.run(
                position, slippage=0, buy_fee_tax=0, sell_fee_tax=0
            )
        else:
            simulator = self.simulator.run(position)

        if not worker:
            print(simulator.performance)  # type: ignore
        return simulator

    def _get_nan_signal(self) -> np.ndarray:
        """NaN으로 채워진 신호 배열 반환"""
        return np.full(len(self.stock_data.N), np.nan)

    def _create_signal_dataframe(
        self, signal_list: list, date_index: list
    ) -> pd.DataFrame:
        """신호 DataFrame 생성"""
        df = pd.DataFrame(
            signal_list,
            index=date_index,
            columns=list(self.stock_data.N),
        )
        self._validate_signal(df)
        return df

    @staticmethod
    def _validate_signal(df: pd.DataFrame):
        """신호 유효성 검증"""
        if (df.abs().sum(axis=1) == 0).all():
            raise ValueError("all signal is 0")
        if df.abs().sum(axis=1).any() > 1.0:
            print("some signal is over exposure")
        if df.abs().sum(axis=1).any() < 1.0:
            print("some signal is under exposure")

    @staticmethod
    def _create_position_dataframe(
        signal: pd.DataFrame, start: int, end: int
    ) -> pd.DataFrame:
        """포지션 DataFrame 생성"""
        signal = normalize_signal(signal)
        return signal * BaseSignal.POSITION_SCALE_FACTOR

    def _validate_and_adjust_dates(
        self, start: int, start_pos: int, signal_start_pos: int
    ) -> tuple[int, int, int]:
        """날짜 범위 검증 및 조정"""
        if signal_start_pos < self.configs.data_lookback:
            required_lookback = (
                self.configs.data_lookback + 1 + self.configs.signal_lookback
            )
            first_available_date = self.stock_data.T[required_lookback]

            print("-" * 50)
            print(
                f"Warning: Start date {start} requires {self.configs.data_lookback} days of lookback data "
                f"plus 1 day for shift and {self.configs.signal_lookback} days for signal lookback."
            )
            print(
                f"Adjusting start date from {start} to {first_available_date.strftime('%Y%m%d')}"
            )
            print("-" * 50)

            return (
                int(first_available_date.strftime("%Y%m%d")),
                required_lookback,
                self.configs.data_lookback,
            )

        return start, start_pos, signal_start_pos

    def _calculate_signals_batch(
        self, signal_start_pos: int, end_pos: int, start: int, end: int
    ) -> tuple[list[np.ndarray], list[pd.Timestamp]]:
        """신호 계산을 위한 배치 처리 - 메모리 최적화"""
        total_size = min(end_pos, len(self.stock_data.T)) - signal_start_pos

        # 미리 크기를 알고 있으므로 리스트 최적화 (예비 할당)
        signal_list: list[np.ndarray] = [] * total_size if total_size > 0 else []
        date_index: list[pd.Timestamp] = [] * total_size if total_size > 0 else []

        # first_date 인덱스 한 번만 계산
        first_date = self._parse_date(self.configs.first_date)
        first_date_idx = bisect.bisect_left(self.stock_data.T, first_date)

        # 배치 처리로 신호 계산
        iterator = range(signal_start_pos, min(end_pos, len(self.stock_data.T)))

        # tqdm 활성화/비활성화 조건에 따라 처리
        if not self._disable_tqdm:
            iterator = tqdm(
                iterator,
                desc=f"Calculating signals from {start} to {end}",
                total=total_size,
            )

        for idx in iterator:
            t = self.stock_data.T[idx]
            signal_t = self.run_step(t, idx, first_date_idx)

            # 입력 유효성 검사
            self._validate_signal_shape(signal_t)

            signal_list.append(signal_t)
            date_index.append(pd.Timestamp(t))

        return signal_list, date_index

    def _validate_signal_shape(self, signal: np.ndarray) -> None:
        """신호 배열 모양 검증"""
        if signal.ndim != 1:
            raise ValueError(
                f"run_step() must return 1D array, but got {signal.ndim}D array. shape: {signal.shape}"
            )

    def _cache_adapter_data(self):
        if DataType.STOCK in self.adapter.dm.data:
            self.stock_data = self.adapter.stock
        if DataType.MACRO in self.adapter.dm.data:
            self.macro_data = self.adapter.macro
        if DataType.ENTITY in self.adapter.dm.data:
            self.entity_data = self.adapter.entity
        if DataType.STATIC in self.adapter.dm.data:
            self.static_data = self.adapter.static

    def _parse_date(self, date: int) -> pd.Timestamp:
        """Convert YYYYMMDD integer to pandas Timestamp."""
        return pd.Timestamp(datetime.strptime(str(date), "%Y%m%d"))

    def explore(
        self,
        start: int,
        end: int,
        param_ranges: dict,
        expert_defaults: dict | None = None,
        fee: bool = True,
        max_workers: int | None = None,
        method: str = "full",
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        병렬처리로 파라미터 조합들을 탐색하고 백테스트 결과를 반환

        Args:
            param_ranges: 각 파라미터의 값 범위
            start: 백테스트 시작 날짜
            end: 백테스트 종료 날짜
            fee: 수수료 적용 여부
            max_workers: 병렬 처리 워커 수
            method: 조합 생성 방법 ("full", "tercile")
            expert_defaults: expert point를 위한 기본값 (tercile method에서 사용)

        Returns:
            백테스트 결과 DataFrame
        """
        if expert_defaults is None:
            expert_defaults = self.params.default

        # 파라미터 조합 생성
        param_combinations = generate_param_combinations(
            param_ranges, method=method, expert_defaults=expert_defaults
        )

        # 백테스트 실행
        return run_param_exploration(
            signal_instance=self,
            param_combinations=param_combinations,
            start=start,
            end=end,
            fee=fee,
            max_workers=max_workers,
        )

    def explore_greedy(
        self,
        start: int,
        end: int,
        fee: bool = True,
        max_workers: int | None = None,
    ):
        stat, nav = self.explore(
            start=start,
            end=end,
            fee=fee,
            max_workers=max_workers,
            method="midpoint",
            param_ranges=self.params.range,
            expert_defaults=self.params.default,
        )
        selected = greedy_select(nav, stat)

        selected_points = [
            dict(zip(self.params.range.keys(), selected[i]))
            for i in range(len(selected))
        ]

        return (
            stat,
            nav,
            selected,
            selected_points,
        )

    def explore_one_way(
        self,
        start: int,
        end: int,
        key: str,
        initial_params: dict,
        fee: bool = True,
        max_workers: int | None = None,
        plot: bool = False,
    ):
        assert key in self.params.range, f"key {key} not in {self.params.range}"

        param_ranges = {key: self.params.range[key]}
        self.update_params(**initial_params)
        stat, nav = self.explore(
            start=start,
            end=end,
            fee=fee,
            max_workers=max_workers,
            method="full",
            param_ranges=param_ranges,
            expert_defaults=initial_params,
        )
        self.reset_params()

        control_var = [k for k in self.params.range.keys() if k is not key]
        stat = stat.T.reset_index(control_var, drop=True).sort_index().T
        nav = nav.T.reset_index(control_var, drop=True).sort_index().T

        if plot:
            control_params = {
                k: initial_params[k] for k in control_var if k in initial_params
            }
            print(f"Stats plot for {stat.columns.name}")
            quick_plot_stats(stat, stat.columns.name, control_params)

        return stat, nav

    def explore_two_way(
        self,
        start: int,
        end: int,
        key: list[str],
        initial_params: dict,
        fee: bool = True,
        max_workers: int | None = None,
        plot: bool = False,
        plot_type: str = "heatmap",
    ):
        assert isinstance(key, list) and len(key) == 2, (
            "key must be a list of 2 elements"
        )
        assert all(k in self.params.range for k in key), (
            f"key {key} not in {self.params.range}"
        )

        param_ranges = {k: self.params.range[k] for k in key}
        self.update_params(**initial_params)
        stat, nav = self.explore(
            start=start,
            end=end,
            fee=fee,
            max_workers=max_workers,
            method="full",
            param_ranges=param_ranges,
            expert_defaults=initial_params,
        )
        self.reset_params()

        control_var = [k for k in self.params.range.keys() if k not in key]
        stat = stat.T.reset_index(control_var, drop=True).sort_index().T
        nav = nav.T.reset_index(control_var, drop=True).sort_index().T

        if plot:
            control_params = {
                k: initial_params[k] for k in control_var if k in initial_params
            }
            print(f"Stats plot for {key[0]} vs {key[1]}")
            quick_plot_two_way(stat, key, control_params, plot_type=plot_type)

        return stat, nav
