import sys
import os
import logging
import json

ai_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ai')
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
dialogs_dir = os.path.join(ai_dir, 'dialogs')
os.makedirs(dialogs_dir, exist_ok=True)

if ai_dir not in sys.path:
    sys.path.append(ai_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from palette import Palette
from ai.run_cycle import run_cycle
from ai.make_context import make_context
from ai.system_context import system_context
import ai.config as config
from ai.localization import t, get_translator

# Инициализация переводчика и языка
translator = get_translator()
if hasattr(config, 'language'):
    translator.set_language(config.language)
else:
    config.language = 'en'
    translator.set_language('en')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
palette = Palette()

def main():
    messages = [system_context()]

    while True:
        try:
            prompt = make_context("user", input(palette.italic + t("prompt_field") + " \n" + palette.blue))
            if not prompt['content'].strip():
                continue
            print(palette.normal, end="")
            if prompt['content'] == "/stop":
                logger.warning(palette.yellow + t('stop') + palette.normal)
                break
            elif prompt['content'] == "/wipe":
                messages = [system_context()]
                logger.info(palette.green + t('wipe_ok') + palette.normal)
            elif prompt['content'].find("/config") == 0:
                args = prompt['content'].split()
                if len(args) == 1:
                    logger.info(palette.green + t('config_show',
                          model_name=config.model_name,
                          model_operation_limit=config.model_operation_limit,
                          github_username=config.github_username,
                          coding_case=config.coding_case,
                          use_markdown=config.use_markdown,
                          preferred_languages='any' if not config.preferred_languages else ', '.join(config.preferred_languages),
                          language=config.language) + palette.normal)
                elif len(args) == 2:
                    match args[1]:
                        case "check":
                            try:
                                config.check_config()
                                logger.info(palette.green + t('config_check_ok') + palette.normal)
                            except config.ConfigError as e:
                                logger.error(palette.red + t('config_check_error', error=str(e)) + palette.normal)
                        case "reset":
                            config.set_default_config()
                            translator.set_language(config.language)
                            logger.info(palette.green + t('config_reset_ok') + palette.normal)
                        case _:
                            logger.error(palette.red + t('config_invalid') + palette.normal)
                elif len(args) == 3:
                    key, value = args[1], args[2]
                    if key == "language":
                        if value in ['en', 'ru', 'es', 'fr', 'zh', 'ar', 'de', 'ko', 'pt', 'ja', 'hi', 'bn', 'it']:
                            config.language = value
                            translator.set_language(value)
                            logger.info(palette.green + t('config_language_changed', lang=value) + palette.normal)
                        else:
                            logger.error(palette.red + t('config_set_error', key='language', type='en/ru/es/fr/zh/zr/de/ko/pt/ja/hi/bn/it') + palette.normal)
                    elif key == "model_name":
                        config.model_name = value
                        logger.info(palette.green + t('config_set_ok', key='model_name', value=value) + palette.normal)
                    elif key == "model_operation_limit":
                        try:
                            config.model_operation_limit = int(value)
                            logger.info(palette.green + t('config_set_ok', key='model_operation_limit', value=value) + palette.normal)
                        except ValueError:
                            logger.error(palette.red + t('config_set_error', key='model_operation_limit', type='integer') + palette.normal)
                    elif key == "github_username":
                        config.github_username = value
                        logger.info(palette.green + t('config_set_ok', key='github_username', value=value) + palette.normal)
                    elif key == "coding_case":
                        if value in ['snake', 'camel', 'pascal']:
                            config.coding_case = value
                            logger.info(palette.green + t('config_set_ok', key='coding_case', value=value) + palette.normal)
                        else:
                            logger.error(palette.red + t('config_set_error', key='coding_case', type='snake/camel/pascal') + palette.normal)
                    elif key == "use_markdown":
                        if value.lower() in ['true', 'false']:
                            config.use_markdown = value.lower() == 'true'
                            logger.info(palette.green + t('config_set_ok', key='use_markdown', value=str(config.use_markdown)) + palette.normal)
                        else:
                            logger.error(palette.red + t('config_set_error', key='use_markdown', type='true/false') + palette.normal)
                    elif key == "preferred_languages":
                        if value == "any":
                            config.preferred_languages = []
                            logger.info(palette.green + t('config_set_ok', key='preferred_languages', value='any') + palette.normal)
                        else:
                            langs = [lang.strip() for lang in value.split(',')]
                            valid_langs = ['assembly', 'bash', 'basic', 'c++', 'cpp', 'c#', 'csharp', 'c', 'go',
                                           'java', 'js', 'javascript', 'kotlin', 'lua', 'pascal', 'php', 'python',
                                           'ruby', 'rust', 'sql', 'sqlite', 'swift', 'typescript', 'visual_basic']
                            invalid = [l for l in langs if l not in valid_langs]
                            if invalid:
                                logger.error(palette.red + t('config_set_error', key='preferred_languages', type='valid language codes') + palette.normal)
                            else:
                                config.preferred_languages = langs
                                logger.info(palette.green + t('config_set_ok', key='preferred_languages', value=', '.join(langs)) + palette.normal)
                    else:
                        logger.error(palette.red + t('config_unknown', key=key) + palette.normal)
                else:
                    logger.error(palette.red + t('config_invalid') + palette.normal)

            elif prompt['content'] == "/help":
                print(palette.purple + t('command_help') + palette.normal)

            elif prompt['content'].find("/save") == 0:
                args = prompt['content'].split()
                if len(args) != 2:
                    logger.error(palette.red + t('save_usage') + palette.normal)
                    continue
                filename = args[1].strip() + ".json"
                filepath = os.path.join(dialogs_dir, filename)
                try:
                    with open(filepath, "x", encoding='utf-8') as f:
                        pass
                    with open(filepath, "w", encoding='utf-8') as f:
                        json.dump(messages, f, ensure_ascii=False, indent=4)
                    logger.info(palette.green + t('save_ok', filename=filename) + palette.normal)
                except FileExistsError:
                    logger.error(palette.red + t('save_exists', filename=filename) + palette.normal)

            elif prompt['content'].find("/load") == 0:
                args = prompt['content'].split()
                if len(args) != 2:
                    logger.error(palette.red + t('load_usage') + palette.normal)
                    continue
                filename = args[1].strip() + ".json"
                filepath = os.path.join(dialogs_dir, filename)
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        loaded = json.load(f)
                    if isinstance(loaded, list) and all(isinstance(m, dict) for m in loaded):
                        messages = loaded
                        logger.info(palette.green + t('load_ok', filename=filename) + palette.normal)
                    else:
                        raise ValueError(t('load_invalid'))
                except FileNotFoundError:
                    logger.error(palette.red + t('load_not_found', filename=filename) + palette.normal)
                except Exception as e:
                    logger.error(palette.red + t('load_error', error=str(e)) + palette.normal)

            elif prompt['content'].find("/del") == 0:
                args = prompt['content'].split()
                if len(args) != 2:
                    logger.error(palette.red + t('del_usage') + palette.normal)
                    continue
                filename = args[1].strip() + ".json"
                filepath = os.path.join(dialogs_dir, filename)
                try:
                    os.remove(filepath)
                    logger.info(palette.green + t('del_ok', filename=filename) + palette.normal)
                except FileNotFoundError:
                    logger.error(palette.red + t('del_not_found', filename=filename) + palette.normal)
                except Exception as e:
                    logger.error(palette.red + t('del_error', error=str(e)) + palette.normal)

            else:
                messages.append(prompt)
                print(palette.italic + t('terminal_thinking') + palette.normal)
                for event in run_cycle(messages):
                    if event['type'] == 'llm_call':
                        pass
                    elif event['type'] == 'tool_call':
                        args_str = json.dumps(event['data']['arguments'], ensure_ascii=False)
                        print(palette.yellow + t('terminal_tool_call', name=event['data']['name'], args=args_str) + palette.normal)
                    elif event['type'] == 'tool_result':
                        result_preview = json.dumps(event['data']['result'], ensure_ascii=False)[:200]
                        print(palette.green + t('terminal_tool_result', name=event['data']['name'], result=result_preview) + palette.normal)
                    elif event['type'] == 'final_answer':
                        print(palette.white + t('terminal_final_answer') + palette.normal)
                        print(palette.white + event['data']['content'] + palette.normal)
                    elif event['type'] == 'warning':
                        print(palette.red + t('terminal_warning', message=event['data']['message']) + palette.normal)

        except KeyboardInterrupt:
            logger.warning(palette.yellow + t('ctrl_c') + palette.normal)
            break
        except Exception as e:
            logger.error(palette.red + str(e) + palette.normal)

if __name__ == '__main__':
    main()