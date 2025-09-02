from dataclasses import dataclass, field
from typing import List, Optional, Union

from finter.data import ContentFactory
from finter.data.manager.main import DataManager

# Universe별 필드 매핑 (간단하게)
FIELD_MAPPING = {
    "kr_stock": {
        "open": "price_open",
        "high": "price_high",
        "low": "price_low",
        "close": "price_close",
        "volume": "volume_sum",
        "market_cap": "mkt_cap",
    },
    "us_stock": {
        "open": "price_open",
        "high": "price_high",
        "low": "price_low",
        "close": "price_close",
        "volume": "trading_volume",
    },
}
CACHE_TIMEOUT = 300


@dataclass
class DataAdapter:
    """
    ContentFactory 간단 래퍼

    사용법:
        adapter = DataAdapter("kr_stock", 20200101, 20231231)
        adapter.add(["open", "high", "low", "close", "volume"])

        # 데이터 접근
        stock_data = adapter.stock
        dm = adapter.dm
    """

    universe: str
    start: int
    end: int
    dm: DataManager = field(default_factory=DataManager)
    _cf: Optional[ContentFactory] = field(default=None, init=False)

    def __post_init__(self):
        self._cf = ContentFactory(
            self.universe, self.start, self.end, cache_timeout=CACHE_TIMEOUT
        )

    def add(self, fields: Union[str, List[str]]) -> "DataAdapter":
        """필드 추가"""
        if isinstance(fields, str):
            fields = [fields]

        for field_name in fields:
            # 필드명 매핑
            cf_field_name = self._get_cf_field_name(field_name)

            # 데이터 로드
            data = self._cf.get_df(cf_field_name)

            # DataManager에 추가 (모든 데이터는 stock으로 처리)
            self.dm.add_stock(field_name, data)

            print(f"✓ Successfully Added '{field_name}'")

        return self

    def _get_cf_field_name(self, field_name: str) -> str:
        """Universe별 필드명 매핑"""
        universe_mapping = FIELD_MAPPING.get(self.universe, {})
        return universe_mapping.get(field_name, field_name)

    def add_data(self, name: str, data, data_type: str = "stock") -> "DataAdapter":
        """외부 데이터를 DataManager에 직접 추가"""
        if data_type == "stock":
            self.dm.add_stock(name, data)
        elif data_type == "macro":
            self.dm.add_macro(name, data)
        elif data_type == "entity":
            self.dm.add_entity(name, data)
        elif data_type == "static":
            self.dm.add_static(name, data)
        else:
            raise ValueError(f"Unknown data_type: {data_type}")

        print(f"✓ Successfully Added '{name}' as {data_type}")
        return self

    @property
    def stock(self):
        """Stock 데이터 직접 접근"""
        return self.dm.stock

    @property
    def macro(self):
        """Macro 데이터 직접 접근"""
        return self.dm.macro

    @property
    def entity(self):
        """Entity 데이터 직접 접근"""
        return self.dm.entity

    @property
    def static(self):
        """Static 데이터 직접 접근"""
        return self.dm.static

    def info(self):
        """정보 출력"""
        print(f"\nDataAdapter ({self.universe}): {self.start} ~ {self.end}")
        print("-" * 50)
        self.dm.info()
        print("-" * 50 + "\n")


if __name__ == "__main__":
    import pandas as pd

    # 기본 사용법
    adapter = DataAdapter("kr_stock", 20200101, 20231231)
    adapter.add(["open", "high", "low", "close", "volume"])

    # 외부 데이터 추가 예시
    from datetime import datetime

    adapter.add_data(
        "market_sentiment",
        pd.Series(
            [0.5, 0.7, 0.3],
            index=[datetime(2020, 1, 1), datetime(2020, 1, 2), datetime(2020, 1, 3)],
        ),
        "macro",
    )
    adapter.add_data("analysis_date", "2024-01-01", "static")

    # 전처리는 직접 코드에서
    close_data = adapter.stock.data[:, :, adapter.stock.F.index("close")]
    normalized_close = (close_data - close_data.min()) / (
        close_data.max() - close_data.min()
    )

    adapter.info()

    # 다른 universe
    print("\n" + "=" * 50)
    us_adapter = DataAdapter("us_stock", 20200101, 20231231)
    us_adapter.add(["open", "close"])
    us_adapter.info()
