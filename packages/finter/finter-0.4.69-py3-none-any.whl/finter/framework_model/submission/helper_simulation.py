import json
from enum import Enum

import pandas as pd

from finter.framework_model.simulation import adj_stat_container_helper
from finter.framework_model.submission.config import (
    DefaultBenchmark,
    get_model_info,
    validate_and_get_benchmark_name,
    validate_and_get_model_type_name,
)
from finter.settings import log_section, log_with_traceback, log_with_user_event, logger
from finter.utils.timer import timer


class Simulation:
    """
    A class representing a financial model simulation.

    Attributes:
        model_universe (str): The model universe for the simulation.
        model_type (str): The model type for the simulation.
        position (pd.DataFrame): The position for the simulation.
        benchmark (str or list, optional): The benchmark(s) for the simulation. Defaults to None.

    Methods:
        run(start, end, **kwargs):
            Runs the simulation based on the model's configuration.
    """

    def __init__(self, model_universe, model_type, position, benchmark=None):
        """
        Initializes a Simulation object with the required parameters for running a financial model simulation.

        Args:
            model_universe (str): The model universe for the simulation.
            model_type (str): The model type for the simulation.
            position (pd.DataFrame): The position for the simulation.
            benchmark (str or list, optional): The benchmark(s) for the simulation. Defaults to None.

        Example:
            >>> sim = Simulation(model_universe=universe, model_type=model_type, position=position, benchmark=None)
            >>> model_stat = sim.run(start=20200101, end=20210101)
        """

        self.position = position

        self.model_info = get_model_info(model_universe, model_type)
        self.model_type = validate_and_get_model_type_name(model_type)
        self.benchmark = validate_and_get_benchmark_name(model_universe, benchmark)

        self.model_stat = None

    def run(self, start, end, **kwargs):
        """
        Executes the simulation for the given period using the specified model configuration.

        Args:
            start (int): The start date for the simulation in YYYYMMDD format.
            end (int): The end date for the simulation in YYYYMMDD format.
            **kwargs: Additional keyword arguments to customize the simulation settings.

        Keyword Args:
            volcap_pct (float): Volume cap as a percentage, limiting the amount of shares to be traded.
            decay (float): Decay factor to apply to the model's signals over time.
            cost_list (list[float]): A list of transaction costs associated with trading, expressed in percentage terms.
            slippage (float): Estimated slippage cost per trade, reflecting the impact of market impact.
            return_calc_method (str): Method for calculating returns ('arithmetic' or 'geometric').
            turnover_calc_method (str): Method to calculate turnover during the simulation.
            booksize (float): Total value of the book to be managed in the simulation.
            close (bool): Flag to indicate whether positions should be closed at the end of the simulation.
            adj_dividend (bool): Flag to adjust returns for dividends.

        Returns:
            ModelStat: An object containing the detailed results of the simulation, including performance metrics and statistical analysis.

        Raises:
            Exception: Captures and logs any exceptions during the simulation, providing error details for troubleshooting.
        """
        log_section("Simulation")

        # Determine the return calculation method based on the model type
        if self.model_type.lower() == "alpha":
            return_calc_method = "arithmetic"
        else:
            return_calc_method = "geometric"

        try:
            model_stat = run_simulation(
                self.model_info,
                start,
                end,
                position=self.position,
                return_calc_method=return_calc_method,
                benchmark=self.benchmark,
                **kwargs,
            )
        except Exception as e:
            log_with_user_event(
                "model_simulation_error",
                source="Simulation",
                method="run",
                category="error",
                log_type="error",
                log_message=str(e),
            )
            log_with_traceback(f"Error occurred during simulation run: {e}")
            raise

        log_with_user_event(
            "model_simulation_success",
            source="Simulation",
            method="run",
            category="info",
            log_type="info",
            log_message="Simulation run successfully based on the extracted positions.",
        )
        return model_stat


@timer
def run_simulation(model_info, start, end, **kwargs):
    """
    Runs a simulation based on the given model information and time range, applying additional specified settings.

    This function initializes the simulation with default parameters, which can be overridden by the kwargs argument. It processes the model statistics using the 'adj_stat_container_helper' function, then creates and returns a ModelStat object populated with the simulation results and any additional settings.

    Parameters:
    - model_info: An object containing model configuration information.
    - start (datetime): The start date of the simulation.
    - end (datetime): The end date of the simulation.
    - **kwargs: Optional keyword arguments to specify additional simulation settings. Default values are:
        - volcap_pct: 1 (Volume cap percentage),
        - decay: 1 (Decay factor for the model),
        - cost_list: ["hi_low", "fee_tax"] (List of transaction costs to consider),
        - slippage: 10 (Slippage in the model's transactions),
        - return_calc_method: "arithmetic" (Method for calculating returns),
        - turnover_calc_method: "diff" (Method for calculating turnover),
        - booksize: 1e8 (Size of the book in the simulation),
        - close: True (Whether to close the positions at the end of the simulation),
        - adj_dividend: False (Whether to adjust for dividends).

    Returns:
    - A ModelStat object containing the results of the simulation along with the settings used for the simulation.

    The 'kwargs' argument allows for flexible configuration of the simulation, accommodating various scenarios and model behaviors.
    """
    defaults = {
        "volcap_pct": 1,
        "decay": 1,
        "cost_list": ["hi_low", "fee_tax"],
        "slippage": 10,
        "return_calc_method": "arithmetic",
        "turnover_calc_method": "diff",
        "booksize": 1e8,
        "close": True,
        "adj_dividend": False,
    }

    for key, value in defaults.items():
        kwargs.setdefault(key, value)

    benchmark = kwargs.pop("benchmark", None)

    model_stat = adj_stat_container_helper(
        model_info=model_info, start=start, end=end, **kwargs
    )

    kwargs.pop("position", None)

    return ModelStat(model_stat, benchmark, **kwargs)


