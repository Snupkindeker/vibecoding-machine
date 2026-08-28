# run_cycle.py (исправленный генератор)

import openai
import logging
from httpx import Client
from system_context import make_context, system_context
from tools import *
from config import model_name, model_operation_limit
from palette import Palette
from dotenv import load_dotenv
from os import getenv

load_dotenv()
ai_key = getenv("AI_API_KEY")
ai_endpoint = getenv("AI_API_ENDPOINT")

proxy_url = "http://202.28.194.139:31280"
http_client = Client(proxy=proxy_url, timeout=30.0)

ai_client = openai.OpenAI(
    base_url=ai_endpoint,
    api_key=ai_key,
    http_client=http_client
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
palette = Palette()


def run_cycle(messages: list[dict[str, str]]):
    """
    Генератор, который выполняет шаги и выдаёт события в реальном времени.
    События: dict с полями 'type' и 'data'
    """
    max_iterations = model_operation_limit
    iteration_count = 0

    while iteration_count < max_iterations:
        iteration_count += 1

        # 1. Вызов LLM
        resp = ai_client.chat.completions.create(
            model=model_name,
            tools=tools,
            messages=messages
        )
        # Добавляем ответ ассистента в историю
        assistant_msg = resp.choices[0].message.model_dump()
        messages.append(assistant_msg)

        # Отдаём событие о вызове LLM
        yield {
            'type': 'llm_call',
            'data': {
                'response': assistant_msg,
                'tool_calls': resp.choices[0].message.tool_calls
            }
        }

        # В run_cycle.py, внутри while:
        logger.info(f"Итерация {iteration_count}, проверяем tool_calls...")
        if resp.choices[0].message.tool_calls is not None:
            logger.info(f"Обнаружены tool_calls: {resp.choices[0].message.tool_calls}")
            # ... далее код
        else:
            logger.info("Нет tool_calls, завершаем.")

        # Проверяем, есть ли запрос на вызов инструментов
        if resp.choices[0].message.tool_calls is not None:
            tool_call = resp.choices[0].message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # 2. Событие: вызов инструмента
            yield {
                'type': 'tool_call',
                'data': {
                    'name': tool_name,
                    'arguments': tool_args
                }
            }

            # 3. Выполняем инструмент
            tool_result = TOOL_MAPPING[tool_name](**tool_args)
            content = json.dumps(tool_result, ensure_ascii=False)

            # 4. Событие: результат инструмента
            yield {
                'type': 'tool_result',
                'data': {
                    'name': tool_name,
                    'result': tool_result
                }
            }

            # 5. Добавляем ответ инструмента в историю
            tool_message = make_context("tool", content, tool_call.id)
            messages.append(tool_message)

            # Продолжаем цикл (модель может снова вызвать инструменты)
            continue
        else:
            # Финальный ответ (без вызова инструментов)
            final_content = resp.choices[0].message.content
            yield {
                'type': 'final_answer',
                'data': {'content': final_content}
            }
            break

    if iteration_count >= max_iterations:
        yield {
            'type': 'warning',
            'data': {'message': 'Maximum iterations reached'}
        }