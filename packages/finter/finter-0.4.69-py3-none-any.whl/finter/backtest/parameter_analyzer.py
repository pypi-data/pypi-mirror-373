import inspect
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import product
from typing import Any, Dict, List

import pandas as pd
from tqdm import tqdm


class ParameterAnalyzer:
    def __init__(self, alpha_class, simulator, logger=None):
        self.alpha_class = alpha_class
        self.simulator = simulator
        self.logger = logger or logging.getLogger(__name__)

        # Alpha.get 메서드의 파라미터 정보 추출
        self.alpha_params = self._inspect_alpha_params()

    def _inspect_alpha_params(self):
        """Alpha.get 메서드의 파라미터 정보 추출"""
        sig = inspect.signature(self.alpha_class.get)
        params_info = {}

        for name, param in sig.parameters.items():
            if name in ["self", "start", "end"]:  # 필수 파라미터 제외
                continue

            params_info[name] = {
                "default": param.default
                if param.default != inspect.Parameter.empty
                else None,
                "annotation": param.annotation
                if param.annotation != inspect.Parameter.empty
                else None,
                "kind": str(param.kind),
            }

        return params_info

    def validate_params(self, params: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
        """파라미터 검증 및 기본값 처리"""
        validated_params = {}

        # 제공된 파라미터가 Alpha.get에 존재하는지 확인
        for param_name, param_values in params.items():
            if param_name not in self.alpha_params:
                self.logger.warning(
                    f"Parameter '{param_name}' not found in Alpha.get method. Skipping."
                )
                continue
            validated_params[param_name] = param_values

        # Alpha.get의 파라미터 중 제공되지 않은 것들 확인
        for param_name, param_info in self.alpha_params.items():
            if param_name not in validated_params and param_info["default"] is not None:
                self.logger.info(
                    f"Parameter '{param_name}' not provided. Using default: {param_info['default']}"
                )

        return validated_params

    def generate_param_grid(self, params):
        """파라미터 조합 생성"""
        keys = list(params.keys())
        values = list(params.values())
        combinations = list(product(*values))
        return [dict(zip(keys, combo)) for combo in combinations]

    def print_execution_plan(self, params: Dict[str, List[Any]], start: int, end: int):
        """실행 계획 출력"""
        validated_params = self.validate_params(params)
        param_grid = self.generate_param_grid(validated_params)

        print("\n" + "=" * 60)
        print("Parameter Analysis Execution Plan")
        print("=" * 60)
        print(f"\nAlpha Class: {self.alpha_class.__name__}")
        print(f"Date Range: {start} - {end}")
        print(f"\nTotal Combinations: {len(param_grid)}")

        print("\nParameter Ranges:")
        for param, values in validated_params.items():
            print(f"  - {param}: {values}")

        print("\nAlpha.get Parameters Info:")
        for param, info in self.alpha_params.items():
            print(f"  - {param}: default={info['default']}, type={info['annotation']}")

        print("\nSample Combinations (first 5):")
        for i, combo in enumerate(param_grid[:5]):
            print(f"  {i+1}. {combo}")

        if len(param_grid) > 5:
            print(f"  ... and {len(param_grid) - 5} more combinations")

        print("=" * 60 + "\n")

        return validated_params, param_grid

    def run_single_backtest(self, params, start, end):
        """단일 파라미터 조합으로 백테스트 실행"""
        try:
            alpha = self.alpha_class()
            positions = alpha.get(start, end, **params)
            result = self.simulator.run(positions)

            # 파라미터와 summary DataFrame을 딕셔너리로 반환
            return {"params": params, "summary": result.statistics}
        except Exception as e:
            self.logger.error(f"Error with params {params}: {str(e)}")
            return None

    def analyze_all(self, params, start, end, n_jobs=4, dry_run=False):
        """모든 파라미터 조합 분석"""
        # 실행 계획 출력 및 파라미터 검증
        validated_params, param_grid = self.print_execution_plan(params, start, end)

        if dry_run:
            print("Dry run mode - not executing backtests")
            return pd.DataFrame(param_grid)

        # 사용자 확인
        user_input = input("\nProceed with analysis? (y/n): ")
        if user_input.lower() != "y":
            print("Analysis cancelled.")
            return None

        results = []

        # 병렬 처리 - ThreadPoolExecutor 사용 (pickle 에러 방지)
        print(f"\nRunning {len(param_grid)} backtests with {n_jobs} workers...")
        with ThreadPoolExecutor(max_workers=n_jobs) as executor:
            futures = {
                executor.submit(self.run_single_backtest, p, start, end): p
                for p in param_grid
            }

            for future in tqdm(as_completed(futures), total=len(futures)):
                result = future.result()
                if result is not None:
                    results.append(result)

        # 결과를 DataFrame으로 변환
        if results:
            df_rows = []
            for result in results:
                # 파라미터와 statistics를 하나의 행으로 합치기
                row = result["params"].copy()
                
                # statistics가 Series라면 딕셔너리로 변환
                if hasattr(result["summary"], 'to_dict'):
                    stats_dict = result["summary"].to_dict()
                else:
                    stats_dict = result["summary"]
                
                row.update(stats_dict)
                df_rows.append(row)
            
            results_df = pd.DataFrame(df_rows)
            
            # 파라미터 컬럼들을 인덱스로 설정
            param_columns = list(validated_params.keys())
            if param_columns:
                results_df = results_df.set_index(param_columns)
        else:
            print("\nNo valid results found.")
            return None

        # 에러 발생한 조합 확인
        failed_count = len(param_grid) - len(results)
        if failed_count > 0:
            print(f"\nWarning: {failed_count} combinations failed with errors")

        return results_df

    def get_best_params(self, results_df, metric="sharpe_ratio", top_n=5):
        """최적 파라미터 조합 추출"""
        # 에러가 없는 결과만 필터링
        valid_results = (
            results_df[results_df["error"].isna()]
            if "error" in results_df
            else results_df
        )
        return valid_results.nlargest(top_n, metric)

    def summarize_results(self, results_df):
        """결과 요약 통계"""
        print("\n" + "=" * 60)
        print("Results Summary")
        print("=" * 60)

        # 에러 제외한 유효한 결과만
        valid_results = (
            results_df[results_df["error"].isna()]
            if "error" in results_df
            else results_df
        )

        if len(valid_results) == 0:
            print("No valid results found.")
            return

        metrics = ["sharpe_ratio", "annual_return", "max_drawdown", "volatility"]

        for metric in metrics:
            if metric in valid_results.columns:
                print(f"\n{metric}:")
                print(f"  Mean: {valid_results[metric].mean():.4f}")
                print(f"  Std:  {valid_results[metric].std():.4f}")
                print(f"  Min:  {valid_results[metric].min():.4f}")
                print(f"  Max:  {valid_results[metric].max():.4f}")
