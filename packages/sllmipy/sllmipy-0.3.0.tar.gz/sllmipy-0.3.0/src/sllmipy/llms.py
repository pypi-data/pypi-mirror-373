import os
from typing import AsyncGenerator, Generator

from .config_model import ConfigModel
from .gemini import GeminiModel

_api_key = os.getenv("GENAI_API_KEY")


class LLMs:

    def __init__(self):
        self.models = {
            "gemini-2.5-pro": GeminiModel("gemini-2.5-pro", _api_key),
            "gemini-2.5-flash": GeminiModel("gemini-2.5-flash", _api_key),
            "gemini-2.5-flash-lite": GeminiModel("gemini-2.5-flash-lite", _api_key),
            "gemini-2.0-flash": GeminiModel("gemini-2.0-flash", _api_key),
            "gemini-2.0-flash-lite": GeminiModel("gemini-2.0-flash-lite", _api_key),
            "gemma-3-27b-it": GeminiModel("gemma-3-27b-it", _api_key),
        }

    def generate(
        self, model_code, prompt: str | None, config: ConfigModel | None = None
    ) -> str:
        if model_code in self.models:
            model = self.models[model_code]
            response = model.generate(prompt, config)
            return response
        else:
            raise ValueError(f"Model {model_code} not found in registry.")

    async def agenerate(
        self, model_code, prompt: str | None, config: ConfigModel | None = None
    ) -> str:
        if model_code in self.models:
            model = self.models[model_code]
            response = await model.agenerate(prompt, config)
            return response
        else:
            raise ValueError(f"Model {model_code} not found in registry.")

    def generate_stream(
        self, model_code, prompt: str | None, config: ConfigModel | None = None
    ) -> Generator[str, None, None]:
        if model_code in self.models:
            model = self.models[model_code]
            yield from model.generate_stream(prompt, config)
        else:
            raise ValueError(f"Model {model_code} not found in registry.")

    async def agenerate_stream(
        self, model_code, prompt: str | None, config: ConfigModel | None = None
    ) -> AsyncGenerator[str, None]:
        if model_code in self.models:
            model = self.models[model_code]
            async for chunk in model.agenerate_stream(prompt, config):
                yield chunk
        else:
            raise ValueError(f"Model {model_code} not found in registry.")

    def list_models(self):
        return list(self.models.keys())


genai = LLMs()
