from abc import ABC, abstractmethod

from jinja2 import Environment, Template


class Result(ABC):
    @abstractmethod
    def template(self, env: Environment) -> Template:
        ...
