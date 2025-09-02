from __future__ import print_function

import finter
from finter.settings import get_api_client
from finter.rest import ApiException
from finter.utils import with_spinner
from finter.utils.convert import get_json_with_columns_from_dataframe


@with_spinner(text="Waiting Simulation result...")
def adj_stat_container_helper(**kwargs):
    if 'position' in kwargs:
        kwargs['position'], kwargs['position_column_types'] = get_json_with_columns_from_dataframe(kwargs['position'])

    body = finter.SimulationRequest(**kwargs)  # SimulationRequest |

    try:
        api_response = finter.SimulationApi(get_api_client()).simulation_create(body)
        return api_response.result
    except ApiException as e:
        print("Exception when calling SimulationApi->simulation_create: %s\n" % e)