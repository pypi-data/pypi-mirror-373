import os

from .config_model import ConfigModel
from .gemini import GeminiModel

_api_key = os.getenv("GENAI_API_KEY")


class LLMs:

    def __init__(self):
        self.registry = {
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
        if model_code in self.registry:
            model = self.registry[model_code]
            response = model.generate(prompt, config)
            return response
        else:
            raise ValueError(f"Model {model_code} not found in registry.")

    async def agenerate(
        self, model_code, prompt: str | None, config: ConfigModel | None = None
    ) -> str:
        if model_code in self.registry:
            model = self.registry[model_code]
            response = await model.agenerate(prompt, config)
            return response
        else:
            raise ValueError(f"Model {model_code} not found in registry.")

    def list_models(self):
        return list(self.registry.keys())


genai = LLMs()
