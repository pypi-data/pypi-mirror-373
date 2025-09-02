import os

from dotenv import load_dotenv

load_dotenv()


def get_env_variable(var_name):
    value = os.getenv(var_name, None)
    if value is None:
        value = input(f"Enter your {var_name}: ")
    return value
