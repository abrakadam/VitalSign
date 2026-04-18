# Примеры использования VitalSign

## Базовое использование

### Графический интерфейс (GUI)
```bash
# Прямой запуск
python gui_main.py

# Через скрипт (Linux)
bash scripts/run_gui.sh

# Через скрипт (Windows)
scripts\run_gui.bat
```

### Консольный мониторинг
```bash
# Одиночный замер системы
python main.py --single

# Непрерывный мониторинг
python main.py

# Мониторинг с интервалом 2 секунды
python main.py --interval 2
```

## Использование скриптов

### Сборка проекта (Linux)
```bash
bash scripts/build.sh
```

### Сборка проекта (Windows)
```bash
scripts\build.bat
```

### Запуск с автоматической сборкой (Linux)
```bash
bash scripts/run.sh
```

## Программное использование

### Использование SystemMonitor в Python
```python
from python.system_monitor import SystemMonitor

monitor = SystemMonitor()
monitor.update()
stats = monitor.get_stats()

print(f"CPU: {stats['cpu_percent']:.1f}%")
print(f"RAM: {stats['memory_used_gb']:.2f} GB")
```

### Использование ConsoleStyle для красивого вывода
```python
from utils import ConsoleStyle, Color

ConsoleStyle.print_header("Мой заголовок", 50)
ConsoleStyle.print_stat("Значение", "100", Color.GREEN)
ConsoleStyle.print_warning("Предупреждение")
ConsoleStyle.print_error("Ошибка")
ConsoleStyle.print_success("Успех")
```

### Использование FormatUtils для форматирования
```python
from utils import FormatUtils

# Форматирование байтов
print(FormatUtils.format_bytes(1024 * 1024 * 500))  # "500.00 MB"

# Обрезка текста
print(FormatUtils.truncate_text("Длинный текст", 10))  # "Длинный ..."

# Форматирование процентов
print(FormatUtils.format_percent(75.5))  # "75.5%"
```

## C++ использование

### Сборка и запуск
```bash
cd cpp
mkdir -p build && cd build
cmake ..
make
./fps_monitor
```

### Использование библиотеки fps_lib
```cpp
#include "fps_lib.h"

int main() {
    FPSLib fpsLib;
    fpsLib.setTargetWindow("Мое окно");
    fpsLib.startMonitoring();
    
    // ... работа ...
    
    fpsLib.stopMonitoring();
    return 0;
}
```
