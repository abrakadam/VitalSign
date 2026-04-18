# Документация C++ модулей VitalSign

## Обзор

VitalSign включает два C++ модуля для системного мониторинга и захвата FPS.

## Структура C++ части

### Библиотеки (lib/cpp/)

#### fps_lib
- **fps_lib.h**: Заголовочный файл библиотеки FPS
- **fps_lib.cpp**: Реализация библиотеки FPS

#### system_lib
- **system_lib.h**: Заголовочный файл системной библиотеки
- **system_lib.cpp**: Реализация системной библиотеки

### Исполняемые файлы (cpp/)

#### fps_monitor.cpp
Мониторинг FPS для окон и приложений.

#### system_monitor.cpp
Консольный системный монитор с использованием system_lib.

## SystemLib API

### Структура SystemStats
```cpp
struct SystemStats {
    double cpu_usage;        // Использование CPU в %
    double memory_usage;     // Использование памяти в MB
    double memory_total;     // Общий объем памяти в MB
    double disk_usage;       // Использование диска в GB
    double disk_total;       // Общий объем диска в GB
    unsigned long network_sent;  // Отправленные байты
    unsigned long network_recv;  // Полученные байты
};
```

### Методы SystemLib

#### getSystemStats()
Получить полную статистику системы.
```cpp
SystemStats stats = sysLib.getSystemStats();
```

#### getCPUUsage()
Получить использование CPU в процентах.
```cpp
double cpu = sysLib.getCPUUsage();
```

#### getMemoryUsage()
Получить использование памяти в MB.
```cpp
double mem = sysLib.getMemoryUsage();
```

#### getTotalMemory()
Получить общий объем памяти в MB.
```cpp
double total = sysLib.getTotalMemory();
```

#### getDiskUsage(path)
Получить использование диска в GB.
```cpp
double disk = sysLib.getDiskUsage("/");  // Linux
double disk = sysLib.getDiskUsage("C:\\");  // Windows
```

#### getTotalDisk(path)
Получить общий объем диска в GB.
```cpp
double total = sysLib.getTotalDisk("/");
```

#### getNetworkStats(sent, recv)
Получить сетевую статистику.
```cpp
unsigned long sent, recv;
sysLib.getNetworkStats(sent, recv);
```

#### getProcessList()
Получить список запущенных процессов.
```cpp
std::vector<std::string> processes = sysLib.getProcessList();
```

#### getCPUTemperature()
Получить температуру CPU (только Linux).
```cpp
double temp = sysLib.getCPUTemperature();  // В градусах Цельсия
```

## Кроссплатформенность

### Linux
- CPU: Чтение из `/proc/stat`
- Память: `sysinfo()`
- Диск: `statvfs()`
- Сеть: `/proc/net/dev`
- Процессы: `/proc/[pid]/cmdline`
- Температура: `/sys/class/thermal/`

### Windows
- CPU: `GetSystemTimes()`
- Память: `GlobalMemoryStatusEx()`
- Диск: `GetDiskFreeSpaceExA()`
- Сеть: Требует `GetIfTable2()` (упрощено в текущей версии)
- Процессы: `CreateToolhelp32Snapshot()`
- Температура: Требует WMI (не реализовано)

## Сборка

### Linux
```bash
cd cpp
mkdir -p build && cd build
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

## Результаты сборки

После сборки в папке `cpp/build/` будут созданы:
- `fps_monitor` - Исполняемый файл монитора FPS
- `system_monitor` - Исполняемый файл системного монитора

## Использование

### Запуск system_monitor
```bash
./cpp/build/system_monitor  # Linux
cpp\build\Debug\system_monitor.exe  # Windows
```

### Запуск fps_monitor
```bash
./cpp/build/fps_monitor  # Linux
cpp\build\Debug\fps_monitor.exe  # Windows
```

## Интеграция с Python

Для интеграции C++ библиотек с Python можно использовать:
- **ctypes**: Для вызова C++ функций из Python
- **pybind11**: Для создания Python модулей на C++
- **Boost.Python**: Альтернатива pybind11

Пример с ctypes:
```python
import ctypes

# Загрузка библиотеки
sys_lib = ctypes.CDLL('./lib/cpp/libsystem_lib.so')

# Определение типов
sys_lib.getCPUUsage.restype = ctypes.c_double

# Вызов функции
cpu = sys_lib.getCPUUsage()
print(f"CPU: {cpu}%")
```

## Производительность

C++ модули обеспечивают:
- Минимальное использование ресурсов
- Быстрый сбор данных
- Прямой доступ к системным API
- Отсутствие накладных расходов Python GIL

## Будущие улучшения

- [ ] Реализация сетевой статистики для Windows
- [ ] Поддержка GPU мониторинга
- [ ] Мониторинг температуры для Windows
- [ ] Интеграция с Python через pybind11
- [ ] Графический интерфейс на C++ (Qt)
