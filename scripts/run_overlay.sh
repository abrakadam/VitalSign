#!/bin/bash
# Скрипт запуска VitalSign Overlay

echo "=== Запуск VitalSign Overlay ==="
echo

# Используем виртуальное окружение если оно существует
if [ -d "venv" ]; then
    echo "Использую виртуальное окружение..."
    ./venv/bin/python gui_overlay.py
else
    echo "Виртуальное окружение не найдено. Использую системный python3..."
    python3 gui_overlay.py
fi
