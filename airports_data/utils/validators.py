"""
Утилиты для валидации данных
"""

from PyQt6.QtCore import QDateTime
from datetime import datetime, timedelta
from ..data.airports import get_airports_data


class ValidationResult:
    """Результат валидации"""
    
    def __init__(self, is_valid=True, message="", warnings=None):
        self.is_valid = is_valid
        self.message = message
        self.warnings = warnings or []


def validate_airport_code(icao_code):
    """Валидирует ICAO код аэропорта"""
    airports_data = get_airports_data()
    
    if not icao_code:
        return ValidationResult(False, "ICAO код не может быть пустым")
    
    if len(icao_code) != 4:
        return ValidationResult(False, "ICAO код должен содержать 4 символа")
    
    if not icao_code.isalpha():
        return ValidationResult(False, "ICAO код должен содержать только буквы")
    
    if icao_code.upper() not in airports_data:
        return ValidationResult(False, f"Аэропорт с кодом {icao_code} не найден в базе данных")
    
    return ValidationResult(True, "Валидный ICAO код")


def validate_flight_times(departure_time, arrival_time):
    """Валидирует времена отправления и прибытия"""
    if not departure_time or not arrival_time:
        return ValidationResult(False, "Время отправления и прибытия не может быть пустым")
    
    if not isinstance(departure_time, QDateTime) or not isinstance(arrival_time, QDateTime):
        return ValidationResult(False, "Некорректный формат времени")
    
    # Проверяем, что время прибытия больше времени отправления
    if arrival_time <= departure_time:
        return ValidationResult(False, "Время прибытия должно быть больше времени отправления")
    
    # Проверяем разумность полетного времени (не более 24 часов)
    delta = arrival_time.toPython() - departure_time.toPython()
    if delta.total_seconds() > 24 * 3600:
        return ValidationResult(False, "Полетное время не может превышать 24 часа")
    
    # Проверяем минимальное полетное время (не менее 5 минут)
    if delta.total_seconds() < 5 * 60:
        return ValidationResult(False, "Полетное время должно быть не менее 5 минут")
    
    return ValidationResult(True, "Валидные времена полета")


def validate_fdp_duration(hours, minutes=0):
    """Валидирует продолжительность FDP"""
    total_minutes = hours * 60 + minutes
    
    if total_minutes < 0:
        return ValidationResult(False, "Продолжительность FDP не может быть отрицательной")
    
    if total_minutes > 24 * 60:
        return ValidationResult(False, "Продолжительность FDP не может превышать 24 часа")
    
    if total_minutes < 60:
        return ValidationResult(False, "Продолжительность FDP должна быть не менее 1 часа")
    
    # Предупреждения
    warnings = []
    if total_minutes > 14 * 60:  # Более 14 часов
        warnings.append("FDP превышает 14 часов - требуется дополнительный отдых")
    
    if total_minutes > 16 * 60:  # Более 16 часов
        warnings.append("FDP превышает 16 часов - критическое превышение")
    
    return ValidationResult(True, "Валидная продолжительность FDP", warnings)


def validate_acclimatization_time(hours, minutes=0):
    """Валидирует время акклиматизации"""
    total_minutes = hours * 60 + minutes
    
    if total_minutes < 0:
        return ValidationResult(False, "Время акклиматизации не может быть отрицательным")
    
    if total_minutes > 72 * 60:  # Более 72 часов
        return ValidationResult(False, "Время акклиматизации не может превышать 72 часа")
    
    return ValidationResult(True, "Валидное время акклиматизации")


def validate_rest_time(hours, minutes=0):
    """Валидирует время отдыха"""
    total_minutes = hours * 60 + minutes
    
    if total_minutes < 0:
        return ValidationResult(False, "Время отдыха не может быть отрицательным")
    
    if total_minutes < 10 * 60:  # Менее 10 часов
        return ValidationResult(False, "Время отдыха должно быть не менее 10 часов")
    
    if total_minutes > 48 * 60:  # Более 48 часов
        warnings = ["Время отдыха превышает 48 часов - проверьте корректность данных"]
        return ValidationResult(True, "Валидное время отдыха", warnings)
    
    return ValidationResult(True, "Валидное время отдыха")


