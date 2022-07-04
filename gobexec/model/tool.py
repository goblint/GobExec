from typing import Protocol

from gobexec.model.benchmark import Single


class Tool(Protocol):
    def run(self, benchmark: Single) -> str:
        pass
