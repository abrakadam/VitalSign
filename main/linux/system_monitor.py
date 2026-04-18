import psutil
import time
from typing import Dict, Any


class SystemMonitor:
    """Мониторинг системных ресурсов: CPU, RAM, диск, сеть"""
    
    def __init__(self):
        self.cpu_percent = 0
        self.memory_percent = 0
        self.memory_used = 0
        self.memory_total = 0
        self.disk_usage = 0
        self.network_sent = 0
        self.network_recv = 0
    
    def update(self):
        """Обновить данные о системе"""
        self.cpu_percent = psutil.cpu_percent(interval=0.1)
        
        memory = psutil.virtual_memory()
        self.memory_percent = memory.percent
        self.memory_used = memory.used / (1024 ** 3)  # GB
        self.memory_total = memory.total / (1024 ** 3)  # GB
        
        disk = psutil.disk_usage('/')
        self.disk_usage = disk.percent
        
        network = psutil.net_io_counters()
        self.network_sent = network.bytes_sent / (1024 ** 2)  # MB
        self.network_recv = network.bytes_recv / (1024 ** 2)  # MB
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику в виде словаря"""
        return {
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_used_gb': self.memory_used,
            'memory_total_gb': self.memory_total,
            'disk_usage_percent': self.disk_usage,
            'network_sent_mb': self.network_sent,
            'network_recv_mb': self.network_recv
        }
    
    def print_stats(self):
        """Вывести статистику в консоль"""
        stats = self.get_stats()
        print(f"\n=== Системная статистика ===")
        print(f"CPU: {stats['cpu_percent']:.1f}%")
        print(f"RAM: {stats['memory_used_gb']:.2f} GB / {stats['memory_total_gb']:.2f} GB ({stats['memory_percent']:.1f}%)")
        print(f"Диск: {stats['disk_usage_percent']:.1f}%")
        print(f"Сеть (отправлено): {stats['network_sent_mb']:.2f} MB")
        print(f"Сеть (получено): {stats['network_recv_mb']:.2f} MB")


if __name__ == "__main__":
    monitor = SystemMonitor()
    while True:
        monitor.update()
        monitor.print_stats()
        time.sleep(1)
