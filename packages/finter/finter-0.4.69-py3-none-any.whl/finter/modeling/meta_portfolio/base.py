import os
from pathlib import Path
import re
import inspect

from tempfile import TemporaryDirectory
from contextlib import contextmanager

from abc import ABCMeta
from typing import Optional, Type, Set
from pydantic import BaseModel

from finter import BasePortfolio
from finter.data import ContentFactory, ModelData
from finter.settings import logger
from finter.framework_model.submission.helper_submission import submit_model


from finter.framework_model.submission.config import (
    ModelTypeConfig,
    ModelUniverseConfig,
)


def _datestr(date_int: int):
    date_str = str(date_int)
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"


class AlphaLoader:
    """to support legacy portfolio"""

    def __init__(self, start: int, end: int):
        self.start = _datestr(start)
        self.end = _datestr(end)

    def get_alpha(self, alpha):
        return ModelData.load("alpha." + alpha).loc[self.start : self.end]


class PortfolioClassMeta(ABCMeta):
    def __new__(cls, name, bases, dct) -> Type["BaseMetaPortfolio"]:
        return super().__new__(cls, name, bases, dct)


class BaseParameters(BaseModel):
    universe: ModelUniverseConfig
    alpha_set: Set[str]


class BaseMetaPortfolio(BasePortfolio, metaclass=PortfolioClassMeta):
    _param: Optional[BaseParameters] = None
    _model_type = ModelTypeConfig.PORTFOLIO

    class Parameters(BaseParameters): ...

    universe: ModelUniverseConfig = ModelUniverseConfig.KR_STOCK
    alpha_set: Set[str] = set()

    def alpha_loader(self, start: int, end: int):
        return AlphaLoader(start, end)

    @classmethod
    def get_model_info(cls):
        return cls.universe.get_config(cls._model_type)

    @classmethod
    def create(cls, params: BaseParameters):
        dct = params.dict()
        dct["_param"] = params

        clz = PortfolioClassMeta("Portfolio", (cls,), dct)
        return clz

    # @classmethod
    # def generate_model_submit_zip_file(cls, temporary=T) -> str:

    @classmethod
    def submit(
        cls,
        model_name: str,
        staging: bool = False,
        outdir: Optional[str] = None,
        **kwargs,
    ):
        """
        Submits the portfolio model to the Finter platform.

        :param docker_submit: Whether to submit the model using Docker.
        :param outdir: if not null, submitted code and json file are saved.
        :return: The result of the submission if successful, None otherwise.
        """

        @contextmanager
        def nullcontext():
            yield outdir

        context = TemporaryDirectory() if outdir is None else nullcontext()

        with context as odir:
            assert odir is not None

            source = cls.get_submit_code()

            modeldir = Path(odir) / model_name

            os.makedirs(modeldir, exist_ok=True)
            with open(
                modeldir / cls._model_type.file_name, "w", encoding="utf-8"
            ) as fd:
                fd.write(source)

            model_info = cls.get_model_info()

            if "insample" in kwargs:
                insample = kwargs.pop("insample")

                if not re.match(r"^\d+ days$", insample):
                    raise ValueError("insample should be like '100 days'")

                model_info["insample"] = insample

            if kwargs:
                logger.warn(f"Unused parameters: {kwargs}")

            res = submit_model(
                model_info, str(modeldir), docker_submit=False, staging=staging
            )

        return res

    @classmethod
    def get_source_code(cls):
        return inspect.getsource(cls.__bases__[0])

    @classmethod
    def get_submit_code(cls):
        meta_model = cls.__bases__[0]
        module_path = meta_model.__module__
        param = cls._param
        jsonstr = param.json()

        return f"""
from {module_path} import {meta_model.__name__}

param_json = r'{jsonstr}'
params = {meta_model.__name__}.Parameters.parse_raw(param_json)
Portfolio = {meta_model.__name__}.create(params)
"""
