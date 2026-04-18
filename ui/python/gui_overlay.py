#!/usr/bin/env python3
"""
VitalSign Overlay - Оверлей для отображения FPS и нагрузки в играх/приложениях
"""

import sys
import psutil
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QCheckBox, QSlider, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from typing import Dict, Any
from utils import GUITheme, StyledLabel


class OverlayWorker(QThread):
    """Фоновый поток для сбора данных оверлея"""
    data_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def run(self):
        while self.running:
            data = self.collect_data()
            self.data_updated.emit(data)
            self.msleep(500)  # Обновление 2 раза в секунду
    
    def collect_data(self) -> Dict[str, Any]:
        """Собрать данные"""
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        return {
            'cpu': cpu,
            'memory': memory.percent,
            'memory_used': memory.used / (1024 ** 3),
            'memory_total': memory.total / (1024 ** 3)
        }
    
    def stop(self):
        self.running = False
        self.wait()


class VitalSignOverlay(QWidget):
    """Оверлей для отображения FPS и нагрузки"""
    
    def __init__(self):
        super().__init__()
        self.worker = OverlayWorker()
        self.init_ui()
        self.worker.start()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        # Настройки окна
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Размер и позиция
        self.setFixedSize(250, 120)
        self.move_to_corner()
        
        # Прозрачность
        self.opacity = 0.8
        self.set_opacity(self.opacity)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Фон
        self.background = QFrame()
        self.background.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 35, 200);
                border-radius: 10px;
                border: 1px solid rgba(67, 133, 245, 150);
            }
        """)
        bg_layout = QVBoxLayout(self.background)
        bg_layout.setContentsMargins(10, 10, 10, 10)
        bg_layout.setSpacing(8)
        
        # Заголовок
        title = StyledLabel('VitalSign Overlay', 'subtitle')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bg_layout.addWidget(title)
        
        # CPU
        self.cpu_label = StyledLabel('CPU: 0%', 'normal')
        self.cpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bg_layout.addWidget(self.cpu_label)
        
        # RAM
        self.memory_label = StyledLabel('RAM: 0%', 'normal')
        self.memory_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bg_layout.addWidget(self.memory_label)
        
        # FPS (заглушка)
        self.fps_label = StyledLabel('FPS: --', 'accent')
        self.fps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bg_layout.addWidget(self.fps_label)
        
        layout.addWidget(self.background)
        
        # Подключаем сигнал обновления
        self.worker.data_updated.connect(self.update_data)
        
        # Таймер для перемещения окна при изменении экрана
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.move_to_corner)
        self.position_timer.start(5000)  # Проверять каждые 5 секунд
    
    def move_to_corner(self):
        """Переместить в правый верхний угол"""
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = geometry.right() - self.width() - 20
            y = geometry.top() + 20
            self.move(x, y)
    
    def set_opacity(self, value: float):
        """Установить прозрачность"""
        self.opacity = value
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(value)
        self.setGraphicsEffect(effect)
    
    def update_data(self, data: Dict[str, Any]):
        """Обновить данные"""
        cpu = data['cpu']
        memory = data['memory']
        
        # Цвет в зависимости от нагрузки
        cpu_color = GUITheme.ACCENT_SUCCESS
        if cpu > 50:
            cpu_color = GUITheme.ACCENT_WARNING
        if cpu > 80:
            cpu_color = GUITheme.ACCENT_ERROR
        
        self.cpu_label.setText(f'CPU: {cpu:.1f}%')
        self.cpu_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {cpu_color.name()};
                padding: 2px;
            }}
        """)
        
        self.memory_label.setText(
            f'RAM: {data["memory_used"]:.1f}GB / {data["memory_total"]:.1f}GB ({memory:.0f}%)'
        )
        
        # FPS заглушка (в реальности нужно интегрировать с C++ FPS библиотекой)
        import random
        fps = random.randint(55, 65)
        self.fps_label.setText(f'FPS: {fps}')
    
    def mousePressEvent(self, event):
        """Обработка нажатия мыши для перемещения"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event):
        """Перемещение окна"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_position)
    
    def closeEvent(self, event):
        """Обработка закрытия"""
        self.worker.stop()
        event.accept()


class OverlaySettings(QWidget):
    """Настройки оверлея"""
    
    def __init__(self, overlay: VitalSignOverlay):
        super().__init__()
        self.overlay = overlay
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle('VitalSign Overlay Settings')
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Прозрачность
        layout.addWidget(QLabel('Прозрачность:'))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(int(self.overlay.opacity * 100))
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        layout.addWidget(self.opacity_slider)
        
        # Показать/скрыть
        self.visible_checkbox = QCheckBox('Показать оверлей')
        self.visible_checkbox.setChecked(True)
        self.visible_checkbox.toggled.connect(self.toggle_visibility)
        layout.addWidget(self.visible_checkbox)
        
        # Кнопка закрытия
        close_button = QPushButton('Закрыть настройки')
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
    
    def change_opacity(self, value: int):
        """Изменить прозрачность"""
        self.overlay.set_opacity(value / 100.0)
    
    def toggle_visibility(self, checked: bool):
        """Показать/скрыть оверлей"""
        self.overlay.setVisible(checked)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('VitalSign Overlay')
    
    # Создаем оверлей
    overlay = VitalSignOverlay()
    overlay.show()
    
    # Создаем настройки
    settings = OverlaySettings(overlay)
    settings.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
