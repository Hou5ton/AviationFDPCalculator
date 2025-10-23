"""
Утилиты для форматирования данных
"""

from PyQt6.QtCore import QDateTime
from datetime import datetime, timedelta
import pytz


def format_time_duration(hours, minutes=0):
    """Форматирует время в формате ЧЧ:ММ"""
    total_minutes = hours * 60 + minutes
    formatted_hours = total_minutes // 60
    formatted_minutes = total_minutes % 60
    return f"{formatted_hours:02d}:{formatted_minutes:02d}"


def format_datetime(qdatetime):
    """Форматирует QDateTime в строку"""
    if isinstance(qdatetime, QDateTime):
        return qdatetime.toString("dd.MM.yyyy hh:mm")
    return str(qdatetime)


def parse_time_string(time_str):
    """Парсит строку времени в часы и минуты"""
    try:
        if ":" in time_str:
            parts = time_str.split(":")
            hours = int(parts[0])
            minutes = int(parts[1])
            return hours, minutes
        else:
            return int(time_str), 0
    except (ValueError, IndexError):
        return 0, 0


def calculate_time_difference(start_time, end_time):
    """Вычисляет разность между двумя временами в минутах"""
    if isinstance(start_time, QDateTime) and isinstance(end_time, QDateTime):
        start_dt = start_time.toPython()
        end_dt = end_time.toPython()
        delta = end_dt - start_dt
        return delta.total_seconds() / 60
    return 0


def add_time_duration(base_time, hours, minutes=0):
    """Добавляет к базовому времени указанную продолжительность"""
    if isinstance(base_time, QDateTime):
        base_dt = base_time.toPython()
        delta = timedelta(hours=hours, minutes=minutes)
        new_dt = base_dt + delta
        return QDateTime.fromPython(new_dt)
    return base_time


def get_timezone_offset(timezone_str):
    """Возвращает смещение часового пояса в часах"""
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        return now.utcoffset().total_seconds() / 3600
    except:
        return 0


def convert_timezone(datetime_obj, from_tz, to_tz):
    """Конвертирует время из одного часового пояса в другой"""
    try:
        if isinstance(datetime_obj, QDateTime):
            dt = datetime_obj.toPython()
        else:
            dt = datetime_obj
            
        # Устанавливаем исходный часовой пояс
        from_timezone = pytz.timezone(from_tz)
        if dt.tzinfo is None:
            dt = from_timezone.localize(dt)
        
        # Конвертируем в целевой часовой пояс
        to_timezone = pytz.timezone(to_tz)
        converted_dt = dt.astimezone(to_timezone)
        
        if isinstance(datetime_obj, QDateTime):
            return QDateTime.fromPython(converted_dt)
        return converted_dt
    except:
        return datetime_obj


def format_airport_display(icao, iata, city, name):
    """Форматирует отображение аэропорта"""
    return f"{icao}/{iata} - {city}, {name}"


def format_airport_codes(icao, iata):
    """Форматирует коды аэропорта"""
    return f"{icao}/{iata}"


def truncate_text(text, max_length=50):
    """Обрезает текст до указанной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_percentage(value, decimals=1):
    """Форматирует процентное значение"""
    return f"{value:.{decimals}f}%"


def format_boolean(value, true_text="Да", false_text="Нет"):
    """Форматирует булево значение"""
    return true_text if value else false_text
