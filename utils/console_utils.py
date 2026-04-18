"""
Утилиты для красивого вывода в консоль
"""

from enum import Enum
from typing import Optional


class Color(Enum):
    """Цвета для консольного вывода"""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class ConsoleStyle:
    """Класс для стилизации консольного вывода"""
    
    @staticmethod
    def colorize(text: str, color: Color) -> str:
        """Окрасить текст"""
        return f"{color.value}{text}{Color.RESET.value}"
    
    @staticmethod
    def red(text: str) -> str:
        return ConsoleStyle.colorize(text, Color.RED)
    
    @staticmethod
    def green(text: str) -> str:
        return ConsoleStyle.colorize(text, Color.GREEN)
    
    @staticmethod
    def yellow(text: str) -> str:
        return ConsoleStyle.colorize(text, Color.YELLOW)
    
    @staticmethod
    def blue(text: str) -> str:
        return ConsoleStyle.colorize(text, Color.BLUE)
    
    @staticmethod
    def cyan(text: str) -> str:
        return ConsoleStyle.colorize(text, Color.CYAN)
    
    @staticmethod
    def bold(text: str) -> str:
        return ConsoleStyle.colorize(text, Color.BOLD)
    
    @staticmethod
    def print_header(text: str, width: int = 50):
        """Вывести красивый заголовок"""
        print("\n" + "=" * width)
        print(ConsoleStyle.bold(ConsoleStyle.cyan(text.center(width))))
        print("=" * width + "\n")
    
    @staticmethod
    def print_section(title: str):
        """Вывести заголовок секции"""
        print(f"\n{ConsoleStyle.bold(ConsoleStyle.yellow(f'--- {title} ---'))}")
    
    @staticmethod
    def print_stat(label: str, value: str, color: Color = Color.GREEN):
        """Вывести статистику с цветом"""
        colored_value = ConsoleStyle.colorize(value, color)
        print(f"{label}: {colored_value}")
    
    @staticmethod
    def print_progress_bar(current: int, total: int, width: int = 30, prefix: str = "Progress"):
        """Вывести прогресс-бар"""
        percent = current / total
        filled = int(width * percent)
        bar = "█" * filled + "░" * (width - filled)
        print(f"\r{prefix}: [{bar}] {percent:.1%}", end="", flush=True)
        if current == total:
            print()
    
    @staticmethod
    def print_table(headers: list, rows: list):
        """Вывести таблицу"""
        # Вычислить ширину колонок
        col_widths = []
        for i, header in enumerate(headers):
            max_width = len(header)
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max_width + 2)
        
        # Вывести заголовок
        header_line = ""
        for i, header in enumerate(headers):
            header_line += f"{header:<{col_widths[i]}}"
        print(ConsoleStyle.bold(header_line))
        print("-" * sum(col_widths))
        
        # Вывести строки
        for row in rows:
            row_line = ""
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    row_line += f"{str(cell):<{col_widths[i]}}"
            print(row_line)
    
    @staticmethod
    def print_warning(text: str):
        """Вывести предупреждение"""
        print(f"{ConsoleStyle.yellow('⚠')} {text}")
    
    @staticmethod
    def print_error(text: str):
        """Вывести ошибку"""
        print(f"{ConsoleStyle.red('✗')} {text}")
    
    @staticmethod
    def print_success(text: str):
        """Вывести успех"""
        print(f"{ConsoleStyle.green('✓')} {text}")
    
    @staticmethod
    def print_info(text: str):
        """Вывести информацию"""
        print(f"{ConsoleStyle.blue('ℹ')} {text}")
