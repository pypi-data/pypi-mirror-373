import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_explore_stats(
    df: pd.DataFrame,
    title: str = "Explore One-Way Statistics",
    subtitle: str | None = None,
):
    """
    Plot statistics from explore_one_way function across percentiles.

    Args:
        df: DataFrame with percentiles as columns and statistics as rows
        title: Title for the entire figure
        subtitle: Subtitle showing control variables configuration
    """
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))

    # Add title and subtitle
    if subtitle:
        fig.suptitle(title, fontsize=16, y=1.04)
        fig.text(
            0.5, 1.01, subtitle, ha="center", fontsize=12, color="gray", style="italic"
        )
    else:
        fig.suptitle(title, fontsize=16, y=1.02)

    params = df.columns

    # 1. Sharpe Ratio - Line plot with fill
    ax = axes[0, 0]
    ax.plot(params, df.loc["sharpe_ratio"], marker="o", linewidth=2, markersize=4)
    ax.axhline(y=0, color="r", linestyle="--", alpha=0.3)
    ax.fill_between(
        params,
        df.loc["sharpe_ratio"],
        0,
        where=(df.loc["sharpe_ratio"] > 0),
        alpha=0.3,
        color="green",
        label="Positive",
    )
    ax.fill_between(
        params,
        df.loc["sharpe_ratio"],
        0,
        where=(df.loc["sharpe_ratio"] <= 0),
        alpha=0.3,
        color="red",
        label="Negative",
    )
    ax.set_title("Sharpe Ratio", fontsize=12, fontweight="bold")
    ax.set_xlabel(f"{params.name}")
    ax.set_ylabel("Sharpe Ratio")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")

    # 2. K-Ratio - Line plot
    ax = axes[0, 1]
    ax.plot(
        params,
        df.loc["k_ratio"],
        marker="s",
        linewidth=2,
        markersize=4,
        color="orange",
    )
    ax.axhline(y=0, color="r", linestyle="--", alpha=0.3)
    ax.set_title("K-Ratio", fontsize=12, fontweight="bold")
    ax.set_xlabel(f"{params.name}")
    ax.set_ylabel("K-Ratio")
    ax.grid(True, alpha=0.3)

    # 3. Return per Turnover (bp) - Bar chart
    ax = axes[1, 0]
    values = df.loc["return_per_turnover_bp"]
    colors = ["green" if values.iloc[i] > 0 else "red" for i in range(len(values))]
    ax.bar(
        params,
        df.loc["return_per_turnover_bp"],
        color=colors,
        alpha=0.7,
        width=0.8,
    )
    ax.axhline(y=0, color="black", linestyle="-", alpha=0.5)
    ax.set_title("Return per Turnover (bp)", fontsize=12, fontweight="bold")
    ax.set_xlabel(f"{params.name}")
    ax.set_ylabel("Basis Points")
    ax.grid(True, alpha=0.3, axis="y")

    # 4. Maximum Drawdown - Line plot (inverted for visualization)
    ax = axes[1, 1]
    ax.plot(
        params,
        df.loc["mdd_pct"],
        marker="^",
        linewidth=2,
        markersize=4,
        color="darkred",
    )
    ax.fill_between(params, df.loc["mdd_pct"], alpha=0.3, color="red")
    ax.set_title("Maximum Drawdown (%)", fontsize=12, fontweight="bold")
    ax.set_xlabel(f"{params.name}")
    ax.set_ylabel("MDD (%)")
    ax.grid(True, alpha=0.3)

    # 5. Hit Ratio - Line plot with reference line
    ax = axes[2, 0]
    ax.plot(
        params,
        df.loc["hit_ratio_pct"],
        marker="o",
        linewidth=2,
        markersize=4,
        color="blue",
    )
    ax.axhline(y=50, color="green", linestyle="--", alpha=0.5, label="50% Reference")
    ax.fill_between(
        params,
        df.loc["hit_ratio_pct"],
        50,
        where=(df.loc["hit_ratio_pct"] > 50),
        alpha=0.3,
        color="green",
    )
    ax.fill_between(
        params,
        df.loc["hit_ratio_pct"],
        50,
        where=(df.loc["hit_ratio_pct"] <= 50),
        alpha=0.3,
        color="red",
    )
    ax.set_title("Hit Ratio (%)", fontsize=12, fontweight="bold")
    ax.set_xlabel(f"{params.name}")
    ax.set_ylabel("Hit Ratio (%)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")

    # 6. Holding Count - Bar chart with log scale option
    ax = axes[2, 1]
    ax.bar(params, df.loc["holding_count"], color="purple", alpha=0.7, width=0.8)
    ax.set_title("Holding Count", fontsize=12, fontweight="bold")
    ax.set_xlabel(f"{params.name}")
    ax.set_ylabel("Count")
    ax.grid(True, alpha=0.3, axis="y")

    # Adjust layout
    plt.tight_layout()

    return fig


