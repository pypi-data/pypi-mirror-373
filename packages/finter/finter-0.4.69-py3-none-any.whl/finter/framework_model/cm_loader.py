from __future__ import print_function

from collections import namedtuple
from importlib import import_module

import finter
from finter.log import PromtailLogger
from finter.rest import ApiException
from finter.settings import get_api_client, logger
from finter.utils import to_dataframe


class ContentModelLoader(object):
    __MODULE_CLASS = namedtuple("__MODULE_CLASS", ["module", "loader"])
    __CM_MAP = {
        "content.fnguide.ftp.financial": __MODULE_CLASS(
            "finter.framework_model.content_loader.krx.fnguide.financial",
            "KrFinancialLoader",
        ),
        "content.fnguide.ftp.consensus": __MODULE_CLASS(
            "finter.framework_model.content_loader.krx.fnguide.consensus",
            "KrConsensusLoader",
        ),
        "content.fnguide.ftp.economy": __MODULE_CLASS(
            "finter.framework_model.content_loader.krx.fnguide.economy", "EconomyLoader"
        ),
        "content.fnguide.ftp.investor_activity": __MODULE_CLASS(
            "finter.framework_model.content_loader.krx.fnguide.stock", "StockLoader"
        ),
        "content.fnguide.ftp.credit": __MODULE_CLASS(
            "finter.framework_model.content_loader.krx.fnguide.stock", "StockLoader"
        ),
        "content.fnguide.ftp.cax": __MODULE_CLASS(
            "finter.framework_model.content_loader.krx.fnguide.stock", "StockLoader"
        ),
        "content.fnguide.ftp.status": __MODULE_CLASS(
            "finter.framework_model.content_loader.krx.fnguide.stock", "StockLoader"
        ),
        "content.fnguide.ftp.price_volume": __MODULE_CLASS(
            "finter.framework_model.content_loader.krx.fnguide.price_volume",
            "PriceVolumeLoader",
        ),
        "content.fnguide.ftp.capital": __MODULE_CLASS(
            "finter.framework_model.content_loader.krx.fnguide.capital", "CapitalLoader"
        ),
        "content.quantit.fnguide_cm.factor": __MODULE_CLASS(
            "finter.framework_model.content_loader.di.loader.di", "DILoader"
        ),
        "content.quantit.fnguide_cm.descriptor": __MODULE_CLASS(
            "finter.framework_model.content_loader.krx.fnguide.descriptor",
            "DescriptorLoader",
        ),
        "content.bloomberg.api.future.": __MODULE_CLASS(
            "finter.framework_model.content_loader.bloomberg.price_volume",
            "BloombergLoader",
        ),
        "content.spglobal.compustat.financial.vnm": __MODULE_CLASS(
            "finter.framework_model.content_loader.spglobal.compustat.financial",
            "CompustatFinancialLoader",
        ),
        "content.spglobal.compustat.financial.us-stock-": __MODULE_CLASS(
            "finter.framework_model.content_loader.spglobal.compustat.financial",
            "CompustatFinancialLoader",
        ),
        "content.spglobal.compustat.financial.us-stock_pit-": __MODULE_CLASS(
            "finter.framework_model.content_loader.us-stock.spglobal.compustat.financial_pit",
            "CompustatFinancialPitLoader",
        ),
        "content.spglobal.compustat.price_volume.id": __MODULE_CLASS(
            "finter.framework_model.content_loader.spglobal.compustat.idn",
            "CompustatLoader",
        ),
        "content.spglobal.compustat.cax.id": __MODULE_CLASS(
            "finter.framework_model.content_loader.spglobal.compustat.idn",
            "CompustatLoader",
        ),
        "content.spglobal.compustat.classification.id": __MODULE_CLASS(
            "finter.framework_model.content_loader.spglobal.compustat.idn",
            "CompustatLoader",
        ),
        "content.spglobal.compustat.price_volume.vnm": __MODULE_CLASS(
            "finter.framework_model.content_loader.spglobal.compustat.vnm",
            "CompustatLoader",
        ),
        "content.spglobal.compustat.cax.vnm": __MODULE_CLASS(
            "finter.framework_model.content_loader.spglobal.compustat.vnm",
            "CompustatLoader",
        ),
        "content.spglobal.compustat.classification.vnm": __MODULE_CLASS(
            "finter.framework_model.content_loader.spglobal.compustat.vnm",
            "CompustatLoader",
        ),
        "content.spglobal.compustat.universe.vnm": __MODULE_CLASS(
            "finter.framework_model.content_loader.spglobal.compustat.vnm",
            "CompustatLoader",
        ),
        "content.spglobal.compustat.price_volume.us-etf": __MODULE_CLASS(
            "finter.framework_model.content_loader.us-etf.spglobal.compustat.price_volume",
            "PriceVolumeLoader",
        ),
        "content.spglobal.compustat.price_volume.us-stock": __MODULE_CLASS(
            "finter.framework_model.content_loader.us-stock.spglobal.compustat.price_volume",
            "PriceVolumeLoader",
        ),
        "content.spglobal.compustat.classification.us-stock": __MODULE_CLASS(
            "finter.framework_model.content_loader.us-stock.spglobal.compustat.classification",
            "ClassificationLoader",
        ),
        "content.spglobal.compustat": __MODULE_CLASS(
            "finter.framework_model.content_loader.spglobal.compustat.us",
            "CompustatLoader",
        ),
        "content.quantit.compustat_cm.factor": __MODULE_CLASS(
            "finter.framework_model.content_loader.us-stock.spglobal.compustat.factor",
            "FactorLoader",
        ),
        "content.vaiv.api.theme": __MODULE_CLASS(
            "finter.framework_model.content_loader.vaiv.buzz",
            "ThemeLoader",
        ),
        "content.handa.dataguide.ews": __MODULE_CLASS(
            "finter.framework_model.content_loader.ews.krx",
            "EwsLoader",
        ),
        "content.handa.unstructured.ews": __MODULE_CLASS(
            "finter.framework_model.content_loader.ews.sent_index",
            "RawSentLoader",
        ),
        "content.handa.unstructured.ews": __MODULE_CLASS(
            "finter.framework_model.content_loader.ews.sent_index",
            "SarimaSentLoader",
        ),
        "content.daumsoft.keyterm.sentiment": __MODULE_CLASS(
            "finter.framework_model.content",
            "LoaderTemplate",
        ),
        "content.fiintek.api": __MODULE_CLASS(
            "finter.framework_model.content_loader.fiintek.stock", "FiintekLoader"
        ),
        "content.binance.daily": __MODULE_CLASS(
            "finter.framework_model.content_loader.binance.price_volume",
            "BinancePriceVolumeLoader",
        ),
        "content.binance.api": __MODULE_CLASS(
            "finter.framework_model.content_loader.binance.price_volume_parquet",
            "BinancePriceVolumeLoader",
        ),
        "content.krx.live.cax": __MODULE_CLASS(
            "finter.framework_model.content_loader.krx.live.cax", "StockEventLoader"
        ),
        "content.quandaflow": __MODULE_CLASS(
            "finter.framework_model.content_loader.quandaflow.quandaflow",
            "QuandaFlowLoader",
        ),
        "content.bareksa.ftp.price_volume": __MODULE_CLASS(
            "finter.framework_model.content_loader.bareksa.price_volume",
            "BareksaLoader",
        ),
        "content": __MODULE_CLASS(
            "finter.framework_model.content",
            "LoaderTemplate",
        ),
    }

    @classmethod
    def load(cls, key):
        for k, md_class in cls.__CM_MAP.items():
            if key.startswith(k):
                module = import_module(md_class.module)
                attr = getattr(module, md_class.loader)
                if key != k:
                    return attr(key)
                else:
                    return attr

        # Todo: Current __CM_MAP only supports fnguide data.
        return GetCMGetDf(identity_name=key)


class GetCMGetDf(object):
    def __init__(self, identity_name):
        self.identity_name = identity_name

    def get_df(self, start, end, code_format="fnguide_to_quantit", **kwargs):
        # if start or end is str, convert it to str
        param = {
            "identity_name": self.identity_name,
            "start": str(start),
            "end": str(end),
            "code_format": code_format,
        }
        param.update(kwargs)
        if ("fnguide" in self.identity_name) and (code_format == "fnguide_to_quantit"):
            param["code_format"] = "fnguide_to_quantit"
        try:
            api_response = finter.AlphaApi(
                get_api_client()
            ).alpha_base_alpha_cm_retrieve(**param)
            response = api_response.to_dict()
            PromtailLogger.send_log(
                level="INFO",
                message=f"{self.identity_name}",
                service="finterlabs-jupyterhub",
                user_id=PromtailLogger.get_user_info(),
                operation="load_model_data",
                status="success",
            )
            return to_dataframe(response["cm"], response["column_types"])
        except ApiException as e:
            logger.error(
                "Exception when calling AlphaApi->alpha_base_alpha_cm_retrieve: %s\n"
                % e
            )
        return