class ModelStat:
    """
    A class that manages the extraction and manipulation of statistical data for financial models.

    This class provides methods to access various statistics at different frequencies and integrates benchmark comparisons if provided.

    Attributes:
        model_stat (dict): A dictionary containing statistical data for the model.
        benchmark (str or list): An optional benchmark(s) identifier for comparison.
        kwargs (dict): Additional keyword arguments that may affect computations, such as 'return_calc_method'.

    Methods:
        extract_statistics(frequency): Returns a DataFrame of statistics based on the specified frequency.
        whole_period, yearly, half_yearly, quarterly, monthly, weekly, daily: Properties that return statistics for their respective frequencies.
        cummulative_return: Calculates and returns the cumulative returns adjusted for the benchmark, if applicable.
        raw_return: Calculates and returns the raw returns based on the cumulative returns.

    Raises:
        ValueError: If an invalid frequency is specified for statistics extraction.
    """

    class Frequency(Enum):
        WholePeriod = "WholePeriod"
        Yearly = "Yearly"
        HalfYearly = "HalfYearly"
        Quarterly = "Quarterly"
        Monthly = "Monthly"
        Weekly = "Weekly"
        Daily = "Daily"

    def __init__(self, model_stat, benchmark, **kwargs):
        """
        Initializes the ModelStat object with statistical data, an optional benchmark, and other keyword arguments.

        Parameters:
            model_stat (dict): Dictionary containing the statistical data for the model.
            benchmark (str or list): The benchmark identifier for comparison purposes. Set to None if no benchmark is used.
            **kwargs: Additional keyword arguments that can influence the processing of returns and other calculations.

        Note:
            If benchmark is not None and is provided, the benchmark data will be fetched and stored for comparison purposes.
        """
        self.model_stat = model_stat
        self.benchmark = benchmark
        self.kwargs = kwargs

        if benchmark is not None:
            self.bm = DefaultBenchmark().get_benchmark_df(self.benchmark)

    def extract_statistics(self, frequency):
        """
        Extracts statistical data for a specified frequency and returns it as a pandas DataFrame.

        Parameters:
            frequency (str): The frequency of the statistical data to be extracted. Valid options are 'WholePeriod', 'Yearly', 'HalfYearly', 'Quarterly', 'Monthly', 'Weekly', 'Daily'.

        Returns:
            pandas.DataFrame: A DataFrame containing the statistical data for the specified frequency.

        Raises:
            ValueError: If the specified frequency is not one of the valid options listed in the Frequency enum.
        """
        try:
            frequency = self.Frequency(frequency).value
        except ValueError:
            valid_options = ", ".join(
                [f"'{option.value}'" for option in self.Frequency]
            )
            raise ValueError(
                f"Frequency must be one of the following: {valid_options}. Please choose one."
            ) from None

        parsed_json = json.loads(self.model_stat["statistics"][frequency])

        df = pd.DataFrame(
            parsed_json["data"],
            columns=parsed_json["columns"],
            index=pd.to_datetime(parsed_json["index"]),
        )
        df.index = pd.to_datetime(df.index).date

        return df

    @property
    def whole_period(self):
        return self.extract_statistics("WholePeriod")

    @property
    def yearly(self):
        return self.extract_statistics("Yearly")

    @property
    def half_yearly(self):
        return self.extract_statistics("HalfYearly")

    @property
    def quarterly(self):
        return self.extract_statistics("Quarterly")

    @property
    def monthly(self):
        return self.extract_statistics("Monthly")

    @property
    def weekly(self):
        return self.extract_statistics("Weekly")

    @property
    def daily(self):
        return self.extract_statistics("Daily")

    @property
    def cummulative_return(self):
        """
        Calculates and returns the cumulative returns adjusted for the benchmark, if applicable.

        Returns:
            pandas.Series: A Series containing the cumulative returns, adjusted for the benchmark if provided.
        """
        cum_ret = pd.read_json(self.model_stat["cum_ret"], orient="records").set_index(
            "index"
        )["data"]
        cum_ret.index = pd.to_datetime(cum_ret.index).date

        if self.benchmark is False:
            cum_ret.columns = ["model"]
        else:
            logger.info(f"benchmark: {self.benchmark if self.benchmark else 'default'}")

            for bench in self.bm.keys():  # take multiple benchmarks
                bm = self.bm[bench].reindex(cum_ret.index)
                bm = bm.fillna(0)
                if self.kwargs["return_calc_method"] == "arithmetic":
                    bm = bm.cumsum()
                else:
                    bm = (1 + bm).cumprod() - 1
                cum_ret = pd.concat([cum_ret, bm], axis=1)
            cum_ret.columns = ["model"] + list(self.bm.keys())

        return cum_ret

    @property
    def raw_return(self):
        """
        Calculates and returns the raw returns based on the cumulative returns.

        Returns:
            pandas.Series: A Series containing the raw returns.
        """
        if self.kwargs["return_calc_method"] == "arithmetic":
            raw_ret = self.cummulative_return.diff()
        else:
            raw_ret = (1 + self.cummulative_return).pct_change(fill_method=None)
        return raw_ret
