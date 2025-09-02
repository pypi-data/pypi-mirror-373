from abc import ABCMeta, abstractmethod

from finter.framework_model import BaseAlpha, ContentModelLoader


class BaseCm(metaclass=ABCMeta):
    __CM_LOADER = ContentModelLoader()
    __cm_set = set()

    @abstractmethod
    def get(self, start, end):
        pass

    @classmethod
    def get_cm(cls, key):
        return BaseAlpha.get_cm(key)

    def depends(self):
        # ContentFactory load data with BaseAlpha
        return BaseAlpha.depends(BaseAlpha)


class BaseSm(metaclass=ABCMeta):
    @abstractmethod
    def get(self, start, end):
        pass

    def depends(self):
        pass
