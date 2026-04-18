# C++ Helpers

Эта папка содержит C++ хелперы для оценки производительности оборудования и работы с веб-ресурсами.

## Содержание

### 1. cpu_rater.h / cpu_rater.cpp
Модуль для оценки производительности процессоров.

#### Описание
`CPURater` - класс для оценки процессоров на основе их характеристик и базы данных известных моделей.

#### Структура CPUInfo
```cpp
struct CPUInfo {
    std::string name;           // Название процессора
    int cores;                  // Количество ядер
    double frequency;           // Частота в GHz
    std::string architecture;   // Архитектура
    int score;                  // Оценка (0-100)
    std::string rating;         // Текстовая оценка (Отлично, Хорошо и т.д.)
    std::string category;       // Категория (flagship, high_end, mid_range и т.д.)
    bool estimated;             // Была ли оценка по характеристикам (true) или по базе (false)
};
```

#### Основные методы

**`static std::map<std::string, int> get_cpu_database()`**
- Возвращает базу данных процессоров с оценками
- Ключ: название процессора, Значение: оценка (0-100)

**`static CPUInfo rate_cpu(std::string cpu_name, int cores = 0, double freq = 0)`**
- Оценивает процессор
- Параметры:
  - `cpu_name`: название процессора
  - `cores`: количество ядер (опционально)
  - `freq`: частота в GHz (опционально)
- Возвращает: структуру CPUInfo с оценкой

**`static CPUInfo get_cpu_info_from_system()`**
- Считывает информацию о CPU из `/proc/cpuinfo`
- Возвращает: структуру CPUInfo с данными из системы

**`static int estimate_cpu_score(int cores, double freq)`**
- Оценивает процессор по количеству ядер и частоте
- Используется, если процессор не найден в базе данных

#### Примеры использования

```cpp
#include "cpu_rater.h"

// Пример 1: Оценка по названию (поиск в базе данных)
CPURater::CPUInfo info1 = CPURater::rate_cpu("Intel Core i7-12700K");
std::cout << "Оценка: " << info1.score << "/100" << std::endl;
std::cout << "Категория: " << info1.rating << std::endl;

// Пример 2: Оценка по характеристикам (если не в базе)
CPURater::CPUInfo info2 = CPURater::rate_cpu("Unknown CPU", 8, 3.5);
std::cout << "Оценка: " << info2.score << "/100" << std::endl;
std::cout << "Оценено по характеристикам: " << (info2.estimated ? "да" : "нет") << std::endl;

// Пример 3: Получение информации из системы
CPURater::CPUInfo sys_info = CPURater::get_cpu_info_from_system();
std::cout << "Процессор: " << sys_info.name << std::endl;
std::cout << "Ядра: " << sys_info.cores << std::endl;
std::cout << "Частота: " << sys_info.frequency << " GHz" << std::endl;
```

---

### 2. gpu_rater.h / gpu_rater.cpp
Модуль для оценки производительности видеокарт.

#### Описание
`GPURater` - класс для оценки видеокарт на основе их характеристик и базы данных известных моделей.

#### Структура GPUInfo
```cpp
struct GPUInfo {
    std::string name;           // Название видеокарты
    int vram;                   // Объем видеопамяти в MB
    bool is_integrated;         // Встроенная ли видеокарта
    int score;                  // Оценка (0-100)
    std::string rating;         // Текстовая оценка
    std::string category;       // Категория
    bool estimated;             // Была ли оценка по характеристикам
};
```

#### Основные методы

**`static std::map<std::string, int> get_gpu_database()`**
- Возвращает базу данных видеокарт с оценками

**`static GPUInfo rate_gpu(std::string gpu_name, int vram = 0, bool is_integrated = false)`**
- Оценивает видеокарту
- Параметры:
  - `gpu_name`: название видеокарты
  - `vram`: объем видеопамяти в MB (опционально)
  - `is_integrated`: встроенная ли видеокарта (опционально)
- Возвращает: структуру GPUInfo с оценкой
- Примечание: встроенные видеокарты получают сниженную оценку (на 40%)

**`static bool is_integrated_gpu(std::string gpu_name)`**
- Определяет, является ли видеокарта встроенной
- Проверяет наличие ключевых слов: Intel Iris/UHD/HD, AMD Radeon Vega/Graphics и т.д.

**`static int estimate_gpu_score(int vram)`**
- Оценивает видеокарту по объему VRAM
- Используется, если видеокарта не найдена в базе данных

#### Примеры использования

```cpp
#include "gpu_rater.h"

// Пример 1: Оценка дискретной видеокарты
GPURater::GPUInfo info1 = GPURater::rate_gpu("NVIDIA RTX 4070", 8192, false);
std::cout << "Оценка: " << info1.score << "/100" << std::endl;
std::cout << "Категория: " << info1.rating << std::endl;

// Пример 2: Оценка встроенной видеокарты
GPURater::GPUInfo info2 = GPURater::rate_gpu("Intel Iris Xe", 0, true);
std::cout << "Оценка: " << info2.score << "/100" << std::endl;
std::cout << "Встроенная: " << (info2.is_integrated ? "да" : "нет") << std::endl;

// Пример 3: Проверка типа видеокарты
std::string gpu_name = "AMD Radeon Graphics";
bool is_igpu = GPURater::is_integrated_gpu(gpu_name);
std::cout << gpu_name << " - " << (is_igpu ? "встроенная" : "дискретная") << std::endl;
```

