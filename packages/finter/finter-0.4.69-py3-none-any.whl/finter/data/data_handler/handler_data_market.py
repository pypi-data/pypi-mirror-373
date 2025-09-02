from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import yaml

from finter.data import ContentFactory
from finter.data.data_handler.handler_abstract import AbstractDataHandler
from finter.data.data_handler.registry import DataHandlerRegistry


def load_item_mapping_by_item(item: str) -> Dict[str, str]:
    yaml_path = Path(__file__).parent / "item_mappings.yaml"
    with open(yaml_path, "r") as f:
        mappings = yaml.safe_load(f)

    items = {}
    for key in mappings:
        if item in mappings[key]:
            items[key] = mappings[key][item]
    return items


class PriceHandler(AbstractDataHandler):
    def __init__(self):
        self.item_mapping = load_item_mapping_by_item("price")

    def get_data(self, cf: ContentFactory, universe: str, **kwargs) -> Any:
        if universe not in self.item_mapping:
            raise ValueError(f"Unsupported universe: {universe}")
        return cf.get_df(self.item_mapping[universe], quantit_universe=False, **kwargs)


class VolumeHandler(AbstractDataHandler):
    def __init__(self):
        self.item_mapping = load_item_mapping_by_item("volume")

    def get_data(self, cf: ContentFactory, universe: str, **kwargs) -> Any:
        if universe == "us_future":
            price = cf.get_df(
                load_item_mapping_by_item("price")["us_future"],
                quantit_universe=False,
                **kwargs,
            )
            return pd.DataFrame(np.inf, index=price.index, columns=price.columns)
        else:
            if universe not in self.item_mapping:
                raise ValueError(f"Unsupported universe: {universe}")
        return cf.get_df(self.item_mapping[universe], quantit_universe=False, **kwargs)


class AdjustmentRatioHandler(AbstractDataHandler):
    def __init__(self):
        self.item_mapping = load_item_mapping_by_item("adjustment_ratio")

    def get_data(self, cf: ContentFactory, universe: str, **kwargs) -> Any:
        if universe not in self.item_mapping:
            return pd.DataFrame()
        if universe in ["us_stock", "us_etf", "id_stock"]:
            return 1 / cf.get_df(
                self.item_mapping[universe], quantit_universe=False, **kwargs
            )
        elif universe == "us_future":
            df = cf.get_df(self.item_mapping[universe], **kwargs)
            return df.apply(np.exp).cumprod()
        return cf.get_df(self.item_mapping[universe], **kwargs).fillna(1)


class DividendFactorHandler(AbstractDataHandler):
    def __init__(self):
        self.item_mapping = load_item_mapping_by_item("dividend_factor")

    def get_data(self, cf: ContentFactory, universe: str, **kwargs) -> Any:
        if universe not in self.item_mapping:
            raise ValueError(f"Unsupported universe: {universe}")
        df = cf.get_df(self.item_mapping[universe], **kwargs)
        if universe == "id_bond":
            return df
        else:
            return df.pct_change()


class ConstituentHandler(AbstractDataHandler):
    def __init__(self):
        self.item_mapping = load_item_mapping_by_item("sub_universe")

    def get_data(
        self, cf: ContentFactory, universe: str, sub_universe: str, **kwargs
    ) -> Any:
        if sub_universe not in self.item_mapping[universe]:
            raise ValueError(f"Unsupported sub_universe: {sub_universe}")
        return cf.get_df(self.item_mapping[universe][sub_universe], **kwargs)


class CurrencyHandler(AbstractDataHandler):
    def __init__(self):
        self.item_mapping = load_item_mapping_by_item("currency")

    def get_data(self, cf: ContentFactory, universe: str, **kwargs) -> Any:
        if universe not in ["common"]:
            raise ValueError(f"Unsupported universe for common handler: {universe}")
        return cf.get_df(self.item_mapping[universe], **kwargs)


class BenchmarkHandler(AbstractDataHandler):
    def __init__(self):
        self.item_mapping = load_item_mapping_by_item("benchmark")

    def get_data(self, cf: ContentFactory, universe: str, **kwargs) -> Any:
        if universe not in self.item_mapping:
            raise ValueError(f"Unsupported universe: {universe}")
        if universe == "common":
            return cf.get_df(self.item_mapping["common"], **kwargs)
        else:
            return cf.get_df(self.item_mapping["common"], **kwargs)[
                self.item_mapping[universe]
            ]


class MarketCapHandler(AbstractDataHandler):
    def __init__(self):
        self.item_mapping = load_item_mapping_by_item("market_cap")

    def get_data(self, cf: ContentFactory, universe: str, **kwargs) -> Any:
        if universe == "kr_stock":
            return (
                cf.get_df("content.fnguide.ftp.price_volume.mkt_cap.1d", **kwargs)
                / 1e11
            )
        elif universe == "vn_stock":
            price = cf.get_df(
                "content.spglobal.compustat.price_volume.vnm-all-price_close.1d",
                **kwargs,
            )
            shares = cf.get_df(
                "content.spglobal.compustat.price_volume.vnm-all-shares_outstanding.1d",
                **kwargs,
            )
            return price * shares
        elif universe == "id_stock":
            price = cf.get_df(
                "content.spglobal.compustat.price_volume.id-all-price_close.1d",
                **kwargs,
            )
            shares = cf.get_df(
                "content.spglobal.compustat.price_volume.id-all-shares_outstanding.1d",
                **kwargs,
            )
            return price * shares
        elif universe == "us_stock":
            price = cf.get_df(
                "content.spglobal.compustat.price_volume.us-stock-price_close.1d",
                **kwargs,
            )
            shares = cf.get_df(
                "content.spglobal.compustat.price_volume.us-stock-shares_outstanding.1d",
                **kwargs,
            )
            return price * shares
        elif universe == "us_etf":
            price = cf.get_df(
                "content.spglobal.compustat.price_volume.us-etf-price_close.1d",
                **kwargs,
            )
            shares = cf.get_df(
                "content.spglobal.compustat.price_volume.us-etf-shares_outstanding.1d",
                **kwargs,
            )
            return price * shares
        else:
            raise ValueError(
                f"Market cap data for universe {universe} is not implemented."
            )


def calc_52week_high(universe, **kwargs) -> pd.Series:
    price_data = universe.price(**kwargs)
    return price_data.rolling(window=252).max()


def calc_52week_low(universe, **kwargs) -> pd.Series:
    price_data = universe.price(**kwargs)
    return price_data.rolling(window=252).min()


def register_handlers():
    """모든 핸들러와 계산 메서드를 등록하는 함수"""
    # 핸들러 클래스들 등록
    DataHandlerRegistry.register_handler("price")(PriceHandler)
    DataHandlerRegistry.register_handler("volume")(VolumeHandler)
    DataHandlerRegistry.register_handler("adjustment_ratio")(AdjustmentRatioHandler)
    DataHandlerRegistry.register_handler("dividend_factor")(DividendFactorHandler)
    DataHandlerRegistry.register_handler("currency")(CurrencyHandler)
    DataHandlerRegistry.register_handler("benchmark")(BenchmarkHandler)
    DataHandlerRegistry.register_handler("market_cap")(MarketCapHandler)
    DataHandlerRegistry.register_handler("constituent")(ConstituentHandler)
    # 계산 메서드들 등록
    DataHandlerRegistry.register_calculated_method("_52week_high")(calc_52week_high)
    DataHandlerRegistry.register_calculated_method("_52week_low")(calc_52week_low)
