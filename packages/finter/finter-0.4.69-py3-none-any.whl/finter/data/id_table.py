import json

import pandas as pd
from finter.api.quanda_data_api import QuandaDataApi


class IdTable:

    def __init__(self, vendor_name):
        self.vendor_name = vendor_name
        self.cache = {}

    @staticmethod
    def support_list():
        return QuandaDataApi().quanda_data_id_table_retrieve(vendor="")['data']

    def get(self, id_type):
        df = self.cache.get(id_type)
        if df is None or df.empty:
            data = QuandaDataApi().quanda_data_id_table_retrieve(vendor=self.vendor_name, id_type=id_type)
            data_dict = json.loads(data['data'])
            df = pd.DataFrame.from_dict(data_dict)
            self.cache[id_type] = df
        return df

    def get_company(self):
        return self.get('company')

    def get_stock(self):
        return self.get('stock')

