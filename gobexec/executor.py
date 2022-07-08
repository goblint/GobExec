import asyncio
from dataclasses import dataclass


@dataclass
class Progress:
    done: int
    total: int
    cpu_sem: asyncio.BoundedSemaphore

    @property
    def active(self):
        sem = self.cpu_sem
        return sem._bound_value - sem._value

    def __enter__(self):
        self.total += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.done += 1
