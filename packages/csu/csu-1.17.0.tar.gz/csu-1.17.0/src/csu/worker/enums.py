from enum import IntEnum
from enum import auto


class WorkerState(IntEnum):
    UNKNOWN = auto()
    READY = auto()
    WORKING = auto()
    COOLDOWN = auto()
    SLEEPING = auto()
    CANCELED = auto()
    FAILED = auto()
    EXITED = auto()
