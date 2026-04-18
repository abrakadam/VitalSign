"""
Библиотека для работы с системными ресурсами
"""

import psutil
from typing import Dict, Any, List


class SystemLib:
    """Библиотека системных функций"""
    
    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """Получить информацию о CPU"""
        return {
            'percent': psutil.cpu_percent(interval=0.1),
            'count': psutil.cpu_count(),
            'freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0
        }
    
    @staticmethod
    def get_memory_info() -> Dict[str, Any]:
        """Получить информацию о памяти"""
        mem = psutil.virtual_memory()
        return {
            'percent': mem.percent,
            'used': mem.used,
            'total': mem.total,
            'available': mem.available
        }
    
    @staticmethod
    def get_disk_info(path: str = '/') -> Dict[str, Any]:
        """Получить информацию о диске"""
        disk = psutil.disk_usage(path)
        return {
            'percent': disk.percent,
            'used': disk.used,
            'total': disk.total,
            'free': disk.free
        }
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """Получить информацию о сети"""
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv
        }
    
    @staticmethod
    def get_process_info(limit: int = 10) -> List[Dict[str, Any]]:
        """Получить информацию о процессах"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Сортировка по CPU
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        return processes[:limit]
    
    @staticmethod
    def get_temperature_info() -> Dict[str, Any]:
        """Получить информацию о температуре (если доступно)"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                return {name: [t.current for t in sensors] for name, sensors in temps.items()}
        except (AttributeError, NotImplementedError):
            pass
        return {}
