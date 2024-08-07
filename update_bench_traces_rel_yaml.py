from pathlib import Path

import gobexec.main
from gobexec.goblint.bench import txtindex
from gobexec.goblint.result import AssertTypeSummary, YamlSummary
from gobexec.goblint.tool import GoblintTool

from gobexec.model.result import TimeResult
from gobexec.model.tools import ExtractTool
from gobexec.output.renderer import FileRenderer, ConsoleRenderer, MultiRenderer

goblint_witness = GoblintTool(
    name="witness_gen",
    program=str(Path("../analyzer/goblint").absolute()),
    args=["--conf", str(Path("../analyzer/conf/traces-rel.json").absolute()), "--enable", "warn.debug", "--enable",
          "witness.yaml.enabled", "--set", "ana.activated[+]", "apron", "--set", "ana.path_sens[+]", "threadflag", "--set", "ana.relation.privatization", "mutex-meet-tid-cluster12", "--set", "witness.yaml.entry-types[-]", "invariant_set"],
    dump='witness'

)


def index_tool_factory(name, args):
    goblint = GoblintTool(
        name=name,
        program=str(Path("../analyzer/goblint").absolute()),
        args=["--conf", str(Path("../analyzer/conf/traces-rel.json").absolute()), "--enable", "allglobs", "--enable", "dbg.timing.enabled", "--enable", "warn.debug", "-v"] + args,
        validate=goblint_witness
    )

    return ExtractTool(
        goblint,
        TimeResult,
        YamlSummary,

    )

# TODO: HTML columns broken

matrix = txtindex.load(Path("../bench/index/traces-rel-yaml.txt").absolute(), index_tool_factory)
matrix.tools.insert(0,goblint_witness)
html_renderer = FileRenderer(Path("out.html"))
console_renderer = ConsoleRenderer()
renderer = MultiRenderer([html_renderer, console_renderer])

gobexec.main.run(matrix, renderer)