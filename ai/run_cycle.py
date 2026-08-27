import openai
from httpx import Client

from system_context import make_context, system_context
from tools import *
from config import model_name, model_operation_limit


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


def run_cycle(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    def call_llm(msgs):
        resp = ai_client.chat.completions.create(
            model=model_name,
            tools=tools,
            messages=msgs
        )
        msgs.append(resp.choices[0].message.model_dump())
        return resp

    def get_tool_response(response):
        tool_call = response.choices[0].message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        tool_result = TOOL_MAPPING[tool_name](**tool_args)
        content = json.dumps(tool_result, ensure_ascii=False)

        return make_context("tool", content, tool_call.id)

    max_iterations = model_operation_limit
    iteration_count = 0

    while iteration_count < max_iterations:
        iteration_count += 1
        resp = call_llm(messages)

        print(resp.choices[0].message.tool_calls)
        if resp.choices[0].message.tool_calls is not None:
            messages.append(get_tool_response(resp))
        else:
            break

    if iteration_count >= max_iterations:
        print("Warning: Maximum iterations reached")

    print(messages[-1]['content'])
    return messages


if __name__ == "__main__":
    messages = [system_context()]
    prompt = ""
    while True:
        prompt = make_context("user", input("Type your message here: "))
        if prompt['content'] == "/stop":
            break
        messages.append(prompt)
        messages = run_cycle.run_cycle(messages)