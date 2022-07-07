import re
from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class RaceSummary:
    safe: int
    vulnerable: int
    unsafe: int
    # total: int

    def template(self, env):
        return env.get_template("racesummary.jinja")

    @staticmethod
    async def extract(stdout) -> 'RaceSummary':
        stdout = stdout.decode("utf-8")
        safe = int(re.search(r"safe:\s+(\d+)", stdout).group(1))
        vulnerable = int(re.search(r"vulnerable:\s+(\d+)", stdout).group(1))
        unsafe = int(re.search(r"unsafe:\s+(\d+)", stdout).group(1))
        return RaceSummary(safe, vulnerable, unsafe)


@dataclass
class AssertSummary:
    success: int
    warning: int
    error: int
    total: Optional[int] = None

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
    async def extract(ctx, stdout) -> 'AssertSummary':
        stdout = stdout.decode("utf-8")
        success = len(re.findall(r"\[Success]\[Assert]", stdout))
        warning = len(re.findall(r"\[Warning]\[Assert]", stdout))
        error = len(re.findall(r"\[Error]\[Assert]", stdout))
        return AssertSummary(success, warning, error)


@dataclass
class AssertSummaryChecker:
    assert_counter: Any

    async def extract(self, ctx, stdout):
        summary = await AssertSummary.extract(ctx, stdout)
        # TODO: better way to find other results
        for tool, result in zip(ctx.tools, ctx.results):
            if tool == self.assert_counter:
                summary.total = (await result).result.total
        return summary
