from datetime import datetime
from enum import Enum
from typing import List, Sequence, Union


class DataType(Enum):
    STOCK = "stock"  # (T, N, F)
    MACRO = "macro"  # (T, F)
    ENTITY = "entity"  # (N, F)
    STATIC = "static"  # (F)


T_TYPE = List[datetime]
N_TYPE = Sequence[Union[str, int, float]]
F_TYPE = List[str]

F_INPUT_TYPE = str
