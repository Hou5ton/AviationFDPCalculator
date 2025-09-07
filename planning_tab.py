# planning_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QComboBox, QSpinBox, QDateTimeEdit,
                             QPushButton, QTextEdit, QFormLayout, QCheckBox,
                             QMessageBox)
from PyQt6.QtCore import QDateTime
from calculator import FDPCalculator
import sqlite3


class PlanningTab(QWidget):
	def __init__(self):
		super().__init__()
		self.calculator = FDPCalculator()
		self.init_ui()
		self.load_crew_members()
		self.load_aircrafts()

	def init_ui(self):
		main_layout = QVBoxLayout()

		# Секция ввода параметров
		input_group = QGroupBox("Параметры планирования")
		input_layout = QFormLayout()

		# Выбор члена экипажа
		self.crew_member_combo = QComboBox()
		input_layout.addRow("Член экипажа:", self.crew_member_combo)

		# Выбор воздушного судна
		self.aircraft_combo = QComboBox()
		input_layout.addRow("Воздушное судно:", self.aircraft_combo)

		# Дата и время начала FDP
		self.fdp_start_edit = QDateTimeEdit()
		self.fdp_start_edit.setDateTime(QDateTime.currentDateTime())
		self.fdp_start_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
		input_layout.addRow("Дата и время начала FDP:", self.fdp_start_edit)

		# Количество секторов
		self.sectors_spin = QSpinBox()
		self.sectors_spin.setRange(1, 10)
		self.sectors_spin.setValue(1)
		input_layout.addRow("Количество секторов:", self.sectors_spin)

		# Аэропорт вылета
		self.departure_edit = QComboBox()
		self.departure_edit.setEditable(True)
		self.departure_edit.addItems(["UMMS", "UEEE", "UWKD", "UUDD", "URSS"])
		input_layout.addRow("Аэропорт вылета:", self.departure_edit)

		# Аэропорт назначения
		self.arrival_edit = QComboBox()
		self.arrival_edit.setEditable(True)
		self.arrival_edit.addItems(["UMMS", "UEEE", "UWKD", "UUDD", "URSS"])
		input_layout.addRow("Аэропорт назначения:", self.arrival_edit)

		# Отдых в полете
		self.rest_in_flight_check = QCheckBox()
		input_layout.addRow("Отдых в полете:", self.rest_in_flight_check)

		# Наличие FRMS
		self.has_frms_check = QCheckBox()
		input_layout.addRow("Наличие FRMS:", self.has_frms_check)

		input_group.setLayout(input_layout)
		main_layout.addWidget(input_group)

		# Кнопки
		button_layout = QHBoxLayout()

		self.calculate_btn = QPushButton("Рассчитать")
		self.calculate_btn.clicked.connect(self.calculate_plan)
		button_layout.addWidget(self.calculate_btn)

		self.save_btn = QPushButton("Сохранить задание")
		self.save_btn.clicked.connect(self.save_duty)
		button_layout.addWidget(self.save_btn)

		main_layout.addLayout(button_layout)

		# Поле вывода результатов
		self.result_text = QTextEdit()
		self.result_text.setReadOnly(True)
		main_layout.addWidget(self.result_text)

		self.setLayout(main_layout)

	def load_crew_members(self):
		"""Загружает список членов экипажа из базы данных"""
		try:
			conn = sqlite3.connect('fdp_data.db')
			cursor = conn.cursor()
			cursor.execute("SELECT id, name, home_base FROM crew_members")
			crew_data = cursor.fetchall()
			conn.close()

			self.crew_member_combo.clear()
			for crew_id, name, home_base in crew_data:
				self.crew_member_combo.addItem(f"{name} ({home_base})", crew_id)

		except sqlite3.Error as e:
			QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить членов экипажа: {e}")

	def load_aircrafts(self):
		"""Загружает список воздушных судов из базы данных"""
		try:
			conn = sqlite3.connect('fdp_data.db')
			cursor = conn.cursor()
			cursor.execute("SELECT id, registration, type FROM aircrafts")
			aircraft_data = cursor.fetchall()
			conn.close()

			self.aircraft_combo.clear()
			for aircraft_id, registration, aircraft_type in aircraft_data:
				self.aircraft_combo.addItem(f"{registration} ({aircraft_type})", aircraft_id)

		except sqlite3.Error as e:
			QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить воздушные суда: {e}")

	def calculate_plan(self):
		"""Рассчитывает план полета на основе введенных параметров"""
		try:
			# Получаем выбранные значения
			crew_member_id = self.crew_member_combo.currentData()
			aircraft_id = self.aircraft_combo.currentData()
			start_time = self.fdp_start_edit.dateTime().toPyDateTime()
			sectors = self.sectors_spin.value()
			departure = self.departure_edit.currentText()
			arrival = self.arrival_edit.currentText()
			rest_in_flight = self.rest_in_flight_check.isChecked()
			has_frms = self.has_frms_check.isChecked()

			if not crew_member_id or not aircraft_id:
				QMessageBox.warning(self, "Предупреждение", "Выберите члена экипажа и воздушное судно!")
				return

			# Получаем дополнительную информацию о члене экипажа
			conn = sqlite3.connect('fdp_data.db')
			cursor = conn.cursor()
			cursor.execute("SELECT home_base FROM crew_members WHERE id = ?", (crew_member_id,))
			home_base = cursor.fetchone()[0]
			conn.close()

			# Определяем часовые пояса (упрощенная реализация)
			# В реальном приложении нужно использовать API для определения часовых поясов аэропортов
			base_timezone = "Europe/Minsk"  # Предполагаем, что домашняя база в Минске
			local_timezone = "Europe/Minsk"  # Предполагаем, что вылет из Минска

			# Определяем акклиматизацию (упрощенно)
			acclimatization_status = self.calculator.determine_acclimatization(
				base_timezone, local_timezone, 0
			)

			# Рассчитываем максимальное FDP
			max_fdp = self.calculator.calculate_max_fdp(
				start_time, sectors, acclimatization_status, has_frms
			)

			# Рассчитываем необходимый отдых
			rest_time = self.calculator.calculate_required_rest(max_fdp, True)

			# Формируем результат
			result = f"ПЛАН ПОЛЕТА\n"
			result += "=" * 50 + "\n\n"
			result += f"Член экипажа: {self.crew_member_combo.currentText()}\n"
			result += f"Воздушное судно: {self.aircraft_combo.currentText()}\n"
			result += f"Маршрут: {departure} -> {arrival}\n"
			result += f"Дата и время начала: {start_time.strftime('%d.%m.%Y %H:%M')}\n"
			result += f"Количество секторов: {sectors}\n"
			result += f"Отдых в полете: {'Да' if rest_in_flight else 'Нет'}\n"
			result += f"Наличие FRMS: {'Да' if has_frms else 'Нет'}\n\n"
			result += f"Максимальное FDP: {max_fdp}\n"
			result += f"Необходимый отдых после: {rest_time}\n\n"

			# Проверяем лимиты
			planned_flight_time = timedelta(hours=2)  # Примерное время полета
			limits = self.calculator.check_limits(crew_member_id, planned_flight_time, sqlite3.connect('fdp_data.db'))

			result += "ПРОВЕРКА ЛИМИТОВ:\n"
			for limit_name, limit_data in limits.items():
				if limit_name == "last_28_days":
					result += f"За последние 28 дней: {limit_data['current']} / {limit_data['limit']}"
					if limit_data['exceeded']:
						result += " ⚠️ ПРЕВЫШЕНИЕ!\n"
					else:
						result += f" (осталось: {limit_data['remaining']})\n"

			self.result_text.setPlainText(result)

		except Exception as e:
			QMessageBox.critical(self, "Ошибка", f"Не удалось рассчитать план: {str(e)}")

	def save_duty(self):
		"""Сохраняет задание в базу данных"""
		try:
			# Получаем выбранные значения
			crew_member_id = self.crew_member_combo.currentData()
			aircraft_id = self.aircraft_combo.currentData()
			start_time = self.fdp_start_edit.dateTime().toPyDateTime()
			sectors = self.sectors_spin.value()
			departure = self.departure_edit.currentText()
			arrival = self.arrival_edit.currentText()
			rest_in_flight = self.rest_in_flight_check.isChecked()
			has_frms = self.has_frms_check.isChecked()

			if not crew_member_id or not aircraft_id:
				QMessageBox.warning(self, "Предупреждение", "Выберите члена экипажа и воздушное судно!")
				return

			# Сохраняем в базу данных
			conn = sqlite3.connect('fdp_data.db')
			cursor = conn.cursor()

			cursor.execute('''
                INSERT INTO duties (crew_member_id, aircraft_id, start_time, scheduled_sectors, 
                                  departure_airport, arrival_airport, rest_in_flight, has_frms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (crew_member_id, aircraft_id, start_time, sectors, departure, arrival, rest_in_flight, has_frms))

			conn.commit()
			conn.close()

			QMessageBox.information(self, "Успех", "Задание успешно сохранено!")

		except Exception as e:
			QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить задание: {str(e)}")