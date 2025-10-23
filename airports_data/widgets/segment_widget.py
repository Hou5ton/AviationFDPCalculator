"""
Виджет для отображения сегмента полета
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                            QDateTimeEdit, QPushButton, QGroupBox)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal
from PyQt6.QtGui import QFont, QMovie
from .airport_search import AirportSearchWidget
from ..data.airports import get_airports_data
import os


class SegmentWidget(QWidget):
    """Виджет для отображения одного сегмента полета"""
    
    # Сигналы
    segment_removed = pyqtSignal(int)  # Сигнал удаления сегмента
    segment_added = pyqtSignal(int)    # Сигнал добавления сегмента
    airport_changed = pyqtSignal()     # Сигнал изменения аэропорта
    
    def __init__(self, segment_number=1, parent=None):
        super().__init__(parent)
        self.segment_number = segment_number
        self.airports_data = get_airports_data()
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Номер сегмента
        self.number_label = QLabel(f"Сегмент {self.segment_number}")
        self.number_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.number_label.setMinimumWidth(80)
        layout.addWidget(self.number_label)
        
        # Аэропорт отправления
        self.departure_combo = AirportSearchWidget(self.airports_data)
        self.departure_combo.setMinimumWidth(160)
        self.departure_combo.setMaximumWidth(160)
        layout.addWidget(self.departure_combo)
        
        # Время отправления
        self.departure_time = QDateTimeEdit()
        self.departure_time.setDisplayFormat("dd.MM.yyyy hh:mm")
        self.departure_time.setDateTime(QDateTime.currentDateTime())
        self.departure_time.setMinimumWidth(90)
        self.departure_time.setMaximumWidth(110)
        layout.addWidget(self.departure_time)
        
        # Аэропорт прибытия
        self.arrival_combo = AirportSearchWidget(self.airports_data)
        self.arrival_combo.setMinimumWidth(160)
        self.arrival_combo.setMaximumWidth(160)
        layout.addWidget(self.arrival_combo)
        
        # Время прибытия
        self.arrival_time = QDateTimeEdit()
        self.arrival_time.setDisplayFormat("dd.MM.yyyy hh:mm")
        self.arrival_time.setDateTime(QDateTime.currentDateTime())
        self.arrival_time.setMinimumWidth(90)
        self.arrival_time.setMaximumWidth(110)
        layout.addWidget(self.arrival_time)
        
        # Кнопки управления
        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(25, 25)
        self.add_button.setStyleSheet("""
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
        """)
        
        self.remove_button = QPushButton("-")
        self.remove_button.setFixedSize(25, 25)
        self.remove_button.setStyleSheet("""
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
        """)
        
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)
        
        self.setLayout(layout)
        
        # Обновляем видимость кнопок
        self.update_buttons_visibility()
    
    def setup_connections(self):
        """Настройка соединений сигналов"""
        self.add_button.clicked.connect(self.add_segment)
        self.remove_button.clicked.connect(self.remove_segment)
        self.departure_combo.airport_selected.connect(self.on_departure_airport_selected)
        self.arrival_combo.airport_selected.connect(self.on_arrival_airport_selected)
    
    def add_segment(self):
        """Добавляет новый сегмент после текущего"""
        self.segment_added.emit(self.segment_number)
    
    def remove_segment(self):
        """Удаляет текущий сегмент"""
        self.segment_removed.emit(self.segment_number)
    
    def update_buttons_visibility(self):
        """Обновляет видимость кнопок управления"""
        # Кнопка добавления видна всегда
        self.add_button.setVisible(True)
        
        # Кнопка удаления видна только если сегментов больше одного
        # Это будет обновляться из родительского виджета
        self.remove_button.setVisible(True)
    
    def set_segment_number(self, number):
        """Устанавливает номер сегмента"""
        self.segment_number = number
        self.number_label.setText(f"Сегмент {number}")
    
    def on_departure_airport_selected(self, icao):
        """Обработка выбора аэропорта отправления"""
        self.update_departure_tooltip(icao)
        self.airport_changed.emit()
    
    def on_arrival_airport_selected(self, icao):
        """Обработка выбора аэропорта прибытия"""
        self.update_arrival_tooltip(icao)
        self.airport_changed.emit()
    
    def update_departure_tooltip(self, icao):
        """Обновляет подсказку для аэропорта отправления"""
        if icao in self.airports_data:
            data = self.airports_data[icao]
            tooltip = f"{icao} - {data['city']}, {data['name']}, {data['country']}"
            self.departure_combo.setToolTip(tooltip)
    
    def update_arrival_tooltip(self, icao):
        """Обновляет подсказку для аэропорта прибытия"""
        if icao in self.airports_data:
            data = self.airports_data[icao]
            tooltip = f"{icao} - {data['city']}, {data['name']}, {data['country']}"
            self.arrival_combo.setToolTip(tooltip)
    
    def get_airport_code(self, combo):
        """Извлекает ICAO код из выбранного аэропорта"""
        text = combo.text()
        if "/" in text:
            return text.split("/")[0]
        return text
    
    def get_airport_info(self, icao):
        """Возвращает информацию об аэропорте по ICAO коду"""
        return self.airports_data.get(icao.upper())
    
    def set_airport(self, combo, icao):
        """Устанавливает аэропорт в комбобокс"""
        if icao in self.airports_data:
            combo.set_airport(icao)
    
    def get_departure_icao(self):
        """Возвращает ICAO код аэропорта отправления"""
        return self.departure_combo.get_current_icao()
    
    def get_arrival_icao(self):
        """Возвращает ICAO код аэропорта прибытия"""
        return self.arrival_combo.get_current_icao()
    
    def get_departure_time(self):
        """Возвращает время отправления"""
        return self.departure_time.dateTime()
    
    def get_arrival_time(self):
        """Возвращает время прибытия"""
        return self.arrival_time.dateTime()
    
    def set_departure_time(self, datetime):
        """Устанавливает время отправления"""
        self.departure_time.setDateTime(datetime)
    
    def set_arrival_time(self, datetime):
        """Устанавливает время прибытия"""
        self.arrival_time.setDateTime(datetime)
