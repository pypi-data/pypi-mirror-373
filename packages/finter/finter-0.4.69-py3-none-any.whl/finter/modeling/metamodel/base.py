import inspect
import itertools
import os
import re
from abc import ABCMeta
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, Iterator, List, Optional, Tuple, Type, Union

import pandas as pd
from pydantic import BaseModel

from finter import BaseAlpha, BasePortfolio
from finter.backtest.builder.main import SimulatorBuilder
from finter.data import ContentFactory
from finter.framework_model.submission.config import (
    ModelTypeConfig,
    ModelUniverseConfig,
)
from finter.framework_model.submission.helper_poetry import prepare_docker_submit_files
from finter.framework_model.submission.helper_submission import submit_model
from finter.settings import logger


def _datestr(date_int: int):
    date_str = str(date_int)
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"


SortKeyFunc = Callable[[pd.DataFrame], object]


def last_nav(e: pd.DataFrame):
    return -e["nav"][-1]  # reverse를 위해 -


class ModelClassMeta(ABCMeta):
    def __new__(
        cls, name, bases, dct
    ) -> Union[
        Type["BaseMetaAlpha"],
        Type["BaseMetaPortfolio"],
    ]:
        # workaround typing fix. (instead of Type["BaseMetaModel"])
        # BaseMetaModel can't represent BaseAlpha, BasePortfolio
        # because there is no base parent base model of BaseAlpha, BasePortfolio)

        return super().__new__(cls, name, bases, dct)


class BaseParameters(BaseModel):
    universe: ModelUniverseConfig

    @classmethod
    def from_field_combinations(
        cls: Type["BaseParameters"], **kwargs
    ) -> Iterator["BaseParameters"]:
        universe = kwargs.pop("universe")
        field_names = []
        value_combinations = []
        for field, values in kwargs.items():
            if field in cls.__fields__:
                field_names.append(field)
                value_combinations.append(values)
            else:
                raise ValueError(
                    f"Field '{field}' is not valid for class {cls.__name__}"
                )

        # itertools.product를 사용해 가능한 모든 조합 생성
        for combination in itertools.product(*value_combinations):
            instance_data = dict(zip(field_names, combination))
            instance_data["universe"] = universe
            yield cls(**instance_data)


