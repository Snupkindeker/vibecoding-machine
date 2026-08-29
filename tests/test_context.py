import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.make_context import make_context
from ai.system_context import system_context

def test_make_context_user():
    msg = make_context("user", "Hello")
    assert msg["role"] == "user"
    assert msg["content"] == "Hello"

def test_make_context_assistant():
    msg = make_context("assistant", "Hi there")
    assert msg["role"] == "assistant"
    assert msg["content"] == "Hi there"

def test_make_context_tool():
    msg = make_context("tool", '{"result": "ok"}', "call_123")
    assert msg["role"] == "tool"
    assert msg["content"] == '{"result": "ok"}'
    assert msg["tool_call_id"] == "call_123"

def test_system_context():
    msg = system_context()
    assert msg["role"] == "system"
    for word in ["GitHub", "tools", "help", "user", "assistant", "restrictions", "security", "politely"]:
        assert word in msg["content"]