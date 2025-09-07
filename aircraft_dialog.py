# aircraft_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt


class AircraftDialog(QDialog):
	def __init__(self, parent=None, aircraft_id=None):
		super().__init__(parent)
		self.aircraft_id = aircraft_id
		self.setWindowTitle("Добавить воздушное судно" if aircraft_id is None else "Редактировать воздушное судно")
		self.setModal(True)
		self.setup_ui()

		if aircraft_id is not None:
			self.load_aircraft_data()

	def setup_ui(self):
		layout = QVBoxLayout(self)

		# Поле для регистрационного номера
		layout.addWidget(QLabel("Регистрационный номер:"))
		self.registration_edit = QLineEdit()
		layout.addWidget(self.registration_edit)

		# Поле для типа ВС
		layout.addWidget(QLabel("Тип воздушного судна:"))
		self.type_edit = QLineEdit()
		layout.addWidget(self.type_edit)

		# Выбор класса места для отдыха
		layout.addWidget(QLabel("Класс места для отдыха:"))
		self.rest_facility_combo = QComboBox()
		self.rest_facility_combo.addItems(["Не предусмотрен", "1 класс", "2 класс", "3 класс"])
		layout.addWidget(self.rest_facility_combo)

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

	def load_aircraft_data(self):
		"""Загружает данные воздушного судна для редактирования"""
		import sqlite3
		try:
			conn = sqlite3.connect('fdp_data.db')
			cursor = conn.cursor()
			cursor.execute("SELECT registration, type, rest_facility_class FROM aircrafts WHERE id = ?",
			               (self.aircraft_id,))
			aircraft_data = cursor.fetchone()
			conn.close()

			if aircraft_data:
				self.registration_edit.setText(aircraft_data[0])
				self.type_edit.setText(aircraft_data[1])
				if aircraft_data[2] is not None:
					self.rest_facility_combo.setCurrentIndex(aircraft_data[2])

		except Exception as e:
			QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")

	def get_data(self):
		"""Возвращает введенные данные в виде словаря."""
		rest_class_map = {"Не предусмотрен": None, "1 класс": 1, "2 класс": 2, "3 класс": 3}

		return {
			"registration": self.registration_edit.text(),
			"type": self.type_edit.text(),
			"rest_facility_class": rest_class_map[self.rest_facility_combo.currentText()]
		}

	def accept(self):
		"""Проверяем ввод и закрываем диалог с результатом OK."""
		if not self.registration_edit.text() or not self.type_edit.text():
			QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
			return
		super().accept()