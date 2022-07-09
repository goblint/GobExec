from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

from gobexec.model.base import Result
from gobexec.model.context import ExecutionContext, CompletedSubprocess

B = TypeVar('B')
R = TypeVar('R', bound=Result)


class Tool(ABC, Generic[B, R]):
    name: str # TODO: not checked by abc

    @abstractmethod
    async def run_async(self, ec: ExecutionContext, benchmark: B) -> R:
        ...


class ResultExtractor(ABC, Generic[R]):
    @abstractmethod
    async def extract(self, ec: ExecutionContext, cp: CompletedSubprocess) -> R:
        ...


class ExtractTool(Tool[B, R]):
    delegate: Tool[B, CompletedSubprocess]
    extractor: ResultExtractor[R] # TODO: multiple, how to get bg color?

    def __init__(self,
                 delegate: Tool[B, CompletedSubprocess],
                 extractor: ResultExtractor[R]
                 ) -> None:
        self.delegate = delegate
        self.extractor = extractor

    @property
    def name(self):
        return self.delegate.name

    async def run_async(self, ec: ExecutionContext, benchmark: B) -> R:
        cp = await self.delegate.run_async(ec, benchmark)
        return await self.extractor.extract(ec, cp)
