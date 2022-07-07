from typing import Protocol, TypeVar

from gobexec.model.base import Result

B = TypeVar('B')
R = TypeVar('R', bound=Result)


class Tool(Protocol[B, R]):
    async def run_async(self, ctx, benchmark: B) -> R:
        ...
