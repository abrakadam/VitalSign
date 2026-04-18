"""
Monitor Analyzer - Анализатор мониторов (Python обертка для C++)
"""

import subprocess
import os
from typing import List, Dict


class MonitorAnalyzer:
    """Анализатор мониторов"""
    
    def __init__(self):
        pass
    
    def get_monitors(self) -> List[Dict[str, any]]:
        """Получить информацию о мониторах"""
        monitors = []
        
        try:
            # Используем xrandr для получения информации о мониторах
            result = subprocess.run(['xrandr'], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            
            current_monitor = {}
            in_monitor = False
            current_refresh_rates = []
            
            for line in lines:
                if ' connected' in line:
                    # Сохраняем предыдущий монитор если есть
                    if in_monitor and current_monitor:
                        # Берем максимальную частоту обновления
                        if current_refresh_rates:
                            current_monitor['refresh_rate'] = max(current_refresh_rates)
                        monitors.append(current_monitor)
                    
                    # Начинаем новый монитор
                    current_monitor = {}
                    in_monitor = True
                    current_refresh_rates = []
                    current_monitor['is_connected'] = True
                    current_monitor['is_enabled'] = 'connected primary' in line or 'connected ' in line
                    current_monitor['is_primary'] = 'primary' in line
                    
                    # Получаем имя монитора
                    parts = line.split()
                    if parts:
                        current_monitor['name'] = parts[0]
                    
                    # Получаем разрешение
                    if 'x' in line:
                        # Ищем разрешение (например, 1920x1080)
                        for part in line.split():
                            if 'x' in part and '+' in part:
                                resolution = part.split('+')[0]
                                if 'x' in resolution:
                                    res_parts = resolution.split('x')
                                    if len(res_parts) == 2:
                                        try:
                                            current_monitor['width'] = int(res_parts[0])
                                            current_monitor['height'] = int(res_parts[1])
                                        except ValueError:
                                            pass
                                break
                    
                    # Получаем тип подключения
                    current_monitor['connection'] = self._get_connection_type(current_monitor.get('name', ''))
                    
                    # Получаем EDID
                    current_monitor['edid'] = self._get_edid_info(current_monitor.get('name', ''))
                    
                    # Извлекаем информацию из EDID
                    if current_monitor.get('edid'):
                        current_monitor['manufacturer'] = self._parse_edid_manufacturer(current_monitor['edid'])
                        current_monitor['model'] = self._parse_edid_model(current_monitor['edid'])
                        current_monitor['serial'] = self._parse_edid_serial(current_monitor['edid'])
                    else:
                        # Если EDID недоступен, пробуем получить информацию из xrandr --props
                        current_monitor['manufacturer'] = self._get_monitor_from_xrandr_props(current_monitor.get('name', ''))
                        current_monitor['model'] = current_monitor.get('name', 'Unknown')
                        current_monitor['serial'] = 'Unknown'
                    
                    # Получаем частоту обновления из текущей строки
                    refresh_rate = self._get_refresh_rate(line)
                    if refresh_rate > 0:
                        current_refresh_rates.append(refresh_rate)
                    
                    # Статус
                    current_monitor['status'] = 'Active' if current_monitor['is_enabled'] else 'Connected but disabled'
                elif in_monitor and line.strip().startswith('   '):
                    # Парсим строки с разрешениями и частотами
                    refresh_rate = self._get_refresh_rate(line)
                    if refresh_rate > 0:
                        current_refresh_rates.append(refresh_rate)
            
            # Добавляем последний монитор
            if in_monitor and current_monitor:
                if current_refresh_rates:
                    current_monitor['refresh_rate'] = max(current_refresh_rates)
                monitors.append(current_monitor)
                
        except Exception as e:
            print(f"Ошибка при получении информации о мониторах: {e}")
        
        return monitors
    
    def _get_connection_type(self, port: str) -> str:
        """Определить тип подключения"""
        port_lower = port.lower()
        
        if 'hdmi' in port_lower:
            return 'HDMI'
        elif 'dp' in port_lower or 'displayport' in port_lower:
            return 'DisplayPort'
        elif 'vga' in port_lower:
            return 'VGA'
        elif 'dvi' in port_lower:
            return 'DVI'
        elif 'usb' in port_lower:
            return 'USB-C'
        elif 'embedded' in port_lower:
            return 'Embedded (Laptop)'
        
        return 'Unknown'
    
    def _get_edid_info(self, port: str) -> str:
        """Получить EDID информацию"""
        try:
            drm_path = f'/sys/class/drm/{port}'
            edid_file = os.path.join(drm_path, 'edid')
            
            if os.path.exists(edid_file):
                with open(edid_file, 'rb') as f:
                    return f.read().hex()
        except Exception as e:
            print(f"Ошибка при чтении EDID: {e}")
        
        return ''
    
    def _get_monitor_from_xrandr_props(self, monitor_name: str) -> str:
        """Получить информацию о мониторе из xrandr --props"""
        try:
            result = subprocess.run(['xrandr', '--props'], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            
            for i, line in enumerate(lines):
                if monitor_name in line and 'connected' in line:
                    # Ищем информацию о производителе в следующих строках
                    for j in range(i, min(i + 10, len(lines))):
                        if 'EDID' in lines[j]:
                            # Парсим EDID из xrandr --props
                            edid_hex = lines[j].split(':')[-1].strip().strip('"')
                            if len(edid_hex) > 20:
                                return self._parse_edid_manufacturer(edid_hex)
                    break
        except Exception as e:
            print(f"Ошибка при получении информации из xrandr --props: {e}")
        
        return 'Unknown'
    
    def _parse_edid_manufacturer(self, edid: str) -> str:
        """Извлечь производителя из EDID"""
        # EDID производитель в байтах 8-9 (3 бита каждый)
        manufacturer_map = {
            'AAC': 'Acer', 'ACI': 'Asus', 'ADK': 'AOC', 'AOC': 'AOC',
            'APP': 'Apple', 'AUO': 'AU Optronics', 'BOE': 'BOE',
            'CMN': 'Chimei Innolux', 'DEL': 'Dell', 'Dell': 'Dell',
            'HPN': 'HP', 'HWP': 'HP', 'IBM': 'IBM', 'LEN': 'Lenovo',
            'LGD': 'LG Display', 'MSI': 'MSI', 'NVD': 'NVIDIA',
            'PHL': 'Philips', 'SAM': 'Samsung', 'SEC': 'Samsung',
            'SII': 'Seiko', 'SNY': 'Sony', 'TSB': 'Toshiba',
            'VSC': 'ViewSonic', 'YMH': 'Yamaha'
        }
        
        try:
            if len(edid) >= 20:
                # Байты 8-9 в hex (пропускаем первые 16 символов - это заголовок EDID)
                # Формат: 3 бита + 3 бита + 2 бита (padding)
                if len(edid) >= 32:
                    byte8 = int(edid[16:18], 16)
                    byte9 = int(edid[18:20], 16)
                    
                    # Декодируем производителя (5-битные коды)
                    char1 = ((byte8 >> 2) & 0x1F)
                    char2 = ((byte8 & 0x03) << 3) | ((byte9 >> 5) & 0x07)
                    char3 = (byte9 & 0x1F)
                    
                    # Конвертируем в ASCII (сдвиг на 64)
                    mfg = chr(char1 + 64) + chr(char2 + 64) + chr(char3 + 64)
                    
                    if mfg in manufacturer_map:
                        return manufacturer_map[mfg]
                    return mfg
        except Exception as e:
            print(f"Ошибка при парсинге производителя EDID: {e}")
        
        return 'Unknown'
    
    def _parse_edid_model(self, edid: str) -> str:
        """Извлечь модель из EDID"""
        # Модель в байтах 10-11 (little-endian)
        try:
            if len(edid) >= 32:
                byte10 = int(edid[20:22], 16)
                byte11 = int(edid[22:24], 16)
                model = (byte11 << 8) | byte10
                if model > 0:
                    return str(model)
        except Exception as e:
            print(f"Ошибка при парсинге модели EDID: {e}")
        return 'Unknown'
    
    def _parse_edid_serial(self, edid: str) -> str:
        """Извлечь серийный номер из EDID"""
        # Серийный номер в байтах 12-15 (little-endian)
        try:
            if len(edid) >= 40:
                byte12 = int(edid[24:26], 16)
                byte13 = int(edid[26:28], 16)
                byte14 = int(edid[28:30], 16)
                byte15 = int(edid[30:32], 16)
                serial = (byte15 << 24) | (byte14 << 16) | (byte13 << 8) | byte12
                if serial > 0:
                    return str(serial)
        except Exception as e:
            print(f"Ошибка при парсинге серийного номера EDID: {e}")
        return 'Unknown'
    
    def _get_refresh_rate(self, line: str) -> int:
        """Извлечь частоту обновления из строки xrandr"""
        # Ищем частоту в формате "60.00*+" или "60.00"
        for part in line.split():
            try:
                if '*' in part or '+' in part:
                    freq_str = part.rstrip('*+')
                    freq = float(freq_str)
                    return int(freq)
            except ValueError:
                pass
        return 0
    
    def check_monitor_health(self, monitor: Dict[str, any]) -> Dict[str, any]:
        """Проверить здоровье монитора"""
        health = {
            'is_healthy': True,
            'issues': [],
            'overall_status': 'Healthy',
            'health_score': 100
        }
        
        # Обнаруживаем проблемы
        health['issues'] = self._detect_monitor_issues(monitor)
        
        # Вычисляем общий статус
        if not health['issues']:
            health['overall_status'] = 'Healthy'
            health['is_healthy'] = True
            health['health_score'] = 100
        elif len(health['issues']) <= 2:
            health['overall_status'] = 'Minor Issues'
            health['is_healthy'] = True
            health['health_score'] = 80
        elif len(health['issues']) <= 4:
            health['overall_status'] = 'Some Issues'
            health['is_healthy'] = False
            health['health_score'] = 60
        else:
            health['overall_status'] = 'Major Issues'
            health['is_healthy'] = False
            health['health_score'] = 40
        
        # Пересчитываем оценку
        health['health_score'] = self._calculate_health_score(monitor, health['issues'])
        
        return health
    
    def _detect_monitor_issues(self, monitor: Dict[str, any]) -> List[str]:
        """Обнаружить проблемы с монитором"""
        issues = []
        
        # Проверка подключения
        if not monitor.get('is_connected', True):
            issues.append('Monitor not connected')
        
        # Проверка включения
        if monitor.get('is_connected', True) and not monitor.get('is_enabled', True):
            issues.append('Monitor connected but disabled')
        
        # Проверка разрешения
        width = monitor.get('width', 0)
        height = monitor.get('height', 0)
        if width == 0 or height == 0:
            issues.append('No resolution detected')
        elif width < 1024 or height < 768:
            issues.append('Low resolution detected')
        
        # Проверка частоты обновления
        refresh_rate = monitor.get('refresh_rate', 0)
        if refresh_rate == 0:
            issues.append('No refresh rate detected')
        elif refresh_rate < 60:
            issues.append('Low refresh rate (< 60 Hz)')
        
        # Проверка EDID
        if not monitor.get('edid'):
            issues.append('No EDID information available')
        
        # Проверка производителя
        if not monitor.get('manufacturer') or monitor.get('manufacturer') == 'Unknown':
            issues.append('Manufacturer information not available')
        
        # Проверка модели
        if not monitor.get('model'):
            issues.append('Model information not available')
        
        # Проверка типа подключения
        if monitor.get('connection') == 'Unknown':
            issues.append('Connection type not detected')
        
        # Если это встроенный монитор ноутбука
        if monitor.get('connection') == 'Embedded (Laptop)':
            if not monitor.get('is_primary', False):
                issues.append('Laptop monitor is not primary')
        
        return issues
    
    def _calculate_health_score(self, monitor: Dict[str, any], issues: List[str]) -> int:
        """Вычислить оценку здоровья"""
        score = 100
        
        # Вычитаем баллы за каждую проблему
        for issue in issues:
            if 'not connected' in issue:
                score -= 50
            elif 'disabled' in issue:
                score -= 30
            elif 'No resolution' in issue:
                score -= 40
            elif 'Low resolution' in issue:
                score -= 20
            elif 'No refresh rate' in issue:
                score -= 30
            elif 'Low refresh rate' in issue:
                score -= 15
            elif 'No EDID' in issue:
                score -= 20
            elif 'Manufacturer' in issue:
                score -= 10
            elif 'Model' in issue:
                score -= 10
            elif 'Connection type' in issue:
                score -= 15
            else:
                score -= 10
        
        return max(0, score)
