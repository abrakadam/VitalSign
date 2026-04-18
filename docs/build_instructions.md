# Инструкции по сборке проекта

## Python часть

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Запуск
```bash
python main.py
```

### Опции
```bash
# Одиночный замер
python main.py --single

# Интервал обновления 2 секунды
python main.py --interval 2
```

## C++ часть

### Linux
```bash
cd cpp
mkdir build && cd build
cmake ..
make
```

### Windows
```bash
cd cpp
mkdir build && cd build
cmake ..
cmake --build .
```

### Запуск C++ монитора FPS
```bash
# Linux
./cpp/build/fps_monitor

# Windows
cpp\build\Debug\fps_monitor.exe
```

## Полная сборка проекта

```bash
# Python зависимости
pip install -r requirements.txt

# C++ часть
cd cpp
mkdir build && cd build
cmake ..
make
cd ../..

# Запуск
python main.py
```
