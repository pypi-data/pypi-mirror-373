"""
Use Example:

from finter.modeling.meta_portfolios.equal_weight_portfolio import (
    FixedWeightMetaPortfolio,
)
from finter.framework_model.submission.config import ModelUniverseConfig

Portfolio = FixedWeightMetaPortfolio.create(
    FixedWeightMetaPortfolio.Parameters(
        universe=ModelUniverseConfig.KR_STOCK,
        alpha_set={
            "krx.krx.stock.soobeom33_qt.low_vol_factor_simple",
            "krx.krx.stock.ldh0127_qt.sample_univ_1",
        },
        weights = {
            "krx.krx.stock.soobeom33_qt.low_vol_factor_simple":0.2,
            "krx.krx.stock.ldh0127_qt.sample_univ_1":0.8
        }
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


class FixedWeightMetaPortfolio(BaseMetaPortfolio):
    # No need to declare separately; it can be defined only in Parameters.
    # It is supported for convenience in type checking within the `get` method.
    weights: Dict[str, float] = {}

    class Parameters(BaseMetaPortfolio.Parameters):
        # The sum of weights isassumed to be 1. { "krx.krx.stock.user1.alpha1": 0.3, "krx.krx.stock.user1.alpha2": 0.7}
        weights: Dict[str, float]

    def weight(self, start, end):
        alphas = [
            self.alpha_loader_v2(start, end).get_alpha(alpha)
            for alpha in self.weights.keys()
        ]

        all_indices = None
        for alpha in alphas:
            if all_indices is None:
                all_indices = alpha.index
            else:
                all_indices = all_indices.union(alpha.index)

        all_indices = all_indices.sort_values()
        weight_df = pd.DataFrame(
            {alpha: self.weights[alpha] for alpha in self.weights.keys()},
            index=all_indices,
        )
        return weight_df
