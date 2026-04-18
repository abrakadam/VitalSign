"""
Python обертка для C++ библиотеки системной информации
"""

import sys
import os

# Добавляем путь к собранной библиотеке
lib_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'build', 'lib')
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

try:
    # Пробуем импортировать C++ библиотеку
    import system_info_cpp
    CPP_AVAILABLE = True
except ImportError:
    CPP_AVAILABLE = False
    print("Warning: C++ system info library not available, using Python fallback")


class SystemInfo:
    """Обертка для системной информации"""
    
    def __init__(self):
        self.cpp_available = CPP_AVAILABLE
        if self.cpp_available:
            self.cpp_lib = system_info_cpp.SystemInfoLib()
    
    def get_hardware_info(self) -> dict:
        """Получить информацию о железе"""
        if self.cpp_available:
            hw = self.cpp_lib.get_hardware_info()
            return {
                'system_vendor': hw.system_vendor,
                'product_name': hw.product_name,
                'product_version': hw.product_version,
                'board_vendor': hw.board_vendor,
                'board_name': hw.board_name,
                'bios_vendor': hw.bios_vendor,
                'bios_version': hw.bios_version,
                'bios_date': hw.bios_date,
                'cpu_model': hw.cpu_model,
                'total_memory': hw.total_memory
            }
        else:
            return self._get_hardware_info_fallback()
    
    def get_os_info(self) -> dict:
        """Получить информацию об ОС"""
        if self.cpp_available:
            os_info = self.cpp_lib.get_os_info()
            return {
                'system': os_info.system,
                'release': os_info.release,
                'version': os_info.version,
                'machine': os_info.machine,
                'hostname': os_info.hostname,
                'distribution': os_info.distribution,
                'kernel_version': os_info.kernel_version
            }
        else:
            return self._get_os_info_fallback()
    
    def get_environment_info(self) -> dict:
        """Получить информацию об окружении"""
        if self.cpp_available:
            env = self.cpp_lib.get_environment_info()
            return {
                'desktop_environment': env.desktop_environment,
                'display_server': env.display_server,
                'shell': env.shell,
                'window_manager': env.window_manager
            }
        else:
            return self._get_environment_info_fallback()
    
    def get_bootloaders(self) -> list:
        """Получить список загрузчиков"""
        if self.cpp_available:
            bootloaders = self.cpp_lib.get_bootloaders()
            return [
                {
                    'name': bl.name,
                    'path': bl.path,
                    'active': bl.active
                }
                for bl in bootloaders
            ]
        else:
            return self._get_bootloaders_fallback()
    
    def get_installed_os(self) -> list:
        """Получить список установленных ОС"""
        if self.cpp_available:
            return self.cpp_lib.get_installed_os()
        else:
            return self._get_installed_os_fallback()
    
    def get_bios_info(self) -> dict:
        """Получить информацию о BIOS"""
        if self.cpp_available:
            return self.cpp_lib.get_bios_info()
        else:
            return self._get_bios_info_fallback()
    
    def get_drivers(self) -> list:
        """Получить список драйверов"""
        if self.cpp_available:
            return self.cpp_lib.get_drivers()
        else:
            return self._get_drivers_fallback()
    
    def get_serial_number(self) -> str:
        """Получить серийный номер"""
        if self.cpp_available:
            return self.cpp_lib.get_serial_number()
        else:
            return self._get_serial_number_fallback()
    
    def _get_hardware_info_fallback(self) -> dict:
        """Python fallback для информации о железе"""
        import platform
        info = {
            'system_vendor': 'N/A',
            'product_name': 'N/A',
            'product_version': 'N/A',
            'board_vendor': 'N/A',
            'board_name': 'N/A',
            'bios_vendor': 'N/A',
            'bios_version': 'N/A',
            'bios_date': 'N/A',
            'cpu_model': platform.processor(),
            'total_memory': 'N/A'
        }
        
        # Читаем DMI файлы
        dmi_files = {
            'system_vendor': '/sys/class/dmi/id/sys_vendor',
            'product_name': '/sys/class/dmi/id/product_name',
            'product_version': '/sys/class/dmi/id/product_version',
            'board_vendor': '/sys/class/dmi/id/board_vendor',
            'board_name': '/sys/class/dmi/id/board_name',
            'bios_vendor': '/sys/class/dmi/id/bios_vendor',
            'bios_version': '/sys/class/dmi/id/bios_version',
            'bios_date': '/sys/class/dmi/id/bios_date'
        }
        
        for key, path in dmi_files.items():
            try:
                with open(path, 'r') as f:
                    info[key] = f.read().strip()
            except (FileNotFoundError, IOError, PermissionError):
                pass
        
        try:
            import psutil
            mem = psutil.virtual_memory()
            info['total_memory'] = f"{mem.total / (1024**3):.2f} GB"
        except ImportError:
            pass
        
        return info
    
    def _get_os_info_fallback(self) -> dict:
        """Python fallback для информации об ОС"""
        import platform
        info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'hostname': platform.node(),
            'distribution': 'N/A',
            'kernel_version': platform.release()
        }
        
        # Читаем /etc/os-release
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        name = line.split('=', 1)[1].strip('"')
                        info['distribution'] = name
                        break
                    elif line.startswith('NAME='):
                        name = line.split('=', 1)[1].strip('"')
                        if info['distribution'] == 'N/A':
                            info['distribution'] = name
        except (FileNotFoundError, IOError):
            pass
        
        return info
    
    def _get_environment_info_fallback(self) -> dict:
        """Python fallback для информации об окружении"""
        import os
        return {
            'desktop_environment': os.environ.get('XDG_CURRENT_DESKTOP', 'N/A'),
            'display_server': os.environ.get('XDG_SESSION_TYPE', 'N/A'),
            'shell': os.environ.get('SHELL', 'N/A'),
            'window_manager': 'N/A'
        }
    
    def _get_bootloaders_fallback(self) -> list:
        """Python fallback для загрузчиков"""
        bootloaders = []
        import os
        
        if os.path.exists('/boot/grub/grub.cfg'):
            bootloaders.append({'name': 'GRUB', 'path': '/boot/grub/grub.cfg', 'active': True})
        
        if os.path.exists('/boot/loader/loader.conf'):
            bootloaders.append({'name': 'systemd-boot', 'path': '/boot/loader/loader.conf', 'active': True})
        
        return bootloaders
    
    def _get_installed_os_fallback(self) -> list:
        """Python fallback для установленных ОС"""
        os_list = []
        import os
        
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        name = line.split('=', 1)[1].strip('"')
                        os_list.append(f"{name} (Current)")
                        break
        except (FileNotFoundError, IOError):
            pass
        
        return os_list
    
    def _get_bios_info_fallback(self) -> dict:
        """Python fallback для BIOS"""
        bios = {}
        
        # Читаем DMI файлы BIOS
        dmi_files = {
            'vendor': '/sys/class/dmi/id/bios_vendor',
            'version': '/sys/class/dmi/id/bios_version',
            'release_date': '/sys/class/dmi/id/bios_date',
            'revision': '/sys/class/dmi/id/bios_revision'
        }
        
        for key, path in dmi_files.items():
            try:
                with open(path, 'r') as f:
                    bios[key] = f.read().strip()
            except (FileNotFoundError, IOError, PermissionError):
                bios[key] = 'N/A'
        
        return bios
    
    def _get_drivers_fallback(self) -> list:
        """Python fallback для драйверов"""
        drivers = []
        import subprocess
        
        try:
            result = subprocess.run(['lsmod'], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')[1:]  # Пропускаем заголовок
            for line in lines:
                parts = line.split()
                if parts:
                    drivers.append(parts[0])
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return drivers[:50]  # Ограничиваем первые 50 драйверов
    
    def _get_serial_number_fallback(self) -> str:
        """Python fallback для серийного номера"""
        try:
            with open('/sys/class/dmi/id/product_serial', 'r') as f:
                return f.read().strip()
        except (FileNotFoundError, IOError, PermissionError):
            return 'Требуются root права'
