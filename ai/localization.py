import json
import os
from typing import Optional

class Translator:
    _instance = None
    _translations = {}
    _current_lang = 'en'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_translations('en')
        return cls._instance

    def _load_translations(self, lang: str):
        """Загружает переводы для указанного языка."""
        locale_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')
        filepath = os.path.join(locale_dir, f'{lang}.json')
        if not os.path.exists(filepath):
            # fallback на английский
            filepath = os.path.join(locale_dir, 'en.json')
        with open(filepath, 'r', encoding='utf-8') as f:
            self._translations = json.load(f)
        self._current_lang = lang

    def set_language(self, lang: str) -> bool:
        """Устанавливает язык. Возвращает True, если язык поддерживается."""
        locale_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')
        filepath = os.path.join(locale_dir, f'{lang}.json')
        if os.path.exists(filepath):
            self._load_translations(lang)
            return True
        return False

    def translate(self, key: str, **kwargs) -> str:
        """Возвращает перевод по ключу с подстановкой параметров."""
        if key not in self._translations:
            # если ключ не найден, возвращаем ключ как есть
            return key
        text = self._translations[key]
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text

def get_translator() -> Translator:
    """Возвращает глобальный объект переводчика."""
    return Translator()

# Для удобства можно сделать функцию t()
_t = get_translator()
def t(key: str, **kwargs) -> str:
    return _t.translate(key, **kwargs)