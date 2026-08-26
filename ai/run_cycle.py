import os

import openai
from httpx import Client

from tools import *


load_dotenv()
github_key = getenv("GITHUB_PAT")
ai_key = getenv("AI_API_KEY")
ai_endpoint = getenv("AI_API_ENDPOINT")

proxy_url = "http://202.28.194.139:31280"
http_client = Client(proxy=proxy_url, timeout=30.0)

ai_client = openai.OpenAI(
    base_url=ai_endpoint,
    api_key=ai_key,
    http_client=http_client
)

def call_llm(msgs):
    resp = ai_client.chat.completions.create(
        model="google/gemini-3-flash-preview",
        tools=tools,
        messages=msgs
    )
    msgs.append(resp.choices[0].message.dict())
    return resp

def get_tool_response(response):
    tool_call = response.choices[0].message.tool_calls[0]
    tool_name = tool_call.function.name
    tool_args = json.loads(tool_call.function.arguments)

    # Look up the correct tool locally, and call it with the provided arguments
    # Other tools can be added without changing the agentic loop
    tool_result = TOOL_MAPPING[tool_name](**tool_args)

    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": tool_result,
    }

max_iterations = 10
iteration_count = 0

while iteration_count < max_iterations:
    iteration_count += 1
    resp = call_llm(_messages)

    if resp.choices[0].message.tool_calls is not None:
        messages.append(get_tool_response(resp))
    else:
        break

if iteration_count >= max_iterations:
    print("Warning: Maximum iterations reached")

print(messages[-1]['content'])
