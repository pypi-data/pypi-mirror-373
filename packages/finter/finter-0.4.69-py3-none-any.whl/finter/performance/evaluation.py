from datetime import datetime

import pandas as pd

from finter.data import DB, ModelData, Symbol
from finter.utils.func_utils import module_exists


def revise_cum_ret(cum_ret, interest):
    """
    Adjusts cumulative returns based on compounding interest or simple cumulative difference.
    Args:
        cum_ret (pd.Series): Cumulative return data.
        interest (bool): If True, adjusts for compounding interest; otherwise, calculates simple difference.
    Returns:
        pd.Series: Adjusted cumulative return data.
    """
    if interest:
        cum_ret += 1
        cum_ret /= cum_ret.iloc[0]
        cum_ret -= 1
    else:
        cum_ret -= cum_ret.iloc[0]
    return cum_ret


def revise_index(bench, interest):
    """
    Adjusts index data for benchmark based on compounding interest or simple cumulative difference.
    Args:
        bench (pd.Series): Benchmark index data.
        interest (bool): If True, adjusts for compounding interest; otherwise, calculates cumulative sum of changes.
    Returns:
        pd.Series: Adjusted index data.
    """
    if interest:
        bench = bench / bench.iloc[0] - 1
    else:
        bench = bench.pct_change().cumsum()
    return bench


def get_bench_cm(bench):
    """
    Determines the content management path for a given benchmark.
    Args:
        bench (str): Name or identifier of the benchmark.
    Returns:
        tuple: (content management path, boolean indicating if the benchmark is a direct model)
    Raises:
        ValueError: If the benchmark is not recognized or supported.
    """

    is_bm_model = False
    upper_bench = bench.upper()
    if upper_bench in [
        "CSI300",
        "DAX",
        "DJIA",
        "HANGSENG",
        "KOSDAQ",
        "KOSPI",
        "KOSPI200",
        "KOSPI_LARGECAP",
        "KOSPI_MIDCAP",
        "KOSPI_SMALLCAP",
        "MSCI_US_REIT",
        "NASDAQ100",
        "NASDAQ_COMPOSITE",
        "S&P500",
        "S&P_GSCI",
        "S&P_GSCI_CRUDE",
        "S&P_GSCI_PM",
        "STOXX50",
        "STOXX600",
        "US_DOLLAR",
        "VIX",
    ]:
        bench_cm = "content.factset.api.price_volume.world-index-price_close.1d"
    elif upper_bench in [
        "CANADA_S_P_TSX",
        "DOWJONES_INDUSTRIAL",
        "EURO_STOXX_50",
        "FTSE_100_INDEX",
        "HANG_SENG_CHINA_ENTERPRISES_INDEX",
        "HANG_SENG_INDEX",
        "HO_CHI_MINH_STOCK_INDEX",
        "KOREA_KOSPI",
        "NASDAQ_100",
        "NASDAQ_COMPOSITE",
        "NIKKEI_225_INDEX",
        "PHLX_SEMICONDUCTOR_S",
        "RUSSELL_2000",
        "S&P_500",
        "SHANGHAI_COMPOSITE_INDEX",
        "US_DOLLAR_INDEX",
    ]:
        bench_cm = "content.handa.dataguide.index.oversea-close_idx.1d"
    elif upper_bench in ["MSCI ACWI"]:
        bench_cm = "content.msci.crawl.index.us-msci_acwi.1d"
    elif upper_bench in ["JCI", "IMUS"]:
        bench_cm = "content.bloomberg.api.index.px_last.1d"
    elif "." in bench:
        bench_cm = bench
        is_bm_model = True
    else:
        raise ValueError(
            "Not supported benchmark! If you want to add it, please contact maintainer"
        )
    return bench_cm, is_bm_model


