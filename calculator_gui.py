# calculator_gui.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QLineEdit, QComboBox, QSpinBox, QDateTimeEdit,
                             QPushButton, QTextEdit, QFormLayout, QCheckBox,
                             QMessageBox, QScrollArea)
from PyQt6.QtCore import QDateTime, Qt
from calculator import FDPCalculator, AcclimatizationStatus
from datetime import datetime
import pytz


class SegmentWidget(QWidget):
	def __init__(self, segment_number, parent=None):
		super().__init__(parent)
		self.segment_number = segment_number
		self.parent_calculator = parent
		self.init_ui()

	def init_ui(self):
		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)

		# Номер сегмента с эмодзи
		number_label = QLabel(f"{self.get_emoji_number()}")
		number_label.setFixedWidth(30)
		layout.addWidget(number_label)

		# Эмодзи вылета
		departure_emoji = QLabel("🛫")
		departure_emoji.setFixedWidth(30)
		layout.addWidget(departure_emoji)

		# Аэропорт вылета
		self.departure_combo = QComboBox()
		self.departure_combo.setEditable(True)
		self.departure_combo.addItems(["UMMS", "UEEE", "UWKD", "UUDD", "URSS", "EKCH", "EDDF", "LFPG"])
		self.departure_combo.setMinimumWidth(120)
		layout.addWidget(self.departure_combo)

		# Эмодзи назначения
		arrival_emoji = QLabel("🛬")
		arrival_emoji.setFixedWidth(30)
		layout.addWidget(arrival_emoji)

		# Аэропорт назначения
		self.arrival_combo = QComboBox()
		self.arrival_combo.setEditable(True)
		self.arrival_combo.addItems(["UMMS", "UEEE", "UWKD", "UUDD", "URSS", "EKCH", "EDDF", "LFPG"])
		self.arrival_combo.setMinimumWidth(120)
		layout.addWidget(self.arrival_combo)

		# Кнопки (будут обновляться родителем)
		self.add_btn = QPushButton("➕")
		self.add_btn.setFixedSize(30, 30)
		self.add_btn.clicked.connect(self.add_segment)

		self.remove_btn = QPushButton("➖")
		self.remove_btn.setFixedSize(30, 30)
		self.remove_btn.clicked.connect(self.remove_segment)

		# Контейнер для кнопок
		self.buttons_layout = QHBoxLayout()
		self.buttons_layout.addWidget(self.add_btn)
		self.buttons_layout.addWidget(self.remove_btn)
		self.buttons_layout.setSpacing(5)

		layout.addLayout(self.buttons_layout)
		layout.addStretch()

		self.setLayout(layout)

	def get_emoji_number(self):
		"""Возвращает номер сегмента с эмодзи"""
		emoji_numbers = {
			1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
			6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
		}
		return emoji_numbers.get(self.segment_number, f"{self.segment_number}")

	def add_segment(self):
		"""Добавляет новый сегмент"""
		if self.parent_calculator:
			self.parent_calculator.add_segment_after(self.segment_number)

	def remove_segment(self):
		"""Удаляет текущий сегмент"""
		if self.parent_calculator:
			self.parent_calculator.remove_segment(self.segment_number)

	def update_buttons_visibility(self, is_last_segment, total_segments):
		"""Обновляет видимость кнопок в зависимости от позиции сегмента"""
		if total_segments == 1:
			# Единственный сегмент: только кнопка добавления
			self.add_btn.setVisible(True)
			self.remove_btn.setVisible(False)
		elif is_last_segment:
			# Последний сегмент: обе кнопки
			self.add_btn.setVisible(True)
			self.remove_btn.setVisible(True)
		else:
			# Промежуточный сегмент: только кнопка удаления
			self.add_btn.setVisible(False)
			self.remove_btn.setVisible(True)


