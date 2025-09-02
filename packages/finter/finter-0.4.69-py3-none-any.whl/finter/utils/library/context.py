import builtins
import sys

from finter.settings import logger

_dependencies = dict()
_parent = None


class LibraryContext:
    def __init__(self, path, module_name):
        self.__path = path
        self.__builtin_import = builtins.__import__
        self.__parent = None
        self.__md_name = module_name
        logger.debug(self.__md_name)

    def __enter__(self):
        logger.info(self.__path)
        self.__model_cache = self.__get_global_keyset()
        sys.path.insert(0, self.__path)
        builtins.__import__ = self.__import
        exec('import %s' % self.__md_name)
        return sys.modules[self.__md_name]

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.path.remove(self.__path)
        builtins.__import__ = self.__builtin_import
        pass

    @staticmethod
    def __get_global_keyset():
        return set(sys.modules.keys())

    def __module_refresh(self, cache):
        for md in (self.__get_global_keyset() - cache):
            del sys.modules[md]

    def __import(self, name, globals=None, locals=None, fromlist=None, level=0):
        global _parent
        parent = _parent
        _parent = name

        m = self.__builtin_import(name, globals, locals, fromlist, level)

        if parent is not None and hasattr(m, '__file__'):
            l = _dependencies.setdefault(parent, [])
            l.append(m)

        _parent = parent

        return m
