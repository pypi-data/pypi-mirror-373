from google import genai
from typing import AsyncGenerator, Generator
from vertexai.preview import tokenization

from .base_llm_model import BaseLLMModel
from .config_model import ConfigModel


class GeminiModel(BaseLLMModel):

    def __init__(
        self,
        model_code: str,
        api_key: str | None = None,
        project_id: str | None = None,
        location: str | None = None,
    ):
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client(
                vertexai=True, project=project_id, location=location
            )
        if self.client is None:
            raise ValueError("Failed to initialize Gemini client. please provide api")
        self.model_code = model_code

    def generate(self, prompt: str | None, config: ConfigModel | None = None) -> str:
        response = self.client.models.generate_content(
            model=self.model_code,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                max_output_tokens=config.output_length if config else None,
                temperature=config.temperature if config else None,
                top_k=config.top_k if config else None,
                top_p=config.top_p if config else None,
            ),
        )
        return str(response.text)

    def generate_stream(
        self, prompt: str | None, config: ConfigModel | None = None
    ) -> Generator[str, None, None]:
        for response in self.client.models.generate_content_stream(
            model=self.model_code,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                max_output_tokens=config.output_length if config else None,
                temperature=config.temperature if config else None,
                top_k=config.top_k if config else None,
                top_p=config.top_p if config else None,
            ),
        ):
            yield str(response.text)

    async def agenerate(
        self, prompt: str | None, config: ConfigModel | None = None
    ) -> str:
        response = await self.client.aio.models.generate_content(
            model=self.model_code,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                max_output_tokens=config.output_length if config else None,
                temperature=config.temperature if config else None,
                top_k=config.top_k if config else None,
                top_p=config.top_p if config else None,
            ),
        )
        return str(response.text)

    async def agenerate_stream(
        self, prompt: str | None, config: ConfigModel | None = None
    ) -> AsyncGenerator[str, None]:
        async for response in await self.client.aio.models.generate_content_stream(
            model=self.model_code,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                max_output_tokens=config.output_length if config else None,
                temperature=config.temperature if config else None,
                top_k=config.top_k if config else None,
                top_p=config.top_p if config else None,
            ),
        ):
            yield str(response.text)

    def count_tokens(self, prompt: str | None) -> int:
        if prompt is None:
            return 0
        tokenizer = tokenization.get_tokenizer_for_model("gemini-1.5-flash-001")
        result = tokenizer.count_tokens(prompt)
        return result.total_tokens
