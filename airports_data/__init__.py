"""
Рефакторенные компоненты для calculator_gui.py
"""

from .data.airports import get_airports_data
from .widgets.airport_search import AirportSearchWidget
from .widgets.validation_widget import ValidationWidget
from .widgets.segment_widget import SegmentWidget
from .utils.styles import *
from .utils.formatters import *
from .utils.validators import *

__all__ = [
    'get_airports_data',
    'AirportSearchWidget', 
    'ValidationWidget',
    'SegmentWidget',
    # Стили
    'ROUTE_GROUP_STYLE',
    'ADD_BUTTON_STYLE',
    'REMOVE_BUTTON_STYLE',
    # Форматтеры
    'format_time_duration',
    'format_datetime',
    # Валидаторы
    'validate_airport_code',
    'validate_flight_times'
]
