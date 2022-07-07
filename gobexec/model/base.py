from typing import Protocol

from jinja2 import Environment, Template


class Result(Protocol):
    def template(self, env: Environment) -> Template:
        ...
