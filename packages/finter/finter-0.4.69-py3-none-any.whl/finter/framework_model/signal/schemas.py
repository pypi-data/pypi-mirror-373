from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field, model_validator


class ParamSpec(BaseModel):
    """파라미터 명세 - 최적화 탐색용"""

    default: Any
    range: List[Any]  # 탐색할 값들의 리스트
    description: str = ""

    @model_validator(mode="after")
    def check_default_in_range(self):
        if self.range is not None and self.default not in self.range:
            raise ValueError(f"Default value {self.default} not in range")
        return self

    def validate_value(self, value: Any) -> bool:
        """값이 유효한지 확인"""
        return value in self.range


class SignalParams(BaseModel):
    """시그널 파라미터 컨테이너 - 파라메트릭 서치용"""

    class Config:
        extra = "forbid"  # 정의되지 않은 파라미터 방지
        validate_assignment = True

    def __init__(self, **specs):
        super().__init__()
        # 먼저 속성 초기화
        self._specs: Dict[str, ParamSpec] = {}
        self._values: Dict[str, Any] = {}

        # 그 다음 파라미터 설정
        for name, spec_dict in specs.items():
            if isinstance(spec_dict, dict):
                spec = ParamSpec(**spec_dict)
                self._specs[name] = spec
                self._values[name] = spec.default

    def __getattr__(self, name: str) -> Any:
        """속성처럼 접근 가능 (예: params.momentum_window)"""
        if name.startswith("_"):  # private 속성은 그대로 처리
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )
        if name in self._values:
            return self._values[name]
        raise AttributeError(f"Parameter '{name}' not found")

    def update(self, **kwargs) -> None:
        """파라메트릭 서치시 값 업데이트"""
        for name, value in kwargs.items():
            if name not in self._specs:
                raise KeyError(f"Parameter '{name}' not defined")
            if not self._specs[name].validate_value(value):
                raise ValueError(f"Value {value} not in range for parameter '{name}'")
            self._values[name] = value

    @property
    def range(self) -> Dict[str, List]:
        return {name: spec.range for name, spec in self._specs.items()}

    @property
    def default(self) -> Dict[str, Any]:
        return {name: spec.default for name, spec in self._specs.items()}


class SignalConfig(BaseModel):
    """Signal configuration model"""

    universe: Literal["kr_stock", "us_stock"] = Field(
        ..., description="Trading Universe"
    )
    first_date: int = Field(
        ...,
        description="Data start date (YYYYMMDD) - rebalance anchor",
        ge=19900101,
        le=30000101,
    )
    data_list: List[str] = Field(..., description="Data list")

    data_lookback: int = Field(
        default=0,
        ge=0,
        description="Data lookback point",
    )
    signal_lookback: int = Field(
        default=0,
        ge=0,
        description="Previous signal reference point",
    )
