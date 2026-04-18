# Python Helpers

Эта папка содержит Python хелперы для работы с веб-ресурсами и другими утилитами.

## Содержание

### 1. web_helper.py
Модуль для работы с веб-ресурсами и поиска информации о дистрибутивах Linux.

#### Описание
`WebHelper` - класс для управления ссылками на веб-ресурсы о дистрибутивах Linux, драйверах и оборудовании.

---

## WebHelper

### Класс WebHelper

#### Основные атрибуты

**`DISTRO_RESOURCES`** (dict)
- Словарь с ресурсами для конкретных дистрибутивов
- Структура: `{distro_name: {resource_type: url}}`
- Примеры: Ubuntu, Fedora, Arch Linux, Debian, Linux Mint и др.

**`GENERAL_RESOURCES`** (dict)
- Словарь с общими ресурсами о Linux
- Включает: DistroWatch, Linux.org, Arch Wiki и др.

#### Методы

**`static get_distro_resources(distro_name: str) -> Dict[str, str]`**
- Получает ресурсы для конкретного дистрибутива
- Параметры:
  - `distro_name`: название дистрибутива
- Возвращает: словарь с ресурсами (official, documentation, community, download и т.д.)
- Пример:
  ```python
  resources = WebHelper.get_distro_resources("Ubuntu")
  # {'official': 'https://ubuntu.com', 'documentation': 'https://ubuntu.com/server/docs', ...}
  ```

**`static open_url(url: str)`**
- Открывает URL в браузере по умолчанию
- Параметры:
  - `url`: URL для открытия
- Пример:
  ```python
  WebHelper.open_url("https://ubuntu.com")
  ```

**`static search_distro_info(distro_name: str)`**
- Ищет информацию о дистрибутиве в Google
- Параметры:
  - `distro_name`: название дистрибутива
- Пример:
  ```python
  WebHelper.search_distro_info("Ubuntu 22.04")
  ```

**`static get_all_distros() -> List[str]`**
- Получает список всех дистрибутивов в базе данных
- Возвращает: список строк с названиями дистрибутивов
- Пример:
  ```python
  distros = WebHelper.get_all_distros()
  # ['Ubuntu', 'Fedora', 'Arch Linux', 'Debian', ...]
  ```

**`static get_hardware_resources() -> Dict[str, str]`**
- Получает ресурсы по оборудованию
- Возвращает: словарь с ресурсами (Arch Wiki Hardware, Ubuntu Hardware и др.)
- Пример:
  ```python
  hw_resources = WebHelper.get_hardware_resources()
  # {'Arch Wiki - Hardware': 'https://wiki.archlinux.org/index.php/Hardware', ...}
  ```

**`static get_driver_resources() -> Dict[str, str]`**
- Получает ресурсы по драйверам
- Возвращает: словарь с ресурсами (NVIDIA Drivers, AMD Drivers, Intel Drivers и др.)
- Пример:
  ```python
  driver_resources = WebHelper.get_driver_resources()
  # {'NVIDIA Drivers': 'https://www.nvidia.com/Download/index.aspx', ...}
  ```

---

## Примеры использования

### Пример 1: Получение ресурсов для дистрибутива

```python
from helpers.python.web_helper import WebHelper

# Получаем ресурсы для Ubuntu
ubuntu_resources = WebHelper.get_distro_resources("Ubuntu")

print("Официальный сайт:", ubuntu_resources.get("official"))
print("Документация:", ubuntu_resources.get("documentation"))
print("Сообщество:", ubuntu_resources.get("community"))
print("Скачать:", ubuntu_resources.get("download"))
```

### Пример 2: Открытие ресурса в браузере

```python
from helpers.python.web_helper import WebHelper

# Открываем официальный сайт Arch Linux
WebHelper.open_url("https://archlinux.org")

# Или через метод get_distro_resources
arch_resources = WebHelper.get_distro_resources("Arch Linux")
WebHelper.open_url(arch_resources["wiki"])
```

### Пример 3: Поиск информации о дистрибутиве

```python
from helpers.python.web_helper import WebHelper

# Ищем информацию о Fedora в Google
WebHelper.search_distro_info("Fedora 39 review")
```

