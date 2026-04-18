#!/bin/bash
# Скрипт запуска расширенной GUI версии VitalSign

echo "=== Запуск VitalSign Advanced GUI ==="
echo

# Используем виртуальное окружение если оно существует
if [ -d "venv" ]; then
    echo "Использую виртуальное окружение..."
    ./venv/bin/python gui_advanced.py
else
    echo "Виртуальное окружение не найдено. Использую системный python3..."
    # Проверка установки PyQt6
    python3 -c "import PyQt6, matplotlib" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "PyQt6 или matplotlib не установлен. Создаю виртуальное окружение и устанавливаю..."
        python3 -m venv venv
        ./venv/bin/pip install -r requirements.txt
    fi
    python3 gui_advanced.py
fi
