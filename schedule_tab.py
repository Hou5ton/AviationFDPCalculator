# schedule_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QComboBox, QLabel, QPushButton,
                             QHeaderView, QMessageBox)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QBrush
import sqlite3
from datetime import datetime, timedelta


class ScheduleTab(QWidget):
	def __init__(self):
		super().__init__()
		self.init_ui()
		self.load_crew_members()

	def init_ui(self):
		main_layout = QVBoxLayout()

		# Панель управления
		control_layout = QHBoxLayout()

		control_layout.addWidget(QLabel("Член экипажа:"))
		self.crew_member_combo = QComboBox()
		control_layout.addWidget(self.crew_member_combo)

		control_layout.addWidget(QLabel("Неделя:"))
		self.week_combo = QComboBox()

		# Добавляем недели на месяц вперед
		current_date = QDate.currentDate()
		for i in range(4):
			week_start = current_date.addDays(i * 7)
			week_end = week_start.addDays(6)
			self.week_combo.addItem(f"{week_start.toString('dd.MM.yyyy')} - {week_end.toString('dd.MM.yyyy')}",
			                        week_start)

		control_layout.addWidget(self.week_combo)

		self.load_btn = QPushButton("Загрузить график")
		self.load_btn.clicked.connect(self.load_schedule)
		control_layout.addWidget(self.load_btn)

		main_layout.addLayout(control_layout)

		# Таблица графика
		self.schedule_table = QTableWidget()
		self.schedule_table.setColumnCount(8)  # Дни недели + заголовок
		self.schedule_table.setHorizontalHeaderLabels(["Время", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"])
		self.schedule_table.verticalHeader().setDefaultSectionSize(30)
		self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

		# Заполняем временные интервалы
		self.schedule_table.setRowCount(24)  # Часы дня
		for hour in range(24):
			time_item = QTableWidgetItem(f"{hour:02d}:00")
			time_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
			self.schedule_table.setItem(hour, 0, time_item)

		main_layout.addWidget(self.schedule_table)

		self.setLayout(main_layout)

	def load_crew_members(self):
		"""Загружает список членов экипажа из базы данных"""
		try:
			conn = sqlite3.connect('fdp_data.db')
			cursor = conn.cursor()
			cursor.execute("SELECT id, name FROM crew_members")
			crew_data = cursor.fetchall()
			conn.close()

			self.crew_member_combo.clear()
			for crew_id, name in crew_data:
				self.crew_member_combo.addItem(name, crew_id)

		except sqlite3.Error as e:
			QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить членов экипажа: {e}")

	def load_schedule(self):
		"""Загружает график для выбранного члена экипажа и недели"""
		crew_member_id = self.crew_member_combo.currentData()
		week_start = self.week_combo.currentData()

		if not crew_member_id:
			QMessageBox.warning(self, "Предупреждение", "Выберите члена экипажа!")
			return

		# Очищаем таблицу
		for row in range(24):
			for col in range(1, 8):
				self.schedule_table.setItem(row, col, QTableWidgetItem(""))

		try:
			conn = sqlite3.connect('fdp_data.db')
			cursor = conn.cursor()

			# Получаем задания для выбранной недели
			week_end = week_start.addDays(6)
			cursor.execute("""
                SELECT start_time, scheduled_sectors, departure_airport, arrival_airport 
                FROM duties 
                WHERE crew_member_id = ? AND date(start_time) BETWEEN ? AND ?
            """, (crew_member_id, week_start.toString("yyyy-MM-dd"), week_end.toString("yyyy-MM-dd")))

			duties = cursor.fetchall()
			conn.close()

			# Обрабатываем каждое задание
			for start_time, sectors, departure, arrival in duties:
				duty_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").date()
				duty_weekday = duty_date.weekday()  # 0 - понедельник, 6 - воскресенье

				# Определяем продолжительность задания (упрощенно)
				duty_duration = min(sectors * 2, 8)  # Примерно 2 часа на сектор, макс 8 часов

				# Определяем цвет в зависимости от типа задания
				duty_color = QColor(255, 200, 200)  # Светло-красный для работы

				# Заполняем ячейки в таблице
				duty_hour = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").hour
				for hour in range(duty_hour, min(duty_hour + duty_duration, 24)):
					item = QTableWidgetItem(f"{departure}→{arrival} ({sectors} сек.)")
					item.setBackground(QBrush(duty_color))
					item.setToolTip(f"Рейс: {departure}→{arrival}\nСекторов: {sectors}\nНачало: {start_time}")
					self.schedule_table.setItem(hour, duty_weekday + 1, item)

		except Exception as e:
			QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить график: {str(e)}")