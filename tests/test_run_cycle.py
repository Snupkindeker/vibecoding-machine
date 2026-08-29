import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock, ANY

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.run_cycle import run_cycle
from ai.make_context import make_context
from ai.system_context import system_context

@pytest.fixture
def initial_messages():
    return [
        system_context(),
        make_context("user", "What time is it in UTC?")
    ]

# ------------------------------------------------------------
# Тест 1: Модель не вызывает инструменты
# ------------------------------------------------------------
@patch('ai.run_cycle.get_ai_client')   # <- мокаем функцию, а не переменную
def test_run_cycle_no_tools(mock_get_client, initial_messages):
    # Создаём мок-клиент
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(
            content="The current time is 12:34 UTC.",
            tool_calls=None,
            model_dump=lambda: {"role": "assistant", "content": "The current time is 12:34 UTC."}
        ))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client   # <- возвращаем мок-клиент

    events = list(run_cycle(initial_messages))

    assert len(initial_messages) == 3
    assert initial_messages[-1]["role"] == "assistant"
    assert "12:34" in initial_messages[-1]["content"]
    final_events = [e for e in events if e['type'] == 'final_answer']
    assert len(final_events) == 1
    # Проверяем, что клиент вызван один раз
    assert mock_client.chat.completions.create.call_count == 1

# ------------------------------------------------------------
# Тест 2: Модель вызывает один инструмент (get_datetime)
# ------------------------------------------------------------
@patch('ai.run_cycle.get_ai_client')    # <- мокаем функцию
@patch('ai.tools.get_datetime')         # <- мокаем сам инструмент
def test_run_cycle_tool_call(mock_get_datetime, mock_get_client, initial_messages):
    # Создаём мок-клиент
    mock_client = MagicMock()

    # Первый ответ – вызов get_datetime
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
    # Второй ответ – без tool_calls
    mock_response2 = MagicMock()
    mock_response2.choices = [
        MagicMock(message=MagicMock(
            content="The time is 14:30 UTC.",
            tool_calls=None,
            model_dump=lambda: {"role": "assistant", "content": "The time is 14:30 UTC."}
        ))
    ]
    mock_client.chat.completions.create.side_effect = [mock_response1, mock_response2]
    mock_get_client.return_value = mock_client

    # Мокаем результат выполнения инструмента
    mock_get_datetime.return_value = {"datetime": "2026-08-29 14:30:00", "timezone": "UTC"}

    events = list(run_cycle(initial_messages))

    assert len(initial_messages) == 5
    tool_msgs = [m for m in initial_messages if m["role"] == "tool"]
    assert len(tool_msgs) == 1
    assert "datetime" in tool_msgs[0]["content"]
    assert initial_messages[-1]["role"] == "assistant"
    assert "14:30" in initial_messages[-1]["content"]

    event_types = [e['type'] for e in events]
    assert 'llm_call' in event_types
    assert 'tool_call' in event_types
    assert 'tool_result' in event_types
    assert 'final_answer' in event_types
    assert mock_client.chat.completions.create.call_count == 2

# ------------------------------------------------------------
# Тест 3: Превышение лимита итераций
# ------------------------------------------------------------
@patch('ai.run_cycle.get_ai_client')   # <- мокаем функцию
@patch('ai.run_cycle.logger')          # <- мокаем логгер (но проверять не будем)
def test_run_cycle_max_iterations(mock_logger, mock_get_client, initial_messages):
    # Создаём мок-клиент
    mock_client = MagicMock()

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
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client

    with patch('ai.run_cycle.model_operation_limit', 2):
        with patch('ai.tools.get_datetime') as mock_get_datetime:
            mock_get_datetime.return_value = {"datetime": "now"}
            events = list(run_cycle(initial_messages))

    # Проверяем наличие события warning
    warnings = [e for e in events if e['type'] == 'warning']
    assert len(warnings) == 1
    assert "Maximum iterations" in warnings[0]['data']['message']

    # Проверяем, что было 2 итерации (tool_call и tool_result повторились 2 раза)
    tool_calls = [e for e in events if e['type'] == 'tool_call']
    assert len(tool_calls) == 2