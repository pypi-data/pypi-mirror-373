from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Sequence, Tuple, Union
from collections import OrderedDict


import numpy as np
import pandas as pd

from finter.data.manager.pointer import (
    EntityDataPointer,
    MacroDataPointer,
    StaticDataPointer,
    StockDataPointer,
)
from finter.data.manager.schemas import (
    EntityDataInput,
    MacroDataInput,
    StaticDataInput,
    StockDataInput,
)
from finter.data.manager.type import DataType

# Constants
MAX_DISPLAY_ITEMS = 5


@dataclass
class DataManager:
    """각 DataType별로 데이터와 좌표를 관리하는 클래스

    접근 방법:
        - manager.stock : stock 데이터 직접 접근
        - manager.stock.coords : stock의 전체 좌표 딕셔너리
        - manager.stock.point(T_0) : 특정 시점 데이터 추출
        - manager.stock.window(T_0, window=5) : 윈도우 데이터 추출
    """

    def __repr__(self) -> str:
        return f"DataManager(data={self.data.keys()}, coords={self.coords.keys()})"

    def __init__(self):
        # 각 타입별 데이터 저장소
        self.data: Dict[DataType, np.ndarray] = {}

        # 각 타입별 좌표 저장소
        self.coords: Dict[DataType, Dict[str, List]] = {
            DataType.STOCK: {"T": [], "N": [], "F": []},
            DataType.MACRO: {"T": [], "F": []},
            DataType.ENTITY: {"N": [], "F": []},
            DataType.STATIC: {"F": []},
        }

    # Property 접근자들
    @property
    def stock(self) -> StockDataPointer:
        """Stock 데이터를 DataPointer 객체로 접근"""
        return StockDataPointer(
            data=self.data[DataType.STOCK],
            T=self.coords[DataType.STOCK]["T"],
            N=self.coords[DataType.STOCK]["N"],
            F=self.coords[DataType.STOCK]["F"],
        )

    @property
    def macro(self) -> MacroDataPointer:
        """Macro 데이터를 DataPointer 객체로 접근"""
        return MacroDataPointer(
            data=self.data[DataType.MACRO],
            T=self.coords[DataType.MACRO]["T"],
            F=self.coords[DataType.MACRO]["F"],
        )

    @property
    def entity(self) -> EntityDataPointer:
        """Entity 데이터를 DataPointer 객체로 접근"""
        return EntityDataPointer(
            data=self.data[DataType.ENTITY],
            N=self.coords[DataType.ENTITY]["N"],
            F=self.coords[DataType.ENTITY]["F"],
        )

    @property
    def static(self) -> StaticDataPointer:
        """Static 데이터를 DataPointer 객체로 접근"""
        return StaticDataPointer(
            data=self.data[DataType.STATIC],
            F=self.coords[DataType.STATIC]["F"],
        )

    def add(self, data_type: DataType, data: np.ndarray, **coords_info):
        """
        데이터 추가 메서드

        사용 예시:
            # Stock 데이터 추가 (T=5, N=3 데이터)
            manager.add(DataType.STOCK, price_data, T=times, N=stocks, F=['price'])

            # 다른 시간대의 데이터 추가 (자동으로 union하고 NaN으로 채움)
            manager.add(DataType.STOCK, new_data, T=new_times, N=new_stocks, F=['volume'])

            # 추가 후 접근
            manager.stock  # 데이터 배열
            manager.stock_T  # 전체 시간 좌표 (union)
            manager.stock_N  # 전체 종목 좌표 (union)
        """
        if data_type == DataType.STOCK:
            self._add_stock(data, **coords_info)
        elif data_type == DataType.MACRO:
            self._add_macro(data, **coords_info)
        elif data_type == DataType.ENTITY:
            self._add_entity(data, **coords_info)
        elif data_type == DataType.STATIC:
            self._add_static(data, **coords_info)

    def add_stock(self, name: str, stock: pd.DataFrame):
        assert isinstance(stock, pd.DataFrame), "stock must be a pandas DataFrame"
        self.add(
            DataType.STOCK,
            stock.to_numpy(),
            T=stock.index,
            N=list(stock.columns),
            F=name,
        )

    def add_macro(self, name: str, macro: pd.Series):
        assert isinstance(macro, pd.Series), "macro must be a pandas Series"
        self.add(
            DataType.MACRO,
            macro.to_numpy(),
            T=macro.index,
            F=name,
        )

    def add_entity(self, name: str, entity: pd.Series):
        assert isinstance(entity, pd.Series), "entity must be a pandas Series"
        self.add(
            DataType.ENTITY,
            entity.to_numpy(),
            N=list(entity.index),
            F=name,
        )

    def add_static(self, name: str, static: Union[str, int, float, bool]):
        assert isinstance(static, (str, int, float, bool)), (
            "static must be a string, int, float, or bool"
        )
        self.add(
            DataType.STATIC,
            np.array(static),
            F=name,
        )

    def _check_duplicate_features(
        self, existing_features: List[str], new_features: Union[str, List[str]]
    ) -> None:
        """F 차원 중복 검사를 수행하는 공통 메서드"""
        existing_F_set = set(existing_features)

        if isinstance(new_features, str):
            new_features = [new_features]

        new_F_set = set(new_features)
        duplicate_F = existing_F_set & new_F_set

        if duplicate_F:
            raise ValueError(
                f"Duplicate feature names found: {duplicate_F}. "
                f"Existing features: {list(existing_F_set)}"
            )

    def _create_coordinate_mapping(
        self, input_coords: List, target_coords: List
    ) -> Tuple[List, np.ndarray, np.ndarray]:
        """좌표 매핑을 효율적으로 생성하는 공통 메서드"""
        input_dict = {v: k for k, v in enumerate(input_coords)}
        target_dict = {v: k for k, v in enumerate(target_coords)}

        # 공통 좌표와 인덱스 한 번에 계산
        target_set = set(target_dict.keys())
        common_coords = [coord for coord in input_coords if coord in target_set]
        if not common_coords:
            return [], np.array([]), np.array([])

        input_indices = np.array([input_dict[coord] for coord in common_coords])
        target_indices = np.array([target_dict[coord] for coord in common_coords])

        return common_coords, input_indices, target_indices

    def _reshape_data_generic(
        self,
        data: np.ndarray,
        input_coords: Dict[str, List],
        target_coords: Dict[str, List],
        axis_names: List[str],
    ) -> np.ndarray:
        """범용 데이터 재구성 메서드"""
        # 차원 확장 (필요시)
        if data.ndim == len(axis_names) - 1:
            data = np.expand_dims(data, axis=-1)

        # 타겟 shape 계산
        target_shape = [
            len(target_coords[axis]) for axis in axis_names if axis in target_coords
        ]
        if "F" not in axis_names:
            target_shape.append(data.shape[-1])

        # 각 축에 대한 인덱스 매핑
        index_mappings = []
        for i, axis in enumerate(axis_names):
            if axis in target_coords:
                input_axis = input_coords.get(axis, list(range(data.shape[i])))
                _, input_idx, target_idx = self._create_coordinate_mapping(
                    input_axis, target_coords[axis]
                )
                if len(input_idx) == 0:
                    return np.full(target_shape, np.nan)
                index_mappings.append((input_idx, target_idx, len(target_coords[axis])))

        # 데이터 재구성
        if all(len(inp) == tgt_len for inp, _, tgt_len in index_mappings):
            # 모든 좌표가 일치하는 경우
            indices = [mapping[0] for mapping in index_mappings]
            return data[np.ix_(*indices)] if len(indices) > 1 else data[indices[0], :]
        else:
            # 부분 매칭인 경우
            result = np.full(target_shape, np.nan)
            if len(index_mappings) == 1:
                inp, tgt, _ = index_mappings[0]
                result[tgt, :] = data[inp, :]
            elif len(index_mappings) == 2:
                inp1, tgt1, _ = index_mappings[0]
                inp2, tgt2, _ = index_mappings[1]
                result[np.ix_(tgt1, tgt2)] = data[np.ix_(inp1, inp2)]
            return result

    def _reshape_stock_data(
        self,
        data: np.ndarray,
        input_coords: Dict[str, List],
        target_coords: Dict[str, List],
    ) -> np.ndarray:
        """Stock 데이터를 타겟 좌표에 맞게 재구성"""
        if data.ndim == 2:
            data = np.expand_dims(data, axis=-1)

        target_T = target_coords["T"]
        target_N = target_coords["N"]
        input_T = input_coords.get("T", list(range(data.shape[0])))
        input_N = input_coords.get("N", list(range(data.shape[1])))

        target_shape = (len(target_T), len(target_N), data.shape[2])

        _, input_T_indices, target_T_indices = self._create_coordinate_mapping(
            input_T, target_T
        )
        _, input_N_indices, target_N_indices = self._create_coordinate_mapping(
            input_N, target_N
        )

        if len(input_T_indices) == 0 or len(input_N_indices) == 0:
            return np.full(target_shape, np.nan)

        if len(input_T_indices) == len(target_T) and len(input_N_indices) == len(
            target_N
        ):
            return data[np.ix_(input_T_indices, input_N_indices)]
        else:
            result = np.full(target_shape, np.nan)
            result[np.ix_(target_T_indices, target_N_indices)] = data[
                np.ix_(input_T_indices, input_N_indices)
            ]
            return result

    def _reshape_macro_data(
        self,
        data: np.ndarray,
        input_coords: Dict[str, List],
        target_coords: Dict[str, List],
    ) -> np.ndarray:
        """Macro 데이터를 타겟 좌표에 맞게 재구성"""
        return self._reshape_data_generic(data, input_coords, target_coords, ["T"])

    def _reshape_entity_data(
        self,
        data: np.ndarray,
        input_coords: Dict[str, List],
        target_coords: Dict[str, List],
    ) -> np.ndarray:
        """Entity 데이터를 타겟 좌표에 맞게 재구성"""
        return self._reshape_data_generic(data, input_coords, target_coords, ["N"])

    def _add_data_generic(
        self,
        data_type: DataType,
        validated_input,
        reshape_method,
        axis_for_concat: int,
    ):
        """범용 데이터 추가 메서드"""
        if self.data.get(data_type) is None:
            # 첫 데이터 추가 시 차원 확장
            data = validated_input.data
            if data_type == DataType.STOCK and data.ndim == 2:
                # Stock: 2D (T x N) -> 3D (T x N x F)
                data = np.expand_dims(data, axis=-1)
            elif data_type == DataType.MACRO and data.ndim == 1:
                # Macro: 1D (T) -> 2D (T x F)
                data = np.expand_dims(data, axis=-1)
            elif data_type == DataType.ENTITY and data.ndim == 1:
                # Entity: 1D (N) -> 2D (N x F)
                data = np.expand_dims(data, axis=-1)

            self.data[data_type] = data
            for key, value in validated_input.coords.items():
                if key == "N":
                    self.coords[data_type][key] = list(value)
                elif key == "F":
                    self.coords[data_type][key] = [value]
                else:
                    self.coords[data_type][key] = value
        else:
            existing = self.data[data_type]

            # F 차원 중복 검사
            if "F" in validated_input.coords:
                self._check_duplicate_features(
                    self.coords[data_type]["F"], validated_input.coords["F"]
                )
                new_F = self.coords[data_type]["F"] + [validated_input.coords["F"]]
            else:
                new_F = self.coords[data_type].get("F", [])

            # 새로운 좌표 계산 (union)
            target_coords = {"F": new_F}
            for key in self.coords[data_type]:
                if key != "F":
                    if key in validated_input.coords:
                        existing_coords = self.coords[data_type][key]
                        new_coords = validated_input.coords[key]

                        result_coords = list(
                            OrderedDict.fromkeys(existing_coords + new_coords)
                        )
                        target_coords[key] = result_coords
                    else:
                        target_coords[key] = self.coords[data_type][key]

            # 기존 데이터 재구성
            existing_coords = {
                k: v for k, v in self.coords[data_type].items() if k != "F"
            }
            reshaped_existing = reshape_method(existing, existing_coords, target_coords)

            # 새 데이터 재구성
            new_data = validated_input.data
            # 새 데이터도 차원 확장 필요
            if data_type == DataType.STOCK and new_data.ndim == 2:
                new_data = np.expand_dims(new_data, axis=-1)
            elif data_type == DataType.MACRO and new_data.ndim == 1:
                new_data = np.expand_dims(new_data, axis=-1)
            elif data_type == DataType.ENTITY and new_data.ndim == 1:
                new_data = np.expand_dims(new_data, axis=-1)

            reshaped_new = reshape_method(
                new_data,
                {k: v for k, v in validated_input.coords.items() if k != "F"},
                target_coords,
            )

            # 데이터 결합
            self.data[data_type] = np.concatenate(
                [reshaped_existing, reshaped_new], axis=axis_for_concat
            )

            # 좌표 업데이트
            self.coords[data_type] = target_coords

    def _add_stock(
        self,
        data: np.ndarray,
        T: List[datetime],
        N: Sequence[Union[str, int, float]],
        F: str,
    ):
        """Stock 타입 데이터 추가 (T, N, F)"""
        validated = StockDataInput(data=data, T=T, N=N, F=F)
        self._add_data_generic(
            DataType.STOCK, validated, self._reshape_stock_data, axis_for_concat=2
        )

    def _add_macro(
        self,
        data: np.ndarray,
        T: List[datetime],
        F: str,
    ):
        """Macro 타입 데이터 추가 (T, F)"""
        validated = MacroDataInput(data=data, T=T, F=F)
        self._add_data_generic(
            DataType.MACRO, validated, self._reshape_macro_data, axis_for_concat=1
        )

    def _add_entity(
        self,
        data: np.ndarray,
        N: Sequence[Union[str, int, float]],
        F: str,
    ):
        """Entity 타입 데이터 추가 (N, F)"""
        validated = EntityDataInput(data=data, N=N, F=F)
        self._add_data_generic(
            DataType.ENTITY, validated, self._reshape_entity_data, axis_for_concat=1
        )

    def _add_static(
        self,
        data: np.ndarray,
        F: str,
    ):
        """Static 타입 데이터 추가 (F)"""
        validated = StaticDataInput(data=data, F=F)

        # 스칼라 값 추출 (0차원 array에서 Python 객체로)
        value = (
            validated.data.item() if hasattr(validated.data, "item") else validated.data
        )

        if self.data.get(DataType.STATIC) is None:
            # 1차원 배열로 시작, object dtype 사용
            self.data[DataType.STATIC] = np.array([value], dtype=object)
            self.coords[DataType.STATIC]["F"] = [validated.F]
        else:
            # 기존 데이터에 추가
            existing = self.data[DataType.STATIC]

            # F 차원 중복 검사
            self._check_duplicate_features(
                self.coords[DataType.STATIC]["F"], validated.F
            )

            # F 차원에 추가
            new_F = self.coords[DataType.STATIC]["F"] + [validated.F]

            # 데이터 결합 - 직접 append
            self.data[DataType.STATIC] = np.append(existing, value)

            # 좌표 업데이트
            self.coords[DataType.STATIC]["F"] = new_F

    def info(self):
        """저장된 데이터 정보 출력"""
        print("=" * 50)
        print("DataManager Info (Numpy Array)")
        print("=" * 50)

        for dtype in DataType:
            if dtype in self.data:
                print(f"\n{dtype.value}:")
                print(f"  Shape: {self.data[dtype].shape}")

                # NaN 개수 표시 (numeric 데이터만)
                try:
                    if np.issubdtype(self.data[dtype].dtype, np.number):
                        nan_count = np.isnan(self.data[dtype]).sum()
                        if nan_count > 0:
                            print(
                                f"  NaN values: {nan_count} ({nan_count / self.data[dtype].size * 100:.1f}%)"
                            )
                    else:
                        print(f"  Data type: {self.data[dtype].dtype} (non-numeric)")
                except (TypeError, ValueError):
                    print(
                        f"  Data type: {self.data[dtype].dtype} (cannot check for NaN)"
                    )

                for coord_name, coord_vals in self.coords[dtype].items():
                    print(f"  {coord_name}: {len(coord_vals)} items")
                    if len(coord_vals) <= MAX_DISPLAY_ITEMS:
                        print(f"    {coord_vals}")
                    else:
                        print(f"    {coord_vals[:3]} ... {coord_vals[-2:]}")
