"""
Утилиты для графического интерфейса VitalSign
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QPalette, QFont, QLinearGradient, QBrush
from typing import Optional


class GUITheme:
    """Класс для управления темами GUI"""
    
    # Цветовая палитра - темная тема
    DARK_BACKGROUND = QColor(30, 30, 35)
    DARK_WIDGET = QColor(45, 45, 50)
    DARK_GROUP = QColor(55, 55, 60)
    DARK_BORDER = QColor(70, 70, 75)
    
    # Акцентные цвета
    ACCENT_PRIMARY = QColor(67, 133, 245)   # Синий
    ACCENT_SUCCESS = QColor(76, 175, 80)    # Зеленый
    ACCENT_WARNING = QColor(255, 152, 0)   # Оранжевый
    ACCENT_ERROR = QColor(244, 67, 54)     # Красный
    ACCENT_INFO = QColor(33, 150, 243)     # Информационный синий
    
    # Текстовые цвета
    TEXT_PRIMARY = QColor(255, 255, 255)
    TEXT_SECONDARY = QColor(200, 200, 200)
    TEXT_DISABLED = QColor(120, 120, 120)
    
    # Градиенты
    GRADIENT_BLUE = QLinearGradient(0, 0, 0, 1)
    GRADIENT_BLUE.setColorAt(0, QColor(67, 133, 245))
    GRADIENT_BLUE.setColorAt(1, QColor(33, 150, 243))
    
    GRADIENT_GREEN = QLinearGradient(0, 0, 0, 1)
    GRADIENT_GREEN.setColorAt(0, QColor(76, 175, 80))
    GRADIENT_GREEN.setColorAt(1, QColor(56, 142, 60))
    
    GRADIENT_RED = QLinearGradient(0, 0, 0, 1)
    GRADIENT_RED.setColorAt(0, QColor(244, 67, 54))
    GRADIENT_RED.setColorAt(1, QColor(211, 47, 47))
    
    @staticmethod
    def apply_dark_theme(app):
        """Применить темную тему к приложению"""
        app.setStyle('Fusion')
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, GUITheme.DARK_BACKGROUND)
        palette.setColor(QPalette.ColorRole.WindowText, GUITheme.TEXT_PRIMARY)
        palette.setColor(QPalette.ColorRole.Base, GUITheme.DARK_WIDGET)
        palette.setColor(QPalette.ColorRole.AlternateBase, GUITheme.DARK_GROUP)
        palette.setColor(QPalette.ColorRole.ToolTipBase, GUITheme.DARK_WIDGET)
        palette.setColor(QPalette.ColorRole.ToolTipText, GUITheme.TEXT_PRIMARY)
        palette.setColor(QPalette.ColorRole.Text, GUITheme.TEXT_PRIMARY)
        palette.setColor(QPalette.ColorRole.Button, GUITheme.DARK_WIDGET)
        palette.setColor(QPalette.ColorRole.ButtonText, GUITheme.TEXT_PRIMARY)
        palette.setColor(QPalette.ColorRole.BrightText, GUITheme.ACCENT_ERROR)
        palette.setColor(QPalette.ColorRole.Link, GUITheme.ACCENT_PRIMARY)
        palette.setColor(QPalette.ColorRole.Highlight, GUITheme.ACCENT_PRIMARY)
        palette.setColor(QPalette.ColorRole.HighlightedText, GUITheme.TEXT_PRIMARY)
        
        app.setPalette(palette)


class StyledFrame(QFrame):
    """Стилизованный фрейм с закругленными углами и тенью"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            StyledFrame {
                background-color: #2d2d35;
                border-radius: 8px;
                border: 1px solid #3d3d45;
            }
        """)


class StyledLabel(QLabel):
    """Стилизованная метка с кастомным шрифтом"""
    
    def __init__(self, text: str, style: str = 'normal', parent=None):
        super().__init__(text, parent)
        self.apply_style(style)
    
    def apply_style(self, style: str):
        """Применить стиль к метке"""
        if style == 'title':
            self.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #ffffff;
                    padding: 5px;
                }
            """)
        elif style == 'subtitle':
            self.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: 600;
                    color: #e0e0e0;
                    padding: 3px;
                }
            """)
        elif style == 'normal':
            self.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #c0c0c0;
                    padding: 2px;
                }
            """)
        elif style == 'accent':
            self.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: 600;
                    color: #4285f4;
                    padding: 2px;
                }
            """)


class CardWidget(QWidget):
    """Карточка с контентом и стилем"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.init_ui(title)
    
    def init_ui(self, title: str):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Заголовок
        title_label = StyledLabel(title, 'subtitle')
        layout.addWidget(title_label)
        
        # Контент
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(5)
        layout.addLayout(self.content_layout)
        
        # Стилизация
        self.setStyleSheet("""
            CardWidget {
                background-color: #2a2a30;
                border-radius: 10px;
                border: 1px solid #3a3a40;
            }
            CardWidget:hover {
                border: 1px solid #4a4a50;
            }
        """)
    
    def add_widget(self, widget):
        """Добавить виджет в контент"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Добавить layout в контент"""
        self.content_layout.addLayout(layout)


