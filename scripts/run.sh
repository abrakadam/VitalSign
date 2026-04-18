#!/bin/bash
# Скрипт запуска VitalSign

echo "=== VitalSign ==="
echo

# Используем виртуальное окружение если оно существует
if [ -d "venv" ]; then
    echo "Использую виртуальное окружение..."
    ./venv/bin/python ui/python/main.py "$@"
else
    echo "Виртуальное окружение не найдено. Использую системный python3..."
    python3 ui/python/main.py "$@"
fi

# Проверка сборки
if [ ! -f "cpp/build/fps_monitor" ]; then
    echo "C++ модуль не собран. Запускаю сборку..."
    bash scripts/build.sh
fi

# Запуск Python мониторинга
echo "Запуск Python мониторинга..."
$PYTHON_CMD main.py "$@"