---

## Система оценок

### Шкала оценок (0-100)
- **90-100**: Флагман (Отлично) - топовые модели
- **75-89**: Высокий уровень (Очень хорошо) - высокопроизводительные модели
- **60-74**: Средний уровень (Хорошо) - средний сегмент
- **45-59**: Начальный уровень (Средне) - бюджетный сегмент
- **30-44**: Бюджетный (Ниже среднего) - очень бюджетные модели
- **1-29**: Слабо - устаревшие или очень слабые модели
- **0**: Неизвестно - нет данных

### Особенности оценки
- Встроенные видеокарты получают сниженную оценку (на 40%)
- Если модель не найдена в базе данных, оценка производится по характеристикам
- Для CPU: оценка по количеству ядер и частоте
- Для GPU: оценка по объему VRAM

---

## Компиляция

### Отдельная компиляция
```bash
g++ -c cpu_rater.cpp -o cpu_rater.o
g++ -c gpu_rater.cpp -o gpu_rater.o
```

### Статическая библиотека
```bash
ar rcs libhelpers.a cpu_rater.o gpu_rater.o
```

### CMake
Добавьте в ваш CMakeLists.txt:
```cmake
add_library(helpers_cpp STATIC
    cpu_rater.cpp
    gpu_rater.cpp
)

target_include_directories(helpers_cpp PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
```

---

## Интеграция с Python

Для использования C++ хелперов из Python можно использовать pybind11.

### Пример модуля pybind11

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "cpu_rater.h"
#include "gpu_rater.h"

namespace py = pybind11;

PYBIND11_MODULE(hardware_rater_cpp, m) {
    m.doc() = "C++ Hardware Rating Helpers";
    
    // CPU Rater
    py::class_<CPURater::CPUInfo>(m, "CPUInfo")
        .def(py::init<>())
        .def_readwrite("name", &CPURater::CPUInfo::name)
        .def_readwrite("cores", &CPURater::CPUInfo::cores)
        .def_readwrite("frequency", &CPURater::CPUInfo::frequency)
        .def_readwrite("architecture", &CPURater::CPUInfo::architecture)
        .def_readwrite("score", &CPURater::CPUInfo::score)
        .def_readwrite("rating", &CPURater::CPUInfo::rating)
        .def_readwrite("category", &CPURater::CPUInfo::category)
        .def_readwrite("estimated", &CPURater::CPUInfo::estimated);
    
    m.def("rate_cpu", &CPURater::rate_cpu, 
          py::arg("cpu_name"), py::arg("cores") = 0, py::arg("freq") = 0,
          "Rate a CPU by name and characteristics");
    
    m.def("get_cpu_info_from_system", &CPURater::get_cpu_info_from_system,
          "Get CPU information from system (/proc/cpuinfo)");
    
    // GPU Rater
    py::class_<GPURater::GPUInfo>(m, "GPUInfo")
        .def(py::init<>())
        .def_readwrite("name", &GPURater::GPUInfo::name)
        .def_readwrite("vram", &GPURater::GPUInfo::vram)
        .def_readwrite("is_integrated", &GPURater::GPUInfo::is_integrated)
        .def_readwrite("score", &GPURater::GPUInfo::score)
        .def_readwrite("rating", &GPURater::GPUInfo::rating)
        .def_readwrite("category", &GPURater::GPUInfo::category)
        .def_readwrite("estimated", &GPURater::GPUInfo::estimated);
    
    m.def("rate_gpu", &GPURater::rate_gpu,
          py::arg("gpu_name"), py::arg("vram") = 0, py::arg("is_integrated") = false,
          "Rate a GPU by name and characteristics");
    
    m.def("is_integrated_gpu", &GPURater::is_integrated_gpu,
          "Check if a GPU is integrated");
}
```

### Компиляция с pybind11
```cmake
find_package(pybind11 REQUIRED)

pybind11_add_module(hardware_rater_cpp
    cpu_rater.cpp
    gpu_rater.cpp
)
```

### Использование из Python
```python
import hardware_rater_cpp

# Оценка CPU
cpu_info = hardware_rater_cpp.rate_cpu("Intel Core i7-12700K", 12, 4.5)
print(f"CPU: {cpu_info.name}")
print(f"Оценка: {cpu_info.score}/100")
print(f"Категория: {cpu_info.rating}")

# Оценка GPU
gpu_info = hardware_rater_cpp.rate_gpu("NVIDIA RTX 4070", 8192, False)
print(f"GPU: {gpu_info.name}")
print(f"Оценка: {gpu_info.score}/100")
print(f"Тип: {'встроенная' if gpu_info.is_integrated else 'дискретная'}")
```

---

## Требования

- C++11 или выше
- Linux (для функции get_cpu_info_from_system)
- Для интеграции с Python: pybind11

---

## Лицензия

Этот код является частью проекта VitalSign.
