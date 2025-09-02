import warnings

warnings.filterwarnings(
    action="ignore"
)  # for clean logging, warning is not working on validation

import importlib.util
import os.path
import re
import sys
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from finter.framework_model.calendar import iter_trading_days, iter_trading_times
from finter.framework_model.exception.validation import (
    ModelValidationError,
    ModelValidationErrorMessage,
)
from finter.settings import log_with_traceback, logger
from finter.utils import with_spinner
from finter.utils.index import outsample_end_date
from finter.utils.model.frames import FrameUtil
from finter.utils.timer import timer

REVISION_PATTERN = [
    r".*\.resample\(.{1,20}\)\.sum\(\)",
    r".*\.resample\(.{1,20}\)\.std\(\)",
    r".*\.resample\(.{1,20}\)\.mean\(\)",
]

SLOW_PATTERN = [
    r"\.fillna\(False\)",
]

ITEM = namedtuple(
    "freq_validation",
    ["duration_sec", "validation_range", "validation_end", "date_format"],
)
DAYS = "days"
HOURS = "hours"
MINUTES = "minutes"

FREQ_TO_VALUE = {
    "1T": ITEM(
        20,
        {DAYS: 3, HOURS: 6, MINUTES: 0},
        {DAYS: 7, HOURS: 0, MINUTES: 0},
        "%Y%m%d%H%M",
    ),
    "10T": ITEM(
        200,
        {DAYS: 3, HOURS: 6, MINUTES: 0},
        {DAYS: 7, HOURS: 0, MINUTES: 0},
        "%Y%m%d%H%M",
    ),
    "30T": ITEM(
        600,
        {DAYS: 3, HOURS: 6, MINUTES: 0},
        {DAYS: 7, HOURS: 0, MINUTES: 0},
        "%Y%m%d%H%M",
    ),
    "1H": ITEM(
        600,
        {DAYS: 3, HOURS: 6, MINUTES: 0},
        {DAYS: 30, HOURS: 0, MINUTES: 0},
        "%Y%m%d%H%M",
    ),
    "2H": ITEM(
        1200,
        {DAYS: 3, HOURS: 6, MINUTES: 0},
        {DAYS: 30, HOURS: 0, MINUTES: 0},
        "%Y%m%d%H%M",
    ),
    "8H": ITEM(
        4800,
        {DAYS: 3, HOURS: 8, MINUTES: 0},
        {DAYS: 30, HOURS: 0, MINUTES: 0},
        "%Y%m%d%H%M",
    ),
    "1d": ITEM(
        10800,
        {DAYS: 90, HOURS: 0, MINUTES: 0},
        {DAYS: 730, HOURS: 0, MINUTES: 0},
        "%Y%m%d",
    ),
    "1d_oc": ITEM(
        10800,
        {DAYS: 90, HOURS: 0, MINUTES: 0},
        {DAYS: 730, HOURS: 0, MINUTES: 0},
        "%Y%m%d",
    ),
    "1W": ITEM(
        10800,
        {DAYS: 90, HOURS: 0, MINUTES: 0},
        {DAYS: 730, HOURS: 0, MINUTES: 0},
        "%Y%m%d",
    ),
    "1M": ITEM(
        10800,
        {DAYS: 90, HOURS: 0, MINUTES: 0},
        {DAYS: 730, HOURS: 0, MINUTES: 0},
        "%Y%m%d",
    ),
}


def compare_dfs(orig, variation):
    min_index = max(orig.index[0], variation.index[0])
    max_index = min(orig.index[-1], variation.index[-1])
    shared_columns = orig.columns.union(variation.columns)
    diff = orig.loc[min_index:max_index, shared_columns].copy().fillna(
        0
    ) - variation.loc[min_index:max_index, shared_columns].copy().fillna(0)

    diff_sum = diff.abs().sum(axis=1)
    assert diff_sum.max() < 100000, (
        f"diff at {diff_sum.idxmax()}, amount is {diff_sum.max()}, "
        f"orig start: {orig.index[0]} end: {orig.index[-1]}, "
        f"variation start: {variation.index[0]} end: {variation.index[-1]} "
    )


class PositionValidate:
    @staticmethod
    def compare(orig, variation):
        compare_dfs(orig, variation)

    @staticmethod
    def result(df):
        assert not df.empty, "empty result df"
        assert df.index.is_unique, "not unique index"
        assert df.index.is_all_dates, "not datetime index"
        assert df.index.is_monotonic, "not monotonic index"


class IValidation(object, metaclass=ABCMeta):
    @abstractmethod
    def validate(self):
        pass


