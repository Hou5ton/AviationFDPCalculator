# calculator_gui.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QLineEdit, QComboBox, QSpinBox, QDateTimeEdit,
                             QPushButton, QTextEdit, QFormLayout, QMessageBox)
from PyQt6.QtCore import QDateTime, Qt
from calculator import FDPCalculator, AcclimatizationStatus
from datetime import datetime
import pytz


class CalculatorTab(QWidget):
	def __init__(self):
		super().__init__()
		self.calculator = FDPCalculator()
		self.init_ui()

	def init_ui(self):
		main_layout = QVBoxLayout()

		# Секция ввода параметров
		input_group = QGroupBox("Параметры расчета")
		input_layout = QFormLayout()

		# Базовый часовой пояс
		self.base_timezone_combo = QComboBox()
		self.base_timezone_combo.addItems(pytz.all_timezones)
		self.base_timezone_combo.setCurrentText("Europe/Minsk")
		self.base_timezone_combo.setEditable(True)
		input_layout.addRow("Базовый часовой пояс:", self.base_timezone_combo)

		# Часовой пояс места начала FDP
		self.local_timezone_combo = QComboBox()
		self.local_timezone_combo.addItems(pytz.all_timezones)
		self.local_timezone_combo.setCurrentText("Europe/Minsk")
		self.local_timezone_combo.setEditable(True)
		input_layout.addRow("Часовой пояс места начала FDP:", self.local_timezone_combo)

		# Время с начала выполнения обязанностей
		self.hours_since_duty_spin = QSpinBox()
		self.hours_since_duty_spin.setRange(0, 500)
		self.hours_since_duty_spin.setValue(0)
		input_layout.addRow("Часов с начала выполнения обязанностей:", self.hours_since_duty_spin)

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

		# Наличие FRMS
		self.has_frms_combo = QComboBox()
		self.has_frms_combo.addItems(["Нет", "Да"])
		input_layout.addRow("Наличие FRMS:", self.has_frms_combo)

		# Класс места для отдыха
		self.rest_facility_combo = QComboBox()
		self.rest_facility_combo.addItems(["Не предусмотрен", "1 класс", "2 класс", "3 класс"])
		input_layout.addRow("Класс места для отдыха:", self.rest_facility_combo)

		input_group.setLayout(input_layout)
		main_layout.addWidget(input_group)

		# Кнопки расчета
		button_layout = QHBoxLayout()

		self.calc_acclimatization_btn = QPushButton("Определить акклиматизацию")
		self.calc_acclimatization_btn.clicked.connect(self.calculate_acclimatization)
		button_layout.addWidget(self.calc_acclimatization_btn)

		self.calc_fdp_btn = QPushButton("Рассчитать FDP")
		self.calc_fdp_btn.clicked.connect(self.calculate_fdp)
		button_layout.addWidget(self.calc_fdp_btn)

		self.calc_rest_btn = QPushButton("Рассчитать отдых")
		self.calc_rest_btn.clicked.connect(self.calculate_rest)
		button_layout.addWidget(self.calc_rest_btn)

		self.calc_extension_btn = QPushButton("Рассчитать продление")
		self.calc_extension_btn.clicked.connect(self.calculate_extension)
		button_layout.addWidget(self.calc_extension_btn)

		main_layout.addLayout(button_layout)

		# Поле вывода результатов
		self.result_text = QTextEdit()
		self.result_text.setReadOnly(True)
		main_layout.addWidget(self.result_text)

		self.setLayout(main_layout)

	def calculate_acclimatization(self):
		try:
			base_timezone = self.base_timezone_combo.currentText()
			local_timezone = self.local_timezone_combo.currentText()
			hours_since_duty = self.hours_since_duty_spin.value()

			status = self.calculator.determine_acclimatization(
				base_timezone, local_timezone, hours_since_duty
			)

			result = f"Статус акклиматизации: {status.value}\n\n"
			result += "Расшифровка:\n"
			result += "  'Б' - акклиматизирован к местному времени базового часового пояса\n"
			result += "  'В' - акклиматизирован к местному времени часового пояса, где начинается следующее FDP\n"
			result += "  'Н' - неопределенное состояние акклиматизации\n\n"

			result += f"Базовый часовой пояс: {base_timezone}\n"
			result += f"Часовой пояс места начала FDP: {local_timezone}\n"
			result += f"Часов с начала выполнения обязанностей: {hours_since_duty}"

			self.result_text.setPlainText(result)

		except Exception as e:
			QMessageBox.critical(self, "Ошибка", f"Не удалось рассчитать акклиматизацию: {str(e)}")

	def calculate_fdp(self):
		try:
			base_timezone = self.base_timezone_combo.currentText()
			local_timezone = self.local_timezone_combo.currentText()
			hours_since_duty = self.hours_since_duty_spin.value()
			start_time = self.fdp_start_edit.dateTime().toPyDateTime()
			sectors = self.sectors_spin.value()
			has_frms = self.has_frms_combo.currentText() == "Да"

			# Определяем акклиматизацию
			status = self.calculator.determine_acclimatization(
				base_timezone, local_timezone, hours_since_duty
			)

			# Рассчитываем максимальное FDP
			max_fdp = self.calculator.calculate_max_fdp(
				start_time, sectors, status, has_frms
			)

			result = f"Статус акклиматизации: {status.value}\n"
			result += f"Максимальное FDP: {max_fdp}\n\n"

			result += f"Дата и время начала FDP: {start_time.strftime('%d.%m.%Y %H:%M')}\n"
			result += f"Количество секторов: {sectors}\n"
			result += f"Наличие FRMS: {'Да' if has_frms else 'Нет'}\n"
			result += f"Базовый часовой пояс: {base_timezone}\n"
			result += f"Часовой пояс места начала FDP: {local_timezone}\n"
			result += f"Часов с начала выполнения обязанностей: {hours_since_duty}"

			self.result_text.setPlainText(result)

		except Exception as e:
			QMessageBox.critical(self, "Ошибка", f"Не удалось рассчитать FDP: {str(e)}")

	def calculate_rest(self):
		try:
			base_timezone = self.base_timezone_combo.currentText()
			local_timezone = self.local_timezone_combo.currentText()
			hours_since_duty = self.hours_since_duty_spin.value()
			start_time = self.fdp_start_edit.dateTime().toPyDateTime()
			sectors = self.sectors_spin.value()
			has_frms = self.has_frms_combo.currentText() == "Да"
			rest_facility = self.rest_facility_combo.currentText()

			# Определяем акклиматизацию
			status = self.calculator.determine_acclimatization(
				base_timezone, local_timezone, hours_since_duty
			)

			# Рассчитываем максимальное FDP
			max_fdp = self.calculator.calculate_max_fdp(
				start_time, sectors, status, has_frms
			)

			# Рассчитываем необходимый отдых
			rest_time = self.calculator.calculate_required_rest(max_fdp, is_at_home_base=True)

			# Если выбран класс места для отдыха, рассчитываем отдых в полете
			in_flight_rest = None
			if rest_facility != "Не предусмотрен":
				rest_class = int(rest_facility[0])
				in_flight_rest = self.calculator.calculate_min_in_flight_rest(max_fdp, rest_class)

			result = f"Максимальное FDP: {max_fdp}\n"
			result += f"Необходимый отдых после FDP: {rest_time}\n"

			if in_flight_rest:
				result += f"Минимальный отдых в полете ({rest_facility}): {in_flight_rest}\n"

			result += f"\nДетали расчета:\n"
			result += f"Статус акклиматизации: {status.value}\n"
			result += f"Дата и время начала FDP: {start_time.strftime('%d.%m.%Y %H:%M')}\n"
			result += f"Количество секторов: {sectors}\n"
			result += f"Наличие FRMS: {'Да' if has_frms else 'Нет'}\n"
			result += f"Класс места для отдыха: {rest_facility}\n"
			result += f"Базовый часовой пояс: {base_timezone}\n"
			result += f"Часовой пояс места начала FDP: {local_timezone}\n"
			result += f"Часов с начала выполнения обязанностей: {hours_since_duty}"

			self.result_text.setPlainText(result)

		except Exception as e:
			QMessageBox.critical(self, "Ошибка", f"Не удалось рассчитать отдых: {str(e)}")

	def calculate_extension(self):
		try:
			start_time = self.fdp_start_edit.dateTime().toPyDateTime()
			sectors = self.sectors_spin.value()

			# Рассчитываем продление без отдыха
			extension = self.calculator.calculate_extension_without_rest(start_time, sectors)

			result = f"Предельное значение продления без отдыха в полете: "

			if extension:
				result += f"{extension}\n\n"
				result += f"Дата и время начала FDP: {start_time.strftime('%d.%m.%Y %H:%M')}\n"
				result += f"Количество секторов: {sectors}\n\n"

				result += "Примечание: продление допускается не более двух раз в течение любых 28 последовательных дней, "
				result += "и при каждом продлении необходимо увеличить отдых на 4 часа."
			else:
				result += "не допускается\n\n"
				result += f"Для {sectors} секторов, начинающихся в {start_time.strftime('%H:%M')}, "
				result += "продление без отдыха в полете не разрешено."

			self.result_text.setPlainText(result)

		except Exception as e:
			QMessageBox.critical(self, "Ошибка", f"Не удалось рассчитать продление: {str(e)}")