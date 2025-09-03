from abc import ABC, abstractmethod


class Base(ABC):
    @abstractmethod
    def compile(self):
        raise NotImplementedError()
