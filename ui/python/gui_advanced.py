#!/usr/bin/env python3
"""
VitalSign GUI Advanced - Расширенный графический интерфейс с графиками и историей
"""

import sys
import psutil
import numpy as np
from collections import deque
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QProgressBar, QGroupBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QTabWidget, QFrame, QGridLayout, QPushButton,
                             QComboBox, QSpinBox, QFileDialog)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from typing import Dict, Any, List


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


class HistoryData:
    """Класс для хранения истории данных"""
    
    def __init__(self, max_length: int = 60):
        self.max_length = max_length
        self.cpu_history = deque(maxlen=max_length)
        self.memory_history = deque(maxlen=max_length)
        self.disk_history = deque(maxlen=max_length)
        self.network_sent_history = deque(maxlen=max_length)
        self.network_recv_history = deque(maxlen=max_length)
        self.timestamps = deque(maxlen=max_length)
    
    def add_data(self, data: Dict[str, Any]):
        """Добавить данные в историю"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        self.cpu_history.append(data['cpu'])
        self.memory_history.append(data['memory']['percent'])
        self.disk_history.append(data['disk'])
        self.network_sent_history.append(data['network']['sent'])
        self.network_recv_history.append(data['network']['recv'])
        self.timestamps.append(timestamp)
    
    def get_cpu_data(self) -> tuple:
        """Получить данные CPU для графика"""
        return list(self.timestamps), list(self.cpu_history)
    
    def get_memory_data(self) -> tuple:
        """Получить данные памяти для графика"""
        return list(self.timestamps), list(self.memory_history)
    
    def export_to_csv(self, filename: str):
        """Экспортировать историю в CSV"""
        import csv
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'CPU %', 'Memory %', 'Disk %', 'Network Sent MB', 'Network Recv MB'])
            for i in range(len(self.timestamps)):
                writer.writerow([
                    self.timestamps[i],
                    self.cpu_history[i],
                    self.memory_history[i],
                    self.disk_history[i],
                    self.network_sent_history[i],
                    self.network_recv_history[i]
                ])


class PerformanceGraph(QWidget):
    """Виджет для отображения графика производительности"""
    
    def __init__(self, title: str, color: str):
        super().__init__()
        self.title = title
        self.color = color
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем фигуру matplotlib
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(self.title, fontsize=10, color='white')
        self.ax.set_facecolor('#2d2d2d')
        self.figure.patch.set_facecolor('#2d2d2d')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        
        self.line, = self.ax.plot([], [], color=self.color, linewidth=2)
        self.ax.set_ylim(0, 100)
    
    def update_graph(self, x_data: List[str], y_data: List[float]):
        """Обновить график"""
        self.line.set_data(range(len(y_data)), y_data)
        self.ax.set_xlim(0, max(10, len(y_data)))
        self.canvas.draw()
    
    def clear(self):
        """Очистить график"""
        self.line.set_data([], [])
        self.canvas.draw()


class VitalSignAdvancedGUI(QMainWindow):
    """Расширенное главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.worker = SystemWorker()
        self.history = HistoryData(max_length=60)
        self.init_ui()
        self.worker.start()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle('VitalSign Advanced - Мониторинг системы')
        self.setMinimumSize(1000, 700)
        
        # Применяем темную тему
        self.apply_dark_theme()
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        
        # Заголовок
        title_label = QLabel('VitalSign Advanced - Мониторинг системных ресурсов')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        main_layout.addWidget(title_label)
        
        # Панель управления
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Создаем вкладки
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Вкладка "Система"
        system_tab = self.create_system_tab()
        tab_widget.addTab(system_tab, 'Система')
        
        # Вкладка "Графики"
        graphs_tab = self.create_graphs_tab()
        tab_widget.addTab(graphs_tab, 'Графики')
        
        # Вкладка "Процессы"
        processes_tab = self.create_processes_tab()
        tab_widget.addTab(processes_tab, 'Процессы')
        
        # Кнопка выхода
        exit_button = QPushButton('Выход')
        exit_button.clicked.connect(self.close)
        main_layout.addWidget(exit_button)
        
        # Подключаем сигнал обновления данных
        self.worker.data_updated.connect(self.update_system_data)
    
    def create_control_panel(self) -> QGroupBox:
        """Создать панель управления"""
        group = QGroupBox('Управление')
        layout = QHBoxLayout()
        
        # Интервал обновления
        layout.addWidget(QLabel('Интервал (сек):'))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(1)
        layout.addWidget(self.interval_spin)
        
        # Длина истории
        layout.addWidget(QLabel('История (точек):'))
        self.history_spin = QSpinBox()
        self.history_spin.setRange(10, 300)
        self.history_spin.setValue(60)
        self.history_spin.valueChanged.connect(self.change_history_length)
        layout.addWidget(self.history_spin)
        
        # Кнопка экспорта
        export_button = QPushButton('Экспорт в CSV')
        export_button.clicked.connect(self.export_data)
        layout.addWidget(export_button)
        
        # Кнопка очистки
        clear_button = QPushButton('Очистить историю')
        clear_button.clicked.connect(self.clear_history)
        layout.addWidget(clear_button)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def create_system_tab(self) -> QWidget:
        """Создать вкладку системного мониторинга"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # CPU секция
        cpu_group = QGroupBox('CPU')
        cpu_layout = QVBoxLayout()
        self.cpu_label = QLabel('Загрузка: 0%')
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_bar)
        cpu_group.setLayout(cpu_layout)
        layout.addWidget(cpu_group)
        
        # Память секция
        memory_group = QGroupBox('Оперативная память')
        memory_layout = QVBoxLayout()
        self.memory_label = QLabel('Использование: 0 GB / 0 GB (0%)')
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        memory_layout.addWidget(self.memory_label)
        memory_layout.addWidget(self.memory_bar)
        memory_group.setLayout(memory_layout)
        layout.addWidget(memory_group)
        
        # Диск секция
        disk_group = QGroupBox('Диск')
        disk_layout = QVBoxLayout()
        self.disk_label = QLabel('Использование: 0%')
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        disk_layout.addWidget(self.disk_label)
        disk_layout.addWidget(self.disk_bar)
        disk_group.setLayout(disk_layout)
        layout.addWidget(disk_group)
        
        # Сеть секция
        network_group = QGroupBox('Сеть')
        network_layout = QGridLayout()
        self.network_sent_label = QLabel('Отправлено: 0 MB')
        self.network_recv_label = QLabel('Получено: 0 MB')
        network_layout.addWidget(self.network_sent_label, 0, 0)
        network_layout.addWidget(self.network_recv_label, 0, 1)
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        layout.addStretch()
        return widget
    
    def create_graphs_tab(self) -> QWidget:
        """Создать вкладку с графиками"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # График CPU
        self.cpu_graph = PerformanceGraph('CPU Загрузка (%)', '#44ff44')
        layout.addWidget(self.cpu_graph)
        
        # График памяти
        self.memory_graph = PerformanceGraph('Память (%)', '#44aaff')
        layout.addWidget(self.memory_graph)
        
        return widget
    
    def create_processes_tab(self) -> QWidget:
        """Создать вкладку процессов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Фильтр
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Фильтр:'))
        self.process_filter = QComboBox()
        self.process_filter.addItems(['Все', 'CPU', 'Память'])
        filter_layout.addWidget(self.process_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Таблица процессов
        self.processes_table = QTableWidget()
        self.processes_table.setColumnCount(4)
        self.processes_table.setHorizontalHeaderLabels(['PID', 'Имя', 'CPU %', 'RAM %'])
        
        # Настройка ширины колонок
        header = self.processes_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.processes_table)
        
        # Кнопка обновления
        refresh_button = QPushButton('Обновить процессы')
        refresh_button.clicked.connect(self.update_processes)
        layout.addWidget(refresh_button)
        
        return widget
    
    def apply_dark_theme(self):
        """Применить темную тему"""
        app = QApplication.instance()
        app.setStyle('Fusion')
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        app.setPalette(palette)
    
    def update_system_data(self, data: Dict[str, Any]):
        """Обновить данные системы"""
        # Добавляем в историю
        self.history.add_data(data)
        
        # CPU
        cpu = data['cpu']
        self.cpu_label.setText(f'Загрузка: {cpu:.1f}%')
        self.cpu_bar.setValue(int(cpu))
        
        # Цвет CPU в зависимости от нагрузки
        if cpu > 80:
            self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff4444; }")
        elif cpu > 50:
            self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: #ffaa00; }")
        else:
            self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: #44ff44; }")
        
        # Память
        mem = data['memory']
        self.memory_label.setText(
            f'Использование: {mem["used"]:.2f} GB / {mem["total"]:.2f} GB ({mem["percent"]:.1f}%)'
        )
        self.memory_bar.setValue(int(mem['percent']))
        
        # Диск
        disk = data['disk']
        self.disk_label.setText(f'Использование: {disk:.1f}%')
        self.disk_bar.setValue(int(disk))
        
        # Сеть
        net = data['network']
        self.network_sent_label.setText(f'Отправлено: {net["sent"]:.2f} MB')
        self.network_recv_label.setText(f'Получено: {net["recv"]:.2f} MB')
        
        # Обновляем графики
        timestamps, cpu_data = self.history.get_cpu_data()
        self.cpu_graph.update_graph(timestamps, cpu_data)
        
        timestamps, memory_data = self.history.get_memory_data()
        self.memory_graph.update_graph(timestamps, memory_data)
    
    def update_processes(self):
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
        filter_type = self.process_filter.currentText()
        if filter_type == 'CPU':
            processes.sort(key=lambda x: x['cpu'], reverse=True)
        elif filter_type == 'Память':
            processes.sort(key=lambda x: x['memory'], reverse=True)
        else:
            processes.sort(key=lambda x: x['cpu'], reverse=True)
        
        # Отображение топ-20 процессов
        for i, proc in enumerate(processes[:20]):
            self.processes_table.insertRow(i)
            self.processes_table.setItem(i, 0, QTableWidgetItem(str(proc['pid'])))
            self.processes_table.setItem(i, 1, QTableWidgetItem(proc['name']))
            self.processes_table.setItem(i, 2, QTableWidgetItem(f'{proc["cpu"]:.1f}%'))
            self.processes_table.setItem(i, 3, QTableWidgetItem(f'{proc["memory"]:.1f}%'))
    
    def change_history_length(self, value: int):
        """Изменить длину истории"""
        self.history = HistoryData(max_length=value)
        self.cpu_graph.clear()
        self.memory_graph.clear()
    
    def export_data(self):
        """Экспортировать данные в CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить историю', '', 'CSV Files (*.csv)'
        )
        if filename:
            self.history.export_to_csv(filename)
    
    def clear_history(self):
        """Очистить историю"""
        self.history = HistoryData(max_length=self.history_spin.value())
        self.cpu_graph.clear()
        self.memory_graph.clear()
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.worker.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('VitalSign Advanced')
    
    window = VitalSignAdvancedGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
