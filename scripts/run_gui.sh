#!/bin/bash
# Скрипт запуска VitalSign GUI

echo "=== Запуск VitalSign GUI ==="
echo

# Используем виртуальное окружение если оно существует
if [ -d "venv" ]; then
    echo "Использую виртуальное окружение..."
    ./venv/bin/python ui/python/gui_main.py
else
    echo "Виртуальное окружение не найдено. Использую системный python3..."
    python3 ui/python/gui_main.py
fi
