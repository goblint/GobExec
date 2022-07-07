import re
from dataclasses import dataclass
from typing import Optional

from gobexec.model.base import Result
from gobexec.model.context import ExecutionContext


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
    async def extract(ec: ExecutionContext, stdout: bytes) -> 'RaceSummary':
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
    unreachable: Optional[int] = None

    def __init__(self,
                 success: int,
                 warning: int,
                 error: int,
                 unreachable: Optional[int] = None
                 ) -> None:
        self.success = success
        self.warning = warning
        self.error = error
        self.unreachable = unreachable

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
