import re
import resource
from dataclasses import dataclass
from typing import Optional, Any

from gobexec.model.base import Result, ResultKind
from gobexec.model.context import ExecutionContext, CompletedSubprocess


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
    async def extract(ec: ExecutionContext[Any], cp: CompletedSubprocess) -> 'RaceSummary':
        stdout = cp.stdout.decode("utf-8")
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
        bad = self.warning + self.error
        good = self.success + (self.unreachable or 0)
        if good == 0:
            return ResultKind.FAILURE
        elif bad == 0:
            return ResultKind.SUCCESS
        else:
            return ResultKind.WARNING


@dataclass(init=False)
class Rusage(Result):
    rusage: resource.struct_rusage

    def __init__(self, rusage) -> None:
        super().__init__()
        self.rusage = rusage

    def template(self, env):
        return env.from_string("{{ this.rusage }}")

    @staticmethod
    async def extract(ec: ExecutionContext[Any], cp: CompletedSubprocess) -> 'Rusage':
        return Rusage(cp.rusage)


@dataclass(init=False)
class LineSummary(Result):
    live: int
    dead: int
    total: int

    def __init__(self, live: int, dead: int, total: int):
        self.live = live
        self.dead = dead
        self.total = total

    def template(self, env):
        return env.get_template("linesummary.jinja")

    @staticmethod
    async def extract(ec: ExecutionContext[Any], cp: CompletedSubprocess) -> 'LineSummary':
        stdout = cp.stdout.decode("utf-8")
        live = re.search(r"live:[ ]*([0-9]*)", stdout)
        dead = re.search(r"dead:[ ]*([0-9]*)", stdout)
        if live is None and dead is None:
            return LineSummary(-1, -1, -1)
        else:
            total = int(live.group(1)) + int(dead.group(1))
            return LineSummary(int(live.group(1)), int(dead.group(1)), total)


@dataclass(init=False)
class ThreadSummary(Result):
    thread_id: int
    unique_thread_id: int
    max_protected: int
    sum_protected: int
    mutexes_count: int

    def __init__(self, thread_id: int, unique_thread_id: int,
                 max_protected: int, sum_protected: int, mutexes_count: int):
        self.thread_id = thread_id
        self.unique_thread_id = unique_thread_id
        self.max_protected = max_protected
        self.sum_protected = sum_protected
        self.mutexes_count = mutexes_count

    def template(self, env):
        return env.get_template("threadsummary.jinja")

    @staticmethod
    async def extract(ec: ExecutionContext[Any], cp: CompletedSubprocess) -> 'ThreadSummary':
        stdout = cp.stdout.decode("utf-8")
        thread_id = re.search(r"Encountered number of thread IDs \(unique\): ([0-9]*)", stdout)
        thread_id = 0 if thread_id is None else int(thread_id.group(1))
        unique_thread_id = re.search(r"Encountered number of thread IDs \(unique\): [0-9]* \(([0-9]*)\)", stdout)
        unique_thread_id = 0 if unique_thread_id is None else int(unique_thread_id.group(1))
        max_protected = re.search(r"Max number variables of protected by a mutex: ([0-9]*)", stdout)
        max_protected = 0 if max_protected is None else int(max_protected.group(1))
        sum_protected = re.search(r"Total number of protected variables \(including duplicates\): ([0-9]*)", stdout)
        sum_protected = 0 if sum_protected is None else int(sum_protected.group(1))
        mutexes_count = re.search(r"Number of mutexes: ([0-9]*)", stdout)
        mutexes_count = 0 if mutexes_count is None else int(mutexes_count.group(1))

        return ThreadSummary(thread_id, unique_thread_id, max_protected, sum_protected, mutexes_count)


@dataclass(init=False)
class AssertTypeSummary(Result):
    success: int
    unknown: int

    def __init__(self, success: int, unknown: int):
        self.success = success
        self.unknown = unknown

    def template(self, env):
        return env.get_template("asserttypesummary.jinja")

    @staticmethod
    async def extract(ec: ExecutionContext[Any], cp: CompletedSubprocess) -> 'AssertTypeSummary':
        stdout = cp.stdout.decode("utf-8")
        success = len(re.findall(r"\[Success\]\[Assert\]", stdout))

        unknown = len(re.findall(r"\[Warning\]\[Assert\]", stdout))
        return AssertTypeSummary(success, unknown)


@dataclass(init=False)
class YamlSummary(Result):
    confirmed: int
    unconfirmed: int

    def __init__(self, success: int, unknown: int):
        self.success = success
        self.unknown = unknown

    def template(self, env):
        return env.get_template("yamlsummary.jinja")

    @staticmethod
    async def extract(ec: ExecutionContext[Any], cp: CompletedSubprocess) -> 'AssertTypeSummary':
        stdout = cp.stdout.decode("utf-8")
        confirmed = re.search(r"  confirmed:[ ]*([0-9]*)", stdout)
        confirmed = 0 if confirmed is None else confirmed.group(1)
        unconfirmed = re.search(r"  unconfirmed:[ ]*([0-9]*)", stdout)
        unconfirmed = 0 if unconfirmed is None else unconfirmed.group(1)
        return AssertTypeSummary(int(confirmed), int(unconfirmed))


dataclass(init=False)


class ConcratSummary(Result):
    safe: int
    vulnerable: int
    unsafe: int
    uncalled: int

    def __init__(self, safe: int, vulnerable: int, unsafe: int, uncalled: int):
        self.safe = safe
        self.vulnerable = vulnerable
        self.unsafe = unsafe
        self.uncalled = uncalled

    def template(self, env):
        return env.get_template("concratresult.jinja")

    @staticmethod
    async def extract(ec: ExecutionContext[Any], cp: CompletedSubprocess) -> "ConcratSummary":
        stdout = cp.stdout.decode("utf-8")
        safe = re.search(r"[^n]safe:[ ]*([0-9]*)", stdout)
        safe = -1 if safe is None else safe.group(1)
        vulnerable = re.search(r"vulnerable:[ ]*([0-9]*)", stdout)
        vulnerable = -1 if vulnerable is None else vulnerable.group(1)
        unsafe = re.search(r"unsafe:[ ]*([0-9]*)", stdout)
        unsafe = -1 if unsafe is None else unsafe.group(1)
        uncalled = re.findall(r"will never be called", stdout)
        for elem in uncalled:
            if bool(re.search(r"__check", elem)):
                continue
            else:
                uncalled.remove(elem)
        return ConcratSummary(safe, vulnerable, unsafe, len(uncalled))
