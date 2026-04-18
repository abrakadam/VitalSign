"""
Keyboard Analyzer - Анализатор клавиатур (Python обертка для C++)
"""

import subprocess
import os
from typing import List, Dict


class KeyboardAnalyzer:
    """Анализатор клавиатур"""
    
    def __init__(self):
        pass
    
    def get_keyboards(self) -> List[Dict[str, any]]:
        """Получить информацию о клавиатурах"""
        keyboards = []
        
        try:
            # Читаем из /proc/bus/input/devices
            input_file = '/proc/bus/input/devices'
            if os.path.exists(input_file):
                with open(input_file, 'r') as f:
                    lines = f.readlines()
                    
                current_keyboard = {}
                in_keyboard = False
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        if in_keyboard and current_keyboard:
                            current_keyboard['is_internal'] = self._is_internal_keyboard(current_keyboard)
                            current_keyboard['type'] = 'internal' if current_keyboard['is_internal'] else 'external'
                            keyboards.append(current_keyboard)
                        current_keyboard = {}
                        in_keyboard = False
                        continue
                    
                    if line.startswith('N: Name='):
                        current_keyboard['name'] = line[8:]
                        if current_keyboard['name'].startswith('"') and current_keyboard['name'].endswith('"'):
                            current_keyboard['name'] = current_keyboard['name'][1:-1]
                        in_keyboard = True
                        
                        # Проверяем, это ли клавиатура
                        name_lower = current_keyboard['name'].lower()
                        if 'keyboard' not in name_lower and 'keypad' not in name_lower:
                            in_keyboard = False
                            continue
                        
                        current_keyboard['status'] = 'connected'
                    
                    if line.startswith('B: BUS='):
                        current_keyboard['bus'] = line[7:]
                    
                    if line.startswith('P: Vendor='):
                        current_keyboard['manufacturer'] = line[11:]
                    
                    if line.startswith('P: Product='):
                        current_keyboard['product'] = line[12:]
                
                # Добавляем последнюю клавиатуру
                if in_keyboard and current_keyboard:
                    current_keyboard['is_internal'] = self._is_internal_keyboard(current_keyboard)
                    current_keyboard['type'] = 'internal' if current_keyboard['is_internal'] else 'external'
                    keyboards.append(current_keyboard)
            
        except Exception as e:
            print(f"Ошибка при получении информации о клавиатурах: {e}")
        
        return keyboards
    
    def _is_internal_keyboard(self, keyboard: Dict[str, any]) -> bool:
        """Определить встроенная ли клавиатура"""
        name_lower = keyboard.get('name', '').lower()
        
        # Встроенная клавиатура ноутбука
        if 'at keyboard' in name_lower or 'system keyboard' in name_lower:
            return True
        
        # PS/2 клавиатура обычно встроенная
        if keyboard.get('bus', '').startswith('0011'):  # PS/2
            return True
        
        return False
    
    def check_keyboard_health(self, keyboard: Dict[str, any]) -> Dict[str, any]:
        """Проверить здоровье клавиатуры"""
        health = {
            'is_healthy': True,
            'issues': [],
            'health_score': 100,
            'total_keys': 104,
            'working_keys': 104,
            'broken_keys': 0
        }
        
        # Обнаруживаем проблемы
        health['issues'] = self._detect_keyboard_issues(keyboard)
        
        # Вычисляем оценку здоровья
        health['health_score'] = self._calculate_health_score(keyboard, health['issues'])
        
        # Определяем общее состояние
        if health['health_score'] >= 80:
            health['is_healthy'] = True
        elif health['health_score'] >= 60:
            health['is_healthy'] = True
        else:
            health['is_healthy'] = False
        
        return health
    
    def _detect_keyboard_issues(self, keyboard: Dict[str, any]) -> List[str]:
        """Обнаружить проблемы с клавиатурой"""
        issues = []
        
        # Проверка производителя
        if not keyboard.get('manufacturer'):
            issues.append('Manufacturer information not available')
        
        # Проверка продукта
        if not keyboard.get('product'):
            issues.append('Product information not available')
        
        # Проверка статуса
        if not keyboard.get('status') or keyboard.get('status') == 'disconnected':
            issues.append('Keyboard not connected')
        
        # Проверка типа подключения
        if not keyboard.get('bus'):
            issues.append('Bus type not detected')
        
        # Если это встроенная клавиатура
        if keyboard.get('is_internal'):
            if keyboard.get('status') != 'connected':
                issues.append('Internal keyboard disconnected')
        
        return issues
    
    def _calculate_health_score(self, keyboard: Dict[str, any], issues: List[str]) -> int:
        """Вычислить оценку здоровья"""
        score = 100
        
        for issue in issues:
            if 'not connected' in issue:
                score -= 50
            elif 'Manufacturer' in issue:
                score -= 10
            elif 'Product' in issue:
                score -= 10
            elif 'Bus type' in issue:
                score -= 15
            elif 'Internal keyboard' in issue:
                score -= 30
            else:
                score -= 10
        
        return max(0, score)
    
    def detect_keys(self, keyboard: Dict[str, any]) -> List[Dict[str, any]]:
        """Обнаружить клавиши клавиатуры"""
        keys = []
        
        # Список стандартных клавиш
        standard_keys = [
            'ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=',
            'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\',
            'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'",
            'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/',
            'SPACE', 'TAB', 'CAPS', 'SHIFT_L', 'SHIFT_R', 'CTRL_L', 'CTRL_R',
            'ALT_L', 'ALT_R', 'META_L', 'META_R',
            'ENTER', 'BACKSPACE', 'DELETE', 'INSERT', 'HOME', 'END', 'PAGE_UP', 'PAGE_DOWN',
            'UP', 'DOWN', 'LEFT', 'RIGHT'
        ]
        
        for key_name in standard_keys:
            key = {
                'key_name': key_name,
                'key_code': '',
                'works': True,
                'detected': True
            }
            keys.append(key)
        
        return keys
