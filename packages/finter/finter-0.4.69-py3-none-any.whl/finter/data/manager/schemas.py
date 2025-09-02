"""Data validation schemas for DataManager using Pydantic."""

from datetime import datetime
from typing import List, Sized

import numpy as np
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from finter.data.manager.type import F_INPUT_TYPE, N_TYPE, T_TYPE


def _validate_data_shape(arr: np.ndarray, ndim: int) -> None:
    """Validate array dimensionality."""
    if arr.ndim != ndim:
        expected_shape = f"{ndim}D" if ndim > 0 else "scalar (0D)"
        actual_shape = f"{arr.ndim}D" if arr.ndim > 0 else "scalar (0D)"
        raise ValueError(
            f"Expected {expected_shape} array, got {actual_shape} with shape {arr.shape}"
        )


def _validate_length(seq: Sized, arr: np.ndarray, dim: int) -> None:
    """Validate sequence length matches array dimension."""
    expected = arr.shape[dim]
    actual = len(seq)
    if actual != expected:
        dim_names = {0: "rows (time)", 1: "columns (entities)"}
        dim_name = dim_names.get(dim, f"dimension {dim}")
        raise ValueError(
            f"Coordinate length mismatch for {dim_name}: "
            f"expected {expected}, got {actual}"
        )


def _validate_time_coords(v: List[datetime]) -> None:
    """Validate all time coordinates are datetime objects."""
    invalid_items = [
        (i, type(t).__name__) for i, t in enumerate(v) if not isinstance(t, datetime)
    ]
    if invalid_items:
        invalid_types = set(t for _, t in invalid_items)
        indices = [i for i, _ in invalid_items[:3]]  # Show first 3 invalid indices
        raise ValueError(
            f"All T coordinates must be datetime objects. "
            f"Found {invalid_types} at indices {indices}"
        )


class StockDataInput(BaseModel):
    """Validation schema for stock data input (T x N x F)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: np.ndarray
    T: T_TYPE = Field(..., min_length=1)
    N: N_TYPE = Field(..., min_length=1)
    F: F_INPUT_TYPE = Field(..., min_length=1)

    @field_validator("T", mode="before")
    @classmethod
    def validate_time_coords(cls, v: List[datetime]) -> List[datetime]:
        _validate_time_coords(v)
        return v

    @field_validator("data")
    @classmethod
    def validate_data_shape(cls, v: np.ndarray) -> np.ndarray:
        _validate_data_shape(v, ndim=2)
        return v

    @model_validator(mode="after")
    def validate_time_coords_length(self):
        _validate_length(self.T, self.data, dim=0)
        return self

    @model_validator(mode="after")
    def validate_entity_coords(self):
        _validate_length(self.N, self.data, dim=1)
        return self

    @computed_field
    @property
    def coords(self) -> dict:
        return {"T": self.T, "N": self.N, "F": self.F}


class MacroDataInput(BaseModel):
    """Validation schema for macro data input (T x F)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: np.ndarray
    T: T_TYPE = Field(..., min_length=1)
    F: F_INPUT_TYPE = Field(..., min_length=1)

    @field_validator("T", mode="before")
    @classmethod
    def validate_time_coords(cls, v: List[datetime]) -> List[datetime]:
        _validate_time_coords(v)
        return v

    @field_validator("data")
    @classmethod
    def validate_data_shape(cls, v: np.ndarray) -> np.ndarray:
        _validate_data_shape(v, ndim=1)
        return v

    @model_validator(mode="after")
    def validate_time_coords_length(self):
        _validate_length(self.T, self.data, dim=0)
        return self

    @computed_field
    @property
    def coords(self) -> dict:
        return {"T": self.T, "F": self.F}


class EntityDataInput(BaseModel):
    """Validation schema for entity data input (N x F)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: np.ndarray
    N: N_TYPE = Field(..., min_length=1)
    F: F_INPUT_TYPE = Field(..., min_length=1)

    @field_validator("data")
    @classmethod
    def validate_data_shape(cls, v: np.ndarray) -> np.ndarray:
        _validate_data_shape(v, ndim=1)
        return v

    @model_validator(mode="after")
    def validate_entity_coords(self):
        _validate_length(self.N, self.data, dim=0)
        return self

    @computed_field
    @property
    def coords(self) -> dict:
        return {"N": self.N, "F": self.F}


class StaticDataInput(BaseModel):
    """Validation schema for static data input (F only)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: np.ndarray
    F: F_INPUT_TYPE = Field(..., min_length=1)

    @field_validator("data")
    @classmethod
    def validate_data_shape(cls, v: np.ndarray) -> np.ndarray:
        _validate_data_shape(v, ndim=0)
        return v

    @computed_field
    @property
    def coords(self) -> dict:
        return {"F": self.F}
