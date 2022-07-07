from typing import Protocol, TypeVar

B = TypeVar('B')
R = TypeVar('R')


class Tool(Protocol[B, R]):
    async def run_async(self, ctx, benchmark: B) -> R:
        ...
