"""
Use Example:

from finter.modeling.meta_portfolios.equal_weight_portfolio import (
    EqualWeightMetaPortfolio,
)
from finter.framework_model.submission.config import ModelUniverseConfig

Portfolio = EqualWeightMetaPortfolio.create(
    EqualWeightMetaPortfolio.Parameters(
        universe=ModelUniverseConfig.KR_STOCK,
        alpha_list=[
            "krx.krx.stock.soobeom33_qt.low_vol_factor_simple",
            "krx.krx.stock.ldh0127_qt.sample_univ_1",
        ],
    )
)

- pf = Portfolio()
  start, end = (20190929, 20231230)
  position = pf.get(start, end)
- Portfolio.submit("my_model")
- Portfolio.get_source_code()

"""

from typing import Dict
from functools import reduce

import pandas as pd
import numpy as np

from finter.modeling.metamodel.base import BaseMetaPortfolio


class EqualWeightMetaPortfolio(BaseMetaPortfolio):

    class Parameters(BaseMetaPortfolio.Parameters): ...
