"""
Use Example:

from finter.modeling.meta_portfolios.equal_weight_portfolio import (
    EqualWeightMetaPortfolio,
)
from finter.framework_model.submission.config import ModelUniverseConfig

Portfolio = EqualWeightMetaPortfolio.create(
    EqualWeightMetaPortfolio.Parameters(
        universe=ModelUniverseConfig.KR_STOCK,
        alpha_set={
            "krx.krx.stock.soobeom33_qt.low_vol_factor_simple",
            "krx.krx.stock.ldh0127_qt.sample_univ_1",
        },
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
from finter.modeling.meta_portfolio.base import (
    BaseMetaPortfolio,
    BaseParameters,
)


class EqualWeightMetaPortfolio(BaseMetaPortfolio):

    class Parameters(BaseParameters): ...

    def get(self, start, end):
        alpha_loader = self.alpha_loader(start, end)
        alpha_dict: Dict[str, pd.DataFrame] = {}
        for alpha_idn in self.alpha_set:
            alpha = alpha_loader.get_alpha(alpha_idn)
            alpha.replace(0, np.nan, inplace=True)
            alpha.dropna(axis=1, how="all", inplace=True)
            alpha = alpha.fillna(0)

            row_sums = alpha.sum(axis=1)
            scaling_factors = np.where(row_sums > 1e8, 1e8 / row_sums, 1)
            alpha = alpha.mul(scaling_factors, axis=0)

            alpha_dict[alpha_idn] = alpha.fillna(0)

        pf = reduce(lambda x, y: x.add(y, fill_value=0), alpha_dict.values()) / len(
            alpha_dict.values()
        )
        return pf.fillna(0)
