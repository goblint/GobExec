from dataclasses import dataclass
from pathlib import Path
from typing import List

from jinja2 import Environment, Template, PackageLoader, select_autoescape, ChoiceLoader, FunctionLoader


class Renderer:
    env: Environment
    page_template: Template

    def __init__(self, package) -> None:
        self.env = Environment(
            loader=ChoiceLoader([
                PackageLoader(package),
                FunctionLoader(lambda name: "")
            ]),
            autoescape=select_autoescape()
        )
        self.page_template = self.env.get_template(f"page.jinja")

    def render(self, result, progress=None):
        pass


class FileRenderer(Renderer):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__("gobexec.output.html")
        self.path = path

    def render(self, result, progress=None):
        result_template = result.template(self.env)
        rendered = self.page_template.render(result_template=result_template, result=result, progress=progress)
        with self.path.open("w", buffering=1024 * 1024 * 20) as file:
            file.write(rendered)
            file.flush()


class ConsoleRenderer(Renderer):
    def __init__(self) -> None:
        super().__init__("gobexec.output.console")

    def render(self, result, progress=None):
        result_template = result.template(self.env)
        rendered = self.page_template.render(result_template=result_template, result=result, progress=progress)
        print(rendered, end="", flush=True)


@dataclass
class MultiRenderer:
    renderers: List[Renderer]

    def render(self, result, progress=None):
        for renderer in self.renderers:
            renderer.render(result, progress)
