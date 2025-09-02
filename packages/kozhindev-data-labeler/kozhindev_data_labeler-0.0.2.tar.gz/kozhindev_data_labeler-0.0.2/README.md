# Usage example
```python
from pydantic import BaseModel

from kozhindev_data_labeler import LLMClient
from kozhindev_data_labeler import LLMProcessor


class Step(BaseModel):
    explanation: str = Field(..., description="Объяснение промежуточного вывода")
    think: str = Field(..., description="Анализ промпта и предыдущего шага, согласование рассуждений")


class PredictLLm(BaseModel):
    steps: list[Step] = Field(..., description="Пошаговое рассуждение")
    message: str = Field(..., description="Краткий итог рассуждений")
    target: str = Field(..., description="Классификация отзыва")


llm_client = LLMClient(
    model='gpt-4o-mini',
    api_key='API_KEY',
    system_prompt='SYSTEM PROMPT'
    response_format=PredictLLm
)

llm_processor = LLMProcessor(model_client=llm_client)


llm_processor.run(
    'ОТЗЫВ',
    'Сделай классификацию отзыва. 1 - негативный, 0 - положительный'
)

print(f'Ответ от модели: {llm.result}')
llm_processor.token_info()  # Выведет информацию о потраченных токенах
```