def validate_hours_since_duty(hours):
    """Валидирует количество часов с начала выполнения обязанностей"""
    if hours < 0:
        return ValidationResult(False, "Количество часов не может быть отрицательным")
    
    if hours > 24:
        return ValidationResult(False, "Количество часов не может превышать 24")
    
    warnings = []
    if hours > 14:
        warnings.append("Превышено 14 часов с начала выполнения обязанностей")
    
    return ValidationResult(True, "Валидное количество часов", warnings)


def validate_timezone(timezone_str):
    """Валидирует строку часового пояса"""
    if not timezone_str:
        return ValidationResult(False, "Часовой пояс не может быть пустым")
    
    try:
        import pytz
        pytz.timezone(timezone_str)
        return ValidationResult(True, "Валидный часовой пояс")
    except:
        return ValidationResult(False, "Некорректный часовой пояс")


def validate_flight_segment(segment_data):
    """Валидирует данные сегмента полета"""
    errors = []
    warnings = []
    
    # Валидация аэропорта отправления
    departure_result = validate_airport_code(segment_data.get('departure_icao'))
    if not departure_result.is_valid:
        errors.append(f"Аэропорт отправления: {departure_result.message}")
    
    # Валидация аэропорта прибытия
    arrival_result = validate_airport_code(segment_data.get('arrival_icao'))
    if not arrival_result.is_valid:
        errors.append(f"Аэропорт прибытия: {arrival_result.message}")
    
    # Валидация времен полета
    times_result = validate_flight_times(
        segment_data.get('departure_time'),
        segment_data.get('arrival_time')
    )
    if not times_result.is_valid:
        errors.append(f"Времена полета: {times_result.message}")
    
    # Собираем предупреждения
    if times_result.warnings:
        warnings.extend(times_result.warnings)
    
    is_valid = len(errors) == 0
    message = "; ".join(errors) if errors else "Сегмент валиден"
    
    return ValidationResult(is_valid, message, warnings)


def validate_complete_flight_plan(segments, fdp_params):
    """Валидирует полный план полета"""
    errors = []
    warnings = []
    
    if not segments:
        errors.append("План полета должен содержать хотя бы один сегмент")
        return ValidationResult(False, "; ".join(errors))
    
    # Валидируем каждый сегмент
    for i, segment in enumerate(segments):
        segment_result = validate_flight_segment(segment)
        if not segment_result.is_valid:
            errors.append(f"Сегмент {i+1}: {segment_result.message}")
        if segment_result.warnings:
            warnings.extend([f"Сегмент {i+1}: {w}" for w in segment_result.warnings])
    
    # Валидируем параметры FDP
    fdp_result = validate_fdp_duration(
        fdp_params.get('duration_hours', 0),
        fdp_params.get('duration_minutes', 0)
    )
    if not fdp_result.is_valid:
        errors.append(f"FDP: {fdp_result.message}")
    if fdp_result.warnings:
        warnings.extend([f"FDP: {w}" for w in fdp_result.warnings])
    
    # Валидируем время отдыха
    rest_result = validate_rest_time(
        fdp_params.get('rest_hours', 0),
        fdp_params.get('rest_minutes', 0)
    )
    if not rest_result.is_valid:
        errors.append(f"Отдых: {rest_result.message}")
    if rest_result.warnings:
        warnings.extend([f"Отдых: {w}" for w in rest_result.warnings])
    
    is_valid = len(errors) == 0
    message = "; ".join(errors) if errors else "План полета валиден"
    
    return ValidationResult(is_valid, message, warnings)