### Пример 4: Получение списка всех дистрибутивов

```python
from helpers.python.web_helper import WebHelper

# Получаем список всех дистрибутивов
distros = WebHelper.get_all_distros()

print("Доступные дистрибутивы:")
for distro in distros:
    print(f"- {distro}")
```

### Пример 5: Получение ресурсов по оборудованию

```python
from helpers.python.web_helper import WebHelper

# Получаем ресурсы по оборудованию
hw_resources = WebHelper.get_hardware_resources()

print("Ресурсы по оборудованию:")
for name, url in hw_resources.items():
    print(f"- {name}: {url}")
```

### Пример 6: Получение ресурсов по драйверам

```python
from helpers.python.web_helper import WebHelper

# Получаем ресурсы по драйверам
driver_resources = WebHelper.get_driver_resources()

print("Ресурсы по драйверам:")
for name, url in driver_resources.items():
    print(f"- {name}: {url}")
```

### Пример 7: Использование в GUI (PyQt6)

```python
from PyQt6.QtWidgets import QPushButton
from helpers.python.web_helper import WebHelper

# Создаем кнопку для открытия ресурса
button = QPushButton("Открыть Arch Wiki")
button.clicked.connect(lambda: WebHelper.open_url("https://wiki.archlinux.org"))

# Или с динамическим ресурсом
resources = WebHelper.get_hardware_resources()
for name, url in resources.items():
    btn = QPushButton(name)
    btn.clicked.connect(lambda checked, u=url: WebHelper.open_url(u))
    layout.addWidget(btn)
```

---

## Доступные дистрибутивы

Модуль поддерживает следующие дистрибутивы:
- Ubuntu
- Fedora
- Arch Linux
- Debian
- Linux Mint
- Pop!_OS
- Manjaro
- openSUSE
- CentOS
- Kubuntu
- Lubuntu
- Xubuntu

---

## Доступные ресурсы

### Общие ресурсы
- DistroWatch
- Linux.org
- Linux.com
- Arch Linux Wiki
- Ubuntu Wiki
- Fedora Wiki

### Ресурсы по оборудованию
- Arch Wiki - Hardware
- Ubuntu Hardware Support
- Linux Hardware
- PCI IDs

### Ресурсы по драйверам
- NVIDIA Drivers
- AMD Drivers
- Intel Drivers
- Ubuntu Drivers

---

## Интеграция с проектом

### Добавление в путь Python

```python
import sys
import os

# Добавляем папку helpers/python в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers', 'python'))

from web_helper import WebHelper
```

### Использование в VitalSign GUI

```python
# В ui/python/gui_main.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'helpers', 'python'))

from web_helper import WebHelper

# Использование в create_helper_tab()
resources = WebHelper.get_hardware_resources()
for name, url in resources.items():
    btn = QPushButton(name)
    btn.clicked.connect(lambda checked, u=url: WebHelper.open_url(u))
    layout.addWidget(btn)
```

---

## Расширение функциональности

### Добавление нового дистрибутива

```python
from helpers.python.web_helper import WebHelper

# Добавляем новый дистрибутив в базу данных
WebHelper.DISTRO_RESOURCES["MyDistro"] = {
    'official': 'https://mydistro.org',
    'documentation': 'https://mydistro.org/docs',
    'community': 'https://community.mydistro.org',
    'download': 'https://mydistro.org/download'
}
```

### Добавление нового общего ресурса

```python
from helpers.python.web_helper import WebHelper

# Добавляем новый общий ресурс
WebHelper.GENERAL_RESOURCES["My Resource"] = "https://myresource.com"
```

---

## Требования

- Python 3.6 или выше
- Модуль `webbrowser` (входит в стандартную библиотеку Python)
- Для работы с GUI: PyQt6

---

## Примечания

- Модуль использует браузер по умолчанию системы для открытия URL
- Все URL открываются в новой вкладке/окне браузера
- Модуль не требует интернет-соединения для работы с базой данных URL (только для их открытия)

---

## Лицензия

Этот код является частью проекта VitalSign.
