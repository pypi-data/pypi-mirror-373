import hashlib
import logging
import os
import traceback
import uuid

from dotenv import load_dotenv

import finter
from finter.api.user_api import UserApi
from finter.rest import ApiException

home_dir = os.path.expanduser("~")
dotenv_path = os.path.join(home_dir, ".env")
load_dotenv(dotenv_path)

logger = logging.getLogger("finter_sdk")
logger.setLevel(logging.INFO)

log_handler = logging.StreamHandler()
log_handler.setLevel(logging.INFO)  # 필요한 로깅 레벨 설정
logger.addHandler(log_handler)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)


def check_configuration():
    configuration = finter.Configuration()
    if configuration.api_key["Authorization"] == "Token ":
        error_message = (
            "API Key is not set. Your now using finter Open Version.\n\n"
            "You can set the API Key in one of the following ways:\n"
            "- By setting an environment variable directly in your environment:\n"
            "    import os\n"
            "    os.environ['FINTER_API_KEY'] = 'YOUR_API_KEY'\n\n"
            "- By adding the following line to a .env file located in the project root:\n"
            "    FINTER_API_KEY='YOUR_API_KEY'"
        )
        if not hasattr(check_configuration, "has_logged"):
            logger.info(error_message)
            check_configuration.has_logged = True
    return configuration


def get_api_client():
    return finter.ApiClient(check_configuration())


def log_section(title):
    original_formatter = log_handler.formatter

    log_handler.setFormatter(logging.Formatter("%(message)s"))

    separator = "=" * 40
    header = f"\n{separator} {title} {separator}"
    logger.info(header)

    log_handler.setFormatter(original_formatter)


def log_warning(message):
    original_formatter = log_handler.formatter

    log_handler.setFormatter(logging.Formatter("%(message)s"))

    logger.warning(message)

    log_handler.setFormatter(original_formatter)


def log_with_user_event(
    event_message, source, method, category, log_type=None, log_message=None
):
    if log_message:
        if log_type == "error":
            logger.error(log_message)
        elif log_type == "warning":
            logger.warning(log_message)
        elif log_type == "info":
            logger.info(log_message)
        else:
            pass
    user_event(event_message, source=source, method=method, category=category)


def log_with_traceback(message):
    logger.error(message)
    logger.error(traceback.format_exc())


def user_event(name, source="", method="", category=""):
    def _random_hash():
        random_uuid = uuid.uuid4()
        uuid_bytes = str(random_uuid).encode()
        hash_object = hashlib.sha256(uuid_bytes)
        return hash_object.hexdigest()

    params = {
        "name": name,
        "source": source,
        "method": method,
        "category": category,
        "rand": _random_hash(),
    }
    try:
        UserApi().log_usage_retrieve(**params)
    except ApiException as e:
        logger.error("Exception when calling UserApi->log_usage_retrieve: %s\n" % e)
