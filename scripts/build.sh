#!/bin/bash
# Скрипт сборки проекта VitalSign

set -e

echo "=== Сборка VitalSign ==="
echo

# Проверка Python зависимостей
echo "1. Проверка Python зависимостей..."
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не установлен"
    exit 1
fi

echo "Установка Python зависимостей..."
pip install -r requirements.txt

# Проверка PyQt6
echo
echo "2. Проверка PyQt6 для GUI..."
python3 -c "import PyQt6" 2>/dev/null || {
    echo "PyQt6 не установлен. Устанавливаю..."
    pip install PyQt6
}

# Сборка C++ части
echo
echo "3. Сборка C++ модуля..."
cd cpp
mkdir -p build
cd build
cmake ..
make
cd ../..

echo
echo "=== Сборка завершена успешно ==="
echo
echo "Для запуска:"
echo "  GUI:       python gui_main.py"
echo "  Консоль:   python main.py"
echo "  C++:       ./cpp/build/fps_monitor"
