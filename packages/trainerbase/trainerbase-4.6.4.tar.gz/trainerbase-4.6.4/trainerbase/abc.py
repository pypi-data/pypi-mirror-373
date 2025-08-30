from abc import ABC, abstractmethod


class Switchable(ABC):
    @abstractmethod
    def enable(self):
        pass

    @abstractmethod
    def disable(self):
        pass


class AbstractKeyboardHandler(ABC):
    @property
    @abstractmethod
    def hotkey(self) -> str:
        pass

    @abstractmethod
    def handle(self):
        pass
