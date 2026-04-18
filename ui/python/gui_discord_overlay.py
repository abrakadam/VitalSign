#!/usr/bin/env python3
"""
VitalSign Discord-style Overlay - Оверлей в стиле Discord для отображения FPS, CPU, GPU
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ui', 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'main', 'python'))

import psutil
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QCheckBox, QComboBox, QPushButton, QDialog, QFrame, QSlider)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QFont, QFontDatabase
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from typing import Dict, Any
from utils import GUITheme, StyledLabel, t
try:
    from gpu_monitor import GPUMonitor
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


class OverlayWorker(QThread):
    """Фоновый поток для сбора данных оверлея"""
    data_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        if GPU_AVAILABLE:
            self.gpu_monitor = GPUMonitor()
        else:
            self.gpu_monitor = None
    
    def run(self):
        while self.running:
            data = self.collect_data()
            self.data_updated.emit(data)
            self.msleep(500)
    
    def collect_data(self) -> Dict[str, Any]:
        """Собрать данные"""
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        data = {
            'cpu': cpu,
            'memory': memory.percent,
            'memory_used': memory.used / (1024 ** 3),
            'memory_total': memory.total / (1024 ** 3),
            'gpu_available': False,
            'gpu_load': 0,
            'gpu_temp': 0
        }
        
        # GPU данные
        if self.gpu_monitor and self.gpu_monitor.is_available():
            gpu_stats = self.gpu_monitor.get_gpu_stats(0)
            data['gpu_available'] = gpu_stats['available']
            data['gpu_load'] = gpu_stats['load']
            data['gpu_temp'] = gpu_stats['temperature']
        
        # FPS (заглушка - в реальности нужно интегрировать с C++)
        import random
        data['fps'] = random.randint(55, 65)
        
        return data
    
    def stop(self):
        self.running = False
        self.wait()


class DiscordOverlay(QWidget):
    """Оверлей в стиле Discord"""
    
    def __init__(self, settings: dict):
        super().__init__()
        self.settings = settings
        self.worker = OverlayWorker()
        self.init_ui()
        self.worker.start()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        # Настройки окна для отображения поверх всех окон
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        # Размер
        self.setFixedSize(280, 35)
        self.set_position()
        
        # Прозрачность
        self.set_opacity(self.settings.get('overlay_opacity', 80) / 100)
        
        # Шрифт
        font_name = self.settings.get('overlay_font', 'Roboto')
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'fonts', f'{font_name}-Regular.ttf')
        print(f"Loading font from: {font_path}")
        
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id >= 0:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                print(f"Font families: {font_families}")
                if font_families:
                    self.overlay_font = QFont(font_families[0], 10)
                else:
                    self.overlay_font = QFont(font_name, 10)
            else:
                print(f"Failed to load font, using fallback")
                self.overlay_font = QFont(font_name, 10)
        else:
            print(f"Font file not found: {font_path}")
            self.overlay_font = QFont(font_name, 10)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Фон
        self.background = QFrame()
        self.background.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 35, 245);
                border-radius: 8px;
                border: 2px solid rgba(67, 133, 245, 180);
            }
        """)
        bg_layout = QHBoxLayout(self.background)
        bg_layout.setContentsMargins(12, 6, 12, 6)
        bg_layout.setSpacing(10)
        
        # FPS
        if self.settings.get('show_fps', True):
            self.fps_label = QLabel('60 FPS')
            self.fps_label.setFont(self.overlay_font)
            self.fps_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #4caf50;
                    background: transparent;
                }
            """)
            bg_layout.addWidget(self.fps_label)
        
        # CPU
        if self.settings.get('show_cpu', True):
            self.cpu_label = QLabel('1% CPU')
            self.cpu_label.setFont(self.overlay_font)
            self.cpu_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #4285f4;
                    background: transparent;
                }
            """)
            bg_layout.addWidget(self.cpu_label)
        
        # GPU
        if self.settings.get('show_gpu', True):
            self.gpu_label = QLabel('1% GPU')
            self.gpu_label.setFont(self.overlay_font)
            self.gpu_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #ff9800;
                    background: transparent;
                }
            """)
            bg_layout.addWidget(self.gpu_label)
        
        layout.addWidget(self.background)
        
        # Передаем события мыши от background к окну
        self.background.mousePressEvent = self.mousePressEvent
        self.background.mouseMoveEvent = self.mouseMoveEvent
        self.background.mouseReleaseEvent = self.mouseReleaseEvent
        
        # Подключаем сигнал обновления
        self.worker.data_updated.connect(self.update_data)
    
    def set_position(self):
        """Установить позицию"""
        position = self.settings.get('overlay_position', 'top_right')
        
        # Получаем все экраны
        screens = QApplication.screens()
        if not screens:
            return
        
        # Используем основной экран или последний (для поддержки нескольких мониторов)
        screen = screens[-1] if len(screens) > 1 else screens[0]
        geometry = screen.availableGeometry()
        
        if position == 'top_right':
            x = geometry.right() - self.width() - 20
            y = geometry.top() + 20
        elif position == 'top_left':
            x = geometry.left() + 20
            y = geometry.top() + 20
        elif position == 'bottom_right':
            x = geometry.right() - self.width() - 20
            y = geometry.bottom() - self.height() - 20
        elif position == 'bottom_left':
            x = geometry.left() + 20
            y = geometry.bottom() - self.height() - 20
        else:
            x = geometry.right() - self.width() - 20
            y = geometry.top() + 20
        
        print(f"Setting position: {position} on screen {screens.index(screen)} at ({x}, {y})")
        self.move(x, y)
        print(f"Actual position: {self.pos()}")
    
    def set_opacity(self, value: float):
        """Установить прозрачность"""
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(value)
        self.setGraphicsEffect(effect)
    
    def update_data(self, data: Dict[str, Any]):
        """Обновить данные"""
        # FPS
        if self.settings.get('show_fps', True):
            fps = data['fps']
            self.fps_label.setText(f'{fps} FPS')
        
        # CPU
        if self.settings.get('show_cpu', True):
            cpu = data['cpu']
            self.cpu_label.setText(f'{cpu:.0f}% CPU')
        
        # GPU
        if self.settings.get('show_gpu', True):
            if data['gpu_available']:
                gpu_load = data['gpu_load']
                self.gpu_label.setText(f'{gpu_load:.0f}% GPU')
            else:
                self.gpu_label.setText('N/A')
    
    def mousePressEvent(self, event):
        """Обработка нажатия мыши для перемещения"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()
            self.window_start_position = self.pos()
            print(f"Mouse press at: {self.drag_start_position}, window at: {self.window_start_position}")
            self.background.setStyleSheet("""
                QFrame {
                    background-color: rgba(50, 50, 60, 245);
                    border-radius: 8px;
                    border: 2px solid rgba(67, 133, 245, 255);
                }
            """)
    
    def mouseMoveEvent(self, event):
        """Перемещение окна"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_start_position'):
            current_pos = event.globalPosition().toPoint()
            delta = current_pos - self.drag_start_position
            new_pos = self.window_start_position + delta
            print(f"Moving window to: {new_pos}")
            self.move(new_pos)
    
    def mouseReleaseEvent(self, event):
        """Обработка отпускания мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.background.setStyleSheet("""
                QFrame {
                    background-color: rgba(30, 30, 35, 245);
                    border-radius: 8px;
                    border: 2px solid rgba(67, 133, 245, 180);
                }
            """)
    
    def closeEvent(self, event):
        """Обработка закрытия"""
        self.worker.stop()
        event.accept()


