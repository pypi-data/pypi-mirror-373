import os
from typing import Type

from pydantic import BaseModel
from litellm import completion
from litellm.utils import ModelResponse


class LLMClient:
    def __init__(
        self,
        model: str,
        api_key: str,
        system_prompt: str,
        response_format: Type[BaseModel]
    ) -> None:
        os.environ[self.__get_provider_name(model)] = api_key
        self.model = model
        self.system = {'role': 'system', 'content': system_prompt, 'cache_control': {"type": "ephemeral"}}
        self.response_format = response_format

    def predict(self, message: str) -> ModelResponse:
        response = completion(
            model=self.model,
            messages=[self.system, {'content': message, 'role': 'user'}],
            response_format=self.response_format
        )
        return response

    @staticmethod
    def __get_provider_name(model_name: str) -> str:
        if model_name.startswith('claude'):
            return 'ANTHROPIC_API_KEY'
        if model_name.startswith(('openai', 'gpt')):
            return 'OPENAI_API_KEY'
        if model_name.startswith('deepseek'):
            return 'DEEPSEEK_API_KEY'
        raise ValueError('Передан некорректный провайдер')
