import warnings

from typing_extensions import Literal

from finter.backtest.simulator import Simulator as SimulatorV0
from finter.data.data_handler.main import DataHandler


class Simulator:
    def __init__(self, start, end, data_handler: DataHandler = None):
        warnings.filterwarnings(
            "always", message="This version of Simulator is deprecated.*"
        )
        warnings.warn(
            "This version of Simulator is deprecated. Please use 'from finter.backtest.v0 import Simulator' instead.",
            DeprecationWarning,
        )
        self.data_handler = data_handler

    def run(
        self,
        universe,
        position,
        initial_cash=None,
        buy_fee_tax=None,
        sell_fee_tax=None,
        slippage=None,
        adj_dividend=None,
        auto_rebalance=True,
        debug=False,
        resample_period: Literal[None, "W", "M", "Q"] = None,
    ):
        kwargs = {
            k: v
            for k, v in {
                "position": position,
                "initial_cash": initial_cash,
                "buy_fee_tax": buy_fee_tax,
                "sell_fee_tax": sell_fee_tax,
                "slippage": slippage,
                "resample_period": resample_period,
                "debug": debug,
                "rebalancing_method": "auto" if auto_rebalance else "by_position",
                "drip": "reinvest" if adj_dividend else None,
            }.items()
            if v is not None
        }

        if universe == "kr_stock":
            return self.run_simulation_kr(**kwargs)
        elif universe == "id_stock":
            return self.run_simulation_id(**kwargs)
        elif universe == "id_fund":
            return self.run_simulation_id_fund(**kwargs)
        elif universe == "us_stock":
            return self.run_simulation_us_stock(**kwargs)
        elif universe == "us_etf":
            return self.run_simulation_us_etf(**kwargs)
        elif universe == "vn_stock":
            return self.run_simulation_vn(**kwargs)
        elif universe == "btcusdt_spot_binance":
            return self.run_simulation_crypto_spot(**kwargs)
        elif universe == "us_future":
            return self.run_simulation_us_future(**kwargs)
        else:
            raise ValueError(f"Unsupported universe: {universe}")

    def run_simulation_kr(self, **kwargs):
        simulator = SimulatorV0("kr_stock")
        res = simulator.run(**kwargs)
        return res

    def run_simulation_us_stock(self, **kwargs):
        simulator = SimulatorV0("us_stock")
        res = simulator.run(**kwargs)
        return res

    def run_simulation_us_etf(self, **kwargs):
        simulator = SimulatorV0("us_etf")
        res = simulator.run(**kwargs)
        return res

    def run_simulation_id(self, **kwargs):
        simulator = SimulatorV0("id_stock")
        res = simulator.run(**kwargs)
        return res

    def run_simulation_id_fund(self, **kwargs):
        simulator = SimulatorV0("id_fund")
        res = simulator.run(**kwargs)
        return res

    def run_simulation_vn(self, **kwargs):
        simulator = SimulatorV0("vn_stock")
        res = simulator.run(**kwargs)
        return res

    def run_simulation_crypto_spot(self, **kwargs):
        simulator = SimulatorV0("btcusdt_spot_binance")
        res = simulator.run(**kwargs)
        return res

    def run_simulation_us_future(self, **kwargs):
        simulator = SimulatorV0("us_future")
        res = simulator.run(**kwargs)
        return res


if __name__ == "__main__":
    s = Simulator(20150101, 20240823)

    res = s.run(
        "id_fund",
        position=s.data_handler.load("content.bareksa.ftp.price_volume.nav.1d"),
    )
    res.summary
