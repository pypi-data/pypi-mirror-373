import os
from typing import Literal, overload
from octonomicon_shared.errors import EnvError
from dotenv import load_dotenv


@overload
def load_env_variable(key: str, *, dotenv_path: str | None = None) -> str: ...


@overload
def load_env_variable(
    key: str, *, required: Literal[True], dotenv_path: str | None = None) -> str: ...


@overload
def load_env_variable(
    key: str, *, required: Literal[False], dotenv_path: str | None = None) -> str | None: ...


def load_env_variable(key: str, *, required: bool = True, dotenv_path: str | None = None):
    value = os.getenv(key)

    if not value:
        load_dotenv(dotenv_path)
        value = os.getenv(key)

    if required and not value:
        raise EnvError(key)

    return value
