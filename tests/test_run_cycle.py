# tests/test_run_cycle.py
import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock, ANY

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.run_cycle import run_cycle
from ai.make_context import make_context
from ai.system_context import system_context

# Фикстура для начального списка сообщений
@pytest.fixture
def initial_messages():
    return [
        system_context(),
        make_context("user", "What time is it in UTC?")
    ]

# Тест: модель не вызывает инструменты (простой ответ)
@patch('ai.run_cycle.ai_client')
def test_run_cycle_no_tools(mock_client, initial_messages):
    # Настраиваем мок-ответ без tool_calls
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(
            content="The current time is 12:34 UTC.",
            tool_calls=None,
            model_dump=lambda: {"role": "assistant", "content": "The current time is 12:34 UTC."}
        ))
    ]
    mock_client.chat.completions.create.return_value = mock_response

    updated = run_cycle(initial_messages)

    # Проверяем, что в конце есть сообщение ассистента
    assert len(updated) == len(initial_messages) + 1
    assert updated[-1]["role"] == "assistant"
    assert "12:34" in updated[-1]["content"]
    # Убедимся, что цикл завершился за одну итерацию
    assert mock_client.chat.completions.create.call_count == 1

# Тест: модель вызывает один инструмент (get_datetime)
@patch('ai.run_cycle.ai_client')
@patch('ai.tools.get_datetime')  # подменяем реальную функцию инструмента
def test_run_cycle_tool_call(mock_get_datetime, mock_client, initial_messages):
    # Настраиваем первый ответ модели – вызов get_datetime
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "get_datetime"
    mock_tool_call.function.arguments = json.dumps({"timezone": "UTC"})
    mock_tool_call.id = "call_123"

    mock_response1 = MagicMock()
    mock_response1.choices = [
        MagicMock(message=MagicMock(
            content=None,
            tool_calls=[mock_tool_call],
            model_dump=lambda: {"role": "assistant", "tool_calls": [{"function": {"name": "get_datetime", "arguments": '{"timezone": "UTC"}'}}]}
        ))
    ]
    # Второй ответ – после получения результата, без tool_calls
    mock_response2 = MagicMock()
    mock_response2.choices = [
        MagicMock(message=MagicMock(
            content="The time is 14:30 UTC.",
            tool_calls=None,
            model_dump=lambda: {"role": "assistant", "content": "The time is 14:30 UTC."}
        ))
    ]
    mock_client.chat.completions.create.side_effect = [mock_response1, mock_response2]

    # Мокаем результат выполнения инструмента
    mock_get_datetime.return_value = {"datetime": "2026-08-29 14:30:00", "timezone": "UTC"}

    updated = run_cycle(initial_messages)

    # Проверяем, что были добавлены 3 сообщения: ассистент (tool_call), tool (результат), ассистент (финальный ответ)
    assert len(updated) == len(initial_messages) + 3
    # Проверяем, что среди сообщений есть сообщение от инструмента
    tool_msgs = [m for m in updated if m["role"] == "tool"]
    assert len(tool_msgs) == 1
    assert "datetime" in tool_msgs[0]["content"]
    # Проверяем, что последнее сообщение – ассистент с ответом
    assert updated[-1]["role"] == "assistant"
    assert "14:30" in updated[-1]["content"]
    # Убедимся, что ai_client вызывался дважды
    assert mock_client.chat.completions.create.call_count == 2

# Тест: превышение лимита итераций
@patch('ai.run_cycle.ai_client')
@patch('ai.run_cycle.logger')  # мокаем логгер для проверки предупреждения
def test_run_cycle_max_iterations(mock_logger, mock_client, initial_messages):
    # Мокаем бесконечные вызовы инструментов
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "get_datetime"
    mock_tool_call.function.arguments = json.dumps({"timezone": "UTC"})
    mock_tool_call.id = "call_123"

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(
            content=None,
            tool_calls=[mock_tool_call],
            model_dump=lambda: {"role": "assistant", "tool_calls": [{"function": {"name": "get_datetime", "arguments": '{"timezone": "UTC"}'}}]}
        ))
    ]
    # Все вызовы возвращают один и тот же ответ с tool_calls
    mock_client.chat.completions.create.return_value = mock_response

    # Подменяем модель_лимит на небольшое число (например, 2)
    with patch('ai.run_cycle.model_operation_limit', 2):
        # Для избежания бесконечного цикла, также мокаем инструмент, чтобы он возвращал что-то
        with patch('ai.tools.get_datetime') as mock_get_datetime:
            mock_get_datetime.return_value = {"datetime": "now"}
            updated = run_cycle(initial_messages)

    # Проверяем, что логгер получил предупреждение
    mock_logger.warning.assert_called_with(ANY)  # ANY – любой аргумент
    # Проверяем, что список сообщений содержит два tool_call и два результата (так как лимит 2)
    tool_msgs = [m for m in updated if m["role"] == "tool"]
    assert len(tool_msgs) == 2