"""
Windows Analyzer - Анализатор Windows системы
"""

import subprocess
import platform
import re
from typing import Dict, List


class WindowsAnalyzer:
    """Анализатор Windows системы"""
    
    def __init__(self):
        self.platform = platform.system()
    
    def get_windows_version(self) -> Dict[str, any]:
        """Получить информацию о версии Windows"""
        info = {
            'platform': self.platform,
            'version': 'Unknown',
            'build_number': 'Unknown',
            'edition': 'Unknown',
            'is_windows_11': False,
            'is_windows_10': False,
            'release_id': 'Unknown'
        }
        
        if self.platform != 'Windows':
            return info
        
        try:
            # Получаем версию через wmic
            result = subprocess.run(['wmic', 'os', 'get', 'Caption,BuildNumber,Version'], 
                                  capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'Microsoft Windows' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        info['edition'] = ' '.join(parts[2:])
                        
                        # Определяем версию
                        if 'Windows 11' in line:
                            info['version'] = 'Windows 11'
                            info['is_windows_11'] = True
                        elif 'Windows 10' in line:
                            info['version'] = 'Windows 10'
                            info['is_windows_10'] = True
                        elif 'Windows' in line:
                            info['version'] = line.strip()
                    
                    # Получаем build number
                    if 'Build' in line:
                        build_match = re.search(r'Build (\d+)', line)
                        if build_match:
                            info['build_number'] = build_match.group(1)
                    
                    break
            
            # Альтернативный метод через systeminfo
            result = subprocess.run(['systeminfo'], capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'OS Name:' in line:
                    os_name = line.split(':', 1)[1].strip()
                    if 'Windows 11' in os_name:
                        info['version'] = 'Windows 11'
                        info['is_windows_11'] = True
                    elif 'Windows 10' in os_name:
                        info['version'] = 'Windows 10'
                        info['is_windows_10'] = True
                    info['edition'] = os_name
                
                if 'OS Version:' in line:
                    version_str = line.split(':', 1)[1].strip()
                    parts = version_str.split('.')
                    if len(parts) >= 1:
                        info['build_number'] = parts[0]
                
                if 'System Type:' in line:
                    info['architecture'] = line.split(':', 1)[1].strip()
            
        except Exception as e:
            print(f"Ошибка при получении версии Windows: {e}")
        
        return info
    
    def get_system_info(self) -> Dict[str, any]:
        """Получить системную информацию"""
        info = {
            'platform': self.platform,
            'machine': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node()
        }
        
        if self.platform == 'Windows':
            try:
                # Получаем информацию о CPU
                result = subprocess.run(['wmic', 'cpu', 'get', 'Name,NumberOfCores,MaxClockSpeed'], 
                                      capture_output=True, text=True, timeout=5)
                lines = result.stdout.split('\n')
                
                for line in lines[1:]:  # Пропускаем заголовок
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 1:
                            info['cpu_name'] = parts[0]
                        if len(parts) >= 2:
                            try:
                                info['cpu_cores'] = int(parts[1])
                            except ValueError:
                                pass
                        if len(parts) >= 3:
                            try:
                                info['cpu_clock'] = int(parts[2])
                            except ValueError:
                                pass
                        break
                
                # Получаем информацию о RAM
                result = subprocess.run(['wmic', 'memorychip', 'get', 'Capacity'], 
                                      capture_output=True, text=True, timeout=5)
                lines = result.stdout.split('\n')
                
                total_ram = 0
                for line in lines[1:]:
                    if line.strip():
                        try:
                            capacity = int(line.strip())
                            total_ram += capacity
                        except ValueError:
                            pass
                
                if total_ram > 0:
                    info['total_ram'] = total_ram // (1024 * 1024 * 1024)  # GB
                
            except Exception as e:
                print(f"Ошибка при получении системной информации: {e}")
        
        return info
    
    def recommend_windows_version(self, system_info: Dict[str, any]) -> Dict[str, any]:
        """Рекомендовать версию Windows на основе характеристик"""
        recommendation = {
            'recommended_version': 'Windows 11',
            'reason': '',
            'requirements_met': True,
            'warnings': []
        }
        
        if self.platform != 'Windows':
            recommendation['recommended_version'] = 'N/A (Not Windows)'
            recommendation['reason'] = 'Running on non-Windows platform'
            return recommendation
        
        # Минимальные требования для Windows 11
        win11_requirements = {
            'ram_min': 4,  # GB
            'ram_recommended': 8,  # GB
            'cpu_cores_min': 2,
            'storage_min': 64,  # GB
            'tpm_required': True,
            'secure_boot_required': True
        }
        
        # Проверяем RAM
        total_ram = system_info.get('total_ram', 0)
        if total_ram < win11_requirements['ram_min']:
            recommendation['recommended_version'] = 'Windows 10'
            recommendation['reason'] = f'Insufficient RAM for Windows 11 ({total_ram}GB < {win11_requirements["ram_min"]}GB)'
            recommendation['requirements_met'] = False
            recommendation['warnings'].append(f'Need at least {win11_requirements["ram_min"]}GB RAM for Windows 11')
        elif total_ram < win11_requirements['ram_recommended']:
            recommendation['warnings'].append(f'RAM below recommended for Windows 11 ({total_ram}GB < {win11_requirements["ram_recommended"]}GB)')
        
        # Проверяем CPU
        cpu_cores = system_info.get('cpu_cores', 0)
        if cpu_cores < win11_requirements['cpu_cores_min']:
            recommendation['recommended_version'] = 'Windows 10'
            recommendation['reason'] = f'Insufficient CPU cores for Windows 11 ({cpu_cores} < {win11_requirements["cpu_cores_min"]})'
            recommendation['requirements_met'] = False
            recommendation['warnings'].append(f'Need at least {win11_requirements["cpu_cores_min"]} CPU cores for Windows 11')
        
        # Проверяем TPM (опционально, требует wmic)
        try:
            result = subprocess.run(['wmic', 'tpm', 'get', 'IsEnabled_InitialValue'], 
                                  capture_output=True, text=True, timeout=5)
            tpm_enabled = 'TRUE' in result.stdout.upper()
            if not tpm_enabled:
                recommendation['warnings'].append('TPM 2.0 not enabled - required for Windows 11')
        except:
            pass  # Не можем проверить TPM
        
        # Проверяем Secure Boot (опционально)
        try:
            result = subprocess.run(['powershell', '-Command', 
                                    'Confirm-SecureBootUEFI'], 
                                  capture_output=True, text=True, timeout=5)
            secure_boot = 'True' in result.stdout
            if not secure_boot:
                recommendation['warnings'].append('Secure Boot not enabled - required for Windows 11')
        except:
            pass  # Не можем проверить Secure Boot
        
        return recommendation
    
    def get_installed_windows(self) -> List[Dict[str, any]]:
        """Получить информацию об установленных Windows (если есть несколько)"""
        installed = []
        
        try:
            # Проверяем наличие других разделов с Windows
            result = subprocess.run(['wmic', 'partition', 'get', 'Name,Bootable'], 
                                  capture_output=True, text=True, timeout=5)
            # Парсинг вывода для поиска загрузочных разделов
        except Exception as e:
            print(f"Ошибка при получении установленных Windows: {e}")
        
        return installed
