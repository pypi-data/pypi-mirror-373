from abc import ABC, abstractmethod
from typing import AsyncGenerator, Generator

from .config_model import ConfigModel


class BaseLLMModel(ABC):

    @abstractmethod
    def generate(self, prompt: str | None, config: ConfigModel | None = None) -> str:
        pass

    @abstractmethod
    async def agenerate(self, prompt: str | None, config: ConfigModel | None = None) -> str:
        pass

    @abstractmethod
    def generate_stream(
        self, prompt: str | None, config: ConfigModel | None = None
    ) -> Generator[str, None, None]:
        pass

    @abstractmethod
    async def agenerate_stream(
        self, prompt: str | None, config: ConfigModel | None = None
    ) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    def count_tokens(self, prompt: str | None) -> int:
        pass
