#!/bin/bash
# Скрипт запуска Discord-style VitalSign Overlay

echo "=== Запуск Discord-style VitalSign Overlay ==="
echo

# Используем виртуальное окружение если оно существует
if [ -d "venv" ]; then
    echo "Использую виртуальное окружение..."
    ./venv/bin/python ui/python/gui_discord_overlay.py
else
    echo "Виртуальное окружение не найдено. Использую системный python3..."
    python3 ui/python/gui_discord_overlay.py
fi
