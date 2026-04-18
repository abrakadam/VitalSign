#!/usr/bin/env python3
"""
VitalSign GUI - Графический интерфейс для мониторинга системных ресурсов
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ui', 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'main', 'linux'))

import psutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QProgressBar, QGroupBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QTabWidget, QFrame, QGridLayout, QPushButton,
                             QScrollArea, QSlider, QCheckBox, QSpinBox, QDialog, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont, QColor, QPalette, QFontDatabase
from typing import Dict, Any
from utils import (
    GUITheme, StyledLabel, CardWidget, StatCard, 
    Separator, StatusIndicator, ProgressBarStyle, TableStyle,
    t, set_language, get_current_language, get_available_languages
)
from utils.fire_animation import SubtleFireBackground


class AnimatedTabWidget(QTabWidget):
    """TabWidget с анимацией при переключении"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_animation = None
    
    def setCurrentIndex(self, index: int):
        """Переключение вкладки с анимацией"""
        if index == self.currentIndex():
            return
        
        # Анимация исчезновения текущей вкладки
        self.fade_out_current()
        
        # Задержка перед переключением
        QTimer.singleShot(150, lambda: super().setCurrentIndex(index))
        
        # Анимация появления новой вкладки
        QTimer.singleShot(200, self.fade_in_current)
    
    def fade_out_current(self):
        """Анимация исчезновения"""
        current_widget = self.currentWidget()
        if current_widget:
            self.current_animation = QPropertyAnimation(current_widget, b"windowOpacity")
            self.current_animation.setDuration(150)
            self.current_animation.setStartValue(1.0)
            self.current_animation.setEndValue(0.0)
            self.current_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.current_animation.start()
    
    def fade_in_current(self):
        """Анимация появления"""
        current_widget = self.currentWidget()
        if current_widget:
            current_widget.setWindowOpacity(0.0)
            self.current_animation = QPropertyAnimation(current_widget, b"windowOpacity")
            self.current_animation.setDuration(200)
            self.current_animation.setStartValue(0.0)
            self.current_animation.setEndValue(1.0)
            self.current_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.current_animation.start()


