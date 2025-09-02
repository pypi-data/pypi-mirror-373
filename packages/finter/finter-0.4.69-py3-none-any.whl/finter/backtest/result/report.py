from __future__ import annotations

import io
from typing import TYPE_CHECKING, Optional

import pandas as pd

try:
    import plotly.graph_objects as go
    import plotly.offline as pyo
    from plotly.subplots import make_subplots

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

if TYPE_CHECKING:
    pass


class BacktestReporter:
    """백테스트 결과에 대한 리포트를 생성하는 클래스"""

    def __init__(self, summary: pd.DataFrame, statistics: pd.Series) -> None:
        self.summary = summary
        self.statistics = statistics
        if not PLOTLY_AVAILABLE:
            raise ImportError(
                "plotly is required for report generation. "
                "Please install it with: pip install plotly"
            )

    def _calculate_drawdown(self, nav_series: pd.Series) -> pd.Series:
        """Drawdown을 계산합니다."""
        rolling_max = nav_series.expanding().max()
        drawdown = (nav_series - rolling_max) / rolling_max * 100
        return drawdown

    def create_comprehensive_performance_chart(self) -> go.Figure:
        """NAV, Drawdown, Turnover를 통합한 종합 성과 차트를 생성합니다."""
        nav_data = self.summary.nav

        if nav_data.empty:
            raise ValueError("No NAV data available for plotting")

        # Drawdown 계산
        drawdown = self._calculate_drawdown(nav_data)

        turnover_data = self.summary.actual_turnover

        # 2개 서브플롯 생성 (NAV, Daily Turnover)
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.12,
            subplot_titles=(
                "Portfolio NAV Performance",
                "Daily Portfolio Turnover (%)",
            ),
            row_heights=[0.55, 0.45],
        )

        # 1. 전고점 라인 (회색 점선) - 먼저 그려서 뒤에 위치
        running_max = nav_data.expanding().max()

        fig.add_trace(
            go.Scatter(
                x=running_max.index,
                y=running_max.values,
                mode="lines",
                name="Running Peak",
                line=dict(color="#95A5A6", width=1, dash="dot"),
                opacity=0.7,
                hovertemplate="<b>Date</b>: %{x}<br>"
                + "<b>Peak NAV</b>: %{y:.2f}<br>"
                + "<extra></extra>",
            ),
            row=1,
            col=1,
        )

        # 2. 언더워터 면적 (빨간색) - 전고점과 NAV 사이 면적
        fig.add_trace(
            go.Scatter(
                x=list(nav_data.index) + list(nav_data.index[::-1]),
                y=list(running_max.values) + list(nav_data.values[::-1]),
                fill="toself",
                fillcolor="rgba(231, 76, 60, 0.3)",
                line=dict(color="rgba(231, 76, 60, 0)"),
                name="Underwater Area",
                showlegend=True,
                hoverinfo="skip",
                opacity=0.3,
            ),
            row=1,
            col=1,
        )

        # 3. NAV 라인 (파란색) - 맨 위에 표시
        fig.add_trace(
            go.Scatter(
                x=nav_data.index,
                y=nav_data.values,
                mode="lines",
                name="NAV",
                line=dict(color="#2E86C1", width=2),
                hovertemplate="<b>Date</b>: %{x}<br>"
                + "<b>NAV</b>: %{y:.2f}<br>"
                + "<b>Drawdown</b>: %{customdata:.2f}%<br>"
                + "<extra></extra>",
                customdata=drawdown.values,
            ),
            row=1,
            col=1,
        )

        # 2. Daily Turnover Volume Bar 차트
        fig.add_trace(
            go.Bar(
                x=turnover_data.index,
                y=[float(v) * 100 for v in turnover_data.values],
                name="Daily Turnover",
                marker_color="#3498DB",
                opacity=0.8,
                marker_line=dict(color="#2980B9", width=0.5),
                hovertemplate="<b>Date</b>: %{x}<br>"
                + "<b>Turnover</b>: %{y:.1f}%<br>"
                + "<extra></extra>",
            ),
            row=2,
            col=1,
        )

        # 레이아웃 업데이트
        fig.update_layout(
            height=900,
            template="plotly_white",
            hovermode="x unified",
            showlegend=True,
            margin=dict(l=50, r=50, t=80, b=50),
        )

        # 축 설정
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#E5E5E5")
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#E5E5E5")

        # Y축 제목 설정
        fig.update_yaxes(title_text="NAV", row=1, col=1)
        fig.update_yaxes(title_text="Daily Turnover (%)", row=2, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=1)

        return fig

    def create_enhanced_stats_table(self) -> go.Figure:
        """향상된 통계 테이블을 생성합니다."""
        try:
            stats = self.statistics.copy()
            nav_data = self.summary.nav

            # 추가 통계 계산
            if not nav_data.empty:
                drawdown = self._calculate_drawdown(nav_data)

                # 기존 통계에 추가 정보 포함 (Max Drawdown은 이미 있으므로 제외)
                additional_stats = pd.Series(
                    {
                        "Current Drawdown (%)": f"{drawdown.iloc[-1]:.2f}%",
                        "NAV Start": f"{nav_data.iloc[0]:.2f}",
                        "NAV End": f"{nav_data.iloc[-1]:.2f}",
                    }
                )

                stats = pd.concat([stats, additional_stats])

            # 한 줄 테이블로 구성
            fig = go.Figure(
                data=[
                    go.Table(
                        header=dict(
                            values=["<b>Metric</b>", "<b>Value</b>"],
                            fill_color="#34495E",
                            font=dict(color="white", size=14),
                            align="left",
                            height=40,
                        ),
                        cells=dict(
                            values=[
                                stats.index,
                                [
                                    f"{v:.4f}"
                                    if isinstance(v, (int, float)) and abs(v) < 1000
                                    else f"{v:.2f}"
                                    if isinstance(v, (int, float))
                                    else str(v)
                                    for v in stats.values
                                ],
                            ],
                            fill_color=[["#F8F9FA", "#FFFFFF"] * len(stats)],
                            align=["left", "right"],  # 지표명은 왼쪽, 값은 오른쪽 정렬
                            font=dict(size=12),
                            height=30,
                        ),
                        columnwidth=[0.6, 0.4],  # 열 너비 비율 조정
                    )
                ]
            )

            fig.update_layout(
                title="<b>Performance Statistics</b>",
                height=400,
                margin=dict(l=10, r=10, t=80, b=50),  # 좌우 여백 최소화
                template="plotly_white",
            )

            return fig

        except Exception as e:
            # 에러 발생 시 기본 테이블 반환
            fig = go.Figure()
            fig.add_annotation(
                text=f"Statistics not available: {str(e)}",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14),
            )
            fig.update_layout(title="<b>Performance Statistics</b>", height=200)
            return fig

    def make_report_figure(self) -> go.Figure:
        """2x2 리포트 레이아웃 Figure 생성 (NAV, Turnover, 통계 테이블)"""
        performance_fig = self.create_comprehensive_performance_chart()
        stats_fig = self.create_enhanced_stats_table()

        fig = make_subplots(
            rows=2,
            cols=2,
            specs=[
                [
                    {"type": "xy"},
                    {"type": "table", "rowspan": 2},
                ],
                [{"type": "xy"}, None],
            ],
            subplot_titles=[
                "Portfolio NAV Performance",
                "Performance Statistics",
                "Daily Portfolio Turnover (%)",
            ],
            horizontal_spacing=0.08,
            vertical_spacing=0.12,
            column_widths=[0.68, 0.32],
            row_heights=[0.65, 0.35],
        )

        fig.update_annotations(font_size=14, font_family="Arial", font_color="#2C3E50")

        traces = list(performance_fig.data)
        for i, trace in enumerate(traces):
            if i < 3:
                fig.add_trace(trace, row=1, col=1)
        if len(traces) > 3:
            fig.add_trace(traces[3], row=2, col=1)
        for trace in stats_fig.data:
            fig.add_trace(trace, row=1, col=2)

        fig.update_layout(
            height=800,
            showlegend=True,
            template="plotly_white",
            margin=dict(l=60, r=20, t=120, b=60),
            title=dict(
                text="<b>REPORT</b>",
                font=dict(size=18, family="Arial"),
                x=0.5,
                y=0.97,
            ),
            legend=dict(
                orientation="h",
                x=0.5,
                y=1.05,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1,
                font=dict(size=11),
                xanchor="center",
                yanchor="bottom",
            ),
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#E5E5E5")
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#E5E5E5")
        fig.update_yaxes(title_text="NAV", row=1, col=1)
        fig.update_yaxes(title_text="Daily Turnover (%)", row=2, col=1)
        return fig

    def show(self, browser: bool = False, filename: Optional[str] = None) -> go.Figure:
        fig = self.make_report_figure()
        if browser:
            html_filename = filename or "backtest_report.html"
            pyo.plot(fig, filename=html_filename, auto_open=False)
            import webbrowser

            webbrowser.open(html_filename)
        else:
            fig.show()

        return fig

    def show_in_browser(self, filename: Optional[str] = None) -> None:
        """리포트를 브라우저에서 엽니다.

        Args:
            filename: HTML 파일명 (기본값: backtest_report.html)
        """
        self.show(browser=True, filename=filename)

    def __call__(self) -> Optional[str]:
        self.show()

    def to_qore(self, qore_client, folder_id: str, file_name: str = "") -> dict:
        if not file_name:
            file_name = (
                # f"backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                "backtest_report.html"
            )

        html_str = self.make_report_figure().to_html().encode("utf-8")
        buffer = io.BytesIO(html_str)

        response = qore_client.put_file(
            file_content=buffer,
            file_name=file_name,
            folder_id=folder_id,
        )

        return qore_client.get_file_url(file_id=response["id"])
