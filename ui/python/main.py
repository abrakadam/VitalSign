#!/usr/bin/env python3
"""
VitalSign - Главный скрипт для мониторинга системных ресурсов и FPS
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main', 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

import time
import argparse
from system_monitor import SystemMonitor
from window_monitor import WindowMonitor
from utils import ConsoleStyle, FormatUtils, Color


def print_header():
    """Вывести заголовок"""
    ConsoleStyle.print_header("VitalSign - Мониторинг системы", 50)


def monitor_mode(interval=1):
    """Режим мониторинга с периодическим обновлением"""
    ConsoleStyle.print_info(f"Режим мониторинга (обновление каждые {interval} сек)")
    ConsoleStyle.print_warning("Нажмите Ctrl+C для выхода\n")
    
    system_monitor = SystemMonitor()
    window_monitor = WindowMonitor()
    
    try:
        while True:
            print_header()
            
            # Системная статистика
            system_monitor.update()
            print_system_stats(system_monitor)
            
            # Информация об окнах
            window_monitor.update()
            print_window_stats(window_monitor)
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        ConsoleStyle.print_success("\nМониторинг остановлен")


def print_system_stats(monitor):
    """Вывести системную статистику с красивым форматированием"""
    ConsoleStyle.print_section("Системная статистика")
    
    stats = monitor.get_stats()
    
    # CPU с цветом в зависимости от нагрузки
    cpu_color = Color.GREEN
    if stats['cpu_percent'] > 50:
        cpu_color = Color.YELLOW
    if stats['cpu_percent'] > 80:
        cpu_color = Color.RED
    
    ConsoleStyle.print_stat("CPU", f"{stats['cpu_percent']:.1f}%", cpu_color)
    ConsoleStyle.print_stat("RAM", 
                           f"{stats['memory_used_gb']:.2f} GB / {stats['memory_total_gb']:.2f} GB ({stats['memory_percent']:.1f}%)")
    ConsoleStyle.print_stat("Диск", f"{stats['disk_usage_percent']:.1f}%")
    ConsoleStyle.print_stat("Сеть (отправлено)", f"{stats['network_sent_mb']:.2f} MB")
    ConsoleStyle.print_stat("Сеть (получено)", f"{stats['network_recv_mb']:.2f} MB")


def print_window_stats(monitor):
    """Вывести статистику окон с красивым форматированием"""
    windows = monitor.get_all_windows()
    ConsoleStyle.print_section(f"Активные окна ({len(windows)})")
    
    if windows:
        # Вывести в виде таблицы
        headers = ["№", "Заголовок", "Размер"]
        rows = []
        for i, window in enumerate(windows[:8], 1):
            title = FormatUtils.truncate_text(window['title'], 40)
            size = f"{window['width']}x{window['height']}"
            rows.append([str(i), title, size])
        
        ConsoleStyle.print_table(headers, rows)
        
        if len(windows) > 8:
            ConsoleStyle.print_info(f"... и еще {len(windows) - 8} окон")
    
    # Активное окно
    active = monitor.get_active_window()
    if active:
        ConsoleStyle.print_section("Активное окно")
        ConsoleStyle.print_stat("Заголовок", FormatUtils.truncate_text(active['title'], 60))
        ConsoleStyle.print_stat("Позиция", f"{active['left']}, {active['top']}")
        ConsoleStyle.print_stat("Размер", f"{active['width']}x{active['height']}")


def single_mode():
    """Режим однократного замера"""
    print_header()
    
    system_monitor = SystemMonitor()
    system_monitor.update()
    print_system_stats(system_monitor)
    
    window_monitor = WindowMonitor()
    window_monitor.update()
    print_window_stats(window_monitor)


def main():
    parser = argparse.ArgumentParser(description='VitalSign - Мониторинг системных ресурсов')
    parser.add_argument('--interval', '-i', type=int, default=1,
                        help='Интервал обновления в секундах (по умолчанию: 1)')
    parser.add_argument('--single', '-s', action='store_true',
                        help='Одиночный замер без непрерывного мониторинга')
    
    args = parser.parse_args()
    
    if args.single:
        single_mode()
    else:
        monitor_mode(args.interval)


if __name__ == "__main__":
    main()
