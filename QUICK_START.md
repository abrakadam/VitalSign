# Быстрый старт VitalSign

Быстрая установка и запуск VitalSign за 5 минут.

---

## Linux (Ubuntu/Debian/Fedora/Arch)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/abrakadam/VitalSign.git
cd VitalSign

# 2. Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить
bash scripts/run_gui.sh
```

---

## Windows

### Вариант 1: Через bat-файл (проще)

1. Скачать ZIP с GitHub: https://github.com/abrakadam/VitalSign
2. Распаковать архив
3. Открыть папку `scripts`
4. Дважды кликнуть на `run_gui.bat`

### Вариант 2: Через терминал

```powershell
# 1. Скачать ZIP с GitHub и распаковать

# 2. Открыть терминал в папке проекта

# 3. Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Запустить
python ui/python/gui_main.py
```

**Детальная инструкция для Windows:** [WINDOWS_INSTALLATION.md](WINDOWS_INSTALLATION.md)

---

## Требования

- Python 3.6+
- PyQt6 6.6+
- psutil 5.9+
- matplotlib 3.8+
- numpy 1.26+

---

## Возможные проблемы

### Linux: "python3: command not found"
```bash
sudo apt install python3 python3-pip python3-venv
```

### Windows: "python не является внутренней командой"
1. Переустановить Python
2. Поставить галочку "Add Python to PATH"
3. Перезапустить терминал

---

## Автор

**NPRevenanT** - https://github.com/abrakadam

---

**Удачи! 🎉**
