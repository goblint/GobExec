import re
import resource
from typing import Any, Optional

from gobexec.goblint.bench.tools import AssertCount
from gobexec.goblint.result import AssertSummary, LineSummary
from gobexec.model.context import ExecutionContext, CompletedSubprocess
from gobexec.model.tool import Tool
from gobexec.model.tools import ResultExtractor


class AssertSummaryExtractor(ResultExtractor[AssertSummary]):
    name = "assert"

    assert_counter: Optional[Tool[Any, AssertCount]]

    def __init__(self, assert_counter: Optional[Tool[Any, AssertCount]] = None) -> None:
        self.assert_counter = assert_counter

    async def extract(self, ec: ExecutionContext[Any], cp: CompletedSubprocess) -> AssertSummary:
        stdout = cp.stdout.decode("utf-8")
        success = len(re.findall(r"\[Success]\[Assert]", stdout))
        warning = len(re.findall(r"\[Warning]\[Assert]", stdout))
        error = len(re.findall(r"\[Error]\[Assert]", stdout))
        if self.assert_counter:
            total = (await ec.get_tool_result(self.assert_counter)).total
            unreachable = total - (success + warning + error)
        else:
            unreachable = None
        return AssertSummary(success, warning, error, unreachable)