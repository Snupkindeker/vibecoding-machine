from typing import Any

def make_context(role: str, content: str, tool_call_id: str | None = None) -> dict[str, Any]:
    if type(content) != str:
        raise ValueError("Invalid content type")
    if type(role) != str:
        raise ValueError("Invalid role type")
    if role not in ['system', 'user', 'assistant', 'tool']:
        raise ValueError("Invalid role. Supported roles: system, user, assistant, tool")

    if role == 'tool':
        if tool_call_id is None:
            raise ValueError("Invalid tool call ID")
        return {'role': 'tool', 'tool_call_id': tool_call_id, 'content': content}
    return {"role": role, "content": content}