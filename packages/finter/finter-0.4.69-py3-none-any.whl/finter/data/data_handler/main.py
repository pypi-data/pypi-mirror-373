from datetime import datetime
from functools import wraps
from typing import Any, Callable, List

from cachetools import TTLCache

from finter.data.content_model.loader import ContentFactory
from finter.data.data_handler.handler_data_market import register_handlers
from finter.data.data_handler.handler_mmap import MmapMemoryManager
from finter.data.data_handler.registry import DataHandlerRegistry
from finter.data.load import ModelData


class Universe:
    def __init__(self, name: str, data_handler):
        self.name = name
        self.data_handler = data_handler

    def __getattr__(self, name: str) -> Callable:
        if name in self.data_handler.handlers:

            @wraps(self.data_handler.handlers[name].get_data)
            def wrapper(**kwargs) -> Any:
                return self.data_handler.get_cached_data(name, self.name, **kwargs)

            return wrapper
        elif name in self.data_handler.calculated_methods:
            return lambda **kwargs: self.data_handler.calculated_methods[name](
                self, **kwargs
            )
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __repr__(self) -> str:
        return (
            f"Universe(name='{self.name}', available_methods={self.available_methods})"
        )

    @property
    def available_methods(self) -> List[str]:
        methods = []
        for method_name, method in self.data_handler.handlers.items():
            if self.name in method.item_mapping:
                methods.append(method_name)

        for method_name, method in self.data_handler.calculated_methods.items():
            if all(dep in methods for dep in method.dependencies):
                methods.append(method_name)

        return methods


class DataHandler(DataHandlerRegistry):
    def __init__(
        self,
        start: int,
        end: int,
        cache_timeout: int = 0,
        cache_maxsize: int = 5,
    ):
        super().__init__()
        register_handlers()  # 명시적으로 핸들러들 등록
        self.cf = ContentFactory("raw", start, end)
        self.cache_timeout = cache_timeout
        self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_timeout)

    def __getattr__(self, name: str) -> Universe:
        return Universe(name, self)

    def __repr__(self) -> str:
        universes = self.available_universes
        return f"DataHandler(available_universes={universes})"

    @property
    def available_universes(self) -> List[str]:
        universes = set()
        for handler in self.handlers.values():
            universes.update(handler.item_mapping.keys())
        return list(universes)

    def get_cached_data(self, handler_name: str, universe: str, **kwargs):
        cache_key = (handler_name, universe, frozenset(kwargs.items()))
        if cache_key not in self.cache:
            data = self.handlers[handler_name].get_data(self.cf, universe, **kwargs)
            self.cache[cache_key] = data
        return self.cache[cache_key]

    def get_cached_model(self, model_id: str):
        cache_key = (model_id,)
        if cache_key not in self.cache:
            data = ModelData.load(model_id)
            self.cache[cache_key] = data
        return self.cache[cache_key]

    def load(self, model_id: str):
        return self.get_cached_model(model_id)

    def universe(self, name: str) -> Universe:
        return Universe(name, self)


class MmapHandler(DataHandlerRegistry):
    def __init__(
        self,
        start: int,
        end: int,
        cache_timeout: int = 0,  # Not used
        cache_maxsize: int = 5,  # Not used
        mmap_dir: str = None,
    ):
        super().__init__()
        register_handlers()
        self.mmap_manager = MmapMemoryManager(mmap_dir)
        self.start = start
        self.end = end

    def __getattr__(self, name: str) -> Universe:
        return Universe(name, self)

    def __repr__(self) -> str:
        universes = self.available_universes
        return f"MmapHandler(available_universes={universes})"

    @property
    def available_universes(self) -> List[str]:
        universes = set()
        for handler in self.handlers.values():
            universes.update(handler.item_mapping.keys())
        return list(universes)

    def get_cached_data(self, handler_name: str, universe: str, **kwargs):
        sub_universe = kwargs.pop("sub_universe", None)
        if sub_universe:
            return self.mmap_manager.get(f"{universe}_{handler_name}_{sub_universe}")
        else:
            return self.mmap_manager.get(f"{universe}_{handler_name}")

    def get_cached_model(self, model_id: str):
        return self.mmap_manager.get(f"model_{model_id}")

    def load(self, model_id: str):
        return self.get_cached_model(model_id)

    def universe(self, name: str) -> Universe:
        return Universe(name, self)


class CacheHandler:
    @staticmethod
    def backtest(
        start=20150101,
        end=int(datetime.now().strftime("%Y%m%d")),
        cache_timeout=300,
        cache_maxsize=5,
    ):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                self.start = start
                self.end = end

                if not hasattr(self, "data_handler"):
                    self.data_handler = DataHandler(
                        start,
                        end,
                        cache_timeout=cache_timeout,
                        cache_maxsize=cache_maxsize,
                    )

                return func(self, *args, **kwargs)

            return wrapper

        return decorator


if __name__ == "__main__":
    dh = DataHandler(20240601, 20240630, cache_timeout=500)

    mh = MmapHandler(20240601, 20240630, cache_timeout=500)
    print(dh.kr_stock.price())
    print(dh.kr_stock.price._52week_high())
