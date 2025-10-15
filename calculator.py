# calculator.py
from datetime import datetime, timedelta
import pytz
from enum import Enum


class AcclimatizationStatus(Enum):
	ACCLIMATIZED = 'Б'  # Акклиматизирован к базовому времени
	ACCLIMATIZED_TO_NEW = 'В'  # Акклиматизирован к новому времени
	UNDEFINED = 'Н'  # Неопределенное состояние


class FDPCalculator:
	def __init__(self):
		# Таблицы для расчетов (на основе приложений документа)

		# Приложение 1: Максимальное служебное полетное время, когда состояние акклиматизации
		# членов экипажа ВС не определено и эксплуатант ВС внедрил FRMS
		self.appendix1_values = {
			1: timedelta(hours=12),
			2: timedelta(hours=12),
			3: timedelta(hours=11, minutes=30),
			4: timedelta(hours=11),
			5: timedelta(hours=10, minutes=30),
			6: timedelta(hours=10),
			7: timedelta(hours=9, minutes=30),
			8: timedelta(hours=9)
		}

		# Приложение 3: Значения для расчета максимального служебного полетного времени
		# для минимального состава акклиматизированного экипажа ВС
		self.appendix3_values = {
			# 06:00--14:59
			((6, 0), (14, 59)): {
				1: timedelta(hours=13),
				2: timedelta(hours=13),
				3: timedelta(hours=12, minutes=30),
				4: timedelta(hours=12),
				5: timedelta(hours=11, minutes=30),
				6: timedelta(hours=11),
				7: timedelta(hours=10, minutes=30),
				8: timedelta(hours=10),
				9: timedelta(hours=9, minutes=30),
				10: timedelta(hours=9)
			},
			# 15:00--16:59
			((15, 0), (16, 59)): {
				1: timedelta(hours=12, minutes=30),
				2: timedelta(hours=12, minutes=30),
				3: timedelta(hours=12),
				4: timedelta(hours=11, minutes=30),
				5: timedelta(hours=11),
				6: timedelta(hours=10, minutes=30),
				7: timedelta(hours=10),
				8: timedelta(hours=9, minutes=30),
				9: timedelta(hours=9),
				10: timedelta(hours=9)
			},
			# 17:00--23:59
			((17, 0), (23, 59)): {
				1: timedelta(hours=12),
				2: timedelta(hours=12),
				3: timedelta(hours=11, minutes=30),
				4: timedelta(hours=11),
				5: timedelta(hours=10, minutes=30),
				6: timedelta(hours=10),
				7: timedelta(hours=9, minutes=30),
				8: timedelta(hours=9),
				9: timedelta(hours=9),
				10: timedelta(hours=9)
			},
			# 00:00--05:59
			((0, 0), (5, 59)): {
				1: timedelta(hours=11, minutes=30),
				2: timedelta(hours=11, minutes=30),
				3: timedelta(hours=11),
				4: timedelta(hours=10, minutes=30),
				5: timedelta(hours=10),
				6: timedelta(hours=9, minutes=30),
				7: timedelta(hours=9),
				8: timedelta(hours=9),
				9: timedelta(hours=9),
				10: timedelta(hours=9)
			}
		}

		# Приложение 4: Значения для расчета максимального служебного полетного времени
		# для минимального состава экипажа ВС, когда состояние акклиматизации членов
		# экипажа ВС не определено и не внедрена FRMS
		self.appendix4_values = {
			1: timedelta(hours=11),
			2: timedelta(hours=11),
			3: timedelta(hours=10, minutes=30),
			4: timedelta(hours=10),
			5: timedelta(hours=9, minutes=30),
			6: timedelta(hours=9),
			7: timedelta(hours=9),
			8: timedelta(hours=9)
		}

		# Приложение 5: Предельные значения продления служебного полетного времени без отдыха в полете
		self.appendix5_values = {
			# 06:00--14:59
			((6, 0), (14, 59)): {
				1: timedelta(hours=14),
				2: timedelta(hours=14),
				3: timedelta(hours=13, minutes=30),
				4: timedelta(hours=13),
				5: timedelta(hours=12, minutes=30)
			},
			# 15:00--16:59
			((15, 0), (16, 59)): {
				1: timedelta(hours=13, minutes=30),
				2: timedelta(hours=13, minutes=30),
				3: timedelta(hours=13),
				4: timedelta(hours=12, minutes=30),
				5: None  # Не допускается
			},
			# 17:00--23:59
			((17, 0), (23, 59)): {
				1: timedelta(hours=13),
				2: timedelta(hours=13),
				3: timedelta(hours=12, minutes=30),
				4: timedelta(hours=12),
				5: None  # Не допускается
			},
			# 00:00--05:59
			((0, 0), (5, 59)): {
				1: timedelta(hours=12, minutes=30),
				2: timedelta(hours=12, minutes=30),
				3: None,  # Не допускается
				4: None,  # Не допускается
				5: None  # Не допускается
			}
		}

		# Приложение 6: Минимальное время отдыха в полете для каждого члена экипажа ВС
		self.appendix6_values = {
			timedelta(hours=14, minutes=30): {
				1: timedelta(hours=1, minutes=30),
				2: timedelta(hours=1, minutes=30),
				3: timedelta(hours=1, minutes=30)
			},
			timedelta(hours=15, minutes=0): {
				1: timedelta(hours=1, minutes=45),
				2: timedelta(hours=2),
				3: timedelta(hours=2, minutes=20)
			},
			timedelta(hours=15, minutes=30): {
				1: timedelta(hours=2),
				2: timedelta(hours=2),
				3: timedelta(hours=2, minutes=40)
			},
			timedelta(hours=16, minutes=0): {
				1: timedelta(hours=2, minutes=15),
				2: timedelta(hours=2, minutes=40),
				3: timedelta(hours=3)
			},
			timedelta(hours=16, minutes=30): {
				1: timedelta(hours=2, minutes=35),
				2: timedelta(hours=3),
				3: None  # Не допускается
			},
			timedelta(hours=17, minutes=0): {
				1: timedelta(hours=3),
				2: timedelta(hours=3, minutes=25),
				3: None  # Не допускается
			},
			timedelta(hours=17, minutes=30): {
				1: timedelta(hours=3, minutes=25),
				2: None,  # Не допускается
				3: None  # Не допускается
			},
			timedelta(hours=18, minutes=0): {
				1: timedelta(hours=3, minutes=50),
				2: None,  # Не допускается
				3: None  # Не допускается
			}
		}

		# Приложение 7: Значения минимального количества ночей, предоставляемых для отдыха
		# в основном месте базирования после ротации
		self.appendix7_values = {
			# (максимальная временная разница, продолжительность ротации): минимальное количество ночей
			((4, 6), (0, 48)): 2,
			((4, 6), (48, 72)): 2,
			((4, 6), (72, 96)): 3,
			((4, 6), (96, 1000)): 3,  # >96

			((6, 9), (0, 48)): 2,
			((6, 9), (48, 72)): 3,
			((6, 9), (72, 96)): 3,
			((6, 9), (96, 1000)): 4,  # >96

			((9, 12), (0, 48)): 2,
			((9, 12), (48, 72)): 3,
			((9, 12), (72, 96)): 4,
			((9, 12), (96, 1000)): 5  # >96
		}

	def determine_acclimatization(self, base_time_zone, local_time_zone, hours_since_duty_start):
		"""
        Определяет состояние акклиматизации на основе Приложения 2.
        """
		try:
			base_tz = pytz.timezone(base_time_zone)
			local_tz = pytz.timezone(local_time_zone)

			now = datetime.now()
			base_offset = base_tz.utcoffset(now)
			local_offset = local_tz.utcoffset(now)

			time_difference = (local_offset - base_offset).total_seconds() / 3600

			# Определяем статус акклиматизации по таблице Приложения 2
			if time_difference < 4:
				if hours_since_duty_start < 48:
					return AcclimatizationStatus.ACCLIMATIZED
				else:
					return AcclimatizationStatus.ACCLIMATIZED_TO_NEW
			elif 4 <= time_difference < 6:
				if hours_since_duty_start < 48:
					return AcclimatizationStatus.ACCLIMATIZED
				elif 48 <= hours_since_duty_start < 72:
					return AcclimatizationStatus.UNDEFINED
				else:
					return AcclimatizationStatus.ACCLIMATIZED_TO_NEW
			elif 6 <= time_difference < 9:
				if hours_since_duty_start < 48:
					return AcclimatizationStatus.ACCLIMATIZED
				elif 48 <= hours_since_duty_start < 72:
					return AcclimatizationStatus.UNDEFINED
				elif 72 <= hours_since_duty_start < 96:
					return AcclimatizationStatus.UNDEFINED
				else:
					return AcclimatizationStatus.ACCLIMATIZED_TO_NEW
			elif 9 <= time_difference < 12:
				if hours_since_duty_start < 48:
					return AcclimatizationStatus.ACCLIMATIZED
				elif 48 <= hours_since_duty_start < 72:
					return AcclimatizationStatus.UNDEFINED
				elif 72 <= hours_since_duty_start < 96:
					return AcclimatizationStatus.UNDEFINED
				elif 96 <= hours_since_duty_start < 120:
					return AcclimatizationStatus.UNDEFINED
				else:
					return AcclimatizationStatus.ACCLIMATIZED_TO_NEW
			else:
				return AcclimatizationStatus.UNDEFINED

		except Exception as e:
			print(f"Ошибка при определении акклиматизации: {e}")
			return AcclimatizationStatus.UNDEFINED

	def calculate_max_fdp(self, start_time, sectors, acclimatization_status, has_frms=False, rest_facility_class=None):
		"""
        Расчет максимального FDP на основе приложений документа.
        """
		try:
			# Определяем, какое приложение использовать
			if acclimatization_status == AcclimatizationStatus.ACCLIMATIZED and not has_frms:
				return self._lookup_appendix3(start_time, sectors)
			elif acclimatization_status == AcclimatizationStatus.UNDEFINED and not has_frms:
				return self._lookup_appendix4(sectors)
			elif has_frms:
				return self._lookup_appendix1(sectors)
			else:
				# По умолчанию используем наиболее строгие ограничения
				return min(
					self._lookup_appendix3(start_time, sectors),
					self._lookup_appendix4(sectors)
				)

		except Exception as e:
			print(f"Ошибка при расчете максимального FDP: {e}")
			return timedelta(hours=10)

	def _lookup_appendix1(self, sectors):
		"""Поиск значения в Приложении 1"""
		sectors = min(max(sectors, 1), 8)
		return self.appendix1_values.get(sectors, timedelta(hours=10))

	def _lookup_appendix3(self, start_time, sectors):
		"""Поиск значения в Приложении 3"""
		hour = start_time.hour
		minute = start_time.minute

		for time_range, values in self.appendix3_values.items():
			start_range, end_range = time_range
			start_hour, start_minute = start_range
			end_hour, end_minute = end_range

			if (hour > start_hour or (hour == start_hour and minute >= start_minute)) and \
					(hour < end_hour or (hour == end_hour and minute <= end_minute)):
				sectors = min(max(sectors, 1), 10)
				return values.get(sectors, timedelta(hours=10))

		return timedelta(hours=10)

	def _lookup_appendix4(self, sectors):
		"""Поиск значения в Приложении 4"""
		sectors = min(max(sectors, 1), 8)
		return self.appendix4_values.get(sectors, timedelta(hours=9))

	def calculate_extension_without_rest(self, start_time, sectors):
		"""
        Расчет предельного значения продления служебного полетного времени без отдыха в полете (Приложение 5).
        """
		try:
			hour = start_time.hour
			minute = start_time.minute

			for time_range, values in self.appendix5_values.items():
				start_range, end_range = time_range
				start_hour, start_minute = start_range
				end_hour, end_minute = end_range

				if (hour > start_hour or (hour == start_hour and minute >= start_minute)) and \
						(hour < end_hour or (hour == end_hour and minute <= end_minute)):
					sectors = min(max(sectors, 1), 5)
					return values.get(sectors)

			return None

		except Exception as e:
			print(f"Ошибка при расчете продления без отдыха: {e}")
			return None

	def calculate_min_in_flight_rest(self, extended_fdp_duration, rest_facility_class):
		"""
        Расчет минимального времени отдыха в полете (Приложение 6).
        """
		try:
			# Находим ближайшее значение продолжительности FDP
			closest_duration = None
			min_diff = float('inf')

			for duration in self.appendix6_values.keys():
				diff = abs((extended_fdp_duration - duration).total_seconds())
				if diff < min_diff:
					min_diff = diff
					closest_duration = duration

			if closest_duration:
				class_values = self.appendix6_values[closest_duration]
				return class_values.get(rest_facility_class)

			return None

		except Exception as e:
			print(f"Ошибка при расчете минимального отдыха в полете: {e}")
			return None

	def calculate_min_nights_at_home_base(self, max_time_difference, rotation_duration):
		"""
        Расчет минимального количества ночей для отдыха в основном месте базирования после ротации (Приложение 7).
        """
		try:
			for (min_diff, max_diff), (min_dur, max_dur) in self.appendix7_values.keys():
				if min_diff <= max_time_difference < max_diff and min_dur <= rotation_duration < max_dur:
					return self.appendix7_values[((min_diff, max_diff), (min_dur, max_dur))]

			return 2  # Значение по умолчанию

		except Exception as e:
			print(f"Ошибка при расчете минимального количества ночей: {e}")
			return 2

	def calculate_required_rest(self, previous_fdp_duration, is_at_home_base=True):
		"""
        Расчет необходимого времени отдыха после FDP.
        """
		if is_at_home_base:
			min_rest = max(previous_fdp_duration, timedelta(hours=12))
			return min_rest + timedelta(hours=8)
		else:
			min_rest = max(previous_fdp_duration, timedelta(hours=10))
			return min_rest + timedelta(hours=9)

	def check_limits(self, crew_member_id, planned_flight_time, db_connection):
		"""
        Проверка месячных/годовых лимитов полетного времени.
        """
		try:
			cursor = db_connection.cursor()

			# Sum flight_time from flights joined to duties filtered by crew_member_id
			cursor.execute(
				"""
				SELECT COALESCE(SUM(f.flight_time), 0)
				FROM flights f
				JOIN duties d ON f.duty_id = d.id
				WHERE d.crew_member_id = ? AND date(f.off_block_time) >= date('now', '-28 days')
				""",
				(crew_member_id,),
			)
			last_28_days = cursor.fetchone()[0] or 0

			cursor.execute(
				"""
				SELECT COALESCE(SUM(f.flight_time), 0)
				FROM flights f
				JOIN duties d ON f.duty_id = d.id
				WHERE d.crew_member_id = ? AND strftime('%Y', f.off_block_time) = strftime('%Y', 'now')
				""",
				(crew_member_id,),
			)
			current_year = cursor.fetchone()[0] or 0

			cursor.execute(
				"""
				SELECT COALESCE(SUM(f.flight_time), 0)
				FROM flights f
				JOIN duties d ON f.duty_id = d.id
				WHERE d.crew_member_id = ? AND date(f.off_block_time) >= date('now', '-12 months')
				""",
				(crew_member_id,),
			)
			last_12_months = cursor.fetchone()[0] or 0

			last_28_days_td = timedelta(minutes=last_28_days)
			current_year_td = timedelta(minutes=current_year)
			last_12_months_td = timedelta(minutes=last_12_months)

			planned_minutes = planned_flight_time.total_seconds() / 60

			result = {
				"last_28_days": {
					"current": last_28_days_td,
					"limit": timedelta(hours=90),
					"remaining": timedelta(hours=90) - last_28_days_td,
					"exceeded": last_28_days_td + planned_flight_time > timedelta(hours=90)
				},
				"current_year": {
					"current": current_year_td,
					"limit": timedelta(hours=900),
					"remaining": timedelta(hours=900) - current_year_td,
					"exceeded": current_year_td + planned_flight_time > timedelta(hours=900)
				},
				"last_12_months": {
					"current": last_12_months_td,
					"limit": timedelta(hours=1000),
					"remaining": timedelta(hours=1000) - last_12_months_td,
					"exceeded": last_12_months_td + planned_flight_time > timedelta(hours=1000)
				}
			}

			return result

		except Exception as e:
			print(f"Ошибка при проверке лимитов: {e}")
			return {
				"last_28_days": {"exceeded": False},
				"current_year": {"exceeded": False},
				"last_12_months": {"exceeded": False}
			}


