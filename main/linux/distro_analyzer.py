"""
Distro Analyzer - Анализатор дистрибутивов Linux
"""

import subprocess
import platform
import os
from typing import Dict, List, Tuple


class DistroAnalyzer:
    """Анализатор дистрибутивов Linux"""
    
    def __init__(self):
        self.current_distro = self.get_current_distro()
        self.hardware_info = self.get_hardware_info()
    
    def get_current_distro(self) -> Dict[str, str]:
        """Получить информацию о текущем дистрибутиве"""
        distro = {}
        
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        distro[key.lower()] = value.strip('"')
        except (FileNotFoundError, IOError):
            distro['name'] = 'Unknown'
        
        return distro
    
    def get_hardware_info(self) -> Dict[str, str]:
        """Получить информацию о железе"""
        hw = {}
        
        # CPU
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('model name'):
                        hw['cpu_model'] = line.split(':', 1)[1].strip()
                        break
        except (FileNotFoundError, IOError):
            hw['cpu_model'] = 'Unknown'
        
        # Память
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        mem_kb = int(line.split()[1])
                        hw['memory_gb'] = mem_kb / (1024 * 1024)
                        break
        except (FileNotFoundError, IOError):
            hw['memory_gb'] = 0
        
        # GPU
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
            gpu_lines = [line for line in result.stdout.split('\n') if 'VGA' in line or '3D' in line]
            hw['gpu'] = gpu_lines[0] if gpu_lines else 'Unknown'
        except Exception:
            hw['gpu'] = 'Unknown'
        
        return hw
    
    def get_recommended_distros(self) -> List[Dict[str, str]]:
        """Получить рекомендации по дистрибутивам"""
        recommendations = []
        
        # Определяем тип системы
        is_desktop = any(keyword in self.hardware_info.get('cpu_model', '').lower() 
                        for keyword in ['intel', 'amd', 'ryzen', 'core'])
        is_old_hardware = self.hardware_info.get('memory_gb', 0) < 4
        is_nvidia = 'nvidia' in self.hardware_info.get('gpu', '').lower()
        
        # Ubuntu - универсальный
        recommendations.append({
            'name': 'Ubuntu',
            'description': 'Универсальный дистрибутив с хорошей поддержкой',
            'pros': 'Простота использования, большое количество программ',
            'cons': 'Может быть тяжелым для старых систем',
            'score': 90
        })
        
        # Ubuntu LTS для стабильности
        recommendations.append({
            'name': 'Ubuntu LTS',
            'description': 'Долгосрочная поддержка, стабильность',
            'pros': 'Стабильность, безопасность, корпоративная поддержка',
            'cons': 'Устаревшие пакеты',
            'score': 85
        })
        
        # Fedora для новых технологий
        if not is_old_hardware:
            recommendations.append({
                'name': 'Fedora',
                'description': 'Последние технологии и пакеты',
                'pros': 'Последние версии ПО, инновации',
                'cons': 'Менее стабильный, быстрый цикл обновлений',
                'score': 80
            })
        
        # Arch Linux для продвинутых
        if not is_old_hardware:
            recommendations.append({
                'name': 'Arch Linux',
                'description': 'Минимализм и контроль',
                'pros': 'AUR, rolling release, минимализм',
                'cons': 'Сложная установка, требует знаний Linux',
                'score': 75
            })
        
        # Linux Mint для новичков
        recommendations.append({
            'name': 'Linux Mint',
            'description': 'Простота и стабильность на базе Ubuntu',
            'pros': 'Очень прост в использовании, стабильный',
            'cons': 'Меньше новых технологий',
            'score': 88
        })
        
        # Debian для серверов
        recommendations.append({
            'name': 'Debian',
            'description': 'Стабильность и безопасность',
            'pros': 'Очень стабильный, безопасный',
            'cons': 'Устаревшие пакеты',
            'score': 82
        })
        
        # Pop!_OS для NVIDIA
        if is_nvidia:
            recommendations.append({
                'name': 'Pop!_OS',
                'description': 'Оптимизирован для NVIDIA и игр',
                'pros': 'Отличная поддержка NVIDIA, игры',
                'cons': 'Основан на Ubuntu',
                'score': 92
            })
        
        # Lubuntu для старых систем
        if is_old_hardware:
            recommendations.append({
                'name': 'Lubuntu',
                'description': 'Легковесный дистрибутив',
                'pros': 'Минимальные требования, быстрый',
                'cons': 'Меньше функций',
                'score': 85
            })
        
        # Сортируем по рейтингу
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:5]
    
    def get_distro_compatibility(self, distro_name: str) -> Dict[str, str]:
        """Проверить совместимость с конкретным дистрибутивом"""
        compatibility = {
            'compatible': True,
            'reason': '',
            'issues': []
        }
        
        mem_gb = self.hardware_info.get('memory_gb', 0)
        
        # Проверяем требования по памяти
        if distro_name.lower() in ['ubuntu', 'kubuntu', 'xubuntu']:
            if mem_gb < 2:
                compatibility['compatible'] = False
                compatibility['reason'] = 'Недостаточно памяти'
                compatibility['issues'].append('Требуется минимум 2 GB RAM')
        elif distro_name.lower() in ['fedora', 'arch linux']:
            if mem_gb < 4:
                compatibility['compatible'] = False
                compatibility['reason'] = 'Недостаточно памяти'
                compatibility['issues'].append('Требуется минимум 4 GB RAM')
        elif distro_name.lower() in ['lubuntu', 'xubuntu']:
            if mem_gb < 1:
                compatibility['compatible'] = False
                compatibility['reason'] = 'Недостаточно памяти'
                compatibility['issues'].append('Требуется минимум 1 GB RAM')
        
        return compatibility
