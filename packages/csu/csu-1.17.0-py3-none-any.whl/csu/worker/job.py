from abc import ABCMeta
from abc import abstractmethod
from asyncio import Future
from dataclasses import dataclass
from dataclasses import field


@dataclass
class Job:
    done: Future = field(init=False, default_factory=Future)
    started: Future = field(init=False, default_factory=Future)


class ModelJob(Job, metaclass=ABCMeta):
    @property
    @abstractmethod
    def task_natural_key(self) -> dict:
        pass
