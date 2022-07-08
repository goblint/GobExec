import asyncio
from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import TypeVar, Generic

from gobexec.model.base import Result
from gobexec.model.context import ExecutionContext

B = TypeVar('B')
R = TypeVar('R', bound=Result)

cpu_sem: ContextVar[asyncio.BoundedSemaphore] = ContextVar("cpu_sem")


class Tool(ABC, Generic[B, R]):
    @abstractmethod
    async def run_async(self, ec: ExecutionContext, benchmark: B) -> R:
        ...
