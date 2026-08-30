import streamlit as st
import sys
import os
import json
import time

# Добавляем пути
ai_dir = os.path.join(os.path.dirname(__file__), 'ai')
if ai_dir not in sys.path:
    sys.path.append(ai_dir)

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

# Инициализация состояния сессии
if "messages" not in st.session_state:
    st.session_state.messages = [system_context()]
if "thinking_steps" not in st.session_state:
    st.session_state.thinking_steps = []

# Папка для диалогов
dialogs_dir = os.path.join(ai_dir, 'dialogs')
os.makedirs(dialogs_dir, exist_ok=True)

st.set_page_config(page_title=t('app_title'), layout="wide")
st.title(t('app_title'))
st.caption(t('app_caption'))

# Боковая панель
with st.sidebar:
    st.header(t('sidebar_settings'))
    st.write(f"**{t('sidebar_model')}:** `{config.model_name}`")
    st.write(f"**{t('sidebar_operation_limit')}:** `{config.model_operation_limit}`")
    st.write(f"**{t('sidebar_github_username')}:** `{config.github_username}`")
    st.write(f"**{t('sidebar_coding_case')}:** `{config.coding_case}`")
    st.write(f"**{t('sidebar_use_markdown')}:** `{config.use_markdown}`")
    langs = ['en', 'ru', 'es', 'fr', 'zh', 'ar', 'de', 'ko', 'pt', 'ja', 'hi', 'bn', 'it']
    langs_dict = {'🇬🇧 English': 'en', '🇷🇺 Русский': 'ru', '🇪🇸 Español': 'es', '🇫🇷 Français': 'fr', '🇨🇳 中文': 'zh', '🇸🇦 العربية': 'ar', '🇩🇪 Deutsch': 'de', '🇰🇷 한국어': 'ko', '🇧🇷 Português': 'pt', '🇯🇵 日本語': 'ja', '🇮🇳 हिन्दी': 'hi', '🇧🇩 বাংলা': 'bn', '🇮🇹 Italiano': 'it'}
    current_lang = config.language if config.language in langs else 'en'
    selected_lang = langs_dict[st.selectbox(f"**{t('sidebar_language')}:**", langs_dict.keys(), index=langs.index(current_lang))]
    if selected_lang != config.language:
        if translator.set_language(selected_lang):
            config.language = selected_lang
            st.success(t('config_language_changed', lang=selected_lang))
            st.rerun()

    st.divider()

    # Кнопки управления диалогами
    if st.button(t('sidebar_clear_history')):
        st.session_state.messages = [system_context()]
        st.session_state.thinking_steps = []
        st.rerun()

    st.divider()
    st.subheader(t("save_as_title"))
    col1, col2 = st.columns([3, 1])
    with col1:
        custom_name = st.text_input(t("save_as_placeholder"), placeholder="my_dialog")
    with col2:
        if st.button(t("save_as_button")):
            if custom_name.strip():
                filename = custom_name.strip() + ".json"
                filepath = os.path.join(dialogs_dir, filename)
                if os.path.exists(filepath):
                    st.error(t('save_exists', filename=filename))
                else:
                    try:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
                        st.success(t('save_ok', filename=filename))
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": t('save_ok', filename=filename)
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(t('save_error', error=str(e)))
            else:
                st.warning(t("save_name_required"))

    # Автосохранение с timestamp (можно оставить как есть)
    if st.button(t("save_timestamp_button")):
        filename = f"dialog_{int(time.time())}.json"
        filepath = os.path.join(dialogs_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
        st.success(t('save_ok', filename=filename))
        st.session_state.messages.append({
            "role": "assistant",
            "content": t('save_ok', filename=filename)
        })
        st.rerun()

    # Управление файлами диалогов
    files = [f for f in os.listdir(dialogs_dir) if f.endswith('.json')]
    if files:
        st.subheader(t('sidebar_select_file'))
        selected = st.selectbox(" ", files)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t('sidebar_load_dialog')):
                filepath = os.path.join(dialogs_dir, selected)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        loaded = json.load(f)
                    if isinstance(loaded, list) and all(isinstance(m, dict) for m in loaded):
                        st.session_state.messages = loaded
                        st.session_state.thinking_steps = []
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": t('load_ok', filename=selected)
                        })
                        st.rerun()
                    else:
                        st.error(t('load_invalid'))
                except Exception as e:
                    st.error(t('load_error', error=str(e)))
        with col2:
            if st.button(t('sidebar_delete_file')):
                filepath = os.path.join(dialogs_dir, selected)
                try:
                    os.remove(filepath)
                    st.success(t('del_ok', filename=selected))
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": t('del_ok', filename=selected)
                    })
                    st.rerun()
                except Exception as e:
                    st.error(t('del_error', error=str(e)))
    else:
        st.info(t('sidebar_no_files'))

    st.divider()
    st.caption(t('sidebar_commands_hint'))

# Отображение истории сообщений
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(msg["content"])
    elif msg["role"] == "tool":
        with st.expander(t('chat_tool_call')):
            try:
                st.json(json.loads(msg["content"]))
            except:
                st.write(msg["content"])

# Отображение сохранённого мышления
if st.session_state.thinking_steps:
    with st.expander(t('thinking_title'), expanded=False):
        for step in st.session_state.thinking_steps:
            st.write(step)


