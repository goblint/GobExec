from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

from gobexec.model.base import Result
from gobexec.model.context import ExecutionContext

B = TypeVar('B')
R = TypeVar('R', bound=Result)


class Tool(ABC, Generic[B, R]):
    name: str # TODO: not checked by abc
    columns: List[str] = [""] # TODO: not checked by abc

    @abstractmethod
    async def run_async(self, ec: ExecutionContext[B], benchmark: B) -> R:
        ...


