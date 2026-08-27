import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

if current_dir not in sys.path:
    sys.path.append(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)


from ai.run_cycle import run_cycle
from ai.make_context import make_context
from ai.system_context import system_context
from ai.config import *


def main():
    messages = [system_context()]
    while True:
        prompt = make_context("user", input("Type your message here: "))
        if prompt['content'] == "/stop":
            break
        elif prompt['content'] == "/wipe":
            messages = [system_context()]
            print("The dialog context was successfully wiped.")
        elif prompt['content'].find("/config") == 0:
            args = prompt['content'].split()
            if len(args) == 1:
                print(f"The current model name is set to {model_name}.")
                print(f"The current model operation limit is set to {model_operation_limit}.")
                print(f"The current github username is set to {github_username}.")
                print(f"The current coding case is set to {coding_case}.")
                print(f"The current use markdown is set to {use_markdown}.")
                print(f"The current preferred languages is set to {"any" if len(preferred_languages) == 0 else ', '.join(preferred_languages)}.")
            if len(args) == 2:
                match args[1]:
                    case "model_name":
                        print(f"The current model name is set to {model_name}.")
                    case "model_operation_limit":
                        print(f"The current model operation limit is set to {model_operation_limit}.")
                    case "github_username":
                        print(f"The current github username is set to {github_username}.")
                    case "coding_case":
                        print(f"The current coding case is set to {coding_case}.")
                    case "use_markdown":
                        print(f"The current use markdown is set to {use_markdown}.")
                    case "preferred_languages":
                        print(f"The current preferred languages is set to {"any" if len(preferred_languages) == 0 else ', '.join(preferred_languages)}.")
                    case "check":
                        try:
                            check_config()
                            print("Config checked successfully.")
                        except ConfigError as error:
                            print(f"An error occurred while checking config: {error}")
                    case "reset":
                        set_default_config()
                        print("Config reset successfully.")
                    case _:
                        print("The command argument is invalid. Use /help for more information.")

        messages.append(prompt)
        messages = run_cycle(messages)


if __name__ == '__main__':
    main()