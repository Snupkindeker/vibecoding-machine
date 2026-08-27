from ai import run_cycle
from ai.make_context import make_context
from ai.system_context import system_context


def main():
    messages = [system_context()]
    while True:
        prompt = make_context("user", input("Type your message here: "))
        if prompt['content'] == "/stop":
            break
        messages.append(prompt)
        messages = run_cycle.run_cycle(messages)


if __name__ == '__main__':
    main()