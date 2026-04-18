# Main - Основные анализаторы системы

Эта папка содержит основные анализаторы системы, разделенные по операционным системам.

## Структура

```
main/
├── README.md
├── linux/           # Linux-специфичные анализаторы
│   ├── device_analyzer.py
│   ├── device_analyzer.h
│   ├── device_analyzer.cpp
│   ├── distro_analyzer.py
│   ├── gpu_monitor.py
│   ├── hardware_rater.py
│   ├── system_info_lib.py
│   ├── system_monitor.py
│   └── window_monitor.py
└── windows/         # Windows-специфичные анализаторы (пусто)
```

## Linux Анализаторы

### device_analyzer
Анализатор подключенных устройств, батареи и портов.

**Функции:**
- `get_usb_devices()` - информация о USB устройствах
- `get_battery_info()` - информация о батарее и зарядке
- `get_audio_devices()` - информация об аудиоустройствах
- `get_input_devices()` - информация об устройствах ввода
- `get_port_info()` - информация о портах и типе устройства
- `detect_battery_issues()` - обнаружение проблем с батареей
- `detect_audio_issues()` - обнаружение проблем с аудио
- `get_usb_device_type()` - определение типа USB устройства

### distro_analyzer
Анализатор дистрибутива Linux.

### gpu_monitor
Мониторинг GPU.

### hardware_rater
Оценка производительности CPU и GPU.

### system_info_lib
Библиотека системной информации.

### system_monitor
Мониторинг системы.

### window_monitor
Мониторинг окон.

## Windows Анализаторы

Папка `windows/` предназначена для Windows-специфичных анализаторов.

В настоящее время пусто - планируется добавление аналогичных модулей для Windows.

## Использование

### Python

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'main', 'linux'))

from device_analyzer import DeviceAnalyzer

analyzer = DeviceAnalyzer()
battery_info = analyzer.get_battery_info()
print(f"Заряд: {battery_info['percentage']}%")
```

### C++

```cpp
#include "main/linux/device_analyzer.h"

DeviceAnalyzer::BatteryInfo battery = DeviceAnalyzer::get_battery_info();
std::cout << "Заряд: " << battery.percentage << "%" << std::endl;
```

## Лицензия

Код является частью проекта VitalSign.
