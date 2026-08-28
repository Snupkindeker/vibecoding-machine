import sys
import os
import logging
import json

ai_dir = os.path.dirname(os.path.abspath(__file__)) + '\\ai'
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

if ai_dir not in sys.path:
    sys.path.append(ai_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)


from ai.run_cycle import run_cycle
from ai.make_context import make_context
from ai.system_context import system_context
import ai.config as config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    messages = [system_context()]

    while True:
        try:
            prompt = make_context("user", input("Type your message here: "))
            if prompt['content'] == "/stop":
                break
            elif prompt['content'] == "/wipe":
                messages = [system_context()]
                print("The dialog context was successfully wiped.")
            elif prompt['content'].find("/config") == 0:
                args = prompt['content'].split()
                if len(args) == 1:
                    print(f"The current model name is set to {config.model_name}.")
                    print(f"The current model operation limit is set to {config.model_operation_limit}.")
                    print(f"The current github username is set to {config.github_username}.")
                    print(f"The current coding case is set to {config.coding_case}.")
                    print(f"The current use markdown is set to {config.use_markdown}.")
                    print(f"The current preferred languages is set to {"any" if len(config.preferred_languages) == 0 else ', '.join(config.preferred_languages)}.")
                elif len(args) == 2:
                    match args[1]:
                        case "model_name":
                            print(f"The current model name is set to {config.model_name}.")
                        case "model_operation_limit":
                            print(f"The current model operation limit is set to {config.model_operation_limit}.")
                        case "github_username":
                            print(f"The current github username is set to {config.github_username}.")
                        case "coding_case":
                            print(f"The current coding case is set to {config.coding_case}.")
                        case "use_markdown":
                            print(f"The current use markdown is set to {config.use_markdown}.")
                        case "preferred_languages":
                            print(f"The current preferred languages is set to {"any" if len(config.preferred_languages) == 0 else ', '.join(config.preferred_languages)}.")
                        case "check":
                            try:
                                config.check_config()
                                print("Config checked successfully.")
                            except config.ConfigError as error:
                                print(f"An error occurred while checking config: {error}")
                        case "reset":
                            config.set_default_config()
                            print("Config reset successfully.")
                        case _:
                            print("The command argument is invalid. Use /help for more information.")
                elif len(args) == 3:
                    match args[1]:
                        case "model_name":
                            if type(args[2]) != str:
                                raise ValueError("model_name must be a string.")
                            config.model_name = args[2]
                            print(f"Model name successfully set to {config.model_name}.")
                        case "model_operation_limit":
                            if type(args[2]) != int:
                                raise ValueError("model_operation_limit must be an integer.")
                            config.model_operation_limit = args[2]
                            print(f"Model operation limit successfully set to {config.model_operation_limit}.")
                        case "github_username":
                            if type(args[2]) != str:
                                raise ValueError("github_username must be a string.")
                            config.github_username = args[2]
                            print(f"Github username successfully set to {config.github_username}.")
                        case "coding_case":
                            if type(args[2]) != str:
                                raise ValueError("coding_case must be a string.")
                            if args[2] not in ['snake', 'camel', 'pascal']:
                                raise ValueError("Invalid coding case.")
                            config.coding_case = args[2]
                            print(f"Coding case successfully set to {config.coding_case}.")
                        case "use_markdown":
                            if type(args[2]) != str:
                                raise ValueError("use_markdown must be true or false.")
                            if args[2].lower() not in ['true', 'false']:
                                raise ValueError("use_markdown must be true or false.")
                            config.use_markdown = (True if args[2].lower() == 'true' else False)
                            print(f"Use markdown successfully set to {config.use_markdown}.")
                        case "preferred_languages":
                            if type(args[2]) != str:
                                raise ValueError("preferred_languages must be words separated by commas.")
                            args[2] = list(args[2].split(','))
                            if args[2] == ['any']:
                                config.preferred_languages = []
                                print(f"Preferred languages successfully set to any.")
                            else:
                                for lang in args[2]:
                                    if lang not in ['assembly', 'bash', 'basic', 'c++', 'cpp', 'c#', 'csharp', 'c', 'go',
                                                        'java', 'js', 'javascript', 'kotlin', 'lua', 'pascal', 'php', 'python',
                                                        'ruby', 'rust', 'sql', 'sqlite', 'swift', 'typescript', 'visual_basic']:
                                        raise ValueError("Invalid preferred languages.")
                                config.preferred_languages = args[2]
                                print(f"Preferred languages successfully set to {', '.join(config.preferred_languages)}.")
                        case "check":
                            try:
                                config.check_config()
                                print("Config checked successfully.")
                            except config.ConfigError as error:
                                print(f"An error occurred while checking config: {error}")
                        case "reset":
                            config.set_default_config()
                            print("Config reset successfully.")
                        case _:
                            print("The command argument is invalid. Use /help for more information.")
                else:
                    raise ValueError("Too many arguments.")

            elif prompt['content'] == "/help":
                print("/help - view this menu.")
                print("/config <var/check/reset> [value] - get a config value, set it to a new value, check the config or reset it to default.")
                print("/wipe - wipe the dialog context.")
                print("/stop - stop the program.")

            elif prompt['content'].find("/save") == 0:
                args = prompt['content'].split()
                if len(args) != 2:
                    raise ValueError("Invalid number of arguments. Usage: /save <file_name_without_extension>")

                file_name = args[1].strip() + ".json"
                try:
                    with open(ai_dir + '\\dialogs\\' + file_name, "x", encoding='utf-8') as file:
                        file.close()
                    with open(ai_dir + '\\dialogs\\' + file_name, "w", encoding='utf-8') as file:
                        json.dump(messages, file, ensure_ascii=False, indent=4)

                    print(f"Successfully saved current dialog to {ai_dir + '\\dialogs\\' + file_name}.")
                except FileExistsError:
                    print("The file already exists. Please choose another file name.")

            elif prompt['content'].find("/load") == 0:
                args = prompt['content'].split()
                if len(args) != 2:
                    raise ValueError("Invalid number of arguments. Usage: /load <file_name_without_extension>")

                file_name = args[1].strip() + ".json"
                try:
                    with open(ai_dir + '\\dialogs\\' + file_name, "r", encoding='utf-8') as file:
                        messages = json.load(file)

                    print(f"Successfully loaded the dialog from {ai_dir + '\\dialogs\\' + file_name}.")
                except FileNotFoundError:
                    print("The file doesn't exist. Please choose another file name.")

            elif prompt['content'].find("/del") == 0:
                args = prompt['content'].split()
                if len(args) != 2:
                    raise ValueError("Invalid number of arguments. Usage: /load <file_name_without_extension>")

                file_name = args[1].strip() + ".json"
                try:
                    os.remove(ai_dir + '\\dialogs\\' + file_name)

                    print(f"Successfully deleted the saved dialog from {ai_dir + '\\dialogs\\' + file_name}.")
                except FileNotFoundError:
                    print("The file doesn't exist. Please choose another file name.")
                except PermissionError:
                    print("Permission denied. Please choose another file name.")
                except IsADirectoryError:
                    print("The file doesn't exist. Please choose another file name.")

            else:
                messages.append(prompt)
                messages = run_cycle(messages)

        except KeyboardInterrupt:
            logger.info("Caught KeyboardInterrupt. Shutting down...")
            exit()
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    main()