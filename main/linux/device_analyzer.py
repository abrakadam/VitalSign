"""
Device Analyzer - Анализатор подключенных устройств
"""

import subprocess
import os
from typing import List, Dict


class DeviceAnalyzer:
    """Анализатор подключенных устройств"""
    
    def __init__(self):
        pass
    
    def get_usb_devices(self) -> List[Dict[str, str]]:
        """Получить информацию о USB устройствах"""
        devices = []
        
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 6:
                        device = {
                            'bus': parts[1],
                            'device': parts[3],
                            'id': parts[5],
                            'description': ' '.join(parts[6:]),
                            'type': 'USB'
                        }
                        devices.append(device)
        except Exception as e:
            print(f"Ошибка при получении USB устройств: {e}")
        
        return devices
    
    def get_pci_devices(self) -> List[Dict[str, str]]:
        """Получить информацию о PCI устройствах"""
        devices = []
        
        try:
            result = subprocess.run(['lspci', '-v'], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            
            current_device = None
            for line in lines:
                if ':' in line and not line.startswith('\t'):
                    if current_device:
                        devices.append(current_device)
                    
                    parts = line.split(':', 1)
                    current_device = {
                        'slot': parts[0].strip(),
                        'description': parts[1].strip(),
                        'details': []
                    }
                elif current_device and line.strip():
                    if ':' in line:
                        key, value = line.split(':', 1)
                        current_device['details'].append({
                            'key': key.strip(),
                            'value': value.strip()
                        })
            
            if current_device:
                devices.append(current_device)
                
        except Exception as e:
            print(f"Ошибка при получении PCI устройств: {e}")
        
        return devices
    
    def get_input_devices(self) -> List[Dict[str, str]]:
        """Получить информацию об устройствах ввода"""
        devices = []
        
        # Проверяем /dev/input
        input_dir = '/dev/input'
        if os.path.exists(input_dir):
            try:
                for item in os.listdir(input_dir):
                    if item.startswith('event'):
                        devices.append({
                            'name': item,
                            'path': os.path.join(input_dir, item),
                            'type': 'Input Device'
                        })
            except PermissionError:
                pass
        
        # Проверяем через xinput если доступно
        try:
            result = subprocess.run(['xinput', '--list'], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if '⎡' in line or '↳' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        device_id = parts[-1].strip('[]')
                        device_name = ' '.join(parts[1:-1])
                        devices.append({
                            'name': device_name,
                            'id': device_id,
                            'type': 'Input Device'
                        })
        except Exception:
            pass
        
        return devices
    
    def get_all_devices(self) -> Dict[str, List[Dict[str, str]]]:
        """Получить все устройства"""
        return {
            'usb': self.get_usb_devices(),
            'pci': self.get_pci_devices(),
            'input': self.get_input_devices()
        }
    
    def get_device_summary(self) -> Dict[str, int]:
        """Получить сводку по устройствам"""
        all_devices = self.get_all_devices()
        
        return {
            'usb_count': len(all_devices['usb']),
            'pci_count': len(all_devices['pci']),
            'input_count': len(all_devices['input']),
            'total': len(all_devices['usb']) + len(all_devices['pci']) + len(all_devices['input'])
        }
    
    def get_battery_info(self) -> Dict[str, any]:
        """Получить информацию о батарее и зарядке"""
        info = {
            'is_present': False,
            'is_charging': False,
            'percentage': 0,
            'voltage_mv': 0,
            'current_ma': 0,
            'power_mw': 0,
            'manufacturer': '',
            'model': '',
            'technology': '',
            'status': ''
        }
        
        try:
            battery_path = '/sys/class/power_supply/'
            if os.path.exists(battery_path):
                for item in os.listdir(battery_path):
                    if item.startswith('BAT'):
                        bat_dir = os.path.join(battery_path, item)
                        info['is_present'] = True
                        
                        # Читаем статус
                        status_file = os.path.join(bat_dir, 'status')
                        if os.path.exists(status_file):
                            with open(status_file, 'r') as f:
                                info['status'] = f.read().strip()
                                info['is_charging'] = info['status'] == 'Charging'
                        
                        # Читаем процент
                        capacity_file = os.path.join(bat_dir, 'capacity')
                        if os.path.exists(capacity_file):
                            with open(capacity_file, 'r') as f:
                                info['percentage'] = int(f.read().strip())
                        
                        # Читаем напряжение
                        voltage_file = os.path.join(bat_dir, 'voltage_now')
                        if os.path.exists(voltage_file):
                            with open(voltage_file, 'r') as f:
                                info['voltage_mv'] = int(f.read().strip()) // 1000
                        
                        # Читаем ток
                        current_file = os.path.join(bat_dir, 'current_now')
                        if os.path.exists(current_file):
                            with open(current_file, 'r') as f:
                                info['current_ma'] = int(f.read().strip()) // 1000
                        
                        # Вычисляем мощность
                        if info['voltage_mv'] > 0 and info['current_ma'] > 0:
                            info['power_mw'] = (info['voltage_mv'] * info['current_ma']) // 1000
                        
                        # Читаем производителя
                        manufacturer_file = os.path.join(bat_dir, 'manufacturer')
                        if os.path.exists(manufacturer_file):
                            with open(manufacturer_file, 'r') as f:
                                info['manufacturer'] = f.read().strip()
                        
                        # Читаем модель
                        model_file = os.path.join(bat_dir, 'model_name')
                        if os.path.exists(model_file):
                            with open(model_file, 'r') as f:
                                info['model'] = f.read().strip()
                        
                        # Читаем технологию
                        tech_file = os.path.join(bat_dir, 'technology')
                        if os.path.exists(tech_file):
                            with open(tech_file, 'r') as f:
                                info['technology'] = f.read().strip()
                        
                        break
        except Exception as e:
            print(f"Ошибка при получении информации о батарее: {e}")
        
        return info
    
    def detect_battery_issues(self, battery_info: Dict[str, any]) -> List[str]:
        """Обнаружить проблемы с батареей"""
        issues = []
        
        if not battery_info['is_present']:
            issues.append('Батарея не обнаружена')
            return issues
        
        if battery_info['percentage'] < 20 and not battery_info['is_charging']:
            issues.append('Низкий заряд батареи (< 20%)')
        
        if battery_info['voltage_mv'] > 0 and battery_info['voltage_mv'] < 10000:
            issues.append('Низкое напряжение батареи (возможен износ)')
        
        if battery_info['current_ma'] > 0 and battery_info['is_charging'] and battery_info['current_ma'] < 500:
            issues.append('Медленная зарядка (ток < 500 мА)')
        
        if not battery_info['technology']:
            issues.append('Не удалось определить технологию батареи')
        
        return issues
    
    def get_audio_devices(self) -> List[Dict[str, str]]:
        """Получить информацию об аудиоустройствах"""
        devices = []
        
        try:
            result = subprocess.run(['aplay', '-l'], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            
            current_device = None
            for line in lines:
                if 'card' in line:
                    if current_device:
                        devices.append(current_device)
                    
                    parts = line.split()
                    current_device = {'name': '', 'type': 'unknown', 'status': 'connected'}
                    
                    # Парсим номер карты
                    if 'card' in parts:
                        card_idx = parts.index('card')
                        if card_idx + 1 < len(parts):
                            current_device['card'] = parts[card_idx + 1].rstrip(':')
                    
                    # Парсим номер устройства
                    if 'device' in parts:
                        device_idx = parts.index('device')
                        if device_idx + 1 < len(parts):
                            current_device['device'] = parts[device_idx + 1].rstrip(':')
                    
                    # Получаем имя устройства
                    if ':' in line:
                        name = line.split(':', 1)[1].strip()
                        current_device['name'] = name
                        
                        # Определяем тип
                        name_lower = name.lower()
                        if 'headphone' in name_lower or 'headset' in name_lower:
                            current_device['type'] = 'headphones'
                        elif 'microphone' in name_lower:
                            current_device['type'] = 'microphone'
                        elif 'speaker' in name_lower:
                            current_device['type'] = 'speakers'
            
            if current_device:
                devices.append(current_device)
                
        except Exception as e:
            print(f"Ошибка при получении аудиоустройств: {e}")
        
        return devices
    
    def detect_audio_issues(self, audio_device: Dict[str, str]) -> List[str]:
        """Обнаружить проблемы с аудиоустройством"""
        issues = []
        
        if not audio_device.get('name'):
            issues.append('Не удалось определить имя устройства')
        
        if audio_device.get('type') == 'unknown':
            issues.append('Неизвестный тип аудиоустройства')
        
        return issues
    
    def get_port_info(self) -> Dict[str, any]:
        """Получить информацию о портах и типе устройства"""
        info = {
            'is_laptop': False,
            'has_hdmi': False,
            'has_usb_c': False,
            'has_usb_a': False,
            'has_ethernet': False,
            'has_audio_jack': False,
            'has_sd_card': False,
            'chassis_type': 'unknown'
        }
        
        try:
            # Проверяем DMI информацию
            dmi_file = '/sys/class/dmi/id/chassis_type'
            if os.path.exists(dmi_file):
                with open(dmi_file, 'r') as f:
                    chassis_type = int(f.read().strip())
                    # Типы корпусов: 8=Notebook, 9=Laptop, 10=Tablet, 14=Sub Notebook
                    if chassis_type in [8, 9, 10, 14]:
                        info['is_laptop'] = True
                        info['chassis_type'] = 'laptop'
                    elif chassis_type in [3, 4, 5, 6, 7]:
                        info['chassis_type'] = 'desktop'
            
            # Проверяем наличие портов через lspci
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
            lspci_output = result.stdout.lower()
            
            if 'hdmi' in lspci_output:
                info['has_hdmi'] = True
            if 'ethernet' in lspci_output or 'network' in lspci_output:
                info['has_ethernet'] = True
            
            # Проверяем USB порты
            usb_path = '/sys/bus/usb/devices/'
            if os.path.exists(usb_path):
                for item in os.listdir(usb_path):
                    if item.startswith('usb'):
                        info['has_usb_a'] = True
                        speed_file = os.path.join(usb_path, item, 'speed')
                        if os.path.exists(speed_file):
                            with open(speed_file, 'r') as f:
                                speed = f.read().strip()
                                if '10000' in speed or '5000' in speed:
                                    info['has_usb_c'] = True
            
            info['has_audio_jack'] = True  # По умолчанию для большинства систем
            
        except Exception as e:
            print(f"Ошибка при получении информации о портах: {e}")
        
        return info
    
    def get_usb_device_type(self, device_description: str) -> str:
        """Определить тип USB устройства по описанию"""
        desc_lower = device_description.lower()
        
        if 'flash' in desc_lower or 'storage' in desc_lower or 'disk' in desc_lower:
            return 'flash_drive'
        elif 'headphone' in desc_lower or 'audio' in desc_lower:
            return 'audio_device'
        elif 'keyboard' in desc_lower:
            return 'keyboard'
        elif 'mouse' in desc_lower:
            return 'mouse'
        elif 'camera' in desc_lower or 'webcam' in desc_lower:
            return 'camera'
        elif 'ethernet' in desc_lower or 'network' in desc_lower:
            return 'network_adapter'
        
        return 'unknown'
