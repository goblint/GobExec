import re
from dataclasses import dataclass
from typing import Optional, Any, ForwardRef

# from gobexec.goblint import ResultExtractor
# from gobexec.goblint.bench.tools import AssertCount
from gobexec.model.result import Result
from gobexec.model.tool import Tool


@dataclass(init=False)
class RaceSummary(Result):
    safe: int
    vulnerable: int
    unsafe: int
    # total: int

    def __init__(self,
                 safe: int,
                 vulnerable: int,
                 unsafe: int
                 ) -> None:
        self.safe = safe
        self.vulnerable = vulnerable
        self.unsafe = unsafe

    def template(self, env):
        return env.get_template("racesummary.jinja")

    @staticmethod
    async def extract(stdout: bytes) -> 'RaceSummary':
        stdout = stdout.decode("utf-8")
        safe = int(re.search(r"safe:\s+(\d+)", stdout).group(1))
        vulnerable = int(re.search(r"vulnerable:\s+(\d+)", stdout).group(1))
        unsafe = int(re.search(r"unsafe:\s+(\d+)", stdout).group(1))
        return RaceSummary(safe, vulnerable, unsafe)


@dataclass(init=False)
class AssertSummary(Result):
    success: int
    warning: int
    error: int
    total: Optional[int] = None

    def __init__(self,
                 success: int,
                 warning: int,
                 error: int,
                 total: Optional[int] = None
                 ) -> None:
        self.success = success
        self.warning = warning
        self.error = error
        self.total = total

    def template(self, env):
        return env.get_template("assertsummary.jinja")

    @property
    def kind(self):
        # TODO: generalize to all results
        if self.success == 0:
            return "danger"
        elif self.warning == 0 and self.error == 0:
            return "success"
        else:
            return "warning"

    @staticmethod
    async def extract(ctx, stdout: bytes) -> 'AssertSummary':
        stdout = stdout.decode("utf-8")
        success = len(re.findall(r"\[Success]\[Assert]", stdout))
        warning = len(re.findall(r"\[Warning]\[Assert]", stdout))
        error = len(re.findall(r"\[Error]\[Assert]", stdout))
        return AssertSummary(success, warning, error)


class AssertSummaryChecker:
    assert_counter: Tool[Any, 'AssertCount']

    def __init__(self, assert_counter: Tool[Any, 'AssertCount']) -> None:
        self.assert_counter = assert_counter

    async def extract(self, ctx, stdout: bytes) -> AssertSummary:
        summary = await AssertSummary.extract(ctx, stdout)
        # TODO: better way to find other results
        for tool, result in zip(ctx.tools, ctx.results):
            if tool == self.assert_counter:
                summary.total = (await result).result.total
        return summary
