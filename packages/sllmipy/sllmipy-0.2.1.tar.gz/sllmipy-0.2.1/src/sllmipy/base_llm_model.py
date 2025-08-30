from abc import ABC, abstractmethod

from .config_model import ConfigModel


class BaseLLMModel(ABC):

    @abstractmethod
    def generate(self, prompt: str | None, config: ConfigModel | None = None) -> str:
        pass

    @abstractmethod
    async def agenerate(self, prompt: str | None, config: ConfigModel | None = None) -> str:
        pass

    @abstractmethod
    def count_tokens(self, prompt: str | None) -> int:
        pass
