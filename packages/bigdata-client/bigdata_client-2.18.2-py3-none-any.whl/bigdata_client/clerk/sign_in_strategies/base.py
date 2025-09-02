from abc import ABC, abstractmethod


class SignInStrategy(ABC):
    @abstractmethod
    def get_payload(self): ...

    @abstractmethod
    def get_headers(self): ...

    @property
    @abstractmethod
    def strategy_name(self) -> str: ...
