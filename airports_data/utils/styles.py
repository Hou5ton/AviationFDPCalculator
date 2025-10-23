"""
Стили для приложения
"""

# Основные стили для группы маршрута
ROUTE_GROUP_STYLE = """
QGroupBox {
    font-weight: bold;
    border: 2px solid #bdc3c7;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    background-color: #f8f9fa;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    background-color: #f8f9fa;
    color: #2c3e50;
}
"""

# Стили для кнопок управления сегментами
ADD_BUTTON_STYLE = """
QPushButton {
    background-color: #27ae60;
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: bold;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #229954;
}
QPushButton:pressed {
    background-color: #1e8449;
}
"""

REMOVE_BUTTON_STYLE = """
QPushButton {
    background-color: #e74c3c;
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: bold;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #c0392b;
}
QPushButton:pressed {
    background-color: #a93226;
}
"""

# Стили для полей поиска аэропортов
AIRPORT_SEARCH_STYLE = """
QLineEdit {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 4px 8px;
    background-color: white;
}
QLineEdit:focus {
    border: 2px solid #007acc;
}
"""

# Стили для заблокированных полей
DISABLED_FIELD_STYLE = """
QLineEdit {
    background-color: #f0f0f0;
    color: #666666;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 4px 8px;
}
"""

# Стили для полей времени
TIME_FIELD_STYLE = """
QDateTimeEdit {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 4px 8px;
    background-color: white;
}
QDateTimeEdit:focus {
    border: 2px solid #007acc;
}
"""

# Стили для комбобоксов
COMBOBOX_STYLE = """
QComboBox {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 4px 8px;
    background-color: white;
}
QComboBox:focus {
    border: 2px solid #007acc;
}
QComboBox::drop-down {
    border: none;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #666;
}
"""

# Стили для спинбоксов
SPINBOX_STYLE = """
QSpinBox {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 4px 8px;
    background-color: white;
}
QSpinBox:focus {
    border: 2px solid #007acc;
}
"""

# Стили для кнопок
BUTTON_STYLE = """
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #2980b9;
}
QPushButton:pressed {
    background-color: #21618c;
}
"""

# Стили для заголовков
TITLE_STYLE = """
QLabel {
    color: #2c3e50;
    font-weight: bold;
    font-size: 16px;
    padding: 10px;
}
"""

# Стили для валидации
VALIDATION_VALID_STYLE = """
QLabel {
    color: #27ae60;
    font-weight: bold;
}
"""

VALIDATION_INVALID_STYLE = """
QLabel {
    color: #e74c3c;
    font-weight: bold;
}
"""

VALIDATION_WARNING_STYLE = """
QLabel {
    color: #f39c12;
    font-weight: bold;
}
"""

VALIDATION_NEUTRAL_STYLE = """
QLabel {
    color: #666;
    font-weight: bold;
}
"""

# Стили для скроллируемой области
SCROLL_AREA_STYLE = """
QScrollArea {
    border: none;
    background-color: transparent;
}
"""

# Стили для разделителя
SPLITTER_STYLE = """
QSplitter::handle {
    background-color: #bdc3c7;
    width: 3px;
}
QSplitter::handle:hover {
    background-color: #95a5a6;
}
"""
