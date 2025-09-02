import importlib.util
import sys
import traceback
from pathlib import Path

import pandas as pd

from finter.framework_model.submission.config import ModelTypeConfig
from finter.settings import log_with_traceback, logger
from finter.utils.timer import timer


def load_model_instance(file_path, model_type="alpha"):
    """
    Dynamically loads a class from a given file path and creates an instance.

    :param file_path: Path to the file containing the model class.
    :param model_type: Type of the model (alpha or portfolio).
    :return: An instance of the model class or None if an error occurs.
    """
    class_name = ModelTypeConfig[model_type.upper()].class_name
    file_path = Path(file_path)
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

    try:
        Model = getattr(module, class_name)
        model_instance = Model()
        return model_instance
    except AttributeError as e:
        log_with_traceback(f"Error finding class {class_name} in the module: {e}")
        return None
    except Exception as e:
        logger.error(f"Error creating an instance of {class_name}: {e}")
        logger.error(traceback.format_exc())
        return None


@timer
def load_and_get_position(start, end, file_path, model_type="alpha") -> pd.DataFrame:
    """
    Loads a model instance and executes its 'get' method with start and end parameters.

    :param start: Start date for the position data.
    :param end: End date for the position data.
    :param file_path: Path to the file containing the model class.
    :param model_type: Type of the model (alpha or portfolio).
    """
    model_instance = load_model_instance(file_path, model_type)
    if model_instance is None:
        return None

    try:
        result = model_instance.get(start, end)
        logger.info(f"\nModel abs sum result: \n{result.abs().sum(axis=1).tail()}")
        return result
    except Exception as e:
        log_with_traceback(f"Error executing the 'get' method: {e}")
        return None
