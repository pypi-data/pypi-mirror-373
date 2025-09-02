import numpy as np
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
from finter.framework_model.content import Loader
from finter.settings import logger
from finter.settings import get_api_client

class FactorLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]
        self.gvkeyiid_factor = [
            "z_score",
            "kz_index",
            "eq_dur",
            "ival_me",
            "debt_mev", 
            'pstk_mev',
            'debtlt_mev',
            'debtst_mev',
            'be_mev',
            'at_mev',
            'cash_mev',
            'bev_mev',
            'ppen_mev',
            'gp_mev',
            'ebitda_mev',
            'ebit_mev',
            'sale_mev',
            'ocf_mev',
            'cop_mev',
            'be_me',
            'at_me',
            'cash_me',
            'gp_me',
            'ebitda_me',
            'ebit_me',
            'ope_me',
            'ni_me',
            'sale_me',
            'ocf_me',
            'nix_me',
            'cop_me',
            'rd_me',
            'div_me',
            'debt_me',
            'netdebt_me',
            'aliq_mat'
        ]

    def get_df(
        self,
        start: int,
        end: int,
        fill_nan=True,
        quantit_universe=True,
        *args,
        **kwargs
    ):
        raw = self._load_cache(
            self.__CM_NAME,
            start,
            end,
            freq=self.__FREQ,
            fill_nan=fill_nan,
            *args,
            **kwargs,
        ).dropna(how="all")
        
        
        univ = self._load_cache(
            "content.spglobal.compustat.universe.us-stock-constituent.1d",
            19980401,  # to avoid start dependency in dataset
            end,
            universe="us-compustat-stock",
            freq=self.__FREQ,
            fill_nan=fill_nan,
            *args,
            **kwargs,
        )
        factor_name = self.__CM_NAME.split("-")[-1].replace(".1d", "")

        if factor_name not in self.gvkeyiid_factor:
            univ.columns = [col[:6] for col in univ.columns]
            univ = univ.T.groupby(univ.columns).any().T

        else:
            logger.info(f"{factor_name} cm column is gvkeyiid")
            logger.warning("Loaded Factor CM is calculated using the market cap on the index date. To avoid forward-looking bias, shift it when designing an alpha.")
    

        holiday = pd.date_range('19980401', str(end), freq='D').difference(univ.index)
        bday = CustomBusinessDay(holidays=holiday)
        raw.index = pd.to_datetime(raw.index)
        raw.index = [i + bday if i in holiday else i for i in pd.to_datetime(raw.index)] # holiday면 bday로 이동
        raw = raw.groupby(raw.index).ffill().groupby(level=0).tail(1) # combine; bday로 밀면서 index 겹칠 때 같은 index에 대해 ffill 시키고 tail(1)
        
        if quantit_universe:
            raw *= univ
        else:
            self.client = get_api_client()
            if self.client.user_group != "quantit":
                raise AssertionError("Only quantit user group can use all universe")
            
        raw = raw.replace(0, np.nan)
        return raw