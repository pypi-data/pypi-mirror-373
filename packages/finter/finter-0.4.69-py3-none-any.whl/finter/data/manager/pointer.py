from datetime import datetime
from typing import Union

import numpy as np
from pydantic import BaseModel, ConfigDict

from finter.data.manager.type import F_TYPE, N_TYPE, T_TYPE


def _find_time_index(data: np.ndarray, T: T_TYPE, T_idx: Union[int, datetime]) -> int:
    """시간 인덱스를 찾는 메서드"""
    if isinstance(T_idx, int):
        if T_idx < 0 or T_idx >= data.shape[0]:
            raise IndexError(f"Time index {T_idx} out of range [0, {data.shape[0]})")
        return T_idx
    elif isinstance(T_idx, datetime):
        try:
            return T.index(T_idx)
        except ValueError:
            raise ValueError(f"Time coordinate '{T_idx}' not found in time coordinates")


class BaseDataPointer(BaseModel):
    """데이터 포인터의 기본 클래스"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: np.ndarray


class StockDataPointer(BaseDataPointer):
    """Stock 데이터 포인터 (T x N x F)

    Attributes:
        data: (T, N, F) shape의 numpy array
        T: 시간 좌표 리스트
        N: 엔티티(종목) 좌표 리스트
        F: Feature 좌표 리스트
    """

    T: T_TYPE
    N: N_TYPE
    F: F_TYPE

    @property
    def coords(self) -> dict:
        return {"T": self.T, "N": self.N, "F": self.F}

    def point(self, T_idx: Union[int, datetime]) -> np.ndarray:
        """특정 시점(T)의 데이터를 추출

        Args:
            T_idx: 시간 인덱스 (정수) 또는 datetime 객체

        Returns:
            해당 시점의 데이터 (N, F)
        """
        idx = _find_time_index(self.data, self.T, T_idx)
        return self.data[idx, :, :]  # (N, F)

    def window(self, T_idx: Union[int, datetime], window: int = 5) -> np.ndarray:
        """특정 시점부터 윈도우 크기만큼의 데이터를 추출

        Args:
            T_idx: 시작 시간 인덱스 (정수) 또는 datetime 객체
            window: 윈도우 크기 (기본값: 5)

        Returns:
            윈도우 데이터 (window, N, F)
        """
        end_idx = _find_time_index(self.data, self.T, T_idx) + 1
        start_idx = max(0, end_idx - window)
        return self.data[start_idx:end_idx, :, :]  # (window, N, F)


class MacroDataPointer(BaseDataPointer):
    """Macro 데이터 포인터 (T x F)

    Attributes:
        data: (T, F) shape의 numpy array
        T: 시간 좌표 리스트
        F: Feature 좌표 리스트
    """

    T: T_TYPE
    F: F_TYPE

    @property
    def coords(self) -> dict:
        return {"T": self.T, "F": self.F}

    def point(self, T_idx: Union[int, datetime]) -> np.ndarray:
        """특정 시점(T)의 데이터를 추출

        Args:
            T_idx: 시간 인덱스 (정수) 또는 datetime 객체

        Returns:
            해당 시점의 데이터 (F,)
        """
        idx = _find_time_index(self.data, self.T, T_idx)
        return self.data[idx, :]  # (F,)

    def window(self, T_idx: Union[int, datetime], window: int = 5) -> np.ndarray:
        """특정 시점부터 윈도우 크기만큼의 데이터를 추출

        Args:
            T_idx: 시작 시간 인덱스 (정수) 또는 datetime 객체
            window: 윈도우 크기 (기본값: 5)

        Returns:
            윈도우 데이터 (window, F)
        """
        end_idx = _find_time_index(self.data, self.T, T_idx) + 1
        start_idx = max(0, end_idx - window)
        return self.data[start_idx:end_idx, :]  # (window, F)


class EntityDataPointer(BaseDataPointer):
    """Entity 데이터 포인터 (N x F)

    Attributes:
        data: (N, F) shape의 numpy array
        N: 엔티티 좌표 리스트
        F: Feature 좌표 리스트
    """

    N: N_TYPE
    F: F_TYPE

    @property
    def coords(self) -> dict:
        return {"N": self.N, "F": self.F}


class StaticDataPointer(BaseDataPointer):
    """Static 데이터 포인터 (F,)

    Attributes:
        data: (F,) shape의 numpy array
        F: Feature 좌표 리스트
    """

    F: F_TYPE

    @property
    def coords(self) -> dict:
        return {"F": self.F}


if __name__ == "__main__":
    data = np.random.randn(10, 3, 2)
    T = [datetime(2024, 1, i) for i in range(1, 11)]
    N = ["AAPL", "GOOGL", "MSFT"]
    F = ["price", "volume"]
    stock_data = StockDataPointer(data=data, T=T, N=N, F=F)
    print(stock_data.point(datetime(2024, 1, 5)))
    print(stock_data.window(datetime(2024, 1, 5), window=5))
