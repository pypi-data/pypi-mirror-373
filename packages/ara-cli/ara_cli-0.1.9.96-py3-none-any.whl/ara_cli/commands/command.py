from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs):     # pragma: no cover
        pass