class StatCard(CardWidget):
    """Карточка для отображения статистики"""
    
    def __init__(self, title: str, value: str, color: QColor, parent=None):
        super().__init__(title, parent)
        self.color = color
        self.init_stat_ui(value)
    
    def init_stat_ui(self, value: str):
        """Инициализация UI статистики"""
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {self.color.name()};
                padding: 5px;
            }}
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_widget(value_label)
    
    def update_value(self, value: str):
        """Обновить значение"""
        self.content_layout.itemAt(0).widget().setText(value)


class Separator(QWidget):
    """Разделитель"""
    
    def __init__(self, orientation: str = 'horizontal', parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        if self.orientation == 'horizontal':
            self.setFixedHeight(1)
            self.setStyleSheet("""
                Separator {
                    background-color: #3a3a40;
                    border: none;
                }
            """)
        else:
            self.setFixedWidth(1)
            self.setStyleSheet("""
                Separator {
                    background-color: #3a3a40;
                    border: none;
                }
            """)


class AnimatedWidget(QWidget):
    """Виджет с анимацией появления"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.opacity = 0.0
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def show_animated(self):
        """Показать с анимацией"""
        self.show()
        self.animation.start()
    
    def hide_animated(self):
        """Скрыть с анимацией"""
        self.animation.setDirection(QPropertyAnimation.Direction.Backward)
        self.animation.start()
        self.animation.finished.connect(self.hide)


class StatusIndicator(QWidget):
    """Индикатор статуса с цветом"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.status = 'normal'  # normal, warning, error, success
        self.update_style()
    
    def set_status(self, status: str):
        """Установить статус"""
        self.status = status
        self.update_style()
    
    def update_style(self):
        """Обновить стиль в зависимости от статуса"""
        color_map = {
            'normal': GUITheme.ACCENT_PRIMARY,
            'warning': GUITheme.ACCENT_WARNING,
            'error': GUITheme.ACCENT_ERROR,
            'success': GUITheme.ACCENT_SUCCESS
        }
        
        color = color_map.get(self.status, GUITheme.ACCENT_PRIMARY)
        self.setStyleSheet(f"""
            StatusIndicator {{
                background-color: {color.name()};
                border-radius: 6px;
                border: 2px solid {color.darker(120).name()};
            }}
        """)


class ProgressBarStyle:
    """Стили для прогресс-баров"""
    
    @staticmethod
    def get_style(color: QColor) -> str:
        """Получить стиль для прогресс-бара"""
        return f"""
            QProgressBar {{
                border: 2px solid #3a3a40;
                border-radius: 5px;
                text-align: center;
                background-color: #2a2a30;
                color: #ffffff;
                font-weight: bold;
                padding: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {color.name()};
                border-radius: 3px;
                margin: 1px;
            }}
        """
    
    @staticmethod
    def get_gradient_style(start_color: QColor, end_color: QColor) -> str:
        """Получить стиль с градиентом"""
        return f"""
            QProgressBar {{
                border: 2px solid #3a3a40;
                border-radius: 5px;
                text-align: center;
                background-color: #2a2a30;
                color: #ffffff;
                font-weight: bold;
                padding: 2px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {start_color.name()}, 
                    stop:1 {end_color.name()});
                border-radius: 3px;
                margin: 1px;
            }}
        """


class TableStyle:
    """Стили для таблиц"""
    
    @staticmethod
    def get_dark_style() -> str:
        """Получить темный стиль для таблицы"""
        return """
            QTableWidget {
                background-color: #2a2a30;
                border: 1px solid #3a3a40;
                border-radius: 5px;
                gridline-color: #3a3a40;
            }
            QTableWidget::item {
                padding: 5px;
                color: #c0c0c0;
            }
            QTableWidget::item:selected {
                background-color: #4285f4;
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background-color: #3a3a40;
            }
            QHeaderView::section {
                background-color: #3a3a40;
                color: #ffffff;
                padding: 5px;
                border: none;
                border-bottom: 1px solid #4a4a50;
                font-weight: bold;
            }
            QTableWidget QScrollBar:vertical {
                background-color: #2a2a30;
                width: 10px;
                border-radius: 5px;
            }
            QTableWidget QScrollBar::handle:vertical {
                background-color: #4a4a50;
                border-radius: 5px;
            }
            QTableWidget QScrollBar::handle:vertical:hover {
                background-color: #5a5a60;
            }
        """
