from typing import Any

from gobexec.goblint.bench.tools import AssertCount
from gobexec.goblint.result import AssertSummary
from gobexec.goblint.tool import ResultExtractor
from gobexec.model.tool import Tool


class AssertSummaryChecker(ResultExtractor[AssertSummary]):
    assert_counter: Tool[Any, AssertCount]

    def __init__(self, assert_counter: Tool[Any, AssertCount]) -> None:
        self.assert_counter = assert_counter

    async def extract(self, ctx, stdout: bytes) -> AssertSummary:
        summary = await AssertSummary.extract(ctx, stdout)
        # TODO: better way to find other results
        for tool, result in zip(ctx.tools, ctx.results):
            if tool == self.assert_counter:
                summary.total = (await result).result.total
        return summary
