from typing import Any

from gobexec.goblint.bench.tools import AssertCount
from gobexec.goblint.result import AssertSummary
from gobexec.goblint.tool import ResultExtractor
from gobexec.model.context import ExecutionContext
from gobexec.model.tool import Tool


class AssertSummaryChecker(ResultExtractor[AssertSummary]):
    assert_counter: Tool[Any, AssertCount]

    def __init__(self, assert_counter: Tool[Any, AssertCount]) -> None:
        self.assert_counter = assert_counter

    async def extract(self, ec: ExecutionContext, stdout: bytes) -> AssertSummary:
        summary = await AssertSummary.extract(ec, stdout)
        summary.total = (await ec.get_tool_result(self.assert_counter)).total
        return summary
