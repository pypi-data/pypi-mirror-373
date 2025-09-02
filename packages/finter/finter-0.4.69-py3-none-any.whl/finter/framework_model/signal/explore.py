import itertools
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from tqdm import tqdm

if TYPE_CHECKING:
    from finter.framework_model.signal.main import BaseSignal


def midpoint_hypercube(
    param_ranges: Dict[str, List], expert_defaults: Optional[Dict[str, Any]] = None
) -> List[Tuple]:
    param_names = list(param_ranges.keys())

    # 1. Expert point (center)
    if expert_defaults:
        expert_point = tuple(expert_defaults[name] for name in param_names)
    else:
        # Default: 중간값
        expert_point = tuple(
            param_ranges[name][len(param_ranges[name]) // 2] for name in param_names
        )

    points = [expert_point]

    # 2. 각 파라미터의 min-default 중간값, default-max 중간값 계산
    midpoints = {}
    for name in param_names:
        values = param_ranges[name]

        # expert_defaults가 있으면 사용, 없으면 중간값
        if expert_defaults and name in expert_defaults:
            default_val = expert_defaults[name]
        else:
            default_val = values[len(values) // 2]

        # default_val의 인덱스 찾기
        if default_val in values:
            default_idx = values.index(default_val)
        else:
            # default_val이 리스트에 없는 경우 가장 가까운 값 찾기
            default_idx = min(
                range(len(values)), key=lambda i: abs(values[i] - default_val)
            )

        # min과 default의 중간 인덱스
        low_idx = default_idx // 2

        # default와 max의 중간 인덱스
        high_idx = (default_idx + len(values) - 1) // 2

        # 인덱스 범위 체크
        low_idx = max(0, min(low_idx, len(values) - 1))
        high_idx = max(0, min(high_idx, len(values) - 1))

        midpoints[name] = (values[low_idx], values[high_idx])

    # 3. 2^n corner points 생성
    midpoint_values = [midpoints[name] for name in param_names]

    # itertools.product로 모든 low/high 조합 생성
    corners = list(itertools.product(*midpoint_values))
    points.extend(corners)

    return points


def generate_param_combinations(
    param_ranges: Dict[str, List],
    method: str = "full",
    expert_defaults: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    파라미터 조합 생성 함수

    Args:
        param_ranges: 각 파라미터의 값 범위 (일부만 제공 가능)
        method: 조합 생성 방법 ("full", "midpoint", "random")
        expert_defaults: expert point를 위한 기본값 (제공되지 않은 파라미터에 대한 고정값으로도 사용)

    Returns:
        파라미터 조합 리스트
    """
    # expert_defaults가 있는 경우 모든 파라미터 키 가져오기
    if expert_defaults:
        all_param_keys = list(expert_defaults.keys())
        
        # param_ranges에 없는 파라미터는 expert_defaults 값으로 고정
        fixed_params = {}
        varying_params = {}
        
        for key in all_param_keys:
            if key in param_ranges:
                # 범위가 제공된 파라미터
                varying_params[key] = param_ranges[key]
            else:
                # 범위가 없으면 디폴트값으로 고정
                fixed_params[key] = expert_defaults[key]
    else:
        # expert_defaults가 없으면 기존 로직 그대로
        varying_params = param_ranges
        fixed_params = {}

    param_keys = list(varying_params.keys())

    if method == "full":
        # 변동 파라미터의 모든 조합 생성
        param_values = list(varying_params.values())
        param_combinations = list(itertools.product(*param_values))

    elif method == "midpoint":
        # Midpoint hypercube 방법 사용 (변동 파라미터에 대해서만)
        midpoint_points = midpoint_hypercube(varying_params, expert_defaults)
        param_combinations = midpoint_points

    elif method == "random":
        # 랜덤 샘플링 (추후 구현 가능)
        raise NotImplementedError("Random sampling not yet implemented")

    else:
        raise ValueError(f"Unknown method: {method}")

    params_combinations = list(set(param_combinations))

    # 변동 파라미터 조합을 딕셔너리로 변환하고 고정 파라미터 추가
    result_combinations = []
    for combo in params_combinations:
        param_dict = dict(zip(param_keys, combo))
        # 고정 파라미터 추가
        param_dict.update(fixed_params)
        result_combinations.append(param_dict)

    return result_combinations


def run_backtest_worker(signal_class, param_dict, start, end, fee):
    """
    워커 프로세스에서 실행될 백테스트 함수
    """
    try:
        # 캐시된 context가 있으면 사용, 없으면 새로 생성
        if hasattr(signal_class, "_global_cache") and signal_class._global_cache:
            signal_instance = signal_class(use_cache=True)
        else:
            signal_instance = signal_class()

        # 파라미터 업데이트
        signal_instance.update_params(**param_dict)

        # 백테스트 실행
        simulator = signal_instance.backtest(start, end, fee, worker=True)

        # 성과 지표 추출
        performance = simulator.performance

        # NAV 시계열 데이터 추출
        nav = simulator.summary.nav

        return {
            "stats": {
                "sharpe_ratio": performance.loc["All", "sharpe_ratio"],
                "k_ratio": performance.loc["All", "k_ratio"],
                "return_per_turnover_bp": performance.loc[
                    "All", "profit_per_turnover_bp"
                ],
                "mdd_pct": performance.loc["All", "max_drawdown_pct"],
                "hit_ratio_pct": performance.loc["All", "hit_ratio_pct"],
                "holding_count": performance.loc["All", "all_holdings_count"],
            },
            "nav": nav,
        }

    except Exception as e:
        print(f"Backtest failed for params {param_dict}: {str(e)}")
        return None


def run_param_exploration(
    signal_instance: "BaseSignal",
    param_combinations: List[Dict[str, Any]],
    start: int,
    end: int,
    fee: bool = True,
    max_workers: Optional[int] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    주어진 파라미터 조합들에 대해 백테스트를 실행하고 결과를 반환

    Args:
        signal_instance: BaseSignal 인스턴스
        param_combinations: 파라미터 조합 리스트
        start: 백테스트 시작 날짜
        end: 백테스트 종료 날짜
        fee: 수수료 적용 여부
        max_workers: 병렬 처리 워커 수

    Returns:
        (성과 지표 DataFrame, NAV 시계열 DataFrame) 튜플
    """
    if max_workers is None:
        max_workers = cpu_count()

    # 캐시가 없으면 현재 인스턴스의 데이터를 캐시에 저장
    if not signal_instance._global_cache:
        signal_instance._store_to_cache()
        print("Cache stored for worker processes")

    print(
        f"Exploring {len(param_combinations)} parameter combinations using {max_workers} workers..."
    )

    stats_results = []
    nav_dict = {}

    # 병렬 처리로 백테스트 실행
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 작업 제출
        future_to_params = {}
        for param_dict in param_combinations:
            # 클래스 자체를 전달
            future = executor.submit(
                run_backtest_worker,
                signal_instance.__class__,
                param_dict,
                start,
                end,
                fee,
            )
            future_to_params[future] = param_dict

        # 결과 수집
        pbar = tqdm(
            total=len(param_combinations),
            desc="Running backtests",
        )

        for future in as_completed(future_to_params):
            param_dict = future_to_params[future]
            # tqdm 설명에 현재 파라미터 표시
            param_str = ", ".join([f"{k}={v}" for k, v in param_dict.items()])
            pbar.set_description(f"Testing: {param_str}")

            try:
                result = future.result()
                if result is not None:
                    # 파라미터 정보와 성과 지표 결합
                    stats_dict = param_dict.copy()
                    stats_dict.update(result["stats"])
                    stats_results.append(stats_dict)

                    # NAV 데이터 저장 (파라미터 이름 순서대로 튜플 생성)
                    param_key = tuple(
                        param_dict[name] for name in param_combinations[0].keys()
                    )
                    nav_dict[param_key] = result["nav"]
            except Exception as e:
                print(f"Error with parameters {param_dict}: {str(e)}")

            pbar.update(1)
        pbar.close()

    # 결과를 DataFrame으로 변환
    if stats_results:
        stats_df = (
            pd.DataFrame(stats_results)
            .set_index(list(param_combinations[0].keys()))
            .sort_values("sharpe_ratio", ascending=False)
        ).T

        # NAV 데이터를 DataFrame으로 병합
        # stats_df의 인덱스와 동일한 형태로 nav 데이터 정렬
        nav_list = []
        for idx in stats_df.columns:
            if idx in nav_dict:
                nav_list.append(nav_dict[idx])

        # 모든 NAV series를 outer join으로 병합
        if nav_list:
            nav_df = pd.concat(nav_list, axis=1, join="outer", keys=stats_df.columns)
            nav_df = nav_df.sort_index()
            # NaN 값을 forward fill로 처리 (이전 값으로 채우기)
            nav_df = nav_df.ffill()
        else:
            nav_df = pd.DataFrame()

        return stats_df, nav_df
    else:
        print("No successful backtests completed")
        return pd.DataFrame(), pd.DataFrame()


def greedy_select(nav, stat, alpha=0.5, stat_weight=0.5, min_sharpe=0, max_corr=0.7):
    """
    nav: DataFrame - 시계열 NAV (columns = 전략명)
    stat: DataFrame - 전략별 통계 (index = 전략명)
    alpha: orthogonality 가중치 (0~1)
    stat_weight: stat corr 가중치 (returns corr와의 비율)
    min_sharpe: 최소 샤프 비율 (early exit)
    """
    n = len(stat.columns.names)
    returns = nav.pct_change().dropna()
    returns_corr = returns.corr().values

    stat_corr = stat.corr().values

    combined_corr = (1 - stat_weight) * returns_corr + stat_weight * stat_corr

    sharpe = stat.loc["sharpe_ratio"].values

    # Greedy selection
    selected = []
    remaining = list(range(len(sharpe)))

    # 1. 최고 샤프 선택
    best = np.argmax(sharpe)
    selected.append(best)
    remaining.remove(int(best))

    # 2. 나머지 선택
    while len(selected) < n and remaining:
        scores = []
        candidates = []

        for idx in remaining:
            # 샤프 체크 (early exit)
            if sharpe[idx] < min_sharpe:
                continue

            # 기존 선택과의 최대 상관관계
            max_correlation = max(abs(combined_corr[idx, s]) for s in selected)
            if max_correlation > max_corr:
                continue

            # 점수 계산
            score = alpha * (1 - max_correlation) + (1 - alpha) * (
                sharpe[idx] / max(sharpe)
            )
            scores.append(score)
            candidates.append(idx)

        # 적합한 후보가 없으면 종료
        if not candidates:
            print(
                f"Early exit: No suitable candidates (sharpe >= {min_sharpe}). Selected {len(selected)}/{n}"
            )
            break

        # 최고 점수 선택
        best_pos = np.argmax(scores)
        best_idx = candidates[best_pos]
        selected.append(best_idx)
        remaining.remove(best_idx)

    return nav.columns[selected]
