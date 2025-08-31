from abc import ABC, abstractmethod


class BaseClassTest(ABC):  # base_class_test
    @property
    @abstractmethod
    def component(self) -> str:
        pass