# Обработка команд
def handle_command(command: str) -> str | None:
    args = command.split()
    cmd = args[0].lower()

    if cmd == "/help":
        return t('command_help')
    elif cmd == "/wipe":
        st.session_state.messages = [system_context()]
        st.session_state.thinking_steps = []
        return t('wipe_ok')
    elif cmd == "/config":
        if len(args) == 1:
            return t('config_show',
                     model_name=config.model_name,
                     model_operation_limit=config.model_operation_limit,
                     github_username=config.github_username,
                     coding_case=config.coding_case,
                     use_markdown=config.use_markdown,
                     preferred_languages='any' if not config.preferred_languages else ', '.join(
                         config.preferred_languages),
                     language=config.language)
        elif len(args) == 2 and args[1] == "check":
            try:
                config.check_config()
                return t('config_check_ok')
            except config.ConfigError as e:
                return t('config_check_error', error=str(e))
        elif len(args) == 2 and args[1] == "reset":
            config.set_default_config()
            translator.set_language(config.language)
            return t('config_reset_ok')
        elif len(args) == 3:
            key, value = args[1], args[2]
            if key == "language":
                if value in ['en', 'ru']:
                    config.language = value
                    translator.set_language(value)
                    return t('config_language_changed', lang=value)
                else:
                    return t('config_set_error', key_='language', type='en/ru')
            elif key == "model_name":
                config.model_name = value
                return t('config_set_ok', key_='model_name', value=value)
            elif key == "model_operation_limit":
                try:
                    config.model_operation_limit = int(value)
                    return t('config_set_ok', key_='model_operation_limit', value=value)
                except ValueError:
                    return t('config_set_error', key_='model_operation_limit', type='integer')
            elif key == "github_username":
                config.github_username = value
                return t('config_set_ok', key_='github_username', value=value)
            elif key == "coding_case":
                if value in ['snake', 'camel', 'pascal']:
                    config.coding_case = value
                    return t('config_set_ok', key_='coding_case', value=value)
                else:
                    return t('config_set_error', key_='coding_case', type='snake/camel/pascal')
            elif key == "use_markdown":
                if value.lower() in ['true', 'false']:
                    config.use_markdown = value.lower() == 'true'
                    return t('config_set_ok', key_='use_markdown', value=str(config.use_markdown))
                else:
                    return t('config_set_error', key_='use_markdown', type='true/false')
            elif key == "preferred_languages":
                if value == "any":
                    config.preferred_languages = []
                    return t('config_set_ok', key_='preferred_languages', value='any')
                else:
                    langs = [lang.strip() for lang in value.split(',')]
                    config.preferred_languages = langs
                    return t('config_set_ok', key_='preferred_languages', value=', '.join(langs))
            else:
                return t('config_unknown', key_=key)
        else:
            return t('config_invalid')
    elif cmd == "/save":
        if len(args) != 2:
            return t('save_usage')
        filename = args[1].strip() + ".json"
        filepath = os.path.join(dialogs_dir, filename)
        if os.path.exists(filepath):
            return t('save_exists', filename=filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
            return t('save_ok', filename=filename)
        except Exception as e:
            return t('save_error', error=str(e))
    elif cmd == "/load":
        if len(args) != 2:
            return t('load_usage')
        filename = args[1].strip() + ".json"
        filepath = os.path.join(dialogs_dir, filename)
        if not os.path.exists(filepath):
            return t('load_not_found', filename=filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            if isinstance(loaded, list) and all(isinstance(m, dict) for m in loaded):
                st.session_state.messages = loaded
                st.session_state.thinking_steps = []
                return t('load_ok', filename=filename)
            else:
                return t('load_invalid')
        except Exception as e:
            return t('load_error', error=str(e))
    elif cmd == "/del":
        if len(args) != 2:
            return t('del_usage')
        filename = args[1].strip() + ".json"
        filepath = os.path.join(dialogs_dir, filename)
        if not os.path.exists(filepath):
            return t('del_not_found', filename=filename)
        try:
            os.remove(filepath)
            return t('del_ok', filename=filename)
        except Exception as e:
            return t('del_error', error=str(e))
    else:
        return t('unknown_command', cmd=cmd)


# Поле ввода
if prompt := st.chat_input(t("prompt_field")):
    if prompt.startswith('/'):
        result = handle_command(prompt)
        if result:
            st.session_state.messages.append({"role": "assistant", "content": result})
        st.rerun()
    else:
        user_msg = make_context("user", prompt)
        st.session_state.messages.append(user_msg)
        st.session_state.thinking_steps = []

        with st.status(t('thinking_start'), expanded=True) as status:
            for event in run_cycle(st.session_state.messages):
                if event['type'] == 'llm_call':
                    msg = t('thinking_llm_call')
                    status.write(msg)
                    st.session_state.thinking_steps.append(msg)
                elif event['type'] == 'tool_call':
                    args_str = json.dumps(event['data']['arguments'], ensure_ascii=False)
                    msg = t('thinking_tool_call', name=event['data']['name'], args=args_str)
                    status.write(msg)
                    st.session_state.thinking_steps.append(msg)
                elif event['type'] == 'tool_result':
                    result_preview = json.dumps(event['data']['result'], ensure_ascii=False)[:200]
                    msg = t('thinking_tool_result', name=event['data']['name'], result=result_preview)
                    status.write(msg)
                    st.session_state.thinking_steps.append(msg)
                elif event['type'] == 'final_answer':
                    msg = t('thinking_final_answer', content=event['data']['content'][:500])
                    status.write(msg)
                    st.session_state.thinking_steps.append(msg)
                    if st.session_state.messages[-1]["role"] != "assistant":
                        st.session_state.messages.append(make_context("assistant", event['data']['content']))
                elif event['type'] == 'warning':
                    msg = t('thinking_warning', message=event['data']['message'])
                    status.write(msg)
                    st.session_state.thinking_steps.append(msg)

            status.update(label=t('thinking_done'), state="complete")

        st.rerun()