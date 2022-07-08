from dataclasses import dataclass

from gobexec.model import tool


@dataclass
class Progress:
    done: int
    total: int

    @property
    def active(self):
        sem = tool.cpu_sem.get()
        return sem._bound_value - sem._value

    def __enter__(self):
        self.total += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.done += 1