class ValidationHelper(IValidation):
    """
    ValidationHelper is for Partial Validation of Model.
    It is simple version of Model Validation.

    >>> ValidationHelper("sample_alpha", model_info).validate()
    >>> ValidationHelper("sample_alpha", model_info).validate_start_dependency()
    >>> ValidationHelper("sample_alpha", model_info).validate_end_dependency()

    List of ValidationHelper methods:
    - validate_code(path: str, model: str) -> bool
        - model can be "alpha|portfolio"
    - validate_cm_loading(path: str, model: str) -> bool
        - model can be "alpha|portfolio"
    - validate_start_dependency()
    - validate_end_dependency()
    - validate()
        - do all kind of validation above
    """

    def __init__(self, model_path=None, model_info=None, start_date=None):
        self.__MODEL_PATH = model_path
        self.__MODEL_INFO = model_info

        self.exchange = model_info["exchange"]
        self.model_freq = model_info["freq"]

        if start_date:
            self.end = outsample_end_date(
                datetime.now(),
                n_week=1,
            )

            self.start_date = start_date
            self.end_date = self.times_before(
                self.end, timedelta(days=1), self.exchange, self.model_freq
            )

        else:
            self.end = outsample_end_date(
                datetime.now(),
                n_week=FREQ_TO_VALUE[self.model_freq].validation_end[DAYS] // 7,
            )

            # Validate index
            model_range = timedelta(**FREQ_TO_VALUE[self.model_freq].validation_range)

            self.start_date = self.times_before(
                self.end, model_range, self.exchange, self.model_freq
            )
            self.end_date = self.times_before(
                self.end, timedelta(days=1), self.exchange, self.model_freq
            )

        self.lmit_secs = FREQ_TO_VALUE[self.model_freq].duration_sec

        model_name = Path(model_path).stem

        # Check model path
        assert os.path.exists(model_path), f"model path not exists: {model_path}"

        # No space or dot in model name
        assert re.match(
            r"^[a-zA-Z0-9-_]+$", model_name
        ), f"Invalid model name: {model_name}, The model name can only contain alphabetic characters, numbers, hyphens, and underscores."

        self.FRAME = FrameUtil.frame(self.__MODEL_INFO["type"])
        self.module_file = Path(self.__MODEL_PATH) / (self.FRAME.F_NAME + ".py")

        self.__MODEL = self.model()

    def model(self):
        file_path = Path(self.module_file)
        module_name = file_path.stem
        file_directory = file_path.parent

        if str(file_directory) not in sys.path:
            sys.path.append(str(file_directory))

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            logger.error("Could not load the module.")
            return None
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            log_with_traceback(f"Error loading module: {e}")
            return None

        return getattr(module, self.FRAME.TYPE.title().replace("_", ""))()

    @timer
    def validate(self):
        assert ValidationHelper.validate_code(
            self.module_file, self.__MODEL_INFO["type"]
        ), "model contains (rolling / resmaple).sum() / .std() / .mean() or fillna(False)->replace(np.nan, False)"

        assert ValidationHelper.validate_cm_loading(
            self.module_file, self.__MODEL_INFO["type"]
        ), "Invalid baseclass: please use the correct baseclass for each model (ex:Alpha-> ONLY BaseAlpha can show in code)"

        self.validate_combine_getter()

        # self.validate_start_dependency()
        # self.validate_end_dependency()

    def validate_combine_getter(self):
        try:
            start_time = datetime.now()

            logger.info(
                f"validation start date: {self.start_date} / end date: {self.end_date}"
            )

            test_position = self.getter(self.__MODEL, self.start_date, self.end_date)
            duration_secs = (datetime.now() - start_time).total_seconds()
            test_idx = test_position.index

            expected_idx = list(
                iter_trading_times(
                    self.start_date,
                    self.end_date,
                    exchange=self.exchange,
                    freq=self.model_freq,
                )
            )
            expected_idx = pd.DatetimeIndex(expected_idx)

            if test_idx[0] < expected_idx[0] or test_idx[-1] > expected_idx[-1]:
                raise ModelValidationError(
                    ModelValidationErrorMessage.index_out_of_range_error(
                        self.start_date, self.end_date, test_idx, expected_idx
                    )
                )

            test_idx = test_idx[
                (test_idx >= expected_idx[0]) & (test_idx <= expected_idx[-1])
            ]
            missing_expected_indices = expected_idx[~expected_idx.isin(test_idx)]

            unexpected_indices = test_idx[~test_idx.isin(expected_idx)]
            if (len(missing_expected_indices) > 0) or (len(unexpected_indices) > 0):
                raise ModelValidationError(
                    ModelValidationErrorMessage.index_mismatch_error(
                        expected_idx, missing_expected_indices, unexpected_indices
                    )
                )

            # Validate duration
            if duration_secs > self.lmit_secs:
                raise ModelValidationError(
                    ModelValidationErrorMessage.duration_error(
                        duration_secs, self.lmit_secs
                    )
                )

            # Validate max position size
            max_size = test_position.abs().sum(axis=1).max()
            if max_size > 1e8 * 1.01:
                raise ModelValidationError(
                    ModelValidationErrorMessage.exceed_max_position_error(max_size)
                )

            # Validate all nan
            if any(test_position.count(axis=1) == 0):
                raise ModelValidationError(ModelValidationErrorMessage.all_nan_error())

        except ModelValidationError:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise e

    @with_spinner(
        text="[Validation - start dependency] Processing...",
        msg_success="[Validation - start dependency] Completed!",
    )
    def validate_start_dependency(self):
        def _getter(_end: datetime, _bef: int) -> pd.DataFrame:
            return self.__MODEL.get(
                self.times_before(
                    _end, timedelta(days=_bef), self.exchange, self.model_freq
                ),
                int(_end.strftime(FREQ_TO_VALUE[self.model_freq].date_format)),
            )

        orig = _getter(self.end, 1)
        variation = _getter(self.end, 20)
        variation2 = _getter(self.end, 100)

        assert_index_share(orig, variation)
        assert_max_dependency(orig, variation, "start")
        assert_max_dependency(variation2, variation, "start")

    @with_spinner(
        text="[Validation - end dependency] Processing...",
        msg_success="[Validation - end dependency] Completed!",
    )
    def validate_end_dependency(self):
        def _getter(_end: datetime, _bef: int) -> pd.DataFrame:
            return self.__MODEL.get(
                self.times_before(
                    _end, timedelta(days=100), self.exchange, self.model_freq
                ),
                self.times_before(
                    _end, timedelta(days=_bef), self.exchange, self.model_freq
                ),
            )

        orig = _getter(self.end, 0)

        for i in range(1, 64, 6):
            variation = _getter(self.end, i)
            assert_index_share(orig, variation)
            assert_max_dependency(orig, variation, "end")

    @staticmethod
    def validate_code(path: str, model="") -> bool:
        with open(path, "r", encoding="utf-8") as f:
            return _validate_patterns(f.read(), REVISION_PATTERN + SLOW_PATTERN)

    @staticmethod
    def validate_cm_loading(path: str, model="") -> bool:
        with open(path, "r", encoding="utf-8") as f:
            return _validate_patterns(f.read(), _base_pattern(model))

    @staticmethod
    def days_before(end, days, exchange="krx"):
        # days_before -> times_before
        def last_trading_day(end, exchange="krx"):
            start = end - timedelta(days=30)
            return int(
                list(iter_trading_days(start, end, exchange))[-1].strftime("%Y%m%d")
            )

        # return last trading day when days is 0
        d_before = end - timedelta(days=days)
        return last_trading_day(d_before, exchange)

    @staticmethod
    def times_before(end, times: timedelta, exchange="krx", freq="1d"):
        def last_trading_times(end, exchange="krx"):
            start = end - timedelta(days=30)
            date_format = FREQ_TO_VALUE[freq].date_format
            return int(
                list(iter_trading_times(start, end, exchange=exchange, freq=freq))[
                    -1
                ].strftime(date_format)
            )

        # return last trading day when time is 0
        t_before = end - times
        return last_trading_times(t_before, exchange)

    @staticmethod
    def getter(model, start, end):
        return model.get(start, end)


def assert_max_dependency(orig, variation, name):
    try:
        PositionValidate.compare(orig, variation)
    except AssertionError as e:
        msg = """
        There is %s dependency
        orig start: %s
        var start: %s
        orig end: %s
        var end: %s
        """ % (
            name,
            orig.index[0],
            variation.index[0],
            orig.index[-1],
            variation.index[-1],
        )
        logger.error(msg)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


def assert_index_share(orig, variation):
    share = orig.index.intersection(variation.index)
    assert len(share) > 0, "No index sharing %s, %s" % (orig.index, variation.index)


def _validate_patterns(code, patterns) -> bool:
    code = code.replace("\n", "")
    return all([re.search(p, code) is None for p in patterns])


def _base_pattern(model):
    all_ = {"BaseAlpha", "BasePortfolio", "BaseFund", "BaseFlexibleFund"}
    invalids = all_ - {"Base" + model.title().replace("_", "")}
    patterns = [r".*%s.*" % i for i in invalids]
    return patterns
