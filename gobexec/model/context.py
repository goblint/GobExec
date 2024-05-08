import asyncio
import resource
from asyncio.subprocess import Process
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar, Any, TYPE_CHECKING, Generic

from jinja2 import Environment, Template

from gobexec.asyncio.child_watcher import RusageThreadedChildWatcher
from gobexec.executor import Progress
from gobexec.model.base import Result

if TYPE_CHECKING:
    from gobexec.model.tool import Tool

B = TypeVar('B')
R = TypeVar('R', bound=Result)


@dataclass
class CompletedSubprocess(Result):
    process: Process
    stdout: bytes
    stderr: bytes
    rusage: resource.struct_rusage

    def template(self, env: Environment) -> Template:
        return env.from_string("")


class ExecutionContext(Generic[B]):
    async def get_tool_result(self, tool: 'Tool[B, R]') -> R:
        ...

    def get_tool_data_path(self, tool: 'Tool[B, R]') -> Path:
        ...

    async def subprocess_exec(self, *args, **kwargs) -> CompletedSubprocess:
        ...


class RootExecutionContext:
    data_path: Path
    cpu_sem: asyncio.BoundedSemaphore
    rusage_child_watcher: RusageThreadedChildWatcher
    progress: Progress

    def __init__(self, data_path: Path, cpu_sem: asyncio.BoundedSemaphore, rusage_child_watcher) -> None:
        self.data_path = data_path
        self.cpu_sem = cpu_sem
        self.rusage_child_watcher = rusage_child_watcher
        self.progress = Progress(0, 0, cpu_sem)

    async def subprocess_exec(self, *args, **kwargs) -> CompletedSubprocess:
        async with self.cpu_sem:
            p = await asyncio.create_subprocess_exec(*args, **kwargs)
            stdout, stderr = await p.communicate()
            rusage = self.rusage_child_watcher.rusages.pop(p.pid)
            return CompletedSubprocess(p, stdout, stderr, rusage)