class OverlaySettingsDialog(QDialog):
    """Диалог настроек оверлея"""
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.current_settings = current_settings or {}
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle(t('overlay'))
        self.setMinimumSize(400, 350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Заголовок
        title = StyledLabel(t('overlay'), 'title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Включить оверлей
        self.enable_checkbox = QCheckBox(t('enable_overlay'))
        self.enable_checkbox.setChecked(self.current_settings.get('enable_overlay', False))
        self.enable_checkbox.setStyleSheet("""
            QCheckBox {
                color: #c0c0c0;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #4a4a50;
                background-color: #2a2a30;
            }
            QCheckBox::indicator:checked {
                background-color: #4285f4;
                border-color: #4285f4;
            }
        """)
        layout.addWidget(self.enable_checkbox)
        
        # Показывать элементы
        elements_group = StyledLabel('Показывать элементы:', 'normal')
        layout.addWidget(elements_group)
        
        self.show_fps = QCheckBox(t('show_fps'))
        self.show_fps.setChecked(self.current_settings.get('show_fps', True))
        layout.addWidget(self.show_fps)
        
        self.show_cpu = QCheckBox(t('show_cpu'))
        self.show_cpu.setChecked(self.current_settings.get('show_cpu', True))
        layout.addWidget(self.show_cpu)
        
        self.show_gpu = QCheckBox(t('show_gpu'))
        self.show_gpu.setChecked(self.current_settings.get('show_gpu', True))
        layout.addWidget(self.show_gpu)
        
        # Позиция
        position_label = StyledLabel(f'{t("overlay_position")}:', 'normal')
        layout.addWidget(position_label)
        
        self.position_combo = QComboBox()
        self.position_combo.addItem(t('top_right'), 'top_right')
        self.position_combo.addItem(t('top_left'), 'top_left')
        self.position_combo.addItem(t('bottom_right'), 'bottom_right')
        self.position_combo.addItem(t('bottom_left'), 'bottom_left')
        
        current_pos = self.current_settings.get('overlay_position', 'top_right')
        index = self.position_combo.findData(current_pos)
        if index >= 0:
            self.position_combo.setCurrentIndex(index)
        
        layout.addWidget(self.position_combo)
        
        # Прозрачность
        opacity_label = StyledLabel(f'{t("overlay_opacity")} (%):', 'normal')
        layout.addWidget(opacity_label)
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(self.current_settings.get('overlay_opacity', 80))
        layout.addWidget(self.opacity_slider)
        
        layout.addStretch()
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton(t('save'))
        save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton(t('cancel'))
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def get_settings(self) -> dict:
        """Получить настройки"""
        settings = self.current_settings.copy()
        settings['enable_overlay'] = self.enable_checkbox.isChecked()
        settings['show_fps'] = self.show_fps.isChecked()
        settings['show_cpu'] = self.show_cpu.isChecked()
        settings['show_gpu'] = self.show_gpu.isChecked()
        settings['overlay_position'] = self.position_combo.currentData()
        settings['overlay_opacity'] = self.opacity_slider.value()
        return settings


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('VitalSign Discord Overlay')
    
    settings = {
        'enable_overlay': True,
        'show_fps': True,
        'show_cpu': True,
        'show_gpu': True,
        'overlay_position': 'top_right',
        'overlay_opacity': 80
    }
    
    overlay = DiscordOverlay(settings)
    overlay.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
