from dataclasses import dataclass
from pathlib import Path
from typing import List

from jinja2 import Environment, Template, PackageLoader, select_autoescape, ChoiceLoader, pass_environment


class Renderer:
    env: Environment
    index_template: Template
    progress_template: Template

    def __init__(self, package) -> None:
        self.env = Environment(
            loader=ChoiceLoader([
                PackageLoader(package),
            ]),
            autoescape=select_autoescape()
        )

        @pass_environment
        def template(env, x):
            t = x.template(env)
            return t.render(this=x)
        self.env.filters["template"] = template

        self.index_template = self.env.get_template(f"index.jinja")
        self.progress_template = self.env.get_template(f"progress.jinja")

    def render(self, result, progress=None):
        pass


class FileRenderer(Renderer):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__("gobexec.output.html")
        self.path = path

    def render(self, result, progress=None):
        result_template = result.template(self.env)
        template = self.progress_template if progress else self.index_template
        rendered = template.render(result_template=result_template, result=result, progress=progress)
        with self.path.open("w", buffering=1024 * 1024 * 20) as file:
            file.write(rendered)
            file.flush()


class ConsoleRenderer(Renderer):
    def __init__(self) -> None:
        super().__init__("gobexec.output.console")

    def render(self, result, progress=None):
        result_template = result.template(self.env)
        template = self.progress_template if progress else self.index_template
        rendered = template.render(result_template=result_template, result=result, progress=progress)
        print(rendered, end="", flush=True)


@dataclass
class MultiRenderer:
    renderers: List[Renderer]

    def render(self, result, progress=None):
        for renderer in self.renderers:
            renderer.render(result, progress)
