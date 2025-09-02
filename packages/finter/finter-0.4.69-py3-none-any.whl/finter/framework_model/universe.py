from __future__ import print_function

from datetime import datetime
from typing import List

from finter.rest import ApiException

import finter
from finter.settings import logger, get_api_client


def get_universe_list(region: str, type: str, vendor: str) -> List[int]:
    """
    return universe ccid list
    :param region: str | region name (ex: "korea")
    :param type: str | universe type (ex: "stock", "etf")
    :param vendor: str | vendor name (ex: "fnguide")
    """

    try:
        api_response = api_instance = finter.UniverseApi(get_api_client()).universe_list_retrieve(region, type, vendor)
        return [ccid for ccid in api_response.id_list]
    except ApiException as e:
        logger.error("Exception when calling UniverseApi->universe_list_retrieve: %s\n" % e)
