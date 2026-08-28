# app.py (фрагменты)

import streamlit as st
from ai.localization import t, get_translator
from ai.system_context import system_context

# В начале приложения проверяем язык из конфига и устанавливаем его
from ai import config
translator = get_translator()
if hasattr(config, 'language'):
    translator.set_language(config.language)

# В сайдбаре добавляем переключатель языка
with st.sidebar:
    # ... настройки ...
    st.write(f"**{t('sidebar_model')}:** `{config.model_name}`")
    st.write(f"**{t('sidebar_operation_limit')}:** `{config.model_operation_limit}`")
    st.write(f"**{t('sidebar_github_username')}:** `{config.github_username}`")
    st.write(f"**{t('sidebar_coding_case')}:** `{config.coding_case}`")
    st.write(f"**{t('sidebar_use_markdown')}:** `{config.use_markdown}`")
    langs = ['en', 'ru']
    selected_lang = st.selectbox(t('sidebar_language', default='Language'), langs, index=langs.index(config.language) if config.language in langs else 0)
    if selected_lang != config.language:
        if translator.set_language(selected_lang):
            config.language = selected_lang
            st.success(t('config_language_changed', lang=selected_lang))
            st.rerun()
    # ... далее как раньше, только строки через t()

# В обработчике команд:
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
                      preferred_languages='any' if not config.preferred_languages else ', '.join(config.preferred_languages),
                      language=config.language)
        elif len(args) == 2 and args[1] == "check":
            try:
                config.check_config()
                return t('config_check_ok')
            except config.ConfigError as e:
                return t('config_check_error', error=str(e))
        elif len(args) == 2 and args[1] == "reset":
            config.set_default_config()
            # Обновляем язык в переводчике
            translator.set_language(config.language)
            return t('config_reset_ok')
        elif len(args) == 3:
            key = args[1]
            value = args[2]
            if key == "language":
                if value in ['en', 'ru']:
                    config.language = value
                    translator.set_language(value)
                    return t('config_language_changed', lang=value)
                else:
                    return t('config_set_error', key='language', type='en or ru')
            elif key == "model_name":
                config.model_name = value
                return t('config_set_ok', key='model_name', value=value)
            # ... и так далее для остальных параметров
            else:
                return t('config_unknown', key=key)
        else:
            return t('config_invalid')
    # ... другие команды также заменяем на t() ...