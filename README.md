<div align="center">

# 🖥️ VitalSign

**Продвинутый мониторинг системных ресурсов с графическим интерфейсом**

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey)](https://github.com)

</div>

---

## 📋 Описание

**VitalSign** - это мощное приложение для мониторинга системных ресурсов с современным графическим интерфейсом на PyQt6. Программа предоставляет детальную информацию о системе, процессах, оборудовании и портах с поддержкой множества языков.

### ✨ Основные возможности

- 🖥️ **Мониторинг системы**: CPU, RAM, диск, сеть в реальном времени
- 📊 **Детальная информация**: BIOS, оборудование, драйверы, порты
- 🎮 **Оценка оборудования**: Рейтинг процессора и видеокарты
- 🔌 **Анализ портов**: Проверка HDMI, USB, Ethernet и других портов
- 🔋 **Мониторинг батареи**: Зарядка, напряжение, ток, мощность
- 🎧 **Аудио устройства**: Наушники, микрофоны, колонки
- 📱 **Периферия**: Клавиатура, мышь, другие устройства ввода
- 🖥️ **Анализ мониторов**: Информация о мониторах и их исправности
- 🌍 **Локализация**: Русский, английский и другие языки
- 🎨 **Современный UI**: Темная тема, анимации, карточки

---

## 🚀 Установка

### Быстрый старт

Хотите установить за 5 минут? Смотрите [Быстрый старт](QUICK_START.md).

### Linux (Ubuntu, Debian, Fedora и др.)

#### Клонирование репозитория
```bash
git clone https://github.com/yourusername/VitalSign.git
cd VitalSign
```

#### Установка зависимостей

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
sudo apt install libx11-dev libxtst-dev cmake build-essential
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip python3-venv
sudo dnf install libX11-devel libXtst-devel cmake gcc-c++
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip python-venv
sudo pacman -S libx11 libxtst cmake base-devel
```

#### Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Запуск
```bash
bash scripts/run_gui.sh
```

### Windows

#### Быстрая установка для новичков

Если вы новичок в программировании, следуйте [детальной инструкции для Windows](WINDOWS_INSTALLATION.md).

#### Клонирование репозитория
```bash
git clone https://github.com/yourusername/VitalSign.git
cd VitalSign
```

#### Установка зависимостей
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### Запуск
```powershell
scripts\run_gui.bat
```

---

## 📦 Сборка в EXE (Windows)

### Использование PyInstaller

#### Установка PyInstaller
```bash
pip install pyinstaller
```

#### Сборка
```bash
pyinstaller --onefile --windowed --name VitalSign --icon=resources/icon.ico ui/python/gui_main.py
```

#### Дополнительные опции
```bash
pyinstaller --onefile \
  --windowed \
  --name VitalSign \
  --icon=resources/icon.ico \
  --add-data "locales;locales" \
  --add-data "resources;resources" \
  --hidden-import PyQt6 \
  --hidden-import psutil \
  ui/python/gui_main.py
```

#### Создание spec-файла для сложной сборки
```bash
pyinstaller VitalSign.spec
```

### Использование Nuitka (опционально)

```bash
pip install nuitka
python -m nuitka --standalone --onefile --windows-disable-console ui/python/gui_main.py
```

---

## 📦 Создание DEB/RPM пакетов (Linux)

### DEB пакет (Ubuntu/Debian)

#### Установка инструментов
```bash
sudo apt install checkinstall
```

#### Создание пакета
```bash
sudo checkinstall -D --pkgname=vitalsign --pkgversion=1.0 --pkgrelease=1 \
  --maintainer="your@email.com" --requires="python3,python3-pyqt6,python3-psutil" \
  --nodoc bash scripts/run_gui.sh
```

### RPM пакет (Fedora/RHEL)

#### Установка инструментов
```bash
sudo dnf install rpm-build
```

#### Создание spec-файла
```bash
# Создайте файл vitalsign.spec в каталоге rpmbuild/SPECS/
```

#### Сборка
```bash
rpmbuild -ba vitalsign.spec
```

---

## 🏗️ Структура проекта

```
VitalSign/
├── helpers/                 # Вспомогательные модули
│   ├── cpp/                # C++ хелперы (cpu_rater, gpu_rater, monitor_analyzer, keyboard_analyzer, config_manager)
│   ├── python/             # Python хелперы (web_helper, config_manager)
│   └── README.md
├── main/                   # Основные анализаторы
│   ├── cpp/                # Системные C++ библиотеки
│   ├── linux/              # Linux-специфичные анализаторы
│   │   ├── device_analyzer.py
│   │   ├── distro_analyzer.py
│   │   ├── hardware_rater.py
│   │   └── ...
│   └── windows/            # Windows-специфичные (планируется)
├── ui/                     # Пользовательский интерфейс
│   └── python/             # PyQt6 GUI
│       ├── gui_main.py     # Основной GUI
│       └── ...
├── utils/                  # Утилиты
│   ├── translator.py       # Локализация
│   ├── fire_animation.py   # Анимация фона
│   └── ...
├── locales/                # Переводы
│   ├── ru.json             # Русский (по умолчанию)
│   └── en.json             # Английский
├── resources/              # Ресурсы
│   └── fonts/              # Шрифты
├── scripts/                # Скрипты запуска
├── requirements.txt         # Python зависимости
└── README.md
```

---

## 🎯 Возможности

### 🖥️ Основной GUI

- **Система**: Информация о BIOS, оборудовании, ОС
- **Процессы**: Топ процессов по CPU/RAM
- **Сеть**: Статистика сетевых интерфейсов
- **Температуры**: Мониторинг температуры компонентов
- **Оценка CPU**: Рейтинг процессора с категориями
- **Оценка GPU**: Рейтинг видеокарты (встроенная/дискретная)
- **Драйверы**: Загруженные модули ядра
- **Дистрибутивы**: Анализ и рекомендации по Linux
- **Устройства**: USB, PCI, устройства ввода
- **Порты**: Анализ портов и гнезд ноутбука
- **Мониторы**: Анализ мониторов и их исправности
- **Помощник**: Ссылки на ресурсы

### 🔌 Анализ портов

- Определение типа устройства (ноутбук/десктоп)
- Проверка HDMI, USB-C, USB-A, Ethernet
- Анализ аудиоразъема и SD-слота
- Рекомендации при обнаружении проблем

### 🖥️ Анализ мониторов

- Получение информации о всех подключенных мониторах
- Определение производителя, модели, серийного номера
- Проверка типа подключения (HDMI, DisplayPort, VGA, etc.)
- Анализ разрешения и частоты обновления
- Проверка здоровья монитора с оценкой 0-100
- Обнаружение проблем (низкое разрешение, низкая частота, отсутствие EDID)
- Определение основного монитора

### 🎮 Оценка оборудования

- **CPU**: База данных процессоров с оценками
- **GPU**: База данных видеокарт с оценками
- **Встроенные GPU**: Определение и корректная оценка
- **Категории**: Флагман, Высокий уровень, Средний уровень и др.

### 🌍 Локализация

- Русский (по умолчанию)
- Английский
- Переключение языка в настройках
- Полный перевод интерфейса

---

## 📖 Использование

### Запуск GUI
```bash
# Linux
bash scripts/run_gui.sh

# Windows
scripts\run_gui.bat

# Прямой запуск
python ui/python/gui_main.py
```

### Изменение языка
1. Откройте настройки (⚙️)
2. Выберите язык
3. Интерфейс автоматически обновится

### Проверка портов
Перейдите на вкладку "Порты и гнезда" для анализа состояния портов.

---

## 🛠️ Разработка

### Добавление нового языка

1. Создайте файл `locales/xx.json` (где xx - код языка)
2. Добавьте все ключи из `ru.json`
3. Переведите значения
4. Добавьте язык в `utils/translator.py`

### Добавление новых анализаторов

1. Создайте файл в `main/linux/` или `main/windows/`
2. Добавьте импорт в `main/linux/__init__.py`
3. Используйте в GUI

### Использование Config Manager

ConfigManager создает директорию для хранения конфигураций:
- **Linux/Mac**: `~/.VitalSign/`
- **Windows**: `%APPDATA%\VitalSign\` или `%USERPROFILE%\AppData\Roaming\VitalSign\`

Структура папки:
```
~/.VitalSign/ (Linux/Mac)
или
%APPDATA%\VitalSign\ (Windows)
├── config.ini          # Основной файл конфигурации (INI формат)
└── locales/            # Папка для локализаций
    ├── ru.json         # Русская локализация
    ├── en.json         # Английская локализация
    └── ...
```

Пример использования:
```python
from helpers.python.config_manager import ConfigManager

config = ConfigManager()

# Сохранить настройки
config.save_config("language", "ru")
config.save_config("theme", "dark")

# Загрузить настройки
language = config.load_config("language")
theme = config.load_config("theme")

# Сохранить JSON данные
config.save_json_config("window_state", {"x": 100, "y": 200, "width": 800, "height": 600})

# Сохранить локализацию
config.save_locale_data("ru", '{"hello": "Привет"}')
config.load_locale_data("ru")

# Получить список доступных локализаций
locales = config.get_available_locales()
```

---

## 📝 Требования

- Python 3.6+
- PyQt6 6.6+
- psutil 5.9+
- matplotlib 3.8+
- numpy 1.26+
- GPUtil 1.4+
- py-cpuinfo 9.0+

---

## 🤝 Вклад

Вклады приветствуются! Пожалуйста, создайте Pull Request.

1. Форкните репозиторий
2. Создайте ветку для фичи (`git checkout -b feature/AmazingFeature`)
3. Закоммитьте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Запушьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

---

## 📄 Лицензия

Этот проект лицензирован под лицензией MIT - см. файл [LICENSE](LICENSE) для деталей.

---

## 👨‍💻 Автор

**NPRevenanT** - Разработчик VitalSign

GitHub: https://github.com/abrakadam

---

<div align="center">

**Если вам понравился проект, поставьте ⭐️**

</div>
