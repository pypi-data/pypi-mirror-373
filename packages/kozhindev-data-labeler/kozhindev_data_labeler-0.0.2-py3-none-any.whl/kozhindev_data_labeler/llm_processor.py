import json
from typing import Any

from litellm.utils import ModelResponse

from kozhindev_data_labeler.llm import LLMClient


class LLMProcessor:
    def __init__(
        self,
        model_client: LLMClient
    ) -> None:
        self.__model = model_client
        self.result: dict[str, Any] = None
        self.__model_response: ModelResponse = None 

    def run(self, data: str, prompt: str) -> None:
        self.__model_response = self.__model.predict(f'{prompt}\n{data}')
        self.result = self.__response_to_dict()

    def token_info(self) -> None:
        if hasattr(self.__model_response, "usage"):
            print(f'Входные токены: {self.__model_response.usage["prompt_tokens"]}')
            print(f'Выходные токены: {self.__model_response.usage["completion_tokens"]}')
            print(f'Всего токенов: {self.__model_response.usage["total_tokens"]}')
            print(f'Cache: {self.__model_response.usage.get("prompt_tokens_details")}')
        else:
            print('Информация о токенах недоступна')

    def __response_to_dict(self) -> dict:
        try:
            return json.loads(
                self.__model_response.choices[0].message.content
            )
        except json.decoder.JSONDecodeError as ex:
            raise ValueError(f'Произошла ошибка при декодировании JSON: {ex}')
