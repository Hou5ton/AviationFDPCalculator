# crew_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt

class CrewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить члена экипажа")
        self.setModal(True)  # Модальное окно
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Поле для имени
        layout.addWidget(QLabel("ФИО:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        # Поле для основного места базирования
        layout.addWidget(QLabel("Основное место базирования (код аэропорта):"))
        self.home_base_edit = QLineEdit()
        layout.addWidget(self.home_base_edit)

        # Выбор типа экипажа
        layout.addWidget(QLabel("Тип экипажа:"))
        self.crew_type_combo = QComboBox()
        self.crew_type_combo.addItems(["Летный", "Кабинный"])
        layout.addWidget(self.crew_type_combo)

        # Кнопки
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить")
        self.cancel_button = QPushButton("Отмена")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Подключаем кнопки
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_data(self):
        """Возвращает введенные данные в виде словаря."""
        return {
            "name": self.name_edit.text(),
            "home_base": self.home_base_edit.text(),
            "is_pilot": self.crew_type_combo.currentText() == "Летный"
        }

    def accept(self):
        """Проверяем ввод и закрываем диалог с результатом OK."""
        if not self.name_edit.text() or not self.home_base_edit.text():
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return
        super().accept()