class CalculatorTab(QWidget):
	def __init__(self):
		super().__init__()
		self.calculator = FDPCalculator()
		self.segment_widgets = []  # Список виджетов сегментов
		self.init_ui()

	def init_ui(self):
		main_layout = QVBoxLayout()

		# Создаем скроллируемую область
		scroll_area = QScrollArea()
		scroll_widget = QWidget()
		scroll_layout = QVBoxLayout(scroll_widget)

		# Секция ввода параметров
		input_group = QGroupBox("Параметры расчета")
		input_layout = QVBoxLayout()

		# Секция маршрута
		route_group = QGroupBox("Маршрут полета")
		self.route_layout = QVBoxLayout()

		# Создаем первый сегмент
		self.add_initial_segment()

		route_group.setLayout(self.route_layout)
		input_layout.addWidget(route_group)

		# Основные параметры расчета
		params_group = QGroupBox("Параметры расчета")
		params_layout = QFormLayout()

		# Базовый часовой пояс
		self.base_timezone_combo = QComboBox()
		self.base_timezone_combo.addItems(pytz.all_timezones)
		self.base_timezone_combo.setCurrentText("Europe/Minsk")
		self.base_timezone_combo.setEditable(True)
		params_layout.addRow("Базовый часовой пояс:", self.base_timezone_combo)

		# Часовой пояс места начала FDP
		self.local_timezone_combo = QComboBox()
		self.local_timezone_combo.addItems(pytz.all_timezones)
		self.local_timezone_combo.setCurrentText("Europe/Minsk")
		self.local_timezone_combo.setEditable(True)
		params_layout.addRow("Часовой пояс места начала FDP:", self.local_timezone_combo)

		# Время с начала выполнения обязанностей
		self.hours_since_duty_spin = QSpinBox()
		self.hours_since_duty_spin.setRange(0, 500)
		self.hours_since_duty_spin.setValue(0)
		params_layout.addRow("Часов с начала выполнения обязанностей:", self.hours_since_duty_spin)

		# Дата и время начала FDP
		self.fdp_start_edit = QDateTimeEdit()
		self.fdp_start_edit.setDateTime(QDateTime.currentDateTime())
		self.fdp_start_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
		params_layout.addRow("Дата и время начала FDP:", self.fdp_start_edit)

		# Наличие FRMS
		self.has_frms_combo = QComboBox()
		self.has_frms_combo.addItems(["Нет", "Да"])
		params_layout.addRow("Наличие FRMS:", self.has_frms_combo)

		# Класс места для отдыха
		self.rest_facility_combo = QComboBox()
		self.rest_facility_combo.addItems(["Не предусмотрен", "1 класс", "2 класс", "3 класс"])
		params_layout.addRow("Класс места для отдыха:", self.rest_facility_combo)

		params_group.setLayout(params_layout)
		input_layout.addWidget(params_group)

		input_group.setLayout(input_layout)
		scroll_layout.addWidget(input_group)

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

		scroll_layout.addLayout(button_layout)

		# Поле вывода результатов
		self.result_text = QTextEdit()
		self.result_text.setReadOnly(True)
		scroll_layout.addWidget(self.result_text)

		# Настройка скроллируемой области
		scroll_area.setWidget(scroll_widget)
		scroll_area.setWidgetResizable(True)
		scroll_area.setMinimumHeight(600)

		main_layout.addWidget(scroll_area)
		self.setLayout(main_layout)

	def add_initial_segment(self):
		"""Добавляет начальный сегмент маршрута"""
		segment = SegmentWidget(1, self)
		self.segment_widgets.append(segment)
		self.route_layout.addWidget(segment)
		self.update_buttons_visibility()

	def add_segment_after(self, segment_number):
		"""Добавляет новый сегмент после указанного"""
		if len(self.segment_widgets) >= 10:
			QMessageBox.information(self, "Информация", "Максимальное количество сегментов маршрута - 10")
			return

		# Находим индекс текущего сегмента
		current_index = segment_number - 1

		# Создаем новый сегмент
		new_segment_number = segment_number + 1
		new_segment = SegmentWidget(new_segment_number, self)

		# Автоматически заполняем аэропорт вылета из предыдущего сегмента
		if current_index >= 0 and current_index < len(self.segment_widgets):
			prev_segment = self.segment_widgets[current_index]
			new_segment.departure_combo.setCurrentText(prev_segment.arrival_combo.currentText())

		# Вставляем новый сегмент после текущего
		self.segment_widgets.insert(current_index + 1, new_segment)

		# Перестраиваем все сегменты с новыми номерами
		self.rebuild_segments()

	def remove_segment(self, segment_number):
		"""Удаляет указанный сегмент"""
		if len(self.segment_widgets) <= 1:
			QMessageBox.warning(self, "Предупреждение", "Нельзя удалить единственный сегмент маршрута")
			return

		# Находим индекс удаляемого сегмента
		remove_index = segment_number - 1

		if 0 <= remove_index < len(self.segment_widgets):
			# Удаляем сегмент
			segment_to_remove = self.segment_widgets[remove_index]
			self.route_layout.removeWidget(segment_to_remove)
			segment_to_remove.deleteLater()
			self.segment_widgets.pop(remove_index)

			# Перестраиваем оставшиеся сегменты
			self.rebuild_segments()

	def rebuild_segments(self):
		"""Полностью перестраивает все сегменты с правильными номерами"""
		# Удаляем все сегменты из layout
		for i in reversed(range(self.route_layout.count())):
			item = self.route_layout.itemAt(i)
			if item.widget():
				item.widget().setParent(None)

		# Создаем новые сегменты с правильными номерами
		new_segments = []
		for i, old_segment in enumerate(self.segment_widgets):
			new_segment_number = i + 1
			new_segment = SegmentWidget(new_segment_number, self)

			# Сохраняем значения из старого сегмента
			if i < len(self.segment_widgets):
				new_segment.departure_combo.setCurrentText(old_segment.departure_combo.currentText())
				new_segment.arrival_combo.setCurrentText(old_segment.arrival_combo.currentText())

			new_segments.append(new_segment)
			self.route_layout.addWidget(new_segment)

		# Заменяем старый список сегментов новым
		self.segment_widgets = new_segments

		# Обновляем видимость кнопок
		self.update_buttons_visibility()

	def update_buttons_visibility(self):
		"""Обновляет видимость кнопок для всех сегментов"""
		total_segments = len(self.segment_widgets)

		for i, segment in enumerate(self.segment_widgets):
			is_last_segment = (i == total_segments - 1)
			segment.update_buttons_visibility(is_last_segment, total_segments)

	def get_route_segments(self):
		"""Возвращает список сегментов маршрута"""
		segments = []
		for i, segment in enumerate(self.segment_widgets):
			segments.append({
				'segment': i + 1,
				'departure': segment.departure_combo.currentText(),
				'arrival': segment.arrival_combo.currentText()
			})
		return segments

	def get_sectors_count(self):
		"""Возвращает количество секторов (сегментов маршрута)"""
		return len(self.segment_widgets)

	def calculate_acclimatization(self):
		try:
			base_timezone = self.base_timezone_combo.currentText()
			local_timezone = self.local_timezone_combo.currentText()
			hours_since_duty = self.hours_since_duty_spin.value()

			status = self.calculator.determine_acclimatization(
				base_timezone, local_timezone, hours_since_duty
			)

			# Получаем информацию о маршруте
			route_segments = self.get_route_segments()
			route_info = "Маршрут:\n"
			for segment in route_segments:
				route_info += f"  {segment['segment']}. {segment['departure']} → {segment['arrival']}\n"

			result = f"Статус акклиматизации: {status.value}\n\n"
			result += "Расшифровка:\n"
			result += "  'Б' - акклиматизирован к местному времени базового часового пояса\n"
			result += "  'В' - акклиматизирован к местному времени часового пояса, где начинается следующее FDP\n"
			result += "  'Н' - неопределенное состояние акклиматизации\n\n"

			result += route_info + "\n"
			result += f"Количество секторов: {self.get_sectors_count()}\n"
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
			sectors = self.get_sectors_count()
			has_frms = self.has_frms_combo.currentText() == "Да"

			# Проверяем, что маршрут задан
			if sectors < 1:
				QMessageBox.warning(self, "Предупреждение", "Задайте хотя бы один сегмент маршрута!")
				return

			# Определяем акклиматизацию
			status = self.calculator.determine_acclimatization(
				base_timezone, local_timezone, hours_since_duty
			)

			# Рассчитываем максимальное FDP
			max_fdp = self.calculator.calculate_max_fdp(
				start_time, sectors, status, has_frms
			)

			# Формируем информацию о маршруте
			route_info = "Маршрут:\n"
			for segment in self.get_route_segments():
				route_info += f"  {segment['segment']}. {segment['departure']} → {segment['arrival']}\n"

			result = f"Статус акклиматизации: {status.value}\n"
			result += f"Максимальное FDP: {max_fdp}\n\n"

			result += route_info + "\n"
			result += f"Количество секторов: {sectors}\n"
			result += f"Дата и время начала FDP: {start_time.strftime('%d.%m.%Y %H:%M')}\n"
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
			sectors = self.get_sectors_count()
			has_frms = self.has_frms_combo.currentText() == "Да"
			rest_facility = self.rest_facility_combo.currentText()

			# Проверяем, что маршрут задан
			if sectors < 1:
				QMessageBox.warning(self, "Предупреждение", "Задайте хотя бы один сегмент маршрута!")
				return

			# Определяем акклиматизацию
			status = self.calculator.determine_acclimatization(
				base_timezone, local_timezone, hours_since_duty
			)

			# Рассчитываем максимальное FDP
			max_fdp = self.calculator.calculate_max_fdp(
				start_time, sectors, status, has_frms
			)

			# Рассчитываем необходимый отдых
			rest_time = self.calculator.calculate_required_rest(max_fdp, True)

			# Если выбран класс места для отдыха, рассчитываем отдых в полете
			in_flight_rest = None
			if rest_facility != "Не предусмотрен":
				rest_class = int(rest_facility[0])
				in_flight_rest = self.calculator.calculate_min_in_flight_rest(max_fdp, rest_class)

			# Формируем информацию о маршруте
			route_info = "Маршрут:\n"
			for segment in self.get_route_segments():
				route_info += f"  {segment['segment']}. {segment['departure']} → {segment['arrival']}\n"

			result = f"Максимальное FDP: {max_fdp}\n"
			result += f"Необходимый отдых после FDP: {rest_time}\n"

			if in_flight_rest:
				result += f"Минимальный отдых в полете ({rest_facility}): {in_flight_rest}\n"

			result += f"\nДетали расчета:\n"
			result += route_info + "\n"
			result += f"Количество секторов: {sectors}\n"
			result += f"Статус акклиматизации: {status.value}\n"
			result += f"Дата и время начала FDP: {start_time.strftime('%d.%m.%Y %H:%M')}\n"
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
			sectors = self.get_sectors_count()

			# Проверяем, что маршрут задан
			if sectors < 1:
				QMessageBox.warning(self, "Предупреждение", "Задайте хотя бы один сегмент маршрута!")
				return

			# Рассчитываем продление без отдыха
			extension = self.calculator.calculate_extension_without_rest(start_time, sectors)

			# Формируем информацию о маршруте
			route_info = "Маршрут:\n"
			for segment in self.get_route_segments():
				route_info += f"  {segment['segment']}. {segment['departure']} → {segment['arrival']}\n"

			result = f"Предельное значение продления без отдыха в полете: "

			if extension:
				result += f"{extension}\n\n"
				result += route_info + "\n"
				result += f"Количество секторов: {sectors}\n"
				result += f"Дата и время начала FDP: {start_time.strftime('%d.%m.%Y %H:%M')}\n\n"

				result += "Примечание: продление допускается не более двух раз в течение любых 28 последовательных дней, "
				result += "и при каждом продлении необходимо увеличить отдых на 4 часа."
			else:
				result += "не допускается\n\n"
				result += route_info + "\n"
				result += f"Для {sectors} секторов, начинающихся в {start_time.strftime('%H:%M')}, "
				result += "продление без отдыха в полете не разрешено."

			self.result_text.setPlainText(result)

		except Exception as e:
			QMessageBox.critical(self, "Ошибка", f"Не удалось рассчитать продление: {str(e)}")