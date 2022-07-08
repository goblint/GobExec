from dataclasses import dataclass


@dataclass
class Progress:
    done: int
    total: int
    active: int