def quick_plot_stats(
    df: pd.DataFrame,
    variable_name: str = "Variable",
    control_params: dict | None = None,
):
    """
    Quick plotting function that can be imported and used directly.

    Args:
        df: DataFrame with percentiles/values as columns and stats as rows
        variable_name: Name of the variable being analyzed
        control_params: Dictionary of control parameters and their values

    Example:
        from finter.framework_model.signal.plot import quick_plot_stats
        quick_plot_stats(stats, "my_variable", {"param1": 10, "param2": 0.5})
    """

    # Create subtitle from control parameters
    subtitle = None
    if control_params:
        subtitle = "Control variables: " + ", ".join(
            [f"{k}={v}" for k, v in control_params.items()]
        )

    # Plot and show
    fig = plot_explore_stats(df, f"Explore Statistics - {variable_name}", subtitle)
    plt.show()

    return fig


def plot_explore_two_way_3d(
    df: pd.DataFrame,
    key_names: list[str],
    metric: str = "sharpe_ratio",
    control_params: dict | None = None,
):
    """
    Plot 3D surface visualization for two-way parameter exploration.

    Args:
        df: DataFrame with MultiIndex columns (two parameters) and statistics as rows
        key_names: List of two parameter names being explored
        metric: The metric to plot (default: "sharpe_ratio")
        control_params: Dictionary of control parameters and their values
    """
    fig = plt.figure(figsize=(16, 12))

    # Create subtitle from control parameters
    subtitle = None
    if control_params:
        subtitle = "Control variables: " + ", ".join(
            [f"{k}={v}" for k, v in control_params.items()]
        )

    # Add title
    title = f"Two-Way Parameter Exploration: {key_names[0]} vs {key_names[1]}"
    if subtitle:
        fig.suptitle(title, fontsize=16, y=0.98)
        fig.text(
            0.5, 0.95, subtitle, ha="center", fontsize=12, color="gray", style="italic"
        )
    else:
        fig.suptitle(title, fontsize=16, y=0.96)

    # Get unique values for each parameter
    param1_values = sorted(df.columns.get_level_values(0).unique())
    param2_values = sorted(df.columns.get_level_values(1).unique())

    # Create meshgrid
    X, Y = np.meshgrid(param1_values, param2_values)

    # Prepare data for different metrics
    metrics_to_plot = [
        "sharpe_ratio",
        "k_ratio",
        "return_per_turnover_bp",
        "mdd_pct",
        "hit_ratio_pct",
        "holding_count",
    ]

    for idx, metric in enumerate(metrics_to_plot, 1):
        if metric not in df.index:
            continue

        ax = fig.add_subplot(2, 3, idx, projection="3d")

        # Extract Z values - use float dtype for proper NaN handling
        Z = np.zeros_like(X, dtype=float)
        for i, p1 in enumerate(param1_values):
            for j, p2 in enumerate(param2_values):
                if (p1, p2) in df.columns:
                    Z[j, i] = df.loc[metric, (p1, p2)]
                else:
                    Z[j, i] = np.nan

        # Create surface plot with colormap
        if metric == "sharpe_ratio":
            surf = ax.plot_surface(
                X, Y, Z, cmap="RdYlGn", alpha=0.8, vmin=-1, vmax=2, edgecolor="none"
            )
        elif metric == "k_ratio":
            surf = ax.plot_surface(
                X, Y, Z, cmap="coolwarm", alpha=0.8, edgecolor="none"
            )
        elif metric == "return_per_turnover_bp":
            surf = ax.plot_surface(X, Y, Z, cmap="RdBu", alpha=0.8, edgecolor="none")
        elif metric == "mdd_pct":
            surf = ax.plot_surface(X, Y, Z, cmap="Reds_r", alpha=0.8, edgecolor="none")
        elif metric == "hit_ratio_pct":
            surf = ax.plot_surface(
                X, Y, Z, cmap="BrBG", alpha=0.8, vmin=40, vmax=60, edgecolor="none"
            )
        else:  # holding_count
            surf = ax.plot_surface(X, Y, Z, cmap="viridis", alpha=0.8, edgecolor="none")

        # Add wireframe for better depth perception
        ax.plot_wireframe(X, Y, Z, color="gray", alpha=0.2, linewidth=0.5)

        # Labels and title
        ax.set_xlabel(key_names[0], fontsize=9)
        ax.set_ylabel(key_names[1], fontsize=9)
        ax.set_zlabel(metric.replace("_", " ").title(), fontsize=9)
        ax.set_title(metric.replace("_", " ").title(), fontsize=10, fontweight="bold")

        # Add colorbar
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)

        # Adjust viewing angle for better visualization
        ax.view_init(elev=20, azim=45)

        # Grid
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_two_way_heatmaps(
    df: pd.DataFrame, key_names: list[str], control_params: dict | None = None
):
    """
    Plot heatmaps for two-way parameter exploration.

    Args:
        df: DataFrame with MultiIndex columns (two parameters) and statistics as rows
        key_names: List of two parameter names being explored
        control_params: Dictionary of control parameters and their values
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))

    # Create subtitle from control parameters
    subtitle = None
    if control_params:
        subtitle = "Control variables: " + ", ".join(
            [f"{k}={v}" for k, v in control_params.items()]
        )

    # Add title
    title = f"Two-Way Parameter Exploration Heatmaps: {key_names[0]} vs {key_names[1]}"
    if subtitle:
        fig.suptitle(title, fontsize=16, y=1.02)
        fig.text(
            0.5, 0.99, subtitle, ha="center", fontsize=12, color="gray", style="italic"
        )
    else:
        fig.suptitle(title, fontsize=16, y=1.00)

    metrics = [
        "sharpe_ratio",
        "k_ratio",
        "return_per_turnover_bp",
        "mdd_pct",
        "hit_ratio_pct",
        "holding_count",
    ]

    for idx, metric in enumerate(metrics):
        if metric not in df.index:
            continue

        ax = axes[idx // 3, idx % 3]

        # Pivot data for heatmap
        heatmap_data = df.loc[metric].unstack()

        # Choose colormap based on metric
        if metric == "sharpe_ratio":
            cmap = "RdYlGn"
        elif metric == "mdd_pct":
            cmap = "Reds_r"
        elif metric == "hit_ratio_pct":
            cmap = "BrBG"
        elif metric == "return_per_turnover_bp":
            cmap = "RdBu"
        else:
            cmap = "coolwarm"

        # Create heatmap
        im = ax.imshow(heatmap_data, aspect="auto", cmap=cmap, interpolation="nearest")

        # Set ticks and labels
        ax.set_xticks(range(len(heatmap_data.columns)))
        ax.set_yticks(range(len(heatmap_data.index)))
        ax.set_xticklabels(heatmap_data.columns, rotation=45, ha="right")
        ax.set_yticklabels(heatmap_data.index)

        # Labels and title
        ax.set_xlabel(key_names[1], fontsize=10)
        ax.set_ylabel(key_names[0], fontsize=10)
        ax.set_title(metric.replace("_", " ").title(), fontsize=11, fontweight="bold")

        # Add colorbar
        plt.colorbar(im, ax=ax)

        # Add text annotations for values
        for i in range(len(heatmap_data.index)):
            for j in range(len(heatmap_data.columns)):
                value = heatmap_data.iloc[i, j]
                if not np.isnan(value):
                    text_color = (
                        "white"
                        if abs(value - heatmap_data.mean().mean())
                        > heatmap_data.std().mean()
                        else "black"
                    )
                    ax.text(
                        j,
                        i,
                        f"{value:.2f}",
                        ha="center",
                        va="center",
                        color=text_color,
                        fontsize=8,
                    )

    plt.tight_layout()
    return fig


def quick_plot_two_way(
    df: pd.DataFrame,
    key_names: list[str],
    control_params: dict | None = None,
    plot_type: str = "3d",
):
    """
    Quick plotting function for two-way parameter exploration.

    Args:
        df: DataFrame with MultiIndex columns (two parameters) and stats as rows
        key_names: List of two parameter names being explored
        control_params: Dictionary of control parameters and their values
        plot_type: "3d" for 3D surface plots, "heatmap" for 2D heatmaps, "both" for both

    Example:
        from finter.framework_model.signal.plot import quick_plot_two_way
        quick_plot_two_way(stats, ["param1", "param2"], {"param3": 10}, plot_type="both")
    """
    if plot_type in ["3d", "both"]:
        fig_3d = plot_explore_two_way_3d(df, key_names, control_params=control_params)
        plt.show()

    if plot_type in ["heatmap", "both"]:
        fig_heat = plot_two_way_heatmaps(df, key_names, control_params=control_params)
        plt.show()

    if plot_type == "both":
        return fig_3d, fig_heat
    elif plot_type == "3d":
        return fig_3d
    elif plot_type == "heatmap":
        return fig_heat
