from abc import ABC, abstractmethod
from enum import Enum, auto

from jinja2 import Environment, Template


# noinspection PyArgumentList
class ResultKind(Enum):
    DEFAULT = auto()
    SUCCESS = auto()
    WARNING = auto()
    FAILURE = auto()
    ERROR = auto()


class Result(ABC):
    @abstractmethod
    def template(self, env: Environment) -> Template:
        ...

    @property
    def kind(self) -> ResultKind:
        return ResultKind.DEFAULT
