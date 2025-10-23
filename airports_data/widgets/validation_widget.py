"""
Виджет для отображения валидации FDP
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ValidationWidget(QWidget):
    """Виджет для отображения статуса валидации FDP"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Статус валидации
        self.status_label = QLabel("Статус: Не рассчитано")
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setStyleSheet("color: #666; font-weight: bold;")
        
        # Максимальное время FDP
        self.max_fdp_label = QLabel("Макс. FDP: --:--")
        self.max_fdp_label.setFont(QFont("Arial", 9))
        self.max_fdp_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        
        # Время акклиматизации
        self.acclimatization_label = QLabel("Акклиматизация: --:--")
        self.acclimatization_label.setFont(QFont("Arial", 9))
        self.acclimatization_label.setStyleSheet("color: #e67e22; font-weight: bold;")
        
        # Время отдыха
        self.rest_label = QLabel("Отдых: --:--")
        self.rest_label.setFont(QFont("Arial", 9))
        self.rest_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.max_fdp_label)
        layout.addWidget(self.acclimatization_label)
        layout.addWidget(self.rest_label)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_validation(self, status, max_fdp=None, acclimatization=None, rest=None):
        """Обновляет информацию о валидации"""
        # Обновляем статус
        if status == "valid":
            self.status_label.setText("Статус: ✅ Валидно")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        elif status == "invalid":
            self.status_label.setText("Статус: ❌ Невалидно")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        else:
            self.status_label.setText("Статус: ⚠️ Предупреждение")
            self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        
        # Обновляем максимальное время FDP
        if max_fdp:
            self.max_fdp_label.setText(f"Макс. FDP: {max_fdp}")
        else:
            self.max_fdp_label.setText("Макс. FDP: --:--")
        
        # Обновляем время акклиматизации
        if acclimatization:
            self.acclimatization_label.setText(f"Акклиматизация: {acclimatization}")
        else:
            self.acclimatization_label.setText("Акклиматизация: --:--")
        
        # Обновляем время отдыха
        if rest:
            self.rest_label.setText(f"Отдых: {rest}")
        else:
            self.rest_label.setText("Отдых: --:--")
    
    def clear_validation(self):
        """Очищает информацию о валидации"""
        self.status_label.setText("Статус: Не рассчитано")
        self.status_label.setStyleSheet("color: #666; font-weight: bold;")
        self.max_fdp_label.setText("Макс. FDP: --:--")
        self.acclimatization_label.setText("Акклиматизация: --:--")
        self.rest_label.setText("Отдых: --:--")