# Пример использования
if __name__ == "__main__":
	calculator = FDPCalculator()

	# Тестирование различных функций
	start_time = datetime(2023, 10, 27, 10, 0)

	# Пример определения акклиматизации
	status = calculator.determine_acclimatization(
		"Europe/Minsk",
		"Asia/Dubai",
		60
	)
	print(f"Статус акклиматизации: {status.value}")

	# Пример расчета максимального FDP
	max_fdp = calculator.calculate_max_fdp(
		start_time,
		3,
		status,
		has_frms=False
	)
	print(f"Максимальное FDP: {max_fdp}")

	# Пример расчета продления без отдыха
	extension = calculator.calculate_extension_without_rest(start_time, 3)
	print(f"Продление без отдыха: {extension}")

	# Пример расчета минимального отдыха в полете
	min_rest = calculator.calculate_min_in_flight_rest(
		timedelta(hours=15, minutes=15),
		2
	)
	print(f"Минимальный отдых в полете: {min_rest}")

	# Пример расчета минимального количества ночей
	min_nights = calculator.calculate_min_nights_at_home_base(7, 80)
	print(f"Минимальное количество ночей: {min_nights}")

	# Пример расчета необходимого отдыха
	rest_time = calculator.calculate_required_rest(max_fdp, True)
	print(f"Необходимый отдых: {rest_time}")