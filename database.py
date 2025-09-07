import sqlite3
import os
from datetime import datetime


class Database:
	def __init__(self, db_name='fdp_data.db'):
		self.db_name = db_name
		self.create_tables()

	def create_connection(self):
		"""Создает соединение с базой данных"""
		conn = None
		try:
			conn = sqlite3.connect(self.db_name)
			return conn
		except sqlite3.Error as e:
			print(f"Ошибка подключения к базе данных: {e}")
		return conn

	def create_tables(self):
		"""Создает все необходимые таблицы в базе данных"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()

				# Таблица "Члены экипажа"
				cursor.execute('''
                CREATE TABLE IF NOT EXISTS crew_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    home_base TEXT NOT NULL,
                    is_pilot BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')

				# Таблица "Воздушные суда"
				cursor.execute('''
                CREATE TABLE IF NOT EXISTS aircrafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    registration TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    rest_facility_class INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')

				# Таблица "Задания" (Duties)
				cursor.execute('''
                CREATE TABLE IF NOT EXISTS duties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crew_member_id INTEGER NOT NULL,
                    aircraft_id INTEGER NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    duty_type TEXT NOT NULL DEFAULT 'flight',
                    fdp_start_time TIMESTAMP,
                    fdp_end_time TIMESTAMP,
                    scheduled_sectors INTEGER,
                    actual_sectors INTEGER,
                    rest_in_flight BOOLEAN DEFAULT FALSE,
                    rest_facility_used INTEGER,
                    time_acclimatized TEXT,
                    base_time TEXT,
                    is_acclimatized BOOLEAN,
                    departure_airport TEXT NOT NULL,
                    arrival_airport TEXT NOT NULL,
                    has_frms BOOLEAN DEFAULT FALSE,
                    status TEXT DEFAULT 'planned',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (crew_member_id) REFERENCES crew_members (id),
                    FOREIGN KEY (aircraft_id) REFERENCES aircrafts (id)
                )
                ''')

				# Таблица "Полетное время" (Flights)
				cursor.execute('''
                CREATE TABLE IF NOT EXISTS flights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    duty_id INTEGER NOT NULL,
                    departure_airport TEXT NOT NULL,
                    arrival_airport TEXT NOT NULL,
                    off_block_time TIMESTAMP,
                    on_block_time TIMESTAMP,
                    flight_time INTEGER,
                    sector_number INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (duty_id) REFERENCES duties (id)
                )
                ''')

				# Таблица "Периоды отдыха"
				cursor.execute('''
                CREATE TABLE IF NOT EXISTS rest_periods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crew_member_id INTEGER NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    rest_type TEXT NOT NULL,
                    location TEXT,
                    was_reduced BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (crew_member_id) REFERENCES crew_members (id)
                )
                ''')

				# Таблица "Режим ожидания"
				cursor.execute('''
                CREATE TABLE IF NOT EXISTS standby_periods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crew_member_id INTEGER NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    standby_type TEXT NOT NULL,
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (crew_member_id) REFERENCES crew_members (id)
                )
                ''')

				# Таблица "Резерв"
				cursor.execute('''
                CREATE TABLE IF NOT EXISTS reserve_periods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crew_member_id INTEGER NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (crew_member_id) REFERENCES crew_members (id)
                )
                ''')

				# Таблица "Настройки приложения"
				cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')

				# Вставляем начальные настройки
				cursor.execute('''
                INSERT OR IGNORE INTO app_settings (setting_key, setting_value, description)
                VALUES 
                    ('default_home_base', 'UMMS', 'Основное место базирования по умолчанию'),
                    ('max_fdp_extension', '1', 'Максимальное продление FDP в часах'),
                    ('min_rest_period', '12', 'Минимальный период отдыха в часах'),
                    ('timezone', 'Europe/Minsk', 'Часовой пояс по умолчанию')
                ''')

				# Создаем индексы для улучшения производительности
				cursor.execute('CREATE INDEX IF NOT EXISTS idx_duties_crew_member_id ON duties (crew_member_id)')
				cursor.execute('CREATE INDEX IF NOT EXISTS idx_duties_start_time ON duties (start_time)')
				cursor.execute('CREATE INDEX IF NOT EXISTS idx_flights_duty_id ON flights (duty_id)')
				cursor.execute(
					'CREATE INDEX IF NOT EXISTS idx_rest_periods_crew_member_id ON rest_periods (crew_member_id)')
				cursor.execute('CREATE INDEX IF NOT EXISTS idx_rest_periods_start_time ON rest_periods (start_time)')

				conn.commit()
				print("База данных и все таблицы успешно созданы!")

			except sqlite3.Error as e:
				print(f"Ошибка при создании таблиц: {e}")
			finally:
				conn.close()
		else:
			print("Ошибка! Не удалось создать соединение с базой данных.")

	# Методы для работы с членами экипажа
	def add_crew_member(self, name, home_base, is_pilot=True):
		"""Добавляет нового члена экипажа в базу данных"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute(
					"INSERT INTO crew_members (name, home_base, is_pilot) VALUES (?, ?, ?)",
					(name, home_base, is_pilot)
				)
				conn.commit()
				return cursor.lastrowid
			except sqlite3.Error as e:
				print(f"Ошибка при добавлении члена экипажа: {e}")
			finally:
				conn.close()
		return None

	def get_all_crew_members(self):
		"""Возвращает всех членов экипажа из базы данных"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute("SELECT id, name, home_base, is_pilot FROM crew_members")
				return cursor.fetchall()
			except sqlite3.Error as e:
				print(f"Ошибка при получении членов экипажа: {e}")
			finally:
				conn.close()
		return []

	def get_crew_member(self, crew_member_id):
		"""Возвращает данные о конкретном члене экипажа"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute("SELECT id, name, home_base, is_pilot FROM crew_members WHERE id = ?", (crew_member_id,))
				return cursor.fetchone()
			except sqlite3.Error as e:
				print(f"Ошибка при получении члена экипажа: {e}")
			finally:
				conn.close()
		return None

	def update_crew_member(self, crew_member_id, name, home_base, is_pilot):
		"""Обновляет данные члена экипажа"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute(
					"UPDATE crew_members SET name = ?, home_base = ?, is_pilot = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
					(name, home_base, is_pilot, crew_member_id)
				)
				conn.commit()
				return True
			except sqlite3.Error as e:
				print(f"Ошибка при обновлении члена экипажа: {e}")
			finally:
				conn.close()
		return False

	def delete_crew_member(self, crew_member_id):
		"""Удаляет члена экипажа из базы данных"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute("DELETE FROM crew_members WHERE id = ?", (crew_member_id,))
				conn.commit()
				return True
			except sqlite3.Error as e:
				print(f"Ошибка при удалении члена экипажа: {e}")
			finally:
				conn.close()
		return False

	# Методы для работы с воздушными судами
	def add_aircraft(self, registration, aircraft_type, rest_facility_class=None):
		"""Добавляет новое воздушное судно в базу данных"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute(
					"INSERT INTO aircrafts (registration, type, rest_facility_class) VALUES (?, ?, ?)",
					(registration, aircraft_type, rest_facility_class)
				)
				conn.commit()
				return cursor.lastrowid
			except sqlite3.Error as e:
				print(f"Ошибка при добавлении воздушного судна: {e}")
			finally:
				conn.close()
		return None

	def get_all_aircrafts(self):
		"""Возвращает все воздушные суда из базы данных"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute("SELECT id, registration, type, rest_facility_class FROM aircrafts")
				return cursor.fetchall()
			except sqlite3.Error as e:
				print(f"Ошибка при получении воздушных судов: {e}")
			finally:
				conn.close()
		return []

	def get_aircraft(self, aircraft_id):
		"""Возвращает данные о конкретном воздушном судне"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute("SELECT id, registration, type, rest_facility_class FROM aircrafts WHERE id = ?",
				               (aircraft_id,))
				return cursor.fetchone()
			except sqlite3.Error as e:
				print(f"Ошибка при получении воздушного судна: {e}")
			finally:
				conn.close()
		return None

	def update_aircraft(self, aircraft_id, registration, aircraft_type, rest_facility_class):
		"""Обновляет данные воздушного судна"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute(
					"UPDATE aircrafts SET registration = ?, type = ?, rest_facility_class = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
					(registration, aircraft_type, rest_facility_class, aircraft_id)
				)
				conn.commit()
				return True
			except sqlite3.Error as e:
				print(f"Ошибка при обновлении воздушного судна: {e}")
			finally:
				conn.close()
		return False

	def delete_aircraft(self, aircraft_id):
		"""Удаляет воздушное судно из базы данных"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute("DELETE FROM aircrafts WHERE id = ?", (aircraft_id,))
				conn.commit()
				return True
			except sqlite3.Error as e:
				print(f"Ошибка при удалении воздушного судна: {e}")
			finally:
				conn.close()
		return False

	# Методы для работы с заданиями
	def add_duty(self, crew_member_id, aircraft_id, start_time, scheduled_sectors,
	             departure_airport, arrival_airport, rest_in_flight=False, has_frms=False):
		"""Добавляет новое задание в базу данных"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute('''
                    INSERT INTO duties (crew_member_id, aircraft_id, start_time, scheduled_sectors, 
                                      departure_airport, arrival_airport, rest_in_flight, has_frms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (crew_member_id, aircraft_id, start_time, scheduled_sectors,
				      departure_airport, arrival_airport, rest_in_flight, has_frms))
				conn.commit()
				return cursor.lastrowid
			except sqlite3.Error as e:
				print(f"Ошибка при добавлении задания: {e}")
			finally:
				conn.close()
		return None

	def get_all_duties(self):
		"""Возвращает все задания из базы данных"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute('''
                    SELECT d.id, d.crew_member_id, cm.name, d.aircraft_id, a.registration, 
                           d.start_time, d.scheduled_sectors, d.departure_airport, d.arrival_airport,
                           d.rest_in_flight, d.has_frms, d.status
                    FROM duties d
                    JOIN crew_members cm ON d.crew_member_id = cm.id
                    JOIN aircrafts a ON d.aircraft_id = a.id
                    ORDER BY d.start_time
                ''')
				return cursor.fetchall()
			except sqlite3.Error as e:
				print(f"Ошибка при получении заданий: {e}")
			finally:
				conn.close()
		return []

	def get_duties_by_crew_member(self, crew_member_id, start_date=None, end_date=None):
		"""Возвращает задания для конкретного члена экипажа за указанный период"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				query = '''
                    SELECT d.id, d.crew_member_id, cm.name, d.aircraft_id, a.registration, 
                           d.start_time, d.scheduled_sectors, d.departure_airport, d.arrival_airport,
                           d.rest_in_flight, d.has_frms, d.status
                    FROM duties d
                    JOIN crew_members cm ON d.crew_member_id = cm.id
                    JOIN aircrafts a ON d.aircraft_id = a.id
                    WHERE d.crew_member_id = ?
                '''
				params = [crew_member_id]

				if start_date and end_date:
					query += " AND d.start_time BETWEEN ? AND ?"
					params.extend([start_date, end_date])

				query += " ORDER BY d.start_time"

				cursor.execute(query, params)
				return cursor.fetchall()
			except sqlite3.Error as e:
				print(f"Ошибка при получении заданий: {e}")
			finally:
				conn.close()
		return []

	def update_duty_status(self, duty_id, status):
		"""Обновляет статус задания"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute(
					"UPDATE duties SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
					(status, duty_id)
				)
				conn.commit()
				return True
			except sqlite3.Error as e:
				print(f"Ошибка при обновлении статуса задания: {e}")
			finally:
				conn.close()
		return False

	def delete_duty(self, duty_id):
		"""Удаляет задание из базы данных"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute("DELETE FROM duties WHERE id = ?", (duty_id,))
				conn.commit()
				return True
			except sqlite3.Error as e:
				print(f"Ошибка при удалении задания: {e}")
			finally:
				conn.close()
		return False

	# Методы для работы с настройками
	def get_setting(self, setting_key):
		"""Возвращает значение настройки по ключу"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute("SELECT setting_value FROM app_settings WHERE setting_key = ?", (setting_key,))
				result = cursor.fetchone()
				return result[0] if result else None
			except sqlite3.Error as e:
				print(f"Ошибка при получении настройки: {e}")
			finally:
				conn.close()
		return None

	def update_setting(self, setting_key, setting_value):
		"""Обновляет значение настройки"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute(
					"UPDATE app_settings SET setting_value = ?, updated_at = CURRENT_TIMESTAMP WHERE setting_key = ?",
					(setting_value, setting_key)
				)
				conn.commit()
				return True
			except sqlite3.Error as e:
				print(f"Ошибка при обновлении настройки: {e}")
			finally:
				conn.close()
		return False

	# Дополнительные методы для отчетности и анализа
	def get_flight_time_stats(self, crew_member_id, start_date, end_date):
		"""Возвращает статистику полетного времени для члена экипажа за период"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute('''
                    SELECT SUM(f.flight_time) as total_flight_time,
                           COUNT(f.id) as total_flights,
                           COUNT(DISTINCT DATE(f.off_block_time)) as flight_days
                    FROM flights f
                    JOIN duties d ON f.duty_id = d.id
                    WHERE d.crew_member_id = ? 
                    AND f.off_block_time BETWEEN ? AND ?
                ''', (crew_member_id, start_date, end_date))
				return cursor.fetchone()
			except sqlite3.Error as e:
				print(f"Ошибка при получении статистики полетного времени: {e}")
			finally:
				conn.close()
		return (0, 0, 0)

	def get_rest_periods(self, crew_member_id, start_date, end_date):
		"""Возвращает периоды отдыха для члена экипажа за период"""
		conn = self.create_connection()
		if conn is not None:
			try:
				cursor = conn.cursor()
				cursor.execute('''
                    SELECT start_time, end_time, rest_type, location
                    FROM rest_periods
                    WHERE crew_member_id = ? 
                    AND start_time BETWEEN ? AND ?
                    ORDER BY start_time
                ''', (crew_member_id, start_date, end_date))
				return cursor.fetchall()
			except sqlite3.Error as e:
				print(f"Ошибка при получении периодов отдыха: {e}")
			finally:
				conn.close()
		return []


# Создаем глобальный экземпляр базы данных для использования во всем приложении
db = Database()

if __name__ == "__main__":
	# Тестирование базы данных при прямом запуске
	db = Database()
	print("База данных инициализирована")

	# Добавляем тестовые данные
	crew_id = db.add_crew_member("Иванов Иван Иванович", "UMMS", True)
	aircraft_id = db.add_aircraft("EW-123AB", "Boeing 737-800", 2)

	print(f"Добавлен член экипажа с ID: {crew_id}")
	print(f"Добавлено воздушное судно с ID: {aircraft_id}")

	# Получаем всех членов экипажа
	crew_members = db.get_all_crew_members()
	print("Члены экипажа:")
	for member in crew_members:
		print(member)

	# Получаем все воздушные суда
	aircrafts = db.get_all_aircrafts()
	print("Воздушные суда:")
	for aircraft in aircrafts:
		print(aircraft)