import pandas as pd


def normalize_signal(signal: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    abs_sum = signal.abs().sum(axis=1)

    over_exposed = abs_sum > 1.0

    if over_exposed.any():
        if verbose:
            print(f"✓ Scaling {over_exposed.sum()} days with exposure > 1.0")

        # 벡터화된 연산으로 처리
        # over_exposed인 행들만 선택
        over_exposed_signals = signal[over_exposed]

        # long/short 분리 (over_exposed 행들만)
        long_mask = over_exposed_signals > 0
        short_mask = over_exposed_signals < 0

        # 각 행의 long/short 합계 계산
        long_sum = (over_exposed_signals * long_mask).sum(axis=1)
        short_sum = (over_exposed_signals * short_mask).abs().sum(axis=1)
        total_sum = long_sum + short_sum

        # total_sum이 0이 아닌 경우만 정규화
        valid_mask = total_sum > 0

        # 스케일 팩터 계산 (벡터화)
        scale_factors = pd.Series(0.0, index=over_exposed_signals.index)
        scale_factors[valid_mask] = 1.0 / total_sum[valid_mask]

        # 정규화 적용 (브로드캐스팅 사용)
        normalized_signals = over_exposed_signals.multiply(scale_factors, axis=0)

        # 원본 시그널 업데이트
        signal = pd.concat([signal[~over_exposed], normalized_signals]).sort_index()

    # # 검증
    # final_abs_sum = signal.abs().sum(axis=1)
    # print(f"Max exposure: {final_abs_sum.max():.4f}")
    # print(f"Days with exposure <= 1.0: {(final_abs_sum <= 1.0001).sum()} / {len(final_abs_sum)}")

    return signal
