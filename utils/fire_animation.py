"""
Анимация огня для фона GUI
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QRadialGradient, QBrush
import random
from typing import List


class FireParticle:
    """Частица огня"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.life = 1.0  # Жизнь частицы (1.0 = 100%)
        self.size = random.uniform(5, 15)
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = random.uniform(-2, -4)
        self.decay = random.uniform(0.01, 0.03)
    
    def update(self):
        """Обновить позицию частицы"""
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= self.decay
        self.size *= 0.98
    
    def is_alive(self) -> bool:
        """Проверить, жива ли частица"""
        return self.life > 0


class FireBackground(QWidget):
    """Фон с анимацией огня"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles: List[FireParticle] = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)  # ~33 FPS
        
        # Цвета огня
        self.fire_colors = [
            QColor(255, 200, 0),    # Желтый
            QColor(255, 150, 0),    # Оранжевый
            QColor(255, 100, 0),    # Темно-оранжевый
            QColor(255, 50, 0),     # Красно-оранжевый
            QColor(200, 50, 0),     # Темно-красный
        ]
    
    def update_animation(self):
        """Обновить анимацию"""
        # Добавляем новые частицы внизу
        if len(self.particles) < 100:
            x = random.uniform(0, self.width())
            y = self.height() + 10
            self.particles.append(FireParticle(x, y))
        
        # Обновляем существующие частицы
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
        
        self.update()
    
    def paintEvent(self, event):
        """Отрисовать анимацию"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Фон
        painter.fillRect(self.rect(), QColor(20, 20, 25))
        
        # Рисуем частицы огня
        for particle in self.particles:
            self.draw_particle(painter, particle)
    
    def draw_particle(self, painter: QPainter, particle: FireParticle):
        """Нарисовать частицу"""
        # Выбираем цвет в зависимости от жизни
        color_index = int((1.0 - particle.life) * (len(self.fire_colors) - 1))
        color_index = max(0, min(color_index, len(self.fire_colors) - 1))
        base_color = self.fire_colors[color_index]
        
        # Создаем градиент для частицы
        gradient = QRadialGradient(particle.x, particle.y, particle.size)
        gradient.setColorAt(0, QColor(base_color.red(), base_color.green(), base_color.blue(), 
                                      int(255 * particle.life)))
        gradient.setColorAt(1, QColor(base_color.red(), base_color.green(), base_color.blue(), 0))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(particle.x - particle.size, particle.y - particle.size,
                                   particle.size * 2, particle.size * 2))
    
    def resizeEvent(self, event):
        """Обработка изменения размера"""
        self.particles.clear()
        super().resizeEvent(event)
    
    def stop(self):
        """Остановить анимацию"""
        if self.timer.isActive():
            self.timer.stop()
        self.particles.clear()


class SubtleFireBackground(QWidget):
    """Тонкий фон с огнем (менее заметный)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles: List[FireParticle] = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)  # 20 FPS
        
        # Цвета для тонкого огня
        self.fire_colors = [
            QColor(255, 180, 50, 80),   # Желтый с прозрачностью
            QColor(255, 140, 30, 60),   # Оранжевый с прозрачностью
            QColor(255, 100, 20, 40),   # Темно-оранжевый с прозрачностью
        ]
    
    def update_animation(self):
        """Обновить анимацию"""
        # Добавляем новые частицы
        if len(self.particles) < 50:
            x = random.uniform(0, self.width())
            y = self.height() + 5
            self.particles.append(FireParticle(x, y))
        
        # Обновляем частицы
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
        
        self.update()
    
    def paintEvent(self, event):
        """Отрисовать анимацию"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Фон
        painter.fillRect(self.rect(), QColor(25, 25, 30))
        
        # Рисуем частицы
        for particle in self.particles:
            self.draw_particle(painter, particle)
    
    def draw_particle(self, painter: QPainter, particle: FireParticle):
        """Нарисовать частицу"""
        color_index = int((1.0 - particle.life) * (len(self.fire_colors) - 1))
        color_index = max(0, min(color_index, len(self.fire_colors) - 1))
        base_color = self.fire_colors[color_index]
        
        alpha = int(255 * particle.life)
        gradient = QRadialGradient(particle.x, particle.y, particle.size)
        gradient.setColorAt(0, QColor(base_color.red(), base_color.green(), base_color.blue(), alpha))
        gradient.setColorAt(1, QColor(base_color.red(), base_color.green(), base_color.blue(), 0))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(particle.x - particle.size, particle.y - particle.size,
                                   particle.size * 2, particle.size * 2))
    
    def resizeEvent(self, event):
        """Обработка изменения размера"""
        self.particles.clear()
        super().resizeEvent(event)
    
    def stop(self):
        """Остановить анимацию"""
        if self.timer.isActive():
            self.timer.stop()
        self.particles.clear()
