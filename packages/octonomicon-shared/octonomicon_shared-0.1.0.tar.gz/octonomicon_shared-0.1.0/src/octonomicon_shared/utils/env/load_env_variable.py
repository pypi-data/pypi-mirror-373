import os
from typing import Literal, overload
from errors import EnvError

@overload
def load_env_variable(key: str) -> str:...
@overload
def load_env_variable(key: str, required: Literal[True]) -> str:...
@overload
def load_env_variable(key: str, required: Literal[False]) -> str | None:...


def load_env_variable(key: str, required: bool = True):
  value = os.getenv(key)

  if required and not value: raise EnvError(key)

  return value