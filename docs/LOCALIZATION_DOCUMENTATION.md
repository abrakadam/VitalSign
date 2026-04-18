# Документация локализации VitalSign

## Обзор

VitalSign поддерживает мультиязычный интерфейс (i18n) с возможностью переключения между языками без перезапуска приложения.

## Поддерживаемые языки

- **Русский (ru)** - Язык по умолчанию
- **English (en)** - Английский
- **Polski (pl)** - Польский
- **Deutsch (de)** - Немецкий

## Структура файлов переводов

Файлы переводов находятся в папке `locales/`:
```
locales/
├── en.json  # Английский
├── ru.json  # Русский
├── pl.json  # Польский
└── de.json  # Немецкий
```

## Формат файлов переводов

Каждый файл переводов - это JSON с парами ключ-значение:
```json
{
    "app_name": "VitalSign",
    "app_title": "VitalSign - System Monitor",
    "settings": "Settings",
    ...
}
```

## Использование переводов в коде

### Импорт функции перевода
```python
from utils import t
```

### Получение перевода
```python
# Простой перевод
title = t('app_title')

# С дефолтным значением
title = t('unknown_key', 'Default Text')
```

### Изменение языка
```python
from utils import set_language

# Установить язык
set_language('en')  # Английский
set_language('ru')  # Русский
set_language('pl')  # Польский
set_language('de')  # Немецкий
```

### Получение текущего языка
```python
from utils import get_current_language

current_lang = get_current_language()
print(f"Текущий язык: {current_lang}")
```

### Получение списка доступных языков
```python
from utils import get_available_languages

languages = get_available_languages()
print(f"Доступные языки: {languages}")
# Вывод: ['en', 'ru', 'pl', 'de']
```

## Добавление нового языка

### 1. Создайте файл перевода
Создайте новый файл в `locales/` с кодом языка, например `fr.json` для французского:
```json
{
    "app_name": "VitalSign",
    "app_title": "VitalSign - Moniteur Système",
    "settings": "Paramètres",
    ...
}
```

### 2. Обновите translator.py
Добавьте новый язык в список языков:
```python
languages = ['en', 'ru', 'pl', 'de', 'fr']
```

### 3. Добавьте название языка
Обновите словарь названий языков:
```python
names = {
    'en': 'English',
    'ru': 'Русский',
    'pl': 'Polski',
    'de': 'Deutsch',
    'fr': 'Français'
}
```

### 4. Обновите SettingsDialog
Добавьте язык в комбобокс (автоматически, если используете `get_available_languages()`).

## Добавление новых ключей перевода

### 1. Добавьте ключ во все файлы переводов
```json
// en.json
{
    "new_key": "New text"
}

// ru.json
{
    "new_key": "Новый текст"
}

// pl.json
{
    "new_key": "Nowy tekst"
}

// de.json
{
    "new_key": "Neuer Text"
}
```

### 2. Используйте в коде
```python
text = t('new_key')
```

## Рекомендации по переводу

### Ключи перевода
- Используйте английские ключи
- Используйте snake_case
- Будьте описательными
- Избегайте сокращений

**Хорошо:**
```json
{
    "update_interval": "Update Interval",
    "disk_usage_title": "Disk Usage"
}
```

**Плохо:**
```json
{
    "upd_int": "Update Interval",
    "disk": "Disk Usage"
}
```

### Тексты с переменными
Используйте f-strings для текстов с переменными:
```python
f'{t("top_processes")} - {count}'
```

### Контекст
Если слово имеет несколько значений, используйте описательные ключи:
```json
{
    "usage_cpu": "CPU Usage",
    "usage_memory": "Memory Usage"
}
```

## Тестирование переводов

### Тестирование всех языков
```python
from utils import set_language, t

for lang in get_available_languages():
    set_language(lang)
    print(f"{lang}: {t('app_title')}")
```

### Проверка отсутствующих переводов
```python
from utils import _translator

base_lang = 'en'  # Английский как базовый
base_translations = _translator.translations[base_lang]

for lang in get_available_languages():
    if lang == base_lang:
        continue
    
    lang_translations = _translator.translations[lang]
    missing_keys = set(base_translations.keys()) - set(lang_translations.keys())
    
    if missing_keys:
        print(f"{lang} missing keys: {missing_keys}")
```

## Известные ограничения

- Перевод не применяется автоматически ко всем виджетам при смене языка
- Некоторые элементы требуют перезагрузки интерфейса
- Форматы даты и времени не локализованы
- Числовые форматы не локализованы

## Планируемые улучшения

- [ ] Автоматическое обновление всех виджетов при смене языка
- [ ] Локализация форматов даты и времени
- [ ] Локализация числовых форматов
- [ ] RTL (справа налево) поддержка
- [ ] Автоматическое обнаружение языка системы
