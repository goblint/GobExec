from pathlib import Path

from jinja2 import Environment, Template, PackageLoader, select_autoescape


class Renderer:
    env: Environment
    page_template: Template

    def __init__(self) -> None:
        self.env = Environment(
            loader=PackageLoader("gobexec.output.html"),
            autoescape=select_autoescape()
        )
        self.page_template = self.env.get_template("page.html")

    def render(self, result, progress=None):
        pass


class FileRenderer(Renderer):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path

    def render(self, result, progress=None):
        result_template = result.template(self.env)
        rendered = self.page_template.render(result_template=result_template, result=result, progress=progress)
        with self.path.open("w", buffering=1024 * 1024 * 20) as file:
            file.write(rendered)
            file.flush()