def plot_with_plotly(data, model_name):
    """
    Plots time series data using Plotly with interactive controls.
    Args:
        data (dict): Dictionary where keys are series names and values are Pandas Series of data.
        model_name (str): Name of the model to be highlighted in the plot.
    """
    import plotly.graph_objects as go

    fig = go.Figure()
    for series_name, series_data in data.items():
        if series_name == model_name:
            line_width = 2
        else:
            line_width = 1
        fig.add_trace(
            go.Scatter(
                x=series_data.index,
                y=series_data,
                mode="lines",
                name=series_name.split(".")[-1],
                line=dict(width=line_width),
            )
        )
    fig.add_hline(y=0, line_dash="dash", line_color="grey")
    fig.update_layout(
        title=f"Comparison {model_name.split('.')[-1]} with benchmark{'s' if len(data.keys()) > 1 else ''}",
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all", label="All"),
                    ]
                )
            ),
            rangeslider=dict(visible=True),
            type="date",
        ),
        yaxis=dict(title="Return", fixedrange=False),
        legend=dict(x=1.01, y=0.5, xanchor="left", yanchor="middle"),
        width=1000,
    )
    fig.show()


def plot_with_matplotlib(data, model_name):
    """
    Plots time series data using Matplotlib. This function emphasizes the model series by using a thicker line.

    Args:
        data (dict): Dictionary where keys are series names and values are Pandas Series of data.
        model_name (str): Name of the model to be highlighted in the plot.
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 5))
    for series_name, series_data in data.items():
        if series_name == model_name:
            line_width = 2
        else:
            line_width = 1
        plt.plot(
            series_data.index,
            series_data,
            label=series_name.split(".")[-1],
            linewidth=line_width,
        )
    plt.axhline(0, color="grey", linestyle="--")
    plt.title(
        f"Comparison {model_name.split('.')[-1]} with benchmark{'s' if len(data.keys()) > 1 else ''}"
    )
    plt.legend(loc="upper left")
    plt.xlabel("Date")
    plt.ylabel("Return")
    plt.grid(True)
    plt.show()


class Evaluator:
    @staticmethod
    def top_n_assets(position, n, start=None, end=None, universe=0):
        """
        Retrieves the top n assets based on returns within a specified time frame.
        Args:
            position (str or DataFrame): The position data source or DataFrame.
            n (int): The number of top assets to retrieve.
            start (int, optional): The start date in YYYYMMDD format.
            end (int, optional): The end date in YYYYMMDD format.
            universe (int): Indicates the universe from which to pull data.
        Returns:
            DataFrame: The top n assets sorted by their returns.
        Raises:
            ValueError: If the input parameters are not as expected.
        """
        if not isinstance(position, (str, pd.DataFrame)):
            raise ValueError(
                "The 'position' parameter must be either a string or a pandas DataFrame."
            )

        # Load and preprocess position data
        if isinstance(position, str):
            model_info = position.split(".")
            position = ModelData.load(position)
        if isinstance(position.columns[0], str) and not model_info[2] == "compustat":
            position.columns = position.columns.astype(int)

        position = position.loc[:, abs(position).sum() != 0]
        start, end = Evaluator._parse_edge_dates(start, end)
        position = position.loc[start:end]
        position = position.shift(1)

        # Load price and adjust factor
        raw, adj = Evaluator._load_adjusted_prices(position.columns, model_info)
        raw, adj = raw.loc[start:end], adj.loc[start:end]
        sum_chg, top_n_indices = Evaluator._calculate_cumsum_n_indicies(
            position, n, raw, adj
        )

        if model_info[1] == "krx" and model_info[3] == "future_0":
            mapping = ModelData.load(
                "content.krx.quantize.universe.equity_futures_entity_id_to_underlying_stock_ccid.1d"
            )
            mapping = mapping.mode()
            mapping = mapping.astype(int)
            ccid_dict = mapping.iloc[0][top_n_indices].to_dict()
            ccid_dict = {str(v): str(k) for k, v in ccid_dict.items()}
            ret_dict = sum_chg[top_n_indices].to_dict()
            ret_dict = {str(k): v for k, v in ret_dict.items()}
            top_n_indices = list(ccid_dict.keys())

        # Get entity_name from ccid or entity_id
        if model_info[1] == "krx":
            # Convert symbol IDs to entity names
            mapped = Symbol.convert(
                _from="id", to="entity_name", source=list(top_n_indices)
            )
            if model_info[3] == "future_0":
                return Evaluator._krx_future_mapper(mapped, ccid_dict, ret_dict)
            else:
                return Evaluator._krx_spot_mapper(mapped, sum_chg, False)

        # Make the result DataFrame for us model
        elif model_info[1] == "us":
            if model_info[2] == "compustat":
                return Evaluator._us_spglobal_mapper(sum_chg, top_n_indices)
            elif model_info[2] == "us":
                return Evaluator._us_factset_mapper(sum_chg, top_n_indices)

    @staticmethod
    def bottom_n_assets(position, n, start=None, end=None, universe=0):
        """
        Retrieves the bottom n assets based on returns within a specified time frame.
        Args:
            position (str or DataFrame): The position data source or DataFrame.
            n (int): The number of bottom assets to retrieve.
            start (int, optional): The start date in YYYYMMDD format.
            end (int, optional): The end date in YYYYMMDD format.
            universe (int): Indicates the universe from which to pull data.
        Returns:
            DataFrame: The bottom n assets sorted by their returns.
        Raises:
            ValueError: If the input parameters are not as expected.
        """

        if not isinstance(position, (str, pd.DataFrame)):
            raise ValueError(
                "The 'position' parameter must be either a string or a pandas DataFrame."
            )

        # Load and preprocess position data
        if isinstance(position, str):
            model_info = position.split(".")
            position = ModelData.load(position)
        if isinstance(position.columns[0], str) and not model_info[2] == "compustat":
            position.columns = position.columns.astype(int)

        position = position.loc[:, abs(position).sum() != 0]
        start, end = Evaluator._parse_edge_dates(start, end)
        position = position.loc[start:end]
        position = position.shift(1)

        # Load price and adjust factor
        raw, adj = Evaluator._load_adjusted_prices(position.columns, model_info)
        raw, adj = raw.loc[start:end], adj.loc[start:end]
        sum_chg, bottom_n_indices = Evaluator._calculate_cumsum_n_indicies(
            position, n, raw, adj, True
        )

        if model_info[1] == "krx" and model_info[3] == "future_0":
            mapping = ModelData.load(
                "content.krx.quantize.universe.equity_futures_entity_id_to_underlying_stock_ccid.1d"
            )
            mapping = mapping.mode()
            mapping = mapping.astype(int)
            ccid_dict = mapping.iloc[0][bottom_n_indices].to_dict()
            ccid_dict = {str(v): str(k) for k, v in ccid_dict.items()}
            ret_dict = sum_chg[bottom_n_indices].to_dict()
            ret_dict = {str(k): v for k, v in ret_dict.items()}
            bottom_n_indices = list(ccid_dict.keys())

        # Get entity_name from ccid or entity_id
        if model_info[1] == "krx":
            # Convert symbol IDs to entity names
            mapped = Symbol.convert(
                _from="id", to="entity_name", source=list(bottom_n_indices)
            )
            if model_info[3] == "future_0":
                return Evaluator._krx_future_mapper(mapped, ccid_dict, ret_dict, True)
            else:
                return Evaluator._krx_spot_mapper(mapped, sum_chg, True)

        # Make the result DataFrame for us model
        elif model_info[1] == "us":
            if model_info[2] == "compustat":
                return Evaluator._us_spglobal_mapper(sum_chg, bottom_n_indices, True)
            elif model_info[2] == "us":
                return Evaluator._us_factset_mapper(sum_chg, bottom_n_indices, True)

    @staticmethod
    def compare_with_bm(
        model: str, bms, start=None, end=None, interest=False, interactive=False
    ):
        """
        Compares a model with one or more benchmarks over a specified period using either Plotly or Matplotlib for visualization.

        Args:
            model (str): The model identifier.
            bms (str or list): Benchmark(s) identifiers.
            start (str): Start date for the comparison.
            end (str): End date for the comparison.
            interest (bool): If True, returns are adjusted for compounding interest.
            interactive (bool): If True, uses Plotly for visualization; otherwise, uses Matplotlib.
        Raises:
            ImportError: If the necessary plotting library is not installed.
            ValueError: If the input for benchmarks is not correctly formatted.
        """
        # Ensure necessary libraries are loaded
        if interactive:
            if not module_exists("plotly"):
                raise ImportError(
                    "Plotly is not installed. Install it by running 'pip install plotly'."
                )
        else:
            if not module_exists("matplotlib"):
                raise ImportError(
                    "Matplotlib is not installed. Install it by running 'pip install matplotlib'."
                )

        # Handle single benchmark string input as a list
        if not isinstance(bms, (str, list)):
            raise ValueError("bm should be 'Bench mark's name(str) or a list of it")

        if isinstance(bms, list):
            bms = [
                bm.upper() if "." not in bm else bm for bm in bms
            ]  # Convert all benchmark identifiers to upper case

        benchmarks = {}
        is_bm_models = []
        bm_str = None
        if isinstance(bms, str):
            bm_str = bms
            bms = [bms.upper()] if "." not in bms else [bms]

        # Load benchmark data
        for bm in bms:
            print(bm)
            bench_cm, is_bm_model = get_bench_cm(bm)
            is_bm_models.append(is_bm_model)
            if bm not in benchmarks.keys():
                if is_bm_model:
                    benchmarks[bench_cm] = Evaluator.get_cum_ret(bench_cm, interest)
                else:
                    loaded_data = ModelData.load(bench_cm)
                    loaded_data.columns = loaded_data.columns.str.upper()
                    for key in bms:
                        if key in loaded_data.columns:
                            benchmarks[key] = loaded_data[key]

        # Calculate cumulative returns for the model and parse edge dates
        cum_model_ret = Evaluator.get_cum_ret(model, interest)

        start, end = Evaluator._parse_edge_dates(start, end)
        start_dates = [cum_model_ret.ne(0).idxmax()] + [
            benchmarks[bm].ne(0).idxmax() for bm in bms
        ]
        start = max(start_dates) if start is None else pd.to_datetime(start)
        end = pd.to_datetime(end) if end is not None else None

        cum_model_ret = cum_model_ret.loc[start:end]
        cum_model_ret = revise_cum_ret(cum_model_ret, interest)

        # Prepare data for plotting
        model_name = model.split(".")[-1]
        data = {f"{model_name}": cum_model_ret}
        for i, bm in enumerate(bms):
            bench = benchmarks[bm].loc[start:end]
            if is_bm_models[i]:
                bench = revise_cum_ret(bench, interest)
                bm = bm.split(".")[-1]
            else:
                bench = revise_index(bench, interest)
            data[bm] = bench
            if bm_str:
                spread = cum_model_ret - bench
                data["Spread"] = spread

        # Select plotting function based on 'interactive' flag
        if interactive:
            plot_with_plotly(data, model_name)
        else:
            plot_with_matplotlib(data, model_name)

    @staticmethod
    def _load_adjusted_prices(position_column, model_info):
        """
        Load adjusted prices based on the market and the type of security.
        Args:
            position_column (str): The column from the DataFrame to be adjusted.
            model_info (list): Information about the market and security type.
        Returns:
            tuple: Tuple containing DataFrames for raw and adjusted prices.
        """
        if model_info[1] == "krx":
            if model_info[3] == "future_0":
                raw = ModelData.load(
                    "content.krx.live.price_volume.stock-future_0-price_close.1d"
                )
                adj = ModelData.load(
                    "content.krx.live.cax.stock-future-adjust_factor.1d"
                )
            else:
                raw = ModelData.load("content.fnguide.ftp.price_volume.price_close.1d")
                adj = ModelData.load("content.fnguide.ftp.cax.adjust_factor.1d")
        elif model_info[1] == "us":
            if model_info[2] == "compustat":
                raw = ModelData.load(
                    "content.spglobal.compustat.price_volume.us-all-price_close.1d"
                )
                adj = ModelData.load(
                    "content.spglobal.compustat.cax.us-all-adjust_factor.1d"
                )
            elif model_info[2] == "us":
                if model_info[3] == "etf":
                    raw = ModelData.load(
                        "content.factset.api.price_volume.us-etf-price_close.1d"
                    )
                    adj = ModelData.load(
                        "content.factset.api.cax.us-etf-adjust_factor.1d"
                    )
                elif model_info[3] == "stock":
                    raw = ModelData.load(
                        "content.factset.api.price_volume.us-stock-price_close.1d"
                    )
                    adj = ModelData.load(
                        "content.factset.api.cax.us-stock-adjust_factor.1d"
                    )
        raw = raw[position_column]
        adj = adj[position_column]
        return raw, adj

    @staticmethod
    def _parse_edge_dates(start, end):
        """
        Converts integer dates to formatted string dates.
        Args:
            start (int): Start date in YYYYMMDD format.
            end (int): End date in YYYYMMDD format.
        Returns:
            tuple: Tuple containing formatted string dates.
        """
        if start:
            if isinstance(start, int):
                start = str(start)
                date_object = datetime.strptime(start, "%Y%m%d")
                start = date_object.strftime("%Y-%m-%d")
            else:
                raise ValueError(
                    "The 'start' parameter must be integers in YYYYMMDD format. For example, 20000101."
                )
        if end:
            if isinstance(end, int):
                end = str(end)
                date_object = datetime.strptime(end, "%Y%m%d")
                end = date_object.strftime("%Y-%m-%d")
            else:
                raise ValueError(
                    "The 'end' parameter must be integers in YYYYMMDD format. For example, 20000101."
                )
        return start, end

    @staticmethod
    def _calculate_cumsum_n_indicies(position, n, raw, adj, bottom=False):
        """
        Calculate the cumulative sum of changes and select the top/bottom n indices.
        Args:
            position (DataFrame): Position data for calculating weights.
            n (int): Number of indices to select.
            raw (DataFrame): Raw price data.
            adj (DataFrame): Adjustment factors.
            bottom (bool): Flag to choose bottom n if True, else top n.
        Returns:
            DataFrame: Top or bottom n indices based on the cumulative sum of changes.
        """
        # Calculate daily returns
        chg = (raw * adj).pct_change()

        # Apply position weights
        mask = position / 1e8
        chg *= mask
        chg.fillna(0, inplace=True)

        # Calculate sum of returns and filter only assets with non-zero total position
        sum_chg = chg.sum()

        # Filter only assets with non-zero total position
        valid_assets = position.sum()[position.sum() > 0].index
        sum_chg = sum_chg[sum_chg.index.isin(valid_assets)]

        # Select top n assets
        if bottom:
            n_indices = sum_chg.nsmallest(min(n, len(sum_chg))).index
        else:
            n_indices = sum_chg.nlargest(min(n, len(sum_chg))).index

        return sum_chg, n_indices

    @staticmethod
    def _krx_spot_mapper(mapped, sum_chg, bottom=False):
        """
        Maps and sorts KRX spot data for visualization.
        Args:
            mapped (dict): Mapping from IDs to entity names.
            sum_chg (Series): Cumulative changes for each entity.
            bottom (bool): Sort ascending if True.
        Returns:
            DataFrame: Sorted DataFrame with entity names as indices.
        """
        df = pd.DataFrame(
            {"ret": sum_chg.loc[list(map(int, mapped.keys()))]}
        ).sort_values(by="ret", ascending=bottom)
        df.index = df.index.map(str)
        df["entity_name"] = df.index.astype(int).map(mapped)
        df.set_index("entity_name", inplace=True)
        return df

    @staticmethod
    def _krx_future_mapper(mapped, ccid_dict, ret_dict, bottom=False):
        """
        Maps and sorts KRX future data for visualization.
        Args:
            mapped (dict): Mapping from IDs to entity names.
            ccid_dict (dict): Mapping from future indices to underlying stock CCIDs.
            ret_dict (dict): Cumulative changes for each future index.
            bottom (bool): Sort ascending if True.
        Returns:
            DataFrame: Sorted DataFrame with entity names as indices.
        """
        mapped_reverse = {v: k for k, v in mapped.items()}
        result = pd.DataFrame(
            index=mapped.values(), columns=["ret", "ccid", "entity_id"]
        )
        result["ccid"] = result.index.map(mapped_reverse)
        result["entity_id"] = result["ccid"].astype(int).map(ccid_dict)
        result["ret"] = result["entity_id"].map(ret_dict)
        df = result.sort_values(by="ret", ascending=bottom)
        return df

    @staticmethod
    def _us_spglobal_mapper(sum_chg, indices, bottom=False):
        """
        Maps and sorts S&P Global data for visualization.
        Args:
            sum_chg (Series): Cumulative changes for each index.
            indices (list): List of indices to include.
            bottom (bool): Sort ascending if True.
        Returns:
            DataFrame: Sorted DataFrame with entity names as indices.
        """
        db = DB("spglobal")
        quoted_ids = ",".join(f"'{id_[:6]}'" for id_ in indices)
        mapped = db.query(f"select * from gic_company WHERE gvkey IN ({quoted_ids})")

        ret_df = pd.DataFrame(
            {
                "gvkeyiid": indices.astype(str),
                "ret": [sum_chg[idx].astype(str) for idx in indices],
            }
        )
        ret_df["gvkey"] = ret_df["gvkeyiid"].str[:6]
        mapped["gvkey"] = mapped["gvkey"].astype(str).str.zfill(6)
        df = pd.merge(mapped, ret_df, on="gvkey")[["conm", "ret", "gvkeyiid"]]
        df.rename(columns={"conm": "entity_name"}, inplace=True)
        df.set_index("entity_name", inplace=True)
        df.sort_values("ret", ascending=bottom, inplace=True)
        return df

    @staticmethod
    def _us_factset_mapper(sum_chg, indices, bottom=False):
        """
        Maps and sorts FactSet data for visualization.
        Args:
            sum_chg (Series): Cumulative changes for each index.
            indices (list): List of indices to include.
            bottom (bool): Sort ascending if True.
        Returns:
            DataFrame: Sorted DataFrame with entity names as indices.
        """
        ret_dict = dict(sum_chg[indices])
        mapped_ccid = Symbol.convert(_from="id", to="entity_name", source=list(indices))
        quoted_ids = ",".join(f"'{id_}'" for id_ in list(mapped_ccid.values()))

        db = DB("factset")
        mapper = db.query(
            f"SELECT * FROM sym_v1_sym_entity WHERE factset_entity_id IN ({quoted_ids})"
        )
        mapper = mapper[["factset_entity_id", "entity_proper_name"]]

        tmp_df = pd.DataFrame(
            list(mapped_ccid.items()), columns=["ccid", "factset_entity_id"]
        )
        ret_df = pd.DataFrame(list(ret_dict.items()), columns=["ccid", "ret"]).astype(
            {"ccid": str}
        )

        # Merge the DataFrames to combine all the necessary information
        merged_df = ret_df.merge(tmp_df, on="ccid").merge(
            mapper, on="factset_entity_id"
        )

        # Set the index to 'entity_proper_name' and select the final columns for output
        df = merged_df.set_index("entity_proper_name")[["ret", "ccid"]]
        df.sort_values(by="ret", ascending=bottom, inplace=True)

        return df

    @staticmethod
    def get_cum_ret(model: str, interest=False, raw=False):
        """
        Calculates the cumulative return for a given model.

        Args:
            model (str): Model identifier.
            interest (bool): If True, calculates cumulative returns with compounding interest.

        Returns:
            pd.Series: The cumulative returns for the model.
        """
        model_info = model.split(".")
        position = ModelData.load(model)
        position = position.loc[:, abs(position).sum() != 0]
        if (
            all(isinstance(col, str) for col in position.columns)
            and not model_info[2] == "compustat"
        ):
            position.columns = position.columns.astype(int)
        price, adj = Evaluator._load_adjusted_prices(position.columns, model_info)
        price *= adj
        mask = position.shift(1) / 1e8
        if raw:
            return (price.pct_change() * mask).sum(axis=1)
        if interest:
            cum_ret = (1 + (price.pct_change() * mask).sum(axis=1)).cumprod() - 1
        else:
            cum_ret = (price.pct_change() * mask).sum(axis=1).cumsum()
        return cum_ret
