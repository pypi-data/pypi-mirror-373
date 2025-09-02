from __future__ import print_function

from finter.rest import ApiException
from finter.settings import logger


class AlphaPositionLoader:
    def __init__(
        self,
        start,
        end,
        exchange,
        universe,
        instrument_type,
        freq,
        position_type,
        alpha_set,
    ):
        self.start = start
        self.end = end
        self.exchange = exchange
        self.universe = universe
        self.instrument_type = instrument_type
        self.freq = freq
        self.position_type = position_type
        self.alpha_set = list(alpha_set) if isinstance(alpha_set, set) else alpha_set

    def get_alpha(self, identity_name):
        from finter.data import ModelData

        if identity_name.startswith("alpha."):
            identity_name = identity_name
        else:
            identity_name = "alpha." + identity_name
        try:
            return ModelData.load(identity_name).loc[str(self.start) : str(self.end)]
        except ApiException as e:
            logger.error("Exception when calling AlphaPositionLoader->get_df: %s\n" % e)
        return
