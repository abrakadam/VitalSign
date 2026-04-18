"""
Утилиты для форматирования данных
"""


class FormatUtils:
    """Класс для форматирования значений"""
    
    @staticmethod
    def bytes_to_gb(bytes_value: int) -> float:
        """Конвертировать байты в гигабайты"""
        return bytes_value / (1024 ** 3)
    
    @staticmethod
    def bytes_to_mb(bytes_value: int) -> float:
        """Конвертировать байты в мегабайты"""
        return bytes_value / (1024 ** 2)
    
    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """Форматировать байты в читаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    @staticmethod
    def format_percent(value: float) -> str:
        """Форматировать процент"""
        return f"{value:.1f}%"
    
    @staticmethod
    def format_frequency(hz: float) -> str:
        """Форматировать частоту (Hz)"""
        if hz >= 1_000_000_000:
            return f"{hz / 1_000_000_000:.2f} GHz"
        elif hz >= 1_000_000:
            return f"{hz / 1_000_000:.2f} MHz"
        elif hz >= 1_000:
            return f"{hz / 1_000:.2f} kHz"
        else:
            return f"{hz:.2f} Hz"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Форматировать длительность"""
        if seconds >= 3600:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}ч {minutes}мин"
        elif seconds >= 60:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}мин {secs}сек"
        else:
            return f"{seconds:.1f}сек"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
        """Обрезать текст до максимальной длины"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def format_number(number: int or float, decimals: int = 2) -> str:
        """Форматировать число с разделителями"""
        return f"{number:,.{decimals}f}"
