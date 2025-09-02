import numpy as np
import pandas as pd
from typing_extensions import Literal


class PortfolioAnalyzer:
    @staticmethod
    def nav2stats(nav, period: Literal["M", "Q", "Y", None] = None):
        if period == None:
            return PortfolioAnalyzer._nav_to_stats(nav)
        else:
            columns_order = [
                "Total Return (%)",
                "CAGR (%)",
                "Volatility (%)",
                "Hit Ratio (%)",
                "Sharpe Ratio",
                "Sortino Ratio",
                "Max Drawdown (%)",
                "Mean Drawdown (%)",
                "Calmar Ratio",
                "Avg Tuw",
                "Max Tuw",
                "Skewness",
                "Kurtosis",
                "VaR 95% (%)",
                "VaR 99% (%)",
                "Positive HHI",
                "Negative HHI",
            ]
            result = (
                nav.groupby(pd.Grouper(freq=period))
                .apply(PortfolioAnalyzer._nav_to_stats)
                .unstack()
            )
            return result[columns_order].dropna()

    @staticmethod
    def position2stats(position, period: Literal["D", "M", "Q", "Y", None] = None):
        if period == "D":
            return pd.DataFrame(
                PortfolioAnalyzer._position_to_stats(position, group=False)
            )
        elif period == None:
            return pd.Series(PortfolioAnalyzer._position_to_stats(position, group=True))
        else:
            result = position.groupby(pd.Grouper(freq=period)).apply(
                PortfolioAnalyzer._position_to_stats
            )
            return pd.DataFrame(
                result.tolist(), index=result.index, columns=result.values[0].keys()
            ).dropna()

    @staticmethod
    def nav2stats_dict(returns):
        if len(returns) < 2:
            return {
                "total_return": np.nan,
                "cagr": np.nan,
                "volatility": np.nan,
                "hit_ratio": np.nan,
                "sharpe_ratio": np.nan,
                "sortino_ratio": np.nan,
                "max_drawdown": np.nan,
                "mean_drawdown": np.nan,
                "calmar_ratio": np.nan,
                "avg_tuw": np.nan,
                "max_tuw": np.nan,
                "skewness": np.nan,
                "kurtosis": np.nan,
                "var_95": np.nan,
                "var_99": np.nan,
                "positive_hhi": np.nan,
                "negative_hhi": np.nan,
            }

        total_return = returns.iloc[-1] / returns.iloc[0] - 1
        trading_days = len(returns)
        returns_pct = returns.pct_change().dropna()

        returns_pct_std = returns_pct.std()
        returns_pct_std_neg = returns_pct[returns_pct < 0].std()
        skewness = PortfolioAnalyzer._calculate_skewness(returns_pct)
        kurtosis = PortfolioAnalyzer._calculate_kurtosis(returns_pct)
        positive_hhi = PortfolioAnalyzer._calculatea_run_HHI(returns_pct, 1)
        negative_hhi = PortfolioAnalyzer._calculatea_run_HHI(returns_pct, 0)
        cagr = ((1 + total_return) ** (252 / trading_days) - 1) * 100

        stats_dict = {
            "total_return": total_return,
            "cagr": cagr,
            "volatility": returns_pct.std() * np.sqrt(252),
            "hit_ratio": round((returns_pct > 0).mean() * 100, 3),
            "sharpe_ratio": (
                (returns_pct.mean() / returns_pct_std) * np.sqrt(252)
                if returns_pct_std != 0
                else np.nan
            ),
            "sortino_ratio": (
                (returns_pct.mean() / returns_pct_std_neg) * np.sqrt(252)
                if returns_pct_std_neg != 0
                else np.nan
            ),
            "max_drawdown": (returns / returns.cummax() - 1).min(),
            "mean_drawdown": (returns / returns.cummax() - 1).mean(),
            "calmar_ratio": (
                round((cagr / 100) / abs((returns / returns.cummax() - 1).min()), 3)
                if (returns / returns.cummax() - 1).min() != 0
                else None
            ),
            "avg_tuw": PortfolioAnalyzer._calculate_tuw(returns)[0],
            "max_tuw": PortfolioAnalyzer._calculate_tuw(returns)[1],
            "skewness": skewness,
            "kurtosis": kurtosis,
            "var_95": np.percentile(returns_pct, 5),
            "var_99": np.percentile(returns_pct, 1),
            "positive_hhi": positive_hhi,
            "negative_hhi": negative_hhi,
        }

        return stats_dict

    @staticmethod
    def _nav_to_stats(returns):
        if len(returns) < 2:
            return pd.Series(
                {
                    "Total Return (%)": np.nan,
                    "CAGR (%)": np.nan,
                    "Volatility (%)": np.nan,
                    "Hit Ratio (%)": np.nan,
                    "Sharpe Ratio": np.nan,
                    "Sortino Ratio": np.nan,
                    "Max Drawdown (%)": np.nan,
                    "Mean Drawdown (%)": np.nan,
                    "Calmar Ratio": np.nan,
                    "Avg Tuw": np.nan,
                    "Max Tuw": np.nan,
                    "Skewness": np.nan,
                    "Kurtosis": np.nan,
                    "VaR 95% (%)": np.nan,
                    "VaR 99% (%)": np.nan,
                    "Positive HHI": np.nan,
                    "Negative HHI": np.nan,
                    "Robust K Ratio": np.nan,
                }
            )

        total_return = (returns.iloc[-1] / returns.iloc[0] - 1) * 100
        trading_days = len(returns)
        returns_pct = returns.pct_change().dropna()
        cagr = ((1 + total_return / 100) ** (252 / trading_days) - 1) * 100
        returns_pct_std = returns_pct.std()
        returns_pct_std_neg = returns_pct[returns_pct < 0].std()
        skewness = PortfolioAnalyzer._calculate_skewness(returns_pct)
        kurtosis = PortfolioAnalyzer._calculate_kurtosis(returns_pct)
        positive_hhi = PortfolioAnalyzer._calculatea_run_HHI(returns_pct, 1)
        negative_hhi = PortfolioAnalyzer._calculatea_run_HHI(returns_pct, 0)
        k_ratio = PortfolioAnalyzer._calculate_k_ratio(returns_pct)

        stats_dict = {
            "Total Return (%)": round(total_return, 3),
            "CAGR (%)": round(cagr, 3) if trading_days != 0 else None,
            "Volatility (%)": round(returns_pct.std() * np.sqrt(252) * 100, 3),
            "Hit Ratio (%)": round((returns_pct > 0).mean() * 100, 3),
            "Sharpe Ratio": (
                round((returns_pct.mean() / returns_pct_std) * np.sqrt(252), 3)
                if returns_pct_std != 0
                else None
            ),
            "Sortino Ratio": (
                round(
                    (returns_pct.mean() / returns_pct_std_neg) * np.sqrt(252),
                    3,
                )
                if returns_pct_std_neg != 0
                else None
            ),
            "Max Drawdown (%)": round((returns / returns.cummax() - 1).min() * 100, 3),
            "Mean Drawdown (%)": round(
                (returns / returns.cummax() - 1).mean() * 100, 3
            ),
            "Calmar Ratio": (
                round((cagr / 100) / abs((returns / returns.cummax() - 1).min()), 3)
                if (returns / returns.cummax() - 1).min() != 0
                else None
            ),
            "Avg Tuw": PortfolioAnalyzer._calculate_tuw(returns)[0],
            "Max Tuw": PortfolioAnalyzer._calculate_tuw(returns)[1],
            "Skewness": round(skewness, 3) if skewness is not None else None,
            "Kurtosis": round(kurtosis, 3) if kurtosis is not None else None,
            "VaR 95% (%)": round(np.percentile(returns_pct, 5) * 100, 3),
            "VaR 99% (%)": round(np.percentile(returns_pct, 1) * 100, 3),
            "Positive HHI": (
                round(positive_hhi, 3) if positive_hhi is not None else None
            ),
            "Negative HHI": (
                round(negative_hhi, 3) if negative_hhi is not None else None
            ),
            "K Ratio": round(k_ratio, 3) if k_ratio is not None else None,
        }

        return pd.Series(stats_dict)

    @staticmethod
    def _position_to_stats(position, group=True):
        hhi = PortfolioAnalyzer._calculate_HHI(position)
        normalized_hhi = PortfolioAnalyzer._norm_calculate_HHI(position)
        ens = 1 / hhi.replace(0, np.nan)
        turnover = PortfolioAnalyzer._calculate_turnover(position)
        stats_dict = {
            "con50": position.apply(
                lambda row: PortfolioAnalyzer._calculate_cons(row, 50), axis=1
            ),
            "con80": position.apply(
                lambda row: PortfolioAnalyzer._calculate_cons(row, 80), axis=1
            ),
            "con100": position.apply(
                lambda row: PortfolioAnalyzer._calculate_cons(row, 100), axis=1
            ),
            "HHI": hhi,
            "ENS": ens,
            "Normalized HHI": normalized_hhi,
            "Turnover(%)": turnover,
            "Max Turnover(%)": turnover.max(),
        }
        if group:
            stats_dict["con50"] = stats_dict["con50"].replace(0, np.nan).mean()
            stats_dict["con80"] = stats_dict["con80"].replace(0, np.nan).mean()
            stats_dict["con100"] = stats_dict["con100"].replace(0, np.nan).mean()
            stats_dict["HHI"] = stats_dict["HHI"].replace(0, np.nan).mean()
            stats_dict["ENS"] = stats_dict["ENS"].mean()
            stats_dict["Normalized HHI"] = (
                stats_dict["Normalized HHI"].replace(0, np.nan).mean()
            )
            stats_dict["Turnover(%)"] = turnover.sum()
            stats_dict["Max Turnover(%)"] = turnover.max()
        return stats_dict

    @staticmethod
    def _calculate_kurtosis(pct_pnl):
        pct_pnl = pct_pnl.dropna()
        pnl_mean = pct_pnl.mean()

        m2 = ((pct_pnl - pnl_mean) ** 2).sum()
        m4 = ((pct_pnl - pnl_mean) ** 4).sum()

        n = len(pct_pnl)
        if n < 4:
            return None

        numerator = (n + 1) * n * (n - 1) * m4
        denominator = (n - 2) * (n - 3) * (m2**2)
        first_term = numerator / denominator

        second_term = (3 * ((n - 1) ** 2)) / ((n - 2) * (n - 3))

        return first_term - second_term

    @staticmethod
    def _calculate_skewness(pct_pnl):
        pct_pnl = pct_pnl.dropna()
        pnl_mean = pct_pnl.mean()
        n = len(pct_pnl)

        if n < 3:
            return None

        m3 = ((pct_pnl - pnl_mean) ** 3).sum() / n
        m2 = ((pct_pnl - pnl_mean) ** 2).sum() / n
        g1 = m3 / (m2**1.5)
        return np.sqrt(n * (n - 1)) / (n - 2) * g1

    @staticmethod
    def _calculatea_run_HHI(pct_pnl, sign):
        target = pct_pnl[(pct_pnl > 0 if sign else pct_pnl < 0)]

        tsum = target.sum()
        if tsum == 0:
            return None

        weight = target / tsum
        return (weight**2).sum()

    @staticmethod
    def _calculate_cons(row, percentage):
        # 실제 보유 종목만 필터링 (0이 아닌 값)
        non_zero_holdings = row[row != 0].abs()

        if len(non_zero_holdings) == 0:
            return 0

        sorted_holdings = non_zero_holdings.sort_values(ascending=False)
        cumulative_sum = sorted_holdings.cumsum()
        total_sum = sorted_holdings.sum()

        if total_sum == 0:
            return 0

        # percentage에 도달하는 첫 번째 인덱스 찾기
        threshold_reached = cumulative_sum / total_sum * 100 >= percentage

        if threshold_reached.any():
            assets_count = threshold_reached.argmax() + 1
        else:
            assets_count = len(sorted_holdings)

        return assets_count

    @staticmethod
    def _calculate_k_ratio(pct_pnl, trim_pct=5):
        # lower = np.percentile(pct_pnl, trim_pct)
        # upper = np.percentile(pct_pnl, 100 - trim_pct)

        pct_pnl_trimmed = pct_pnl  # .clip(lower, upper)

        cum_returns = (1 + pct_pnl_trimmed).cumprod()
        log_returns = np.log(cum_returns)

        n = len(log_returns)
        if n < 3:  # 자유도 확보 필요
            return 0.0

        x = np.arange(n, dtype=float)
        y = log_returns.astype(float)

        # polyfit으로 기울기와 절편
        slope, intercept = np.polyfit(x, y, 1)
        fitted = slope * x + intercept

        # SSE, 분산 추정
        resid = y - fitted
        SSE = np.dot(resid, resid)
        s2 = SSE / (n - 2)  # 자유도 n-2

        # 기울기 표준오차
        Sxx = np.sum((x - x.mean()) ** 2)
        se_beta = np.sqrt(s2 / Sxx)

        k_ratio = slope / (se_beta * np.sqrt(n)) if se_beta > 0 else 0.0

        return float(k_ratio)

    @staticmethod
    def _calculate_HHI(row):
        weight = row / 1e8
        return (weight**2).sum(axis=1)

    @staticmethod
    def _norm_calculate_HHI(row):
        weight = row.replace(0, np.nan) / 1e8
        return (weight**2).mean(axis=1)

    @staticmethod
    def _calculate_turnover(position):
        return position.diff().abs().sum(axis=1) / 1e6

    @staticmethod
    def stats(nav, position):
        """
        Comprehensive portfolio statistics showing both All period and Yearly breakdown.

        Args:
            nav: NAV time series (pd.Series with datetime index)
            position: Position data (pd.DataFrame with datetime index)

        Returns:
            pd.DataFrame with all portfolio statistics (All period + yearly breakdown)
        """
        # Calculate stats for entire period
        nav_stats_all = PortfolioAnalyzer._nav_to_stats(nav)
        pos_stats_all = pd.Series(
            PortfolioAnalyzer._position_to_stats(position, group=True)
        )

        # Calculate Hit Ratio only when position exists
        returns_pct = nav.pct_change().dropna()
        position_exists = (position.abs().sum(axis=1) > 0).reindex(
            returns_pct.index, method="ffill"
        )
        hit_ratio_all = (
            round((returns_pct[position_exists] > 0).mean() * 100, 3)
            if position_exists.any()
            else np.nan
        )

        # Calculate profit per turnover for all period (in basis points)
        total_return_all = nav_stats_all["Total Return (%)"]
        total_turnover_all = pos_stats_all["Turnover(%)"]
        profit_per_turnover_all = (
            float(total_return_all)
            / float(total_turnover_all)
            * 10000  # Convert to basis points
            if total_turnover_all != 0
            else np.nan
        )

        # Create All period stats
        all_stats = pd.Series(
            {
                # Risk-adjusted returns
                "sharpe_ratio": nav_stats_all["Sharpe Ratio"],
                "k_ratio": nav_stats_all["K Ratio"],
                # Return metrics
                "profit_per_turnover_bp": round(profit_per_turnover_all, 2)
                if not np.isnan(profit_per_turnover_all)
                else np.nan,
                # Performance metrics
                "hit_ratio_pct": hit_ratio_all,
                "total_return_pct": nav_stats_all["Total Return (%)"],
                "annualized_return_pct": nav_stats_all["CAGR (%)"],
                # Risk metrics
                "annualized_volatility_pct": nav_stats_all["Volatility (%)"],
                # Trading metrics
                "total_turnover_pct": pos_stats_all["Turnover(%)"],
                "max_drawdown_pct": nav_stats_all["Max Drawdown (%)"],
                "max_time_underwater_days": nav_stats_all["Max Tuw"],
                # Portfolio concentration metrics
                "all_holdings_count": pos_stats_all["con100"],
            },
            name="All",
        )

        # Calculate yearly stats
        nav_yearly = (
            nav.groupby(pd.Grouper(freq="Y"))
            .apply(PortfolioAnalyzer._nav_to_stats)
            .unstack()
        )
        pos_yearly = position.groupby(pd.Grouper(freq="Y")).apply(
            lambda x: pd.Series(PortfolioAnalyzer._position_to_stats(x, group=True))
        )

        # Calculate yearly Hit Ratio only when position exists
        def calculate_hit_ratio_with_position(year_idx):
            year_nav = nav[year_idx]
            year_position = position.loc[year_idx]
            year_returns_pct = year_nav.pct_change().dropna()
            year_position_exists = (year_position.abs().sum(axis=1) > 0).reindex(
                year_returns_pct.index, method="ffill"
            )
            return (
                round((year_returns_pct[year_position_exists] > 0).mean() * 100, 3)
                if year_position_exists.any()
                else np.nan
            )

        hit_ratio_yearly = nav.groupby(pd.Grouper(freq="Y")).apply(
            lambda x: calculate_hit_ratio_with_position(x.index)
        )

        # Calculate yearly profit per turnover (in basis points)
        profit_per_turnover_yearly = (
            nav_yearly["Total Return (%)"]
            / pos_yearly["Turnover(%)"]
            * 10000  # Convert to basis points
        )
        profit_per_turnover_yearly = profit_per_turnover_yearly.apply(
            lambda x: round(x, 1)
            if not np.isnan(x) and x != np.inf and x != -np.inf
            else np.nan
        )

        # Create yearly stats DataFrame
        yearly_stats = pd.DataFrame(
            {
                # Risk-adjusted returns
                "sharpe_ratio": nav_yearly["Sharpe Ratio"],
                "k_ratio": nav_yearly["K Ratio"],
                # Return metrics
                "annualized_return_pct": nav_yearly["CAGR (%)"],
                "total_return_pct": nav_yearly["Total Return (%)"],
                # Trading metrics
                "total_turnover_pct": pos_yearly["Turnover(%)"],
                "profit_per_turnover_bp": profit_per_turnover_yearly,
                # Risk metrics
                "annualized_volatility_pct": nav_yearly["Volatility (%)"],
                "max_drawdown_pct": nav_yearly["Max Drawdown (%)"],
                "max_time_underwater_days": nav_yearly["Max Tuw"],
                # Performance metrics
                "hit_ratio_pct": hit_ratio_yearly,
                # Portfolio concentration metrics
                "all_holdings_count": pos_yearly["con100"],
            }
        )

        # Format index for yearly stats (extract year only)
        yearly_stats.index = pd.to_datetime(yearly_stats.index).year

        # Combine All and Yearly stats
        result = pd.concat([all_stats.to_frame().T, yearly_stats])

        # Round all numeric values for cleaner display
        numeric_columns = result.select_dtypes(include=[np.number]).columns
        result[numeric_columns] = result[numeric_columns].round(3)

        return result

    @staticmethod
    def _calculate_tuw(nav):
        nav = nav.dropna().astype(float)
        running_max = nav.cummax()

        # ① 현재 낙폭 비율
        drawdown = nav / running_max - 1  # 0 ~ -1 범위

        # ② drawdown 구간 레이블링
        dd_flag = drawdown < 0
        dd_groups = (dd_flag != dd_flag.shift()).cumsum()  # 구간별 번호
        dd_groups[~dd_flag] = np.nan

        stats = []
        for gid, segment in drawdown.groupby(dd_groups):
            if np.isnan(gid):  # dd_flag == False 영역 skip
                continue
            dd_min = segment.min()  # 최대 낙폭 (%)
            start = segment.index[0]  # 피크 발생 직후 시점
            # 복구 시점 : drawdown이 0 으로 돌아오는 첫 날
            try:
                end = drawdown[segment.index[-1] :].idxmax()  # 0에 가장 먼저 도달
            except ValueError:  # 끝까지 복구 못하면 today로
                end = nav.index[-1]
            tuw = end - start
            stats.append((dd_min, tuw))

        if not stats:  # drawdown이 전혀 없었던 경우
            return 0.0, pd.Timedelta(0)

        # ③ 평균값
        avg_tuw = sum([x[1] for x in stats], pd.Timedelta(0)) / len(stats)
        max_tuw = max([x[1] for x in stats])

        to_days = lambda x: round(x.total_seconds() / 86400, 3)

        avg_tuw_days = to_days(avg_tuw)
        max_tuw_days = to_days(max_tuw)

        return avg_tuw_days, max_tuw_days
