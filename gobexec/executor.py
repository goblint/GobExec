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
