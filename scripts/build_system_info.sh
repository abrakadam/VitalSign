#!/bin/bash
# Скрипт для сборки C++ библиотеки системной информации

echo "=== Сборка C++ System Info Library ==="
echo

# Создаем папку для сборки
mkdir -p build/lib
cd build

# Настраиваем CMake
echo "Настраиваем CMake..."
cmake -DCMAKE_BUILD_TYPE=Release ../cpp

# Собираем
echo "Собираем..."
cmake --build . --config Release

echo "=== Сборка завершена ==="
