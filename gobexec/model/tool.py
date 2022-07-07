from typing import Protocol, TypeVar

from gobexec.model.base import Result
from gobexec.model.context import ExecutionContext

B = TypeVar('B')
R = TypeVar('R', bound=Result)


class Tool(Protocol[B, R]):
    async def run_async(self, ec: ExecutionContext, benchmark: B) -> R:
        ...
