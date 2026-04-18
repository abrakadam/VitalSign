# Helpers

Эта папка содержит вспомогательные модули для проекта VitalSign.

## Структура

```
helpers/
├── cpp/              # C++ хелперы
│   ├── cpu_rater.h
│   ├── cpu_rater.cpp
│   ├── gpu_rater.h
│   ├── gpu_rater.cpp
│   └── README.md
└── python/          # Python хелперы
    ├── web_helper.py
    └── README.md
```

## C++ Helpers

Содержат модули для оценки производительности оборудования на C++:

- **cpu_rater**: Оценка процессоров
- **gpu_rater**: Оценка видеокарт (с поддержкой определения встроенных GPU)

Подробнее: [helpers/cpp/README.md](cpp/README.md)

## Python Helpers

Содержат модули для работы с веб-ресурсами и другими утилитами на Python:

- **web_helper**: Работа с веб-ресурсами о дистрибутивах Linux, драйверах и оборудовании

Подробнее: [helpers/python/README.md](python/README.md)

## Использование

### C++ хелперы

Для использования C++ хелперов:

1. Включите заголовочные файлы:
   ```cpp
   #include "helpers/cpp/cpu_rater.h"
   #include "helpers/cpp/gpu_rater.h"
   ```

2. Используйте классы:
   ```cpp
   CPURater::CPUInfo cpu_info = CPURater::rate_cpu("Intel Core i7-12700K");
   GPURater::GPUInfo gpu_info = GPURater::rate_gpu("NVIDIA RTX 4070", 8192, false);
   ```

### Python хелперы

Для использования Python хелперов:

1. Добавьте путь:
   ```python
   import sys
   import os
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers', 'python'))
   ```

2. Импортируйте модуль:
   ```python
   from web_helper import WebHelper
   ```

3. Используйте:
   ```python
   resources = WebHelper.get_distro_resources("Ubuntu")
   WebHelper.open_url(resources["official"])
   ```

## Компиляция C++ хелперов

### Отдельная компиляция
```bash
cd helpers/cpp
g++ -c cpu_rater.cpp -o cpu_rater.o
g++ -c gpu_rater.cpp -o gpu_rater.o
```

### Статическая библиотека
```bash
ar rcs libhelpers.a cpu_rater.o gpu_rater.o
```

### CMake
```cmake
add_library(helpers_cpp STATIC
    helpers/cpp/cpu_rater.cpp
    helpers/cpp/gpu_rater.cpp
)
```

## Лицензия

Все хелперы являются частью проекта VitalSign.