class SettingsDialog(QDialog):
    """Диалог настроек"""
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.current_settings = current_settings or {}
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса настроек"""
        self.setWindowTitle(t('settings_title'))
        self.setMinimumSize(450, 350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Заголовок
        title = StyledLabel(t('settings'), 'title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Язык
        language_group = CardWidget(t('language'))
        language_layout = QVBoxLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: #3a3a40;
                color: #ffffff;
                border: 1px solid #4a4a50;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                color: #ffffff;
            }
        """)
        
        for lang in get_available_languages():
            self.language_combo.addItem(f"{self.get_language_name(lang)} ({lang})", lang)
        
        self.language_combo.setCurrentText(f"{self.get_language_name(get_current_language())} ({get_current_language()})")
        language_layout.addWidget(self.language_combo)
        language_group.add_layout(language_layout)
        layout.addWidget(language_group)
        
        # Интервал обновления
        interval_group = CardWidget(t('update_interval'))
        interval_layout = QVBoxLayout()
        
        interval_label = StyledLabel(f'{t("update_interval")} ({t("seconds")}):', 'normal')
        interval_layout.addWidget(interval_label)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(self.current_settings.get('interval', 1))
        self.interval_spin.setStyleSheet("""
            QSpinBox {
                background-color: #3a3a40;
                color: #ffffff;
                border: 1px solid #4a4a50;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        interval_layout.addWidget(self.interval_spin)
        interval_group.add_layout(interval_layout)
        layout.addWidget(interval_group)
        
        # Показывать анимацию фона
        fire_group = CardWidget(t('fire_animation'))
        fire_layout = QVBoxLayout()
        
        self.fire_checkbox = QCheckBox(t('show_fire'))
        self.fire_checkbox.setChecked(self.current_settings.get('fire_enabled', True))
        self.fire_checkbox.setStyleSheet("""
            QCheckBox {
                color: #c0c0c0;
                font-size: 12px;
                spacing: 5px;
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
        fire_layout.addWidget(self.fire_checkbox)
        fire_group.add_layout(fire_layout)
        layout.addWidget(fire_group)
        
        # Количество процессов
        processes_group = CardWidget(t('process_count'))
        processes_layout = QVBoxLayout()
        
        processes_label = StyledLabel(f'{t("process_count")}:', 'normal')
        processes_layout.addWidget(processes_label)
        
        self.process_spin = QSpinBox()
        self.process_spin.setRange(5, 50)
        self.process_spin.setValue(self.current_settings.get('process_count', 20))
        self.process_spin.setStyleSheet("""
            QSpinBox {
                background-color: #3a3a40;
                color: #ffffff;
                border: 1px solid #4a4a50;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        processes_layout.addWidget(self.process_spin)
        processes_group.add_layout(processes_layout)
        layout.addWidget(processes_group)
        
        layout.addStretch()
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton(t('save'))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton(t('cancel'))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Применяем стили к диалогу
        self.setStyleSheet("""
            QDialog {
                background-color: #2a2a30;
                border-radius: 10px;
            }
        """)
    
    def get_language_name(self, lang_code: str) -> str:
        """Получить название языка"""
        names = {
            'en': 'English',
            'ru': 'Русский',
            'pl': 'Polski',
            'de': 'Deutsch'
        }
        return names.get(lang_code, lang_code.upper())
    
    def get_settings(self) -> dict:
        """Получить настройки"""
        return {
            'interval': self.interval_spin.value(),
            'fire_enabled': self.fire_checkbox.isChecked(),
            'process_count': self.process_spin.value(),
            'language': self.language_combo.currentData()
        }


class SystemWorker(QThread):
    """Фоновый поток для сбора системных данных"""
    data_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def run(self):
        while self.running:
            data = self.collect_data()
            self.data_updated.emit(data)
            self.msleep(1000)  # Обновление каждую секунду
    
    def collect_data(self) -> Dict[str, Any]:
        """Собрать данные о системе"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        return {
            'cpu': cpu_percent,
            'memory': {
                'percent': memory.percent,
                'used': memory.used / (1024 ** 3),
                'total': memory.total / (1024 ** 3)
            },
            'disk': disk.percent,
            'network': {
                'sent': network.bytes_sent / (1024 ** 2),
                'recv': network.bytes_recv / (1024 ** 2)
            }
        }
    
    def stop(self):
        self.running = False
        self.wait()


class VitalSignGUI(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.worker = SystemWorker()
        self.settings = {
            'interval': 1,
            'fire_enabled': True,
            'process_count': 20,
            'language': 'ru',
            'enable_overlay': False,
            'show_fps': True,
            'show_cpu': True,
            'show_gpu': True,
            'overlay_position': 'top_right'
        }
        self.discord_overlay = None
        self.init_ui()
        self.worker.start()

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle('VitalSign')
        self.setMinimumSize(900, 600)
        self.resize(1100, 750)

        # Загружаем шрифты
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'fonts', 'Roboto-Regular.ttf')
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id >= 0:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    app_font = QFont(font_families[0], 10)
                    QApplication.instance().setFont(app_font)

        # Применяем темную тему
        GUITheme.apply_dark_theme(QApplication.instance())

        # Фон с огнем
        self.fire_background = SubtleFireBackground(self)
        self.fire_background.lower()  # Отправляем на задний план

        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок с индикатором статуса
        header_layout = QHBoxLayout()
        self.status_indicator = StatusIndicator()
        self.status_indicator.set_status('success')
        header_layout.addWidget(self.status_indicator)
        
        title_label = StyledLabel(t('app_title'), 'title')
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Разделитель
        main_layout.addWidget(Separator())
        
        # Панель управления
        control_layout = QHBoxLayout()
        control_layout.addStretch()
        
        settings_button = QPushButton(f'⚙ {t("settings")}')
        settings_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
            QPushButton:pressed {
                background-color: #2850a0;
            }
        """)
        settings_button.clicked.connect(self.open_settings)
        control_layout.addWidget(settings_button)
        
        main_layout.addLayout(control_layout)
        
        # Создаем вкладки с анимацией
        tab_widget = AnimatedTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #3a3a40;
                background-color: #1e1e24;
                border-radius: 10px;
            }
            QTabBar::tab {
                background-color: #2a2a30;
                color: #c0c0c0;
                padding: 12px 25px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 3px;
                font-weight: bold;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: linear-gradient(135deg, #4285f4, #34a853);
                color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3a3a40;
                color: #ffffff;
            }
        """)
        main_layout.addWidget(tab_widget)
        
        # Вкладка "Система"
        system_tab = self.create_system_tab()
        tab_widget.addTab(system_tab, t('system'))
        
        # Вкладка "Процессы"
        processes_tab = self.create_processes_tab()
        tab_widget.addTab(processes_tab, t('processes'))
        
        # Вкладка "Сеть"
        network_tab = self.create_network_tab()
        tab_widget.addTab(network_tab, t('network'))
        
        # Вкладка "Температуры"
        temp_tab = self.create_temperature_tab()
        tab_widget.addTab(temp_tab, t('temperatures'))
        
        # Вкладка "Оценка CPU"
        cpu_rating_tab = self.create_cpu_rating_tab()
        tab_widget.addTab(cpu_rating_tab, t('cpu_rating'))
        
        # Вкладка "Оценка GPU"
        gpu_rating_tab = self.create_gpu_rating_tab()
        tab_widget.addTab(gpu_rating_tab, t('gpu_rating'))
        
        # Вкладка "Информация о системе"
        system_info_tab = self.create_system_info_tab()
        tab_widget.addTab(system_info_tab, t('system_info'))
        
        # Вкладка "Драйверы"
        drivers_tab = self.create_drivers_tab()
        tab_widget.addTab(drivers_tab, t('drivers'))
        
        # Вкладка "Дистрибутивы"
        distros_tab = self.create_distros_tab()
        tab_widget.addTab(distros_tab, t('distros'))
        
        # Вкладка "Устройства"
        devices_tab = self.create_devices_tab()
        tab_widget.addTab(devices_tab, t('devices'))
        
        # Вкладка "Порты и гнезда"
        ports_tab = self.create_ports_tab()
        tab_widget.addTab(ports_tab, t('ports'))
        
        # Вкладка "Мониторы"
        monitors_tab = self.create_monitors_tab()
        tab_widget.addTab(monitors_tab, t('monitors'))
        
        # Вкладка "Помощник"
        helper_tab = self.create_helper_tab()
        tab_widget.addTab(helper_tab, t('helper'))
        
        # Подключаем сигнал обновления данных
        self.worker.data_updated.connect(self.update_system_data)
    
    def create_system_tab(self) -> QWidget:
        """Создать вкладку системного мониторинга"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Grid layout для карточек
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # CPU карточка
        self.cpu_card = CardWidget(t('cpu'))
        self.cpu_label = StyledLabel(f'{t("usage")}: 0%', 'normal')
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setStyleSheet(ProgressBarStyle.get_style(GUITheme.ACCENT_PRIMARY))
        self.cpu_bar.setFixedHeight(25)
        self.cpu_card.add_widget(self.cpu_label)
        self.cpu_card.add_widget(self.cpu_bar)
        
        # Память карточка
        self.memory_card = CardWidget(t('memory'))
        self.memory_label = StyledLabel(f'{t("usage")}: 0 GB / 0 GB (0%)', 'normal')
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        self.memory_bar.setStyleSheet(ProgressBarStyle.get_gradient_style(GUITheme.ACCENT_PRIMARY, GUITheme.ACCENT_INFO))
        self.memory_bar.setFixedHeight(25)
        self.memory_card.add_widget(self.memory_label)
        self.memory_card.add_widget(self.memory_bar)
        
        # Диск карточка
        self.disk_card = CardWidget(t('disk'))
        self.disk_label = StyledLabel(f'{t("usage")}: 0%', 'normal')
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        self.disk_bar.setStyleSheet(ProgressBarStyle.get_style(GUITheme.ACCENT_WARNING))
        self.disk_bar.setFixedHeight(25)
        self.disk_card.add_widget(self.disk_label)
        self.disk_card.add_widget(self.disk_bar)
        
        # Сеть карточка
        self.network_card = CardWidget(t('network'))
        network_layout = QHBoxLayout()
        self.network_sent_label = StyledLabel(f'{t("sent")}: 0 MB', 'normal')
        self.network_recv_label = StyledLabel(f'{t("received")}: 0 MB', 'normal')
        network_layout.addWidget(self.network_sent_label)
        network_layout.addWidget(self.network_recv_label)
        self.network_card.add_layout(network_layout)
        
        # Размещаем карточки в сетке
        grid_layout.addWidget(self.cpu_card, 0, 0)
        grid_layout.addWidget(self.memory_card, 0, 1)
        grid_layout.addWidget(self.disk_card, 1, 0)
        grid_layout.addWidget(self.network_card, 1, 1)
        
        layout.addLayout(grid_layout)
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def create_disk_details_tab(self) -> QWidget:
        """Создать вкладку с деталями диска"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('disk_usage_title'), 'subtitle')
        layout.addWidget(title_label)
        
        # Таблица дисков
        self.disk_table = QTableWidget()
        self.disk_table.setColumnCount(5)
        self.disk_table.setHorizontalHeaderLabels([
            t('file_system'), t('total'), t('used'), t('free'), t('mount_point')
        ])
        self.disk_table.setStyleSheet(TableStyle.get_dark_style())
        
        header = self.disk_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.disk_table)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('refresh'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        refresh_button.clicked.connect(self.update_disk_details)
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def update_disk_details(self):
        """Обновить детали диска"""
        self.disk_table.setRowCount(0)
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                row = self.disk_table.rowCount()
                self.disk_table.insertRow(row)
                
                self.disk_table.setItem(row, 0, QTableWidgetItem(partition.fstype))
                self.disk_table.setItem(row, 1, QTableWidgetItem(f'{usage.total / (1024**3):.2f} GB'))
                self.disk_table.setItem(row, 2, QTableWidgetItem(f'{usage.used / (1024**3):.2f} GB'))
                self.disk_table.setItem(row, 3, QTableWidgetItem(f'{usage.free / (1024**3):.2f} GB'))
                self.disk_table.setItem(row, 4, QTableWidgetItem(partition.mountpoint))
                
                # Подсветка по использованию
                percent = (usage.used / usage.total) * 100
                if percent > 80:
                    self.disk_table.item(row, 2).setBackground(GUITheme.ACCENT_ERROR)
                elif percent > 50:
                    self.disk_table.item(row, 2).setBackground(GUITheme.ACCENT_WARNING)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
    
    def create_network_tab(self) -> QWidget:
        """Создать вкладку сети"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('network_stats'), 'subtitle')
        layout.addWidget(title_label)
        
        # Таблица сетевых интерфейсов
        self.network_table = QTableWidget()
        self.network_table.setColumnCount(4)
        self.network_table.setHorizontalHeaderLabels([
            t('interface'), t('bytes_sent'), t('bytes_recv'), t('download_speed')
        ])
        self.network_table.setStyleSheet(TableStyle.get_dark_style())
        
        header = self.network_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.network_table)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('refresh'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        refresh_button.clicked.connect(self.update_network_tab)
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def update_network_tab(self):
        """Обновить вкладку сети"""
        self.network_table.setRowCount(0)
        
        net_io = psutil.net_io_counters(pernic=True)
        for interface, stats in net_io.items():
            row = self.network_table.rowCount()
            self.network_table.insertRow(row)
            
            self.network_table.setItem(row, 0, QTableWidgetItem(interface))
            self.network_table.setItem(row, 1, QTableWidgetItem(f'{stats.bytes_sent / (1024**3):.2f} GB'))
            self.network_table.setItem(row, 2, QTableWidgetItem(f'{stats.bytes_recv / (1024**3):.2f} GB'))
            self.network_table.setItem(row, 3, QTableWidgetItem(f'{stats.bytes_recv / (1024**2):.2f} MB/s'))
    
    def create_gpu_tab(self) -> QWidget:
        """Создать вкладку GPU"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('gpu_monitor'), 'subtitle')
        layout.addWidget(title_label)
        
        # GPU карточки
        self.gpu_cards_layout = QVBoxLayout()
        self.update_gpu_cards()
        layout.addLayout(self.gpu_cards_layout)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('refresh'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        refresh_button.clicked.connect(self.update_gpu_cards)
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def update_gpu_cards(self):
        """Обновить карточки GPU"""
        # Очистить старые карточки
        while self.gpu_cards_layout.count():
            child = self.gpu_cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        try:
            from gpu_monitor import GPUMonitor
            gpu_monitor = GPUMonitor()
            
            if not gpu_monitor.is_available():
                no_gpu_label = StyledLabel(t('not_available'), 'normal')
                self.gpu_cards_layout.addWidget(no_gpu_label)
                return
            
            gpus = gpu_monitor.get_all_gpus()
            for i, gpu in enumerate(gpus):
                gpu_card = CardWidget(f'{t("gpu")} {i}')
                
                # Имя
                name_label = StyledLabel(f'{t("gpu_name")}: {gpu["name"]}', 'normal')
                gpu_card.add_widget(name_label)
                
                # Загрузка
                load_label = StyledLabel(f'{t("gpu_load")}: {gpu["load"]:.1f}%', 'normal')
                gpu_card.add_widget(load_label)
                
                # Память
                mem_label = StyledLabel(
                    f'{t("gpu_memory")}: {gpu["memory_used"]:.0f} MB / {gpu["memory_total"]:.0f} MB',
                    'normal'
                )
                gpu_card.add_widget(mem_label)
                
                # Температура
                temp_label = StyledLabel(f'{t("gpu_temp")}: {gpu["temperature"]:.0f}°C', 'normal')
                gpu_card.add_widget(temp_label)
                
                self.gpu_cards_layout.addWidget(gpu_card)
        except ImportError:
            no_gpu_label = StyledLabel(t('not_available'), 'normal')
            self.gpu_cards_layout.addWidget(no_gpu_label)
    
    def create_temperature_tab(self) -> QWidget:
        """Создать вкладку температур"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('temperatures'), 'subtitle')
        layout.addWidget(title_label)
        
        # Карточки температур
        self.temp_cards_layout = QVBoxLayout()
        self.update_temperature_cards()
        layout.addLayout(self.temp_cards_layout)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('refresh'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        refresh_button.clicked.connect(self.update_temperature_cards)
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def update_temperature_cards(self):
        """Обновить карточки температур"""
        # Очистить старые карточки
        while self.temp_cards_layout.count():
            child = self.temp_cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # CPU температура (Linux)
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                cpu_temp = int(f.read()) / 1000.0
                cpu_card = CardWidget(t('cpu'))
                cpu_label = StyledLabel(f'{t("temperature")}: {cpu_temp:.1f}°C', 'normal')
                cpu_card.add_widget(cpu_label)
                self.temp_cards_layout.addWidget(cpu_card)
        except (FileNotFoundError, IOError):
            no_temp_label = StyledLabel(t('not_available'), 'normal')
            self.temp_cards_layout.addWidget(no_temp_label)
    
    def create_system_info_tab(self) -> QWidget:
        """Создать вкладку с полной информацией о системе"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('system_info'), 'subtitle')
        layout.addWidget(title_label)
        
        # Загружаем информацию
        try:
            from system_info_lib import SystemInfo
            sys_info = SystemInfo()
            
            # Железо
            hw_card = CardWidget(t('hardware'))
            hw_layout = QVBoxLayout()
            
            hw_info = sys_info.get_hardware_info()
            hw_layout.addWidget(StyledLabel(f'Производитель: {hw_info.get("system_vendor", "N/A")}', 'normal'))
            hw_layout.addWidget(StyledLabel(f'Модель: {hw_info.get("product_name", "N/A")}', 'normal'))
            hw_layout.addWidget(StyledLabel(f'Версия: {hw_info.get("product_version", "N/A")}', 'normal'))
            hw_layout.addWidget(StyledLabel(f'Плата: {hw_info.get("board_name", "N/A")}', 'normal'))
            hw_layout.addWidget(StyledLabel(f'BIOS: {hw_info.get("bios_vendor", "N/A")} {hw_info.get("bios_version", "N/A")}', 'normal'))
            hw_layout.addWidget(StyledLabel(f'CPU: {hw_info.get("cpu_model", "N/A")}', 'normal'))
            hw_layout.addWidget(StyledLabel(f'Память: {hw_info.get("total_memory", "N/A")}', 'normal'))
            hw_layout.addWidget(StyledLabel(f'Серийный номер: {sys_info.get_serial_number()}', 'normal'))
            
            hw_card.add_layout(hw_layout)
            layout.addWidget(hw_card)
            
            # BIOS
            bios_card = CardWidget(t('bios'))
            bios_layout = QVBoxLayout()
            
            bios_info = sys_info.get_bios_info()
            bios_layout.addWidget(StyledLabel(f'Производитель: {bios_info.get("vendor", "N/A")}', 'normal'))
            bios_layout.addWidget(StyledLabel(f'Версия: {bios_info.get("version", "N/A")}', 'normal'))
            bios_layout.addWidget(StyledLabel(f'Дата: {bios_info.get("release_date", "N/A")}', 'normal'))
            bios_layout.addWidget(StyledLabel(f'Ревизия: {bios_info.get("revision", "N/A")}', 'normal'))
            
            bios_card.add_layout(bios_layout)
            layout.addWidget(bios_card)
            
            # Сеть
            network_card = CardWidget(t('network'))
            network_layout = QVBoxLayout()
            
            try:
                import socket
                hostname = socket.gethostname()
                ip_address = socket.gethostbyname(hostname)
                network_layout.addWidget(StyledLabel(f'Имя хоста: {hostname}', 'normal'))
                network_layout.addWidget(StyledLabel(f'IP адрес: {ip_address}', 'normal'))
            except Exception:
                network_layout.addWidget(StyledLabel('Информация недоступна', 'normal'))
            
            network_card.add_layout(network_layout)
            layout.addWidget(network_card)
            
            # Окружение
            env_card = CardWidget(t('environment'))
            env_layout = QVBoxLayout()
            
            env_info = sys_info.get_environment_info()
            env_layout.addWidget(StyledLabel(f'Десктоп: {env_info.get("desktop_environment", "N/A")}', 'normal'))
            env_layout.addWidget(StyledLabel(f'Дисплей: {env_info.get("display_server", "N/A")}', 'normal'))
            env_layout.addWidget(StyledLabel(f'Shell: {env_info.get("shell", "N/A")}', 'normal'))
            env_layout.addWidget(StyledLabel(f'Window Manager: {env_info.get("window_manager", "N/A")}', 'normal'))
            
            env_card.add_layout(env_layout)
            layout.addWidget(env_card)
            
            # Загрузчики
            boot_card = CardWidget(t('bootloaders'))
            boot_layout = QVBoxLayout()
            
            bootloaders = sys_info.get_bootloaders()
            if bootloaders:
                for bl in bootloaders:
                    status = " (активен)" if bl.get('active', False) else ""
                    boot_layout.addWidget(StyledLabel(f'{bl.get("name", "N/A")}: {bl.get("path", "N/A")}{status}', 'normal'))
            else:
                boot_layout.addWidget(StyledLabel('Не найдены', 'normal'))
            
            boot_card.add_layout(boot_layout)
            layout.addWidget(boot_card)
            
            # Установленные ОС
            os_list_card = CardWidget(t('installed_os'))
            os_list_layout = QVBoxLayout()
            
            installed_os = sys_info.get_installed_os()
            if installed_os:
                for os_name in installed_os:
                    os_list_layout.addWidget(StyledLabel(os_name, 'normal'))
            else:
                os_list_layout.addWidget(StyledLabel('Не найдены', 'normal'))
            
            os_list_card.add_layout(os_list_layout)
            layout.addWidget(os_list_card)
            
            # Драйверы (первые 20)
            drivers_card = CardWidget(t('drivers_first_20'))
            drivers_layout = QVBoxLayout()
            
            drivers = sys_info.get_drivers()[:20]
            if drivers:
                for driver in drivers:
                    drivers_layout.addWidget(StyledLabel(driver, 'normal'))
            else:
                drivers_layout.addWidget(StyledLabel('Не найдены', 'normal'))
            
            drivers_card.add_layout(drivers_layout)
            layout.addWidget(drivers_card)
            
        except ImportError:
            error_label = StyledLabel('Модуль системной информации недоступен', 'normal')
            layout.addWidget(error_label)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('refresh'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        refresh_button.clicked.connect(lambda: self.refresh_system_info_tab(scroll))
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def refresh_system_info_tab(self, scroll):
        """Обновить вкладку с информацией о системе"""
        # Заменяем виджет новым
        new_tab = self.create_system_info_tab()
        scroll.setWidget(new_tab)
    
    def create_drivers_tab(self) -> QWidget:
        """Создать вкладку драйверов"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('drivers'), 'subtitle')
        layout.addWidget(title_label)
        
        # Загружаем драйверы
        try:
            from system_info_lib import SystemInfo
            sys_info = SystemInfo()
            
            drivers = sys_info.get_drivers()
            
            # Карточка с информацией о драйверах
            drivers_card = CardWidget('Загруженные модули ядра')
            drivers_layout = QVBoxLayout()
            
            # Таблица драйверов
            self.drivers_table = QTableWidget()
            self.drivers_table.setColumnCount(3)
            self.drivers_table.setHorizontalHeaderLabels(['Модуль', 'Размер', 'Статус'])
            self.drivers_table.setStyleSheet(TableStyle.get_dark_style())
            
            header = self.drivers_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            
            # Заполняем драйверы
            for i, driver in enumerate(drivers[:100]):  # Показываем первые 100
                row = self.drivers_table.rowCount()
                self.drivers_table.insertRow(row)
                
                self.drivers_table.setItem(row, 0, QTableWidgetItem(driver))
                self.drivers_table.setItem(row, 1, QTableWidgetItem('N/A'))
                
                # Проверяем статус (загружен/выгружен)
                status_item = QTableWidgetItem('Загружен')
                status_item.setBackground(GUITheme.ACCENT_SUCCESS)
                self.drivers_table.setItem(row, 2, status_item)
            
            drivers_layout.addWidget(self.drivers_table)
            drivers_card.add_layout(drivers_layout)
            layout.addWidget(drivers_card)
            
            # Информация о проверке обновлений
            update_card = CardWidget('Проверка обновлений')
            update_layout = QVBoxLayout()
            
            update_info = StyledLabel('Для проверки обновлений драйверов используйте:', 'normal')
            update_layout.addWidget(update_info)
            update_layout.addWidget(StyledLabel('  - sudo apt update && sudo apt upgrade (Ubuntu/Debian)', 'normal'))
            update_layout.addWidget(StyledLabel('  - sudo pacman -Syu (Arch Linux)', 'normal'))
            update_layout.addWidget(StyledLabel('  - NVIDIA: sudo apt install nvidia-driver (Ubuntu)', 'normal'))
            
            update_card.add_layout(update_layout)
            layout.addWidget(update_card)
            
        except ImportError:
            error_label = StyledLabel('Модуль системной информации недоступен', 'normal')
            layout.addWidget(error_label)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('refresh'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        refresh_button.clicked.connect(lambda: self.refresh_drivers_tab(scroll))
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def refresh_drivers_tab(self, scroll):
        """Обновить вкладку драйверов"""
        new_tab = self.create_drivers_tab()
        scroll.setWidget(new_tab)
    
    def create_distros_tab(self) -> QWidget:
        """Создать вкладку дистрибутивов"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('distro_analysis'), 'subtitle')
        layout.addWidget(title_label)
        
        # Текущий дистрибутив
        try:
            from distro_analyzer import DistroAnalyzer
            analyzer = DistroAnalyzer()
            
            current_card = CardWidget(t('current_distro'))
            current_layout = QVBoxLayout()
            
            current = analyzer.current_distro
            current_layout.addWidget(StyledLabel(f'Название: {current.get("name", "N/A")}', 'normal'))
            current_layout.addWidget(StyledLabel(f'Версия: {current.get("version", "N/A")}', 'normal'))
            current_layout.addWidget(StyledLabel(f'ID: {current.get("id", "N/A")}', 'normal'))
            current_layout.addWidget(StyledLabel(f'ID_LIKE: {current.get("id_like", "N/A")}', 'normal'))
            
            current_card.add_layout(current_layout)
            layout.addWidget(current_card)
            
            # Рекомендации
            recs_card = CardWidget(t('recommended_distros'))
            recs_layout = QVBoxLayout()
            
            recommendations = analyzer.get_recommended_distros()
            for rec in recommendations:
                rec_label = StyledLabel(f'{rec["name"]} - {rec["score"]}/100', 'subtitle')
                recs_layout.addWidget(rec_label)
                recs_layout.addWidget(StyledLabel(rec["description"], 'normal'))
                recs_layout.addWidget(StyledLabel(f'Плюсы: {rec["pros"]}', 'normal'))
                recs_layout.addWidget(StyledLabel(f'Минусы: {rec["cons"]}', 'normal'))
                recs_layout.addWidget(Separator())
            
            recs_card.add_layout(recs_layout)
            layout.addWidget(recs_card)
            
        except ImportError:
            error_label = StyledLabel('Модуль анализатора дистрибутивов недоступен', 'normal')
            layout.addWidget(error_label)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('refresh'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        refresh_button.clicked.connect(lambda: self.refresh_distros_tab(scroll))
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def refresh_distros_tab(self, scroll):
        """Обновить вкладку дистрибутивов"""
        new_tab = self.create_distros_tab()
        scroll.setWidget(new_tab)
    
    def create_devices_tab(self) -> QWidget:
        """Создать вкладку устройств"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('connected_devices'), 'subtitle')
        layout.addWidget(title_label)
        
        # Загружаем устройства
        try:
            from device_analyzer import DeviceAnalyzer
            analyzer = DeviceAnalyzer()
            
            all_devices = analyzer.get_all_devices()
            summary = analyzer.get_device_summary()
            
            # Сводка
            summary_card = CardWidget(t('summary'))
            summary_layout = QVBoxLayout()
            summary_layout.addWidget(StyledLabel(f'USB устройств: {summary["usb_count"]}', 'normal'))
            summary_layout.addWidget(StyledLabel(f'PCI устройств: {summary["pci_count"]}', 'normal'))
            summary_layout.addWidget(StyledLabel(f'Устройств ввода: {summary["input_count"]}', 'normal'))
            summary_layout.addWidget(StyledLabel(f'Всего: {summary["total"]}', 'normal'))
            summary_card.add_layout(summary_layout)
            layout.addWidget(summary_card)
            
            # USB устройства
            if all_devices['usb']:
                usb_card = CardWidget(t('usb_devices'))
                usb_layout = QVBoxLayout()
                
                for device in all_devices['usb'][:10]:  # Показываем первые 10
                    usb_layout.addWidget(StyledLabel(f'{device["description"]}', 'normal'))
                    usb_layout.addWidget(StyledLabel(f'ID: {device["id"]}', 'small'))
                    usb_layout.addWidget(Separator())
                
                usb_card.add_layout(usb_layout)
                layout.addWidget(usb_card)
            
            # PCI устройства
            if all_devices['pci']:
                pci_card = CardWidget(t('pci_devices'))
                pci_layout = QVBoxLayout()
                
                for device in all_devices['pci'][:10]:  # Показываем первые 10
                    pci_layout.addWidget(StyledLabel(f'{device["description"]}', 'normal'))
                    pci_layout.addWidget(Separator())
                
                pci_card.add_layout(pci_layout)
                layout.addWidget(pci_card)
            
        except ImportError:
            error_label = StyledLabel('Модуль анализатора устройств недоступен', 'normal')
            layout.addWidget(error_label)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('refresh'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        refresh_button.clicked.connect(lambda: self.refresh_devices_tab(scroll))
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def refresh_devices_tab(self, scroll):
        """Обновить вкладку устройств"""
        new_tab = self.create_devices_tab()
        scroll.setWidget(new_tab)
    
    def create_ports_tab(self) -> QWidget:
        """Создать вкладку портов и гнезд"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('port_analysis'), 'subtitle')
        layout.addWidget(title_label)
        
        # Загружаем информацию о портах
        try:
            from device_analyzer import DeviceAnalyzer
            analyzer = DeviceAnalyzer()
            port_info = analyzer.get_port_info()
            
            # Тип устройства
            type_card = CardWidget(t('device_type'))
            type_layout = QVBoxLayout()
            
            chassis_type = port_info['chassis_type']
            if chassis_type == 'laptop':
                type_text = f'{t("laptop")} ✓'
                type_color = '#4caf50'
            elif chassis_type == 'desktop':
                type_text = f'{t("desktop")}'
                type_color = '#2196f3'
            else:
                type_text = f'{t("unknown_type")}'
                type_color = '#ff9800'
            
            type_label = StyledLabel(type_text, 'normal')
            type_label.setStyleSheet(f"color: {type_color}; font-weight: bold; font-size: 16px;")
            type_layout.addWidget(type_label)
            
            if port_info['is_laptop']:
                type_layout.addWidget(StyledLabel(t('laptop_detected'), 'small'))
            else:
                type_layout.addWidget(StyledLabel(t('desktop_detected'), 'small'))
            
            type_card.add_layout(type_layout)
            layout.addWidget(type_card)
            
            # Состояние портов
            status_card = CardWidget(t('port_status'))
            status_layout = QVBoxLayout()
            
            # HDMI
            hdmi_text = f'{t("hdmi_port")}: {t("present") if port_info["has_hdmi"] else t("absent")}'
            hdmi_color = '#4caf50' if port_info['has_hdmi'] else '#f44336'
            hdmi_label = StyledLabel(hdmi_text, 'normal')
            hdmi_label.setStyleSheet(f"color: {hdmi_color};")
            status_layout.addWidget(hdmi_label)
            
            # USB-C
            usbc_text = f'{t("usb_c_port")}: {t("present") if port_info["has_usb_c"] else t("absent")}'
            usbc_color = '#4caf50' if port_info['has_usb_c'] else '#f44336'
            usbc_label = StyledLabel(usbc_text, 'normal')
            usbc_label.setStyleSheet(f"color: {usbc_color};")
            status_layout.addWidget(usbc_label)
            
            # USB-A
            usba_text = f'{t("usb_a_port")}: {t("present") if port_info["has_usb_a"] else t("absent")}'
            usba_color = '#4caf50' if port_info['has_usb_a'] else '#f44336'
            usba_label = StyledLabel(usba_text, 'normal')
            usba_label.setStyleSheet(f"color: {usba_color};")
            status_layout.addWidget(usba_label)
            
            # Ethernet
            eth_text = f'{t("ethernet_port")}: {t("present") if port_info["has_ethernet"] else t("absent")}'
            eth_color = '#4caf50' if port_info['has_ethernet'] else '#f44336'
            eth_label = StyledLabel(eth_text, 'normal')
            eth_label.setStyleSheet(f"color: {eth_color};")
            status_layout.addWidget(eth_label)
            
            # Audio Jack
            audio_text = f'{t("audio_jack")}: {t("present") if port_info["has_audio_jack"] else t("absent")}'
            audio_color = '#4caf50' if port_info['has_audio_jack'] else '#f44336'
            audio_label = StyledLabel(audio_text, 'normal')
            audio_label.setStyleSheet(f"color: {audio_color};")
            status_layout.addWidget(audio_label)
            
            # SD Card
            sd_text = f'{t("sd_card_slot")}: {t("present") if port_info["has_sd_card"] else t("absent")}'
            sd_color = '#4caf50' if port_info['has_sd_card'] else '#f44336'
            sd_label = StyledLabel(sd_text, 'normal')
            sd_label.setStyleSheet(f"color: {sd_color};")
            status_layout.addWidget(sd_label)
            
            status_card.add_layout(status_layout)
            layout.addWidget(status_card)
            
            # Анализ состояния
            health_card = CardWidget(t('port_health'))
            health_layout = QVBoxLayout()
            
            # Подсчитываем количество проблем
            issues = 0
            if not port_info['has_usb_a']: issues += 1
            if port_info['is_laptop'] and not port_info['has_hdmi']: issues += 1
            if port_info['is_laptop'] and not port_info['has_audio_jack']: issues += 1
            
            if issues == 0:
                health_text = t('all_ports_ok')
                health_color = '#4caf50'
            else:
                health_text = f'{t("some_ports_issues")} ({issues})'
                health_color = '#ff9800'
            
            health_label = StyledLabel(health_text, 'normal')
            health_label.setStyleSheet(f"color: {health_color}; font-weight: bold; font-size: 16px;")
            health_layout.addWidget(health_label)
            
            health_card.add_layout(health_layout)
            layout.addWidget(health_card)
            
            # Рекомендации
            if issues > 0:
                recommendations_card = CardWidget(t('recommendations'))
                rec_layout = QVBoxLayout()
                
                if not port_info['has_usb_a']:
                    rec_layout.addWidget(StyledLabel(t('usb_a_absent'), 'small'))
                if port_info['is_laptop'] and not port_info['has_hdmi']:
                    rec_layout.addWidget(StyledLabel(t('laptop_hdmi_recommended'), 'small'))
                if port_info['is_laptop'] and not port_info['has_audio_jack']:
                    rec_layout.addWidget(StyledLabel(t('laptop_audio_recommended'), 'small'))
                
                recommendations_card.add_layout(rec_layout)
                layout.addWidget(recommendations_card)
            
        except ImportError:
            error_label = StyledLabel('Модуль анализа портов недоступен', 'normal')
            layout.addWidget(error_label)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('port_check'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        refresh_button.clicked.connect(lambda: self.refresh_ports_tab(scroll))
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def refresh_ports_tab(self, scroll):
        """Обновить вкладку портов"""
        new_tab = self.create_ports_tab()
        scroll.setWidget(new_tab)
    
    def create_monitors_tab(self) -> QWidget:
        """Создать вкладку мониторов"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('monitor_analysis'), 'subtitle')
        layout.addWidget(title_label)
        
        # Загружаем информацию о мониторах
        try:
            from monitor_analyzer import MonitorAnalyzer
            analyzer = MonitorAnalyzer()
            monitors = analyzer.get_monitors()
            
            if not monitors:
                no_monitors_label = StyledLabel(t('no_monitors'), 'normal')
                layout.addWidget(no_monitors_label)
            else:
                # Показываем каждый монитор
                for monitor in monitors:
                    # Карточка монитора
                    monitor_card = CardWidget(monitor.get('name', 'Unknown'))
                    monitor_layout = QVBoxLayout()
                    
                    # Основная информация
                    monitor_layout.addWidget(StyledLabel(f'{t("monitor_name")}: {monitor.get("name", "N/A")}', 'normal'))
                    monitor_layout.addWidget(StyledLabel(f'{t("monitor_model")}: {monitor.get("model", "N/A")}', 'normal'))
                    monitor_layout.addWidget(StyledLabel(f'{t("monitor_manufacturer")}: {monitor.get("manufacturer", "N/A")}', 'normal'))
                    monitor_layout.addWidget(StyledLabel(f'{t("monitor_connection")}: {monitor.get("connection", "N/A")}', 'normal'))
                    
                    # Разрешение
                    width = monitor.get('width', 0)
                    height = monitor.get('height', 0)
                    if width > 0 and height > 0:
                        monitor_layout.addWidget(StyledLabel(f'{t("monitor_resolution")}: {width}x{height}', 'normal'))
                    
                    # Частота обновления
                    refresh_rate = monitor.get('refresh_rate', 0)
                    if refresh_rate > 0:
                        monitor_layout.addWidget(StyledLabel(f'{t("monitor_refresh")}: {refresh_rate} Hz', 'normal'))
                    
                    # Статус
                    status_text = monitor.get('status', 'Unknown')
                    if monitor.get('is_primary'):
                        status_text += f' ({t("primary_monitor")})'
                    monitor_layout.addWidget(StyledLabel(f'{t("monitor_status")}: {status_text}', 'normal'))
                    
                    # Проверка здоровья
                    health = analyzer.check_monitor_health(monitor)
                    
                    # Оценка здоровья
                    health_score = health.get('health_score', 0)
                    health_color = '#4caf50' if health_score >= 80 else '#ff9800' if health_score >= 60 else '#f44336'
                    health_label = StyledLabel(f'{t("monitor_score")}: {health_score}/100', 'normal')
                    health_label.setStyleSheet(f"color: {health_color}; font-weight: bold;")
                    monitor_layout.addWidget(health_label)
                    
                    # Общий статус
                    overall_status = health.get('overall_status', 'Unknown')
                    monitor_layout.addWidget(StyledLabel(f'{t("monitor_health")}: {overall_status}', 'normal'))
                    
                    # Проблемы
                    issues = health.get('issues', [])
                    if issues:
                        issues_card = CardWidget(t('monitor_issues'))
                        issues_layout = QVBoxLayout()
                        for issue in issues:
                            issues_layout.addWidget(StyledLabel(f'• {issue}', 'small'))
                        issues_card.add_layout(issues_layout)
                        monitor_layout.addWidget(issues_card)
                    
                    monitor_card.add_layout(monitor_layout)
                    layout.addWidget(monitor_card)
                    
        except ImportError:
            error_label = StyledLabel('Модуль анализа мониторов недоступен', 'normal')
            layout.addWidget(error_label)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('monitor_check'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        refresh_button.clicked.connect(lambda: self.refresh_monitors_tab(scroll))
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def refresh_monitors_tab(self, scroll):
        """Обновить вкладку мониторов"""
        new_tab = self.create_monitors_tab()
        scroll.setWidget(new_tab)
    
    def create_cpu_rating_tab(self) -> QWidget:
        """Создать вкладку с оценкой процессора"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('cpu_rating'), 'subtitle')
        layout.addWidget(title_label)
        
        # Загружаем информацию о CPU
        try:
            from hardware_rater import HardwareRater
            cpu_info = HardwareRater.get_cpu_info()
            rating = cpu_info['rating']
            
            # Карточка с оценкой
            rating_card = CardWidget(t('performance_rating'))
            rating_layout = QVBoxLayout()
            
            # Название CPU
            rating_layout.addWidget(StyledLabel(f'Модель: {cpu_info["name"]}', 'subtitle'))
            rating_layout.addWidget(Separator())
            
            # Оценка
            score_label = StyledLabel(f'{t("score")}: {rating["score"]}/100', 'subtitle')
            rating_layout.addWidget(score_label)
            
            # Категория оценки
            rating_text = rating['rating']
            if rating_text == 'Отлично':
                color = '#4caf50'
            elif rating_text == 'Очень хорошо':
                color = '#8bc34a'
            elif rating_text == 'Хорошо':
                color = '#ffeb3b'
            elif rating_text == 'Средне':
                color = '#ff9800'
            elif rating_text == 'Ниже среднего':
                color = '#ff5722'
            elif rating_text == 'Слабо':
                color = '#f44336'
            else:
                color = '#9e9e9e'
            
            rating_desc = StyledLabel(f'{t("category")}: {rating_text}', 'normal')
            rating_desc.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 16px;")
            rating_layout.addWidget(rating_desc)
            
            # Категория оборудования
            category_text = self._get_category_translation(rating['category'])
            category_label = StyledLabel(f'{t("category")}: {category_text}', 'normal')
            rating_layout.addWidget(category_label)
            
            # Если это оценка по характеристикам
            if rating.get('estimated', False):
                est_label = StyledLabel(f'({t("estimated")})', 'small')
                est_label.setStyleSheet("color: #ff9800;")
                rating_layout.addWidget(est_label)
            
            rating_card.add_layout(rating_layout)
            layout.addWidget(rating_card)
            
            # Детальная информация
            info_card = CardWidget(t('cpu_info'))
            info_layout = QVBoxLayout()
            
            info_layout.addWidget(StyledLabel(f'{t("cores")}: {cpu_info["cores"]}', 'normal'))
            info_layout.addWidget(StyledLabel(f'{t("frequency")}: {cpu_info["frequency"]:.2f} GHz', 'normal'))
            info_layout.addWidget(StyledLabel(f'{t("architecture")}: {cpu_info["architecture"]}', 'normal'))
            
            info_card.add_layout(info_layout)
            layout.addWidget(info_card)
            
        except ImportError:
            error_label = StyledLabel('Модуль оценки оборудования недоступен', 'normal')
            layout.addWidget(error_label)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('refresh'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        refresh_button.clicked.connect(lambda: self.refresh_cpu_rating_tab(scroll))
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def refresh_cpu_rating_tab(self, scroll):
        """Обновить вкладку оценки CPU"""
        new_tab = self.create_cpu_rating_tab()
        scroll.setWidget(new_tab)
    
    def create_gpu_rating_tab(self) -> QWidget:
        """Создать вкладку с оценкой видеокарты"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('gpu_rating'), 'subtitle')
        layout.addWidget(title_label)
        
        # Загружаем информацию о GPU
        try:
            from hardware_rater import HardwareRater
            gpus = HardwareRater.get_gpu_info()
            
            for i, gpu_info in enumerate(gpus):
                rating = gpu_info['rating']
                
                # Карточка с оценкой
                rating_card = CardWidget(f'GPU {i + 1}')
                rating_layout = QVBoxLayout()
                
                # Название GPU
                rating_layout.addWidget(StyledLabel(f'Модель: {gpu_info["name"]}', 'subtitle'))
                rating_layout.addWidget(Separator())
                
                # Оценка
                score_label = StyledLabel(f'{t("score")}: {rating["score"]}/100', 'subtitle')
                rating_layout.addWidget(score_label)
                
                # Категория оценки
                rating_text = rating['rating']
                if rating_text == 'Отлично':
                    color = '#4caf50'
                elif rating_text == 'Очень хорошо':
                    color = '#8bc34a'
                elif rating_text == 'Хорошо':
                    color = '#ffeb3b'
                elif rating_text == 'Средне':
                    color = '#ff9800'
                elif rating_text == 'Ниже среднего':
                    color = '#ff5722'
                elif rating_text == 'Слабо':
                    color = '#f44336'
                else:
                    color = '#9e9e9e'
                
                rating_desc = StyledLabel(f'{t("category")}: {rating_text}', 'normal')
                rating_desc.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 16px;")
                rating_layout.addWidget(rating_desc)
                
                # Категория оборудования
                category_text = self._get_category_translation(rating['category'])
                category_label = StyledLabel(f'{t("category")}: {category_text}', 'normal')
                rating_layout.addWidget(category_label)
                
                # Если это оценка по характеристикам
                if rating.get('estimated', False):
                    est_label = StyledLabel(f'({t("estimated")})', 'small')
                    est_label.setStyleSheet("color: #ff9800;")
                    rating_layout.addWidget(est_label)
                
                rating_card.add_layout(rating_layout)
                layout.addWidget(rating_card)
                
                # Детальная информация
                info_card = CardWidget(t('gpu_info'))
                info_layout = QVBoxLayout()
                
                vram_gb = gpu_info['vram'] // 1024 if gpu_info['vram'] > 1024 else gpu_info['vram']
                vram_unit = 'GB' if gpu_info['vram'] > 1024 else 'MB'
                info_layout.addWidget(StyledLabel(f'{t("vram")}: {vram_gb} {vram_unit}', 'normal'))
                
                # Тип видеокарты
                gpu_type = t('integrated') if gpu_info.get('is_integrated', False) else t('discrete')
                info_layout.addWidget(StyledLabel(f'Тип: {gpu_type}', 'normal'))
                
                info_card.add_layout(info_layout)
                layout.addWidget(info_card)
                
                layout.addWidget(Separator())
            
        except ImportError:
            error_label = StyledLabel('Модуль оценки оборудования недоступен', 'normal')
            layout.addWidget(error_label)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('refresh'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        refresh_button.clicked.connect(lambda: self.refresh_gpu_rating_tab(scroll))
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def refresh_gpu_rating_tab(self, scroll):
        """Обновить вкладку оценки GPU"""
        new_tab = self.create_gpu_rating_tab()
        scroll.setWidget(new_tab)
    
    def _get_category_translation(self, category: str) -> str:
        """Получить перевод категории"""
        translations = {
            'flagship': t('flagship'),
            'high_end': t('high_end'),
            'mid_range': t('mid_range'),
            'entry_level': t('entry_level'),
            'budget': t('budget'),
            'unknown': t('unknown')
        }
        return translations.get(category, category)
    
    def create_helper_tab(self) -> QWidget:
        """Создать вкладку помощника"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = StyledLabel(t('web_helper'), 'subtitle')
        layout.addWidget(title_label)
        
        # Общие ресурсы
        general_card = CardWidget(t('general_resources'))
        general_layout = QVBoxLayout()
        
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'helpers', 'python'))
            from web_helper import WebHelper
            
            general_resources = WebHelper.GENERAL_RESOURCES
            for name, url in general_resources.items():
                btn = QPushButton(name)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a40;
                        color: #c0c0c0;
                        border: 1px solid #4a4a50;
                        padding: 8px;
                        border-radius: 5px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #4285f4;
                        color: white;
                    }
                """)
                btn.clicked.connect(lambda checked, u=url: WebHelper.open_url(u))
                general_layout.addWidget(btn)
            
        except ImportError:
            error_label = StyledLabel('Модуль веб-помощника недоступен', 'normal')
            general_layout.addWidget(error_label)
        
        general_card.add_layout(general_layout)
        layout.addWidget(general_card)
        
        # Ресурсы по железу
        hw_card = CardWidget(t('hardware_resources'))
        hw_layout = QVBoxLayout()
        
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'helpers', 'python'))
            from web_helper import WebHelper
            
            hw_resources = WebHelper.get_hardware_resources()
            for name, url in hw_resources.items():
                btn = QPushButton(name)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a40;
                        color: #c0c0c0;
                        border: 1px solid #4a4a50;
                        padding: 8px;
                        border-radius: 5px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #4285f4;
                        color: white;
                    }
                """)
                btn.clicked.connect(lambda checked, u=url: WebHelper.open_url(u))
                hw_layout.addWidget(btn)
            
        except ImportError:
            pass
        
        hw_card.add_layout(hw_layout)
        layout.addWidget(hw_card)
        
        # Ресурсы по драйверам
        drivers_card = CardWidget(t('driver_resources'))
        drivers_layout = QVBoxLayout()
        
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'helpers', 'python'))
            from web_helper import WebHelper
            
            driver_resources = WebHelper.get_driver_resources()
            for name, url in driver_resources.items():
                btn = QPushButton(name)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a40;
                        color: #c0c0c0;
                        border: 1px solid #4a4a50;
                        padding: 8px;
                        border-radius: 5px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #4285f4;
                        color: white;
                    }
                """)
                btn.clicked.connect(lambda checked, u=url: WebHelper.open_url(u))
                drivers_layout.addWidget(btn)
            
        except ImportError:
            pass
        
        drivers_card.add_layout(drivers_layout)
        layout.addWidget(drivers_card)
        
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def create_processes_tab(self) -> QWidget:
        """Создать вкладку процессов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок и сортировка
        header_layout = QHBoxLayout()
        self.process_title_label = StyledLabel(f'{t("top_processes")} - {self.settings["process_count"]}', 'subtitle')
        header_layout.addWidget(self.process_title_label)
        header_layout.addStretch()
        
        # Кнопки сортировки
        sort_cpu_button = QPushButton(t('sort_by_cpu'))
        sort_cpu_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        sort_cpu_button.clicked.connect(lambda: self.update_processes('cpu'))
        header_layout.addWidget(sort_cpu_button)
        
        sort_ram_button = QPushButton(t('sort_by_ram'))
        sort_ram_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        sort_ram_button.clicked.connect(lambda: self.update_processes('ram'))
        header_layout.addWidget(sort_ram_button)
        
        layout.addLayout(header_layout)
        
        # Таблица процессов
        self.processes_table = QTableWidget()
        self.processes_table.setColumnCount(4)
        self.processes_table.setHorizontalHeaderLabels([t('pid'), t('name'), 'CPU %', 'RAM %'])
        self.processes_table.setStyleSheet(TableStyle.get_dark_style())
        
        # Настройка ширины колонок
        header = self.processes_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Сортировка по клику на заголовок
        header.sectionClicked.connect(self.sort_by_column)
        
        layout.addWidget(self.processes_table)
        
        # Кнопка обновления
        refresh_button = QPushButton(t('refresh'))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
            QPushButton:pressed {
                background-color: #2850a0;
            }
        """)
        refresh_button.clicked.connect(lambda: self.update_processes('cpu'))
        layout.addWidget(refresh_button)
        
        return widget
    
    def update_system_data(self, data: Dict[str, Any]):
        """Обновить данные системы"""
        # CPU
        cpu = data['cpu']
        self.cpu_label.setText(f'{t("usage")}: {cpu:.1f}%')
        self.cpu_bar.setValue(int(cpu))
        
        # Цвет CPU в зависимости от нагрузки
        if cpu > 80:
            self.cpu_bar.setStyleSheet(ProgressBarStyle.get_style(GUITheme.ACCENT_ERROR))
            self.status_indicator.set_status('error')
        elif cpu > 50:
            self.cpu_bar.setStyleSheet(ProgressBarStyle.get_style(GUITheme.ACCENT_WARNING))
            self.status_indicator.set_status('warning')
        else:
            self.cpu_bar.setStyleSheet(ProgressBarStyle.get_style(GUITheme.ACCENT_SUCCESS))
            self.status_indicator.set_status('success')
        
        # Память
        mem = data['memory']
        self.memory_label.setText(
            f'{t("usage")}: {mem["used"]:.2f} GB / {mem["total"]:.2f} GB ({mem["percent"]:.1f}%)'
        )
        self.memory_bar.setValue(int(mem['percent']))
        
        # Диск
        disk = data['disk']
        self.disk_label.setText(f'{t("usage")}: {disk:.1f}%')
        self.disk_bar.setValue(int(disk))
        
        # Сеть
        net = data['network']
        self.network_sent_label.setText(f'{t("sent")}: {net["sent"]:.2f} MB')
        self.network_recv_label.setText(f'{t("received")}: {net["recv"]:.2f} MB')
    
    def update_processes(self, sort_by: str = 'cpu'):
        """Обновить таблицу процессов"""
        self.processes_table.setRowCount(0)
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'] or 0,
                    'memory': proc.info['memory_percent'] or 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Сортировка
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu'], reverse=True)
        elif sort_by == 'ram':
            processes.sort(key=lambda x: x['memory'], reverse=True)
        
        # Отображение процессов согласно настройкам
        process_count = self.settings['process_count']
        for i, proc in enumerate(processes[:process_count]):
            self.processes_table.insertRow(i)
            self.processes_table.setItem(i, 0, QTableWidgetItem(str(proc['pid'])))
            self.processes_table.setItem(i, 1, QTableWidgetItem(proc['name']))
            self.processes_table.setItem(i, 2, QTableWidgetItem(f'{proc["cpu"]:.1f}%'))
            self.processes_table.setItem(i, 3, QTableWidgetItem(f'{proc["memory"]:.1f}%'))
            
            # Подсветка процессов с высокой нагрузкой
            if proc['cpu'] > 50:
                self.processes_table.item(i, 2).setBackground(GUITheme.ACCENT_WARNING)
            if proc['cpu'] > 80:
                self.processes_table.item(i, 2).setBackground(GUITheme.ACCENT_ERROR)
            
            if proc['memory'] > 50:
                self.processes_table.item(i, 3).setBackground(GUITheme.ACCENT_WARNING)
            if proc['memory'] > 80:
                self.processes_table.item(i, 3).setBackground(GUITheme.ACCENT_ERROR)
    
    def sort_by_column(self, column: int):
        """Сортировка по клику на колонку"""
        if column == 2:  # CPU
            self.update_processes('cpu')
        elif column == 3:  # RAM
            self.update_processes('ram')
    
    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        self.fire_background.setGeometry(self.rect())
        super().resizeEvent(event)
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        print("Closing application...")
        
        # Останавливаем worker
        if hasattr(self, 'worker') and self.worker:
            self.worker.stop()
        
        # Останавливаем фоновую анимацию
        if hasattr(self, 'fire_background'):
            self.fire_background.stop()
        
        event.accept()
        QApplication.quit()
    
    def open_settings(self):
        """Открыть диалог настроек"""
        dialog = SettingsDialog(self, self.settings)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings = dialog.get_settings()
            self.apply_settings()
    
    def apply_settings(self):
        """Применить настройки"""
        # Показать/скрыть огонь
        if self.settings['fire_enabled']:
            self.fire_background.show()
        else:
            self.fire_background.hide()
        
        # Обновить интервал
        self.worker.interval = self.settings['interval']
        
        # Изменить язык
        new_lang = self.settings['language']
        if new_lang != get_current_language():
            set_language(new_lang)
            # Пересоздаем интерфейс с новым языком
            self.rebuild_ui()
        
        # Обновить количество процессов
        if hasattr(self, 'process_title_label'):
            self.process_title_label.setText(f'{t("top_processes")} - {self.settings["process_count"]}')
        
        # Обновить таблицу процессов
        self.update_processes()
        
        # Обновить интервал (это потребует изменения в worker)
        print(f"Настройки применены: {self.settings}")
    
    def rebuild_ui(self):
        """Пересоздать интерфейс с новым языком"""
        self.setWindowTitle('VitalSign')
        
        # Останавливаем старый фон с огнем
        if hasattr(self, 'fire_background'):
            self.fire_background.stop()
            self.fire_background.deleteLater()
        
        # Пересоздаем интерфейс полностью
        central_widget = self.centralWidget()
        if central_widget:
            central_widget.deleteLater()
        
        self.init_ui()
        self.worker.data_updated.connect(self.update_system_data)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('VitalSign')
    
    window = VitalSignGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
