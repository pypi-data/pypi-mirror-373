import sys
import types

from finter.backtest.simulator import Simulator

v0 = types.ModuleType("v0")
v0.Simulator = Simulator

sys.modules["finter.backtest.v0.main"] = v0
sys.modules["finter.backtest.v0"] = v0

# 먼저 legacy 모듈을 생성하고 등록합니다
legacy = types.ModuleType("legacy")
sys.modules["finter.backtest.main"] = legacy

# 그 다음에 LegacySimulator를 가져옵니다
from finter.backtest.__legacy_support.main import Simulator as LegacySimulator

legacy.Simulator = LegacySimulator
