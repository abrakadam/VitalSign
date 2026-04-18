# Документация GUI утилит VitalSign

## Обзор

Модуль `utils/gui_utils.py` предоставляет набор утилит для создания красивого и современного графического интерфейса.

## Классы и компоненты

### GUITheme

Класс для управления цветовой палитрой и темами.

#### Цветовая палитра
- **DARK_BACKGROUND**: Основной фон (#1e1e23)
- **DARK_WIDGET**: Фон виджетов (#2d2d32)
- **DARK_GROUP**: Фон групп (#37373c)
- **DARK_BORDER**: Цвет границ (#46464b)

#### Акцентные цвета
- **ACCENT_PRIMARY**: Синий (#4285f4)
- **ACCENT_SUCCESS**: Зеленый (#4caf50)
- **ACCENT_WARNING**: Оранжевый (#ff9800)
- **ACCENT_ERROR**: Красный (#f44336)
- **ACCENT_INFO**: Информационный синий (#2196f3)

#### Текстовые цвета
- **TEXT_PRIMARY**: Основной текст (#ffffff)
- **TEXT_SECONDARY**: Вторичный текст (#c8c8c8)
- **TEXT_DISABLED**: Отключенный текст (#787878)

#### Методы
```python
GUITheme.apply_dark_theme(app)  # Применить темную тему
```

### StyledFrame

Стилизованный фрейм с закругленными углами и границей.

```python
frame = StyledFrame()
```

### StyledLabel

Стилизованная метка с предопределенными стилями.

#### Стили
- **title**: Заголовок (18px, bold)
- **subtitle**: Подзаголовок (14px, semi-bold)
- **normal**: Обычный текст (12px)
- **accent**: Акцентный текст (синий, semi-bold)

```python
label = StyledLabel("Текст", "title")
```

### CardWidget

Карточка с контентом и стилем.

```python
card = CardWidget("Заголовок")
card.add_widget(widget)
card.add_layout(layout)
```

### StatCard

Карточка для отображения статистики с цветным значением.

```python
card = StatCard("CPU", "45%", GUITheme.ACCENT_PRIMARY)
card.update_value("50%")
```

### Separator

Разделитель (горизонтальный или вертикальный).

```python
sep = Separator("horizontal")  # или "vertical"
```

### StatusIndicator

Индикатор статуса с цветом.

#### Статусы
- **normal**: Синий
- **warning**: Оранжевый
- **error**: Красный
- **success**: Зеленый

```python
indicator = StatusIndicator()
indicator.set_status("success")
```

### ProgressBarStyle

Стили для прогресс-баров.

#### Методы
```python
# Однотонный стиль
style = ProgressBarStyle.get_style(GUITheme.ACCENT_PRIMARY)

# Градиентный стиль
style = ProgressBarStyle.get_gradient_style(
    GUITheme.ACCENT_PRIMARY, 
    GUITheme.ACCENT_INFO
)
```

### TableStyle

Стили для таблиц.

#### Методы
```python
style = TableStyle.get_dark_style()
```

## Примеры использования

### Создание карточки статистики
```python
from utils import StatCard, GUITheme

cpu_card = StatCard("CPU", "45%", GUITheme.ACCENT_PRIMARY)
```

### Создание стилизованного интерфейса
```python
from utils import GUITheme, StyledLabel, CardWidget, Separator

# Применить тему
GUITheme.apply_dark_theme(app)

# Создать элементы
title = StyledLabel("Мониторинг", "title")
card = CardWidget("Статистика")
separator = Separator()
```

### Стилизация прогресс-бара
```python
from utils import ProgressBarStyle, GUITheme

progress = QProgressBar()
progress.setStyleSheet(ProgressBarStyle.get_style(GUITheme.ACCENT_SUCCESS))
```

### Стилизация таблицы
```python
from utils import TableStyle

table = QTableWidget()
table.setStyleSheet(TableStyle.get_dark_style())
```

## Интеграция с GUI

### В gui_main.py
```python
from utils import (
    GUITheme, StyledLabel, CardWidget, StatCard,
    Separator, StatusIndicator, ProgressBarStyle, TableStyle
)

# Применение темы
GUITheme.apply_dark_theme(QApplication.instance())

# Создание элементов
card = CardWidget("CPU")
label = StyledLabel("Загрузка", "normal")
indicator = StatusIndicator()
```

## Кастомизация

### Добавление своих цветов
```python
class CustomTheme(GUITheme):
    CUSTOM_COLOR = QColor(128, 0, 128)  # Фиолетовый
```

### Создание своих стилей
```python
def get_custom_style():
    return """
        QWidget {
            background-color: #1a1a1a;
            border-radius: 10px;
        }
    """
```

## Производительность

Все утилиты оптимизированы для производительности:
- Минимальное использование ресурсов
- Кэширование стилей
- Эффективная отрисовка

## Будущие улучшения

- [ ] Анимации переходов
- [ ] Темы (светлая/темная)
- [ ] Кастомные иконки
- [ ] Графики в CardWidget
- [ ] Дополнительные виджеты