class BaseMetaModel(metaclass=ModelClassMeta):
    _param: Optional[BaseParameters] = None
    _model_type: ModelTypeConfig = (
        ModelTypeConfig.ALPHA
    )  # 기본 model type은 ALPHA. PORTFOLIO, FUND는 변경해서 사용해야 함

    class Parameters(BaseParameters): ...

    universe: ModelUniverseConfig = ModelUniverseConfig.KR_STOCK

    @classmethod
    def params_from_field_combinations(
        cls, **kwargs
    ) -> Iterator["BaseMetaModel.Parameters"]:
        universe = kwargs.pop("universe")
        field_names = []
        value_combinations = []

        for field, values in kwargs.items():
            if field in cls.Parameters.model_fields:
                field_names.append(field)
                value_combinations.append(values)
            else:
                raise ValueError(
                    f"Field '{field}' is not valid for class {cls.Parameters.__name__}"
                )

        for combination in itertools.product(*value_combinations):
            instance_data = dict(zip(field_names, combination))
            instance_data["universe"] = universe
            yield cls.Parameters(**instance_data)

    def get_default_price(self, start: int, end: int):
        price = ContentFactory(
            self.universe.get_content_base_name(), start, end
        ).get_df("price_close", fill_nan=False)
        return price

    def simulate(
        self,
        position: Optional[pd.DataFrame] = None,
        start: int = 0,
        end: int = 0,
        price: Optional[pd.DataFrame] = None,
        initial_cash: float = 1e8,
        buy_fee_tax: float = 0,
        sell_fee_tax: float = 30,
        slippage: float = 10,
    ) -> pd.DataFrame:
        assert (position is not None) or (start != 0 and end != 0)

        if position is None:
            position = self.get(start, end)  # type:ignore

        assert position is not None

        if start == 0:
            start = position.index.min()
            if price is not None:
                start = max(start, price.index.min())

            start = int(start.strftime("%Y%m%d"))  # type:ignore

        if end == 0:
            end = position.index.max()
            if price is not None:
                end = min(end, price.index.max())

            end = int(end.strftime("%Y%m%d"))  # type:ignore

        if price is None:
            price = self.get_default_price(start, end)

        assert price is not None

        builder = SimulatorBuilder()
        (
            builder.update_data(price=price)
            .update_trade(initial_cash=initial_cash)
            .update_cost(
                buy_fee_tax=buy_fee_tax, sell_fee_tax=sell_fee_tax, slippage=slippage
            )
        )
        sim = builder.build(position)

        return sim.run()

    def plot_nav(
        self,
        start: int,
        end: int,
        initial_cash: float = 1e8,
        buy_fee_tax: float = 0,
        sell_fee_tax=30,
        slippage: float = 10,
    ):
        sim_res = self.simulate(
            start=start,
            end=end,
            initial_cash=initial_cash,
            buy_fee_tax=buy_fee_tax,
            sell_fee_tax=sell_fee_tax,
            slippage=slippage,
        )
        sim_res["nav"].plot()

    @classmethod
    def grid_search_parameters(
        cls,
        start: int,
        end: int,
        param_iter: Iterator["BaseMetaModel.Parameters"],
        sort_key: SortKeyFunc = last_nav,
    ) -> List[Tuple["BaseMetaModel.Parameters", pd.DataFrame]]:
        """
        :param sort_key: function to use sort simulation summary. default is last_nav ( ex. last_nav = lambda summary: summary["nav"][-1])
        :returns: list of tuple (param, simulation_result dataframe)
        """
        # price는 한번 loading해서 계속 사용하기 위해
        price = None

        res = []
        for i, params in enumerate(param_iter):
            try:
                logger.info(f"running {i}th param")
                model = cls.create(params=params)
                mi = model()
                if price is None:
                    price = mi.get_default_price(start, end)

                sim_res = mi.simulate(start=start, end=end, price=price)
                res.append((params, sim_res))

            except Exception as e:
                logger.error(f"{params.dict()} has errror : {e}")

        res.sort(key=lambda e: sort_key(e[1]))
        return res

    @staticmethod
    def cleanup_position(position: pd.DataFrame):
        df_cleaned = position.loc[:, ~((position == 0) | (position.isna())).all(axis=0)]
        df_cleaned = df_cleaned.fillna(0)
        return df_cleaned

    @classmethod
    def get_model_info(cls):
        if cls._model_type is None:
            raise ValueError("metamodel's model type is unknown")
        return cls.universe.get_config(cls._model_type)

    @classmethod
    def create(cls, params: BaseParameters):
        dct = params.dict()
        dct["_param"] = params

        model_cls_name = cls._model_type.class_name
        clz = ModelClassMeta(model_cls_name, (cls,), dct)
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
        Submits the model to the Finter platform.

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
        model_cls_name = cls._model_type.class_name

        return f"""
from {module_path} import {meta_model.__name__}

param_json = r'{jsonstr}'
params = {meta_model.__name__}.Parameters.parse_raw(param_json)
{model_cls_name} = {meta_model.__name__}.create(params)
"""


class BaseMetaAlpha(BaseAlpha, BaseMetaModel):
    _model_type: ModelTypeConfig = ModelTypeConfig.ALPHA


class BaseMetaPortfolio(BasePortfolio, BaseMetaModel):
    _model_type: ModelTypeConfig = ModelTypeConfig.PORTFOLIO

    alpha_list: List[str] = list()

    class Parameters(BaseParameters):
        alpha_list: List[str]

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

            prepare_docker_submit_files(modeldir, gpu=None, image=None)

            return submit_model(
                model_info, str(modeldir), docker_submit=True, staging=staging
            )
