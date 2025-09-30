# main_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem,
                             QTabWidget, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt
from crew_dialog import CrewDialog
from aircraft_dialog import AircraftDialog
from planning_tab import PlanningTab
from calculator_gui import CalculatorTab  # Добавляем импорт CalculatorTab
from schedule_tab import ScheduleTab
from database import db
import os


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Aviation FDP Calculator")
		self.setGeometry(100, 100, 1000, 700)

		# Центральный виджет и основной макет
		central_widget = QWidget()
		self.setCentralWidget(central_widget)
		layout = QVBoxLayout(central_widget)

		# Создаем вкладки
		tabs = QTabWidget()
		layout.addWidget(tabs)

		# Вкладка "Калькулятор"
		self.calculator_tab = CalculatorTab()
		tabs.addTab(self.calculator_tab, "Калькулятор")

		# Вкладка "Планирование" - ДОЛЖНА БЫТЬ ПЕРВОЙ
		self.planning_tab = PlanningTab()
		tabs.addTab(self.planning_tab, "Планирование")

		# Остальные вкладки...
		# Вкладка "Экипаж"
		self.crew_tab = QWidget()
		self.setup_crew_tab()
		tabs.addTab(self.crew_tab, "Экипаж")


		# Вкладка "График"
		self.schedule_tab = ScheduleTab()
		tabs.addTab(self.schedule_tab, "График")

		# Вкладка "Воздушные суда"
		self.aircraft_tab = QWidget()
		self.setup_aircraft_tab()
		tabs.addTab(self.aircraft_tab, "Воздушные суда")

		# Инициализируем базу данных
		self.init_database()

	def init_database(self):
		"""Инициализирует базу данных, если она еще не создана"""
		# База данных уже создается при импорте db из database.py
		# Просто загружаем данные
		self.load_crew_data()
		self.load_aircraft_data()

	def setup_crew_tab(self):
		layout = QVBoxLayout(self.crew_tab)

		# Кнопка "Добавить"
		add_button_layout = QHBoxLayout()
		self.add_crew_button = QPushButton("Добавить")
		self.add_crew_button.clicked.connect(self.open_crew_dialog)
		add_button_layout.addWidget(self.add_crew_button)
		add_button_layout.addStretch()
		layout.addLayout(add_button_layout)

		# Таблица для отображения экипажа
		self.crew_table = QTableWidget()
		self.crew_table.setColumnCount(4)
		self.crew_table.setHorizontalHeaderLabels(["ID", "ФИО", "Основное место базирования", "Тип"])
		self.crew_table.horizontalHeader().setStretchLastSection(True)
		layout.addWidget(self.crew_table)

	def setup_aircraft_tab(self):
		layout = QVBoxLayout(self.aircraft_tab)

		# Кнопки управления
		button_layout = QHBoxLayout()

		self.add_aircraft_btn = QPushButton("Добавить ВС")
		self.add_aircraft_btn.clicked.connect(self.open_aircraft_dialog)
		button_layout.addWidget(self.add_aircraft_btn)

		self.edit_aircraft_btn = QPushButton("Редактировать ВС")
		self.edit_aircraft_btn.clicked.connect(self.edit_aircraft)
		button_layout.addWidget(self.edit_aircraft_btn)

		self.delete_aircraft_btn = QPushButton("Удалить ВС")
		self.delete_aircraft_btn.clicked.connect(self.delete_aircraft)
		button_layout.addWidget(self.delete_aircraft_btn)

		layout.addLayout(button_layout)

		# Таблица для отображения воздушных судов
		self.aircraft_table = QTableWidget()
		self.aircraft_table.setColumnCount(4)
		self.aircraft_table.setHorizontalHeaderLabels(["ID", "Регистрационный номер", "Тип", "Класс отдыха"])
		self.aircraft_table.horizontalHeader().setStretchLastSection(True)
		layout.addWidget(self.aircraft_table)

	def open_crew_dialog(self):
		"""Открывает диалоговое окно для добавления нового члена экипажа"""
		dialog = CrewDialog(self)
		if dialog.exec() == 1:
			data = dialog.get_data()
			self.save_crew_member(data)

	def save_crew_member(self, data):
		"""Сохраняет данные о члене экипажа в базу данных"""
		try:
			crew_id = db.add_crew_member(data['name'], data['home_base'], data['is_pilot'])

			# Обновляем таблицу
			self.load_crew_data()

			QMessageBox.information(self, "Успех", "Член экипажа успешно добавлен!")

		except Exception as e:
			QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось сохранить данные: {e}")

	def load_crew_data(self):
		"""Загружает данные экипажа из БД и отображает их в таблице"""
		try:
			crew_data = db.get_all_crew_members()

			self.crew_table.setRowCount(len(crew_data))
			for row_idx, row_data in enumerate(crew_data):
				for col_idx, col_data in enumerate(row_data):
					item = QTableWidgetItem(str(col_data))
					# Для типа экипажа преобразуем булево значение в текст
					if col_idx == 3:
						item.setText("Летный" if col_data else "Кабинный")
					else:
						item.setText(str(col_data))
					self.crew_table.setItem(row_idx, col_idx, item)

		except Exception as e:
			QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось загрузить данные: {e}")

	def open_aircraft_dialog(self):
		"""Открывает диалоговое окно для добавления нового воздушного судна"""
		dialog = AircraftDialog(self)
		if dialog.exec() == 1:
			data = dialog.get_data()
			self.save_aircraft(data)

	def save_aircraft(self, data):
		"""Сохраняет данные о воздушном судне в базу данных"""
		try:
			aircraft_id = db.add_aircraft(data['registration'], data['type'], data['rest_facility_class'])

			# Обновляем таблицу
			self.load_aircraft_data()

			QMessageBox.information(self, "Успех", "Воздушное судно успешно добавлено!")

		except Exception as e:
			QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось сохранить данные: {e}")

	def load_aircraft_data(self):
		"""Загружает данные о воздушных судах из БД и отображает их в таблице"""
		try:
			aircraft_data = db.get_all_aircrafts()

			self.aircraft_table.setRowCount(len(aircraft_data))
			for row_idx, row_data in enumerate(aircraft_data):
				for col_idx, col_data in enumerate(row_data):
					item = QTableWidgetItem(str(col_data))
					# Для класса отдыха преобразуем числовое значение в текст
					if col_idx == 3:
						if col_data == 1:
							item.setText("1 класс")
						elif col_data == 2:
							item.setText("2 класс")
						elif col_data == 3:
							item.setText("3 класс")
						else:
							item.setText("Не предусмотрен")
					else:
						item.setText(str(col_data))
					self.aircraft_table.setItem(row_idx, col_idx, item)

		except Exception as e:
			QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось загрузить данные: {e}")

	def edit_aircraft(self):
		"""Редактирует выбранное воздушное судно"""
		selected_row = self.aircraft_table.currentRow()
		if selected_row == -1:
			QMessageBox.warning(self, "Предупреждение", "Выберите воздушное судно для редактирования!")
			return

		aircraft_id = int(self.aircraft_table.item(selected_row, 0).text())
		dialog = AircraftDialog(self, aircraft_id)
		if dialog.exec() == 1:
			data = dialog.get_data()
			self.update_aircraft(aircraft_id, data)

	def update_aircraft(self, aircraft_id, data):
		"""Обновляет данные о воздушном судне в базе данных"""
		try:
			success = db.update_aircraft(aircraft_id, data['registration'], data['type'], data['rest_facility_class'])

			if success:
				# Обновляем таблицу
				self.load_aircraft_data()
				QMessageBox.information(self, "Успех", "Данные воздушного судна успешно обновлены!")
			else:
				QMessageBox.critical(self, "Ошибка", "Не удалось обновить данные воздушного судна")

		except Exception as e:
			QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось обновить данные: {e}")

	def delete_aircraft(self):
		"""Удаляет выбранное воздушное судно"""
		selected_row = self.aircraft_table.currentRow()
		if selected_row == -1:
			QMessageBox.warning(self, "Предупреждение", "Выберите воздушное судно для удаления!")
			return

		aircraft_id = int(self.aircraft_table.item(selected_row, 0).text())
		aircraft_name = self.aircraft_table.item(selected_row, 1).text()

		reply = QMessageBox.question(self, "Подтверждение",
		                             f"Вы уверены, что хотите удалить воздушное судно {aircraft_name}?",
		                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

		if reply == QMessageBox.StandardButton.Yes:
			try:
				success = db.delete_aircraft(aircraft_id)

				if success:
					# Обновляем таблицу
					self.load_aircraft_data()
					QMessageBox.information(self, "Успех", "Воздушное судно успешно удалено!")
				else:
					QMessageBox.critical(self, "Ошибка", "Не удалось удалить воздушное судно")

			except Exception as e:
				QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось удалить данные: {e}")


if __name__ == "__main__":
	import sys
	from PyQt6.QtWidgets import QApplication
	from calculator_gui import CalculatorTab

	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())