import inspect
from typing import Callable, Dict

# from finter.data.data_handler.handler_data_market import AbstractDataHandler
from finter.data.data_handler.handler_abstract import AbstractDataHandler


class DataHandlerRegistry:
    handlers: Dict[str, "AbstractDataHandler"] = {}
    calculated_methods: Dict[str, Callable] = {}

    @classmethod
    def register_handler(cls, name: str):
        def decorator(handler_class: type):
            cls.handlers[name] = handler_class()
            return handler_class

        return decorator

    @classmethod
    def register_calculated_method(cls, name: str):
        def decorator(method: Callable):
            cls.calculated_methods[name] = method
            # Automatically detect dependencies
            source = inspect.getsource(method)
            dependencies = [
                handler_name
                for handler_name in cls.handlers.keys()
                if f"universe.{handler_name}" in source
            ]
            method.dependencies = dependencies
            return method

        return decorator
