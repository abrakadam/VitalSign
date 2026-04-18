import sys
import time
from typing import List, Dict, Any

try:
    import pygetwindow as gw
    HAS_WINDOW = True
except ImportError:
    HAS_WINDOW = False
    print("pygetwindow не установлен. Установите: pip install pygetwindow")


class WindowMonitor:
    """Мониторинг активных окон"""
    
    def __init__(self):
        self.windows = []
    
    def update(self):
        """Обновить список окон"""
        if not HAS_WINDOW:
            return
        
        try:
            self.windows = gw.getAllWindows()
        except Exception as e:
            print(f"Ошибка при получении окон: {e}")
            self.windows = []
    
    def get_active_window(self) -> Dict[str, Any]:
        """Получить информацию об активном окне"""
        if not HAS_WINDOW:
            return {}
        
        try:
            active = gw.getActiveWindow()
            if active:
                return {
                    'title': active.title,
                    'left': active.left,
                    'top': active.top,
                    'width': active.width,
                    'height': active.height
                }
        except Exception as e:
            print(f"Ошибка при получении активного окна: {e}")
        
        return {}
    
    def get_all_windows(self) -> List[Dict[str, Any]]:
        """Получить список всех окон"""
        if not HAS_WINDOW:
            return []
        
        windows_info = []
        for window in self.windows:
            if window.title:  # Только окна с заголовком
                windows_info.append({
                    'title': window.title,
                    'left': window.left,
                    'top': window.top,
                    'width': window.width,
                    'height': window.height
                })
        
        return windows_info
    
    def print_windows(self):
        """Вывести список окон"""
        windows = self.get_all_windows()
        print(f"\n=== Активные окна ({len(windows)}) ===")
        for i, window in enumerate(windows[:10], 1):  # Показать первые 10
            print(f"{i}. {window['title'][:50]}... [{window['width']}x{window['height']}]")


if __name__ == "__main__":
    monitor = WindowMonitor()
    monitor.update()
    monitor.print_windows()
    
    active = monitor.get_active_window()
    if active:
        print(f"\n=== Активное окно ===")
        print(f"Заголовок: {active['title']}")
        print(f"Позиция: {active['left']}, {active['top']}")
        print(f"Размер: {active['width']}x{active['height']}")
