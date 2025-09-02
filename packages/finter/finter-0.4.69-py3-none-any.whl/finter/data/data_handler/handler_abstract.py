from abc import ABC, abstractmethod
from typing import Any

from finter.data import ContentFactory


class AbstractDataHandler(ABC):
    @abstractmethod
    def get_data(self, cf: ContentFactory, universe: str, **kwargs) -> Any:
        pass
