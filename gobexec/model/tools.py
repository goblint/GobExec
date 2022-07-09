import asyncio
from abc import ABC, abstractmethod
from typing import Generic, List

from gobexec.model.context import ExecutionContext, CompletedSubprocess
from gobexec.model.result import MultiResult
from gobexec.model.tool import R, Tool, B


class ResultExtractor(ABC, Generic[R]):
    @abstractmethod
    async def extract(self, ec: ExecutionContext, cp: CompletedSubprocess) -> R:
        ...


class ExtractTool(Tool[B, R]):
    delegate: Tool[B, CompletedSubprocess]
    extractors: List[ResultExtractor[R]]  # TODO: how to get bg color?

    def __init__(self,
                 delegate: Tool[B, CompletedSubprocess],
                 *extractors: ResultExtractor[R]
                 ) -> None:
        self.delegate = delegate
        self.extractors = list(extractors)

    @property
    def name(self):
        return self.delegate.name

    async def run_async(self, ec: ExecutionContext, benchmark: B) -> R:
        cp = await self.delegate.run_async(ec, benchmark)
        results = await asyncio.gather(*[extractor.extract(ec, cp) for extractor in self.extractors])
        return MultiResult(results)
