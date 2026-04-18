"""
Модуль для управления переводами (i18n)
"""

import json
import os
from typing import Dict, Optional


class Translator:
    """Класс для управления переводами"""
    
    def __init__(self):
        self.current_language = 'ru'  # Русский по умолчанию
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_translations()
    
    def load_translations(self):
        """Загрузить все переводы"""
        locales_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')
        
        languages = ['en', 'ru', 'pl', 'de']
        for lang in languages:
            file_path = os.path.join(locales_dir, f'{lang}.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
            except FileNotFoundError:
                print(f"Warning: Translation file not found: {file_path}")
                self.translations[lang] = {}
    
    def set_language(self, language: str):
        """Установить язык"""
        if language in self.translations:
            self.current_language = language
        else:
            print(f"Warning: Language '{language}' not found, using 'ru'")
            self.current_language = 'ru'
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """Получить перевод для ключа"""
        if default is None:
            default = key
        
        if self.current_language not in self.translations:
            return default
        
        return self.translations[self.current_language].get(key, default)
    
    def get_available_languages(self) -> list:
        """Получить список доступных языков"""
        return list(self.translations.keys())
    
    def get_language_name(self, lang_code: str) -> str:
        """Получить название языка"""
        names = {
            'en': 'English',
            'ru': 'Русский',
            'pl': 'Polski',
            'de': 'Deutsch'
        }
        return names.get(lang_code, lang_code.upper())


# Глобальный экземпляр переводчика
_translator = Translator()


def t(key: str, default: Optional[str] = None) -> str:
    """Функция для получения перевода (удобная обертка)"""
    return _translator.get(key, default)


def set_language(language: str):
    """Установить язык"""
    _translator.set_language(language)


def get_current_language() -> str:
    """Получить текущий язык"""
    return _translator.current_language


def get_available_languages() -> list:
    """Получить список доступных языков"""
    return _translator.get_available_languages()
