import pandas as pd
import requests

from finter.api.content_api import ContentApi
from finter.settings import get_api_client


def get_data(content_api: ContentApi = None, cm_type: str = "content"):
    if content_api is None:
        content_api = ContentApi(get_api_client())

    response = content_api.cm_catalog_retrieve(cm_type=cm_type)

    data = response["data"]
    df = pd.DataFrame(data[1:], columns=data[0])
    return df
