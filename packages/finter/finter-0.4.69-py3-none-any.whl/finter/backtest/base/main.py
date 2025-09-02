from finter.backtest.base.variables import InputVars, SimulationVariables
from finter.backtest.config.config import SimulatorConfig
from finter.backtest.result.main import BacktestResult
from finter.settings import log_warning


class BaseBacktestor:
    def __init__(
        self,
        config: SimulatorConfig,
        input_vars: InputVars,
        results: list[str] = [],
    ):
        self.results = results

        self.frame = config.frame
        self.trade = config.trade
        self.execution = config.execution
        self.optional = config.optional
        self.cost = config.cost

        self.vars = SimulationVariables(input_vars, self.frame.shape)
        self.vars.initialize(self.trade.initial_cash)

        self._results = BacktestResult(self)

    def _clear_all_variables(self, clear_attrs=True):
        preserved = {}
        for attr_name in self.results:
            if hasattr(self._results, attr_name):
                preserved[attr_name] = getattr(self._results, attr_name)
            else:
                log_warning(
                    f"Attribute '{attr_name}' in results not found in self._results"
                )

        if clear_attrs:
            for attr in list(self.__dict__.keys()):
                delattr(self, attr)

        for attr_name, attr_value in preserved.items():
            if hasattr(self, attr_name):
                log_warning(
                    f"Attribute '{attr_name}' already exists in self, skipping overwrite"
                )
            else:
                setattr(self, attr_name, attr_value)

    def run(self):
        raise NotImplementedError

    def run_step(self, i: int):
        raise NotImplementedError
