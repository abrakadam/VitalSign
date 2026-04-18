# Linux Анализаторы

Эта папка содержит Linux-специфичные анализаторы для проекта VitalSign.

## Содержание

### 1. device_analyzer.py / device_analyzer.h / device_analyzer.cpp
Анализатор подключенных устройств, батареи, аудио и портов.

#### Python Версия (device_analyzer.py)

**Класс DeviceAnalyzer**

**Методы:**

**`get_usb_devices() -> List[Dict[str, str]]`**
- Получает информацию о USB устройствах через lsusb
- Возвращает список словарей с информацией о каждом устройстве

**`get_pci_devices() -> List[Dict[str, str]]`**
- Получает информацию о PCI устройствах через lspci
- Возвращает список словарей с детальной информацией

**`get_input_devices() -> List[Dict[str, str]]`**
- Получает информацию об устройствах ввода
- Проверяет /dev/input и xinput

**`get_battery_info() -> Dict[str, any]`**
- Получает информацию о батарее из /sys/class/power_supply/
- Возвращает:
  - `is_present`: наличие батареи
  - `is_charging`: статус зарядки
  - `percentage`: процент заряда
  - `voltage_mv`: напряжение в мВ
  - `current_ma`: ток в мА
  - `power_mw`: мощность в мВт
  - `manufacturer`: производитель
  - `model`: модель
  - `technology`: технология (Li-ion, etc.)
  - `status`: статус (Charging, Discharging, etc.)

**`detect_battery_issues(battery_info) -> List[str]`**
- Обнаруживает проблемы с батареей
- Проверяет низкий заряд, низкое напряжение, медленную зарядку

**`get_audio_devices() -> List[Dict[str, str]]`**
- Получает информацию об аудиоустройствах через aplay
- Определяет тип: headphones, microphone, speakers

**`detect_audio_issues(audio_device) -> List[str]`**
- Обнаруживает проблемы с аудиоустройством

**`get_port_info() -> Dict[str, any]`**
- Получает информацию о портах и типе устройства
- Проверяет DMI для определения типа (laptop/desktop)
- Проверяет наличие HDMI, USB-C, USB-A, Ethernet
- Возвращает:
  - `is_laptop`: является ли ноутбуком
  - `has_hdmi`: наличие HDMI
  - `has_usb_c`: наличие USB Type-C
  - `has_usb_a`: наличие USB Type-A
  - `has_ethernet`: наличие Ethernet
  - `has_audio_jack`: наличие аудио разъема
  - `has_sd_card`: наличие SD-карты
  - `chassis_type`: тип корпуса (laptop/desktop/unknown)

**`get_usb_device_type(device_description) -> str`**
- Определяет тип USB устройства по описанию
- Возвращает: flash_drive, audio_device, keyboard, mouse, camera, network_adapter, unknown

#### C++ Версия (device_analyzer.h/cpp)

**Класс DeviceAnalyzer**

**Структуры:**

```cpp
struct USBDeviceInfo {
    std::string vendor;
    std::string product;
    std::string serial;
    std::string bus;
    std::string device;
    int power_ma;
    std::string status;
};

struct BatteryInfo {
    bool is_present;
    bool is_charging;
    int percentage;
    int voltage_mv;
    int current_ma;
    int power_mw;
    std::string manufacturer;
    std::string model;
    std::string technology;
    std::string status;
};

struct AudioDeviceInfo {
    std::string name;
    std::string type;
    std::string status;
    std::string card;
    std::string device;
};

struct InputDeviceInfo {
    std::string name;
    std::string type;
    std::string bus;
    std::string vendor;
    std::string product;
    bool is_connected;
    std::string status;
};

struct PortInfo {
    bool is_laptop;
    bool has_hdmi;
    bool has_usb_c;
    bool has_usb_a;
    bool has_ethernet;
    bool has_audio_jack;
    bool has_sd_card;
    std::string chassis_type;
};
```

**Методы:**
- `get_usb_devices()` - аналогично Python версии
- `get_battery_info()` - аналогично Python версии
- `detect_battery_issues()` - аналогично Python версии
- `get_audio_devices()` - аналогично Python версии
- `detect_audio_issues()` - аналогично Python версии
- `get_input_devices()` - получает устройства ввода из /proc/bus/input/devices
- `detect_input_issues()` - обнаруживает проблемы с устройствами ввода
- `get_port_info()` - аналогично Python версии
- `get_usb_device_type()` - аналогично Python версии

#### Примеры использования

**Python:**
```python
from device_analyzer import DeviceAnalyzer

analyzer = DeviceAnalyzer()

# Информация о батарее
battery = analyzer.get_battery_info()
print(f"Заряд: {battery['percentage']}%")
print(f"Мощность зарядки: {battery['power_mw']} мВт")
print(f"Производитель: {battery['manufacturer']}")

# Проверка проблем
issues = analyzer.detect_battery_issues(battery)
if issues:
    print("Проблемы:", issues)

# Информация о портах
ports = analyzer.get_port_info()
print(f"Тип устройства: {ports['chassis_type']}")
print(f"Ноутбук: {ports['is_laptop']}")
print(f"USB-C: {ports['has_usb_c']}")
```

**C++:**
```cpp
#include "device_analyzer.h"

// Информация о батарее
DeviceAnalyzer::BatteryInfo battery = DeviceAnalyzer::get_battery_info();
std::cout << "Заряд: " << battery.percentage << "%" << std::endl;
std::cout << "Мощность: " << battery.power_mw << " мВт" << std::endl;

// Проверка проблем
auto issues = DeviceAnalyzer::detect_battery_issues(battery);
for (const auto& issue : issues) {
    std::cout << "Проблема: " << issue << std::endl;
}

// Информация о портах
DeviceAnalyzer::PortInfo ports = DeviceAnalyzer::get_port_info();
std::cout << "Тип: " << ports.chassis_type << std::endl;
std::cout << "Ноутбук: " << (ports.is_laptop ? "да" : "нет") << std::endl;
```

---

### 2. distro_analyzer.py
Анализатор дистрибутива Linux.

---

### 3. gpu_monitor.py
Мониторинг GPU.

---

### 4. hardware_rater.py
Оценка производительности CPU и GPU.

---

### 5. system_info_lib.py
Библиотека системной информации.

---

### 6. system_monitor.py
Мониторинг системы.

---

### 7. window_monitor.py
Мониторинг окон.

---

## Требования

### Python
- Python 3.6+
- psutil
- py-cpuinfo

### C++
- C++17 или выше
- filesystem (C++17)
- Linux kernel headers

---

## Компиляция C++

```bash
cd main/linux
g++ -std=c++17 -c device_analyzer.cpp -o device_analyzer.o
ar rcs libdevice_analyzer.a device_analyzer.o
```

---

## Лицензия

Код является частью проекта VitalSign.
