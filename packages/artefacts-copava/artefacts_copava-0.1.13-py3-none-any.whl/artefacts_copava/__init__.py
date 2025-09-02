from typing import Optional, Union

from .parsing import Parser
from .validating import Validator


def parse(config: Union[str, dict]) -> Optional[dict]:
    return Parser().parse(config)


def validate(config: dict) -> dict:
    return check(config)


def check(config: dict) -> dict:
    return Validator().check(config)
