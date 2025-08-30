from abc import ABC, abstractmethod


class AbstractUIComponent(ABC):
    @abstractmethod
    def add_to_ui(self) -> None:
        pass
