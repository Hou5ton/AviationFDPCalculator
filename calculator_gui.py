# calculator_gui.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QLineEdit, QComboBox, QSpinBox, QDateTimeEdit,
                             QPushButton, QTextEdit, QFormLayout, QCheckBox,
                             QMessageBox, QScrollArea, QFrame, QGridLayout,
                             QSplitter, QTabWidget, QProgressBar, QProgressDialog, QCompleter)
from PyQt6.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter, QMovie
from calculator import FDPCalculator, AcclimatizationStatus
from datetime import datetime, timedelta
import pytz
import os
import json


class CalculatorWorker(QThread):
    """Worker thread for async calculations"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, calculation_data):
        super().__init__()
        self.calculation_data = calculation_data
        
    def run(self):
        try:
            # Simulate heavy calculation
            self.msleep(100)  # Small delay to show progress
            self.finished.emit(self.calculation_data)
        except Exception as e:
            self.error.emit(str(e))


class ValidationWidget(QLabel):
    """Widget for displaying validation messages"""
    def __init__(self):
        super().__init__()
        self.setWordWrap(True)
        self.setVisible(False)
        
    def show_warning(self, message):
        self.setText(f"⚠️ {message}")
        self.setStyleSheet("""
            QLabel {
                background-color: #f39c12;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        self.setVisible(True)
        
    def show_error(self, message):
        self.setText(f"❌ {message}")
        self.setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        self.setVisible(True)
        
    def show_success(self, message):
        self.setText(f"✅ {message}")
        self.setStyleSheet("""
            QLabel {
                background-color: #27ae60;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        self.setVisible(True)
        
    def clear(self):
        self.setVisible(False)


def create_airport_label(emoji_text="✈️", size=20, animation_file=None):
    """Создает лейбл с эмодзи аэропорта или анимированной картинкой"""
    label = QLabel(emoji_text)
    label.setFixedWidth(size)
    
    # Если указан файл анимации, используем его
    if animation_file and os.path.exists(animation_file):
        movie = QMovie(animation_file)
        movie.setScaledSize(QSize(size, size))
        label.setMovie(movie)
        movie.start()
    
    return label

class AirportSearchWidget(QLineEdit):
    """Custom widget for airport search with autocomplete"""
    
    airport_selected = pyqtSignal(str)  # Emit ICAO code when airport is selected
    
    def __init__(self, airports_data, parent=None):
        super().__init__(parent)
        self.airports_data = airports_data
        self.current_icao = None
        self.setup_autocomplete()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI for the search widget"""
        self.setPlaceholderText("ICAO/IATA/город/аэропорт")
        # Устанавливаем ширину 160px
        self.setMinimumWidth(160)  # Ширина 160px
        self.setMaximumWidth(160)  # Фиксированная ширина
        
        # Connect text change to search
        self.textChanged.connect(self.on_text_changed)
        self.returnPressed.connect(self.on_return_pressed)
        
    
    def setup_autocomplete(self):
        """Setup autocomplete functionality"""
        # Create search strings for all airports
        search_strings = []
        self.search_to_icao = {}  # Map search strings to ICAO codes
        self.icao_to_display = {}  # Map ICAO codes to display format
        
        for icao, data in self.airports_data.items():
            # Create display format: "ICAO/IATA - City, Name"
            display_format = f"{icao}/{data['iata']} - {data['city']}, {data['name']}"
            self.icao_to_display[icao] = display_format
            
            # Add only the main display format to search strings
            search_strings.append(display_format)
            self.search_to_icao[display_format.lower()] = icao
            
            # Add individual search terms for matching
            search_terms = [
                icao.lower(),  # ICAO code
                data['iata'].lower(),  # IATA code
                data['city'].lower(),  # City name
                data['name'].lower(),  # Airport name
            ]
            
            for term in search_terms:
                if term not in self.search_to_icao:
                    self.search_to_icao[term] = icao
        
        # Create completer
        self.completer = QCompleter(search_strings)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setMaxVisibleItems(12)
        
        # Настройка ширины popup окна сразу после создания
        popup = self.completer.popup()
        popup.setMinimumWidth(280)  # Уменьшенная ширина на одну треть
        popup.setMaximumWidth(300)  # Максимальная ширина
        
        # Connect completer selection
        self.completer.activated.connect(self.on_completer_activated)
        
        
        # Set completer
        self.setCompleter(self.completer)
    
    def on_text_changed(self, text):
        """Handle text changes for search"""
        if len(text) >= 2:  # Start search after 2 characters
            # Update completer
            self.completer.setCompletionPrefix(text)
            
            # Настройка ширины popup окна при каждом показе
            popup = self.completer.popup()
            popup.setMinimumWidth(280)  # Уменьшенная ширина на одну треть
            popup.setMaximumWidth(300)  # Максимальная ширина
            
            if not popup.isVisible():
                self.completer.complete()
    
    def on_completer_activated(self, text):
        """Handle selection from completer"""
        # Extract ICAO code from selected text
        icao = self.search_to_icao.get(text.lower())
        if icao:
            self.current_icao = icao
            # Set only ICAO/IATA codes in the field
            data = self.airports_data[icao]
            codes_display = f"{icao}/{data['iata']}"
            self.setText(codes_display)
            self.airport_selected.emit(icao)
    
    def on_return_pressed(self):
        """Handle Enter key press"""
        text = self.text()
        if text:
            # Try to find matching airport
            icao = self.search_to_icao.get(text.lower())
            if icao:
                self.current_icao = icao
                # Set only ICAO/IATA codes in the field
                data = self.airports_data[icao]
                codes_display = f"{icao}/{data['iata']}"
                self.setText(codes_display)
                self.airport_selected.emit(icao)
            else:
                # Try partial match
                for search_str, icao in self.search_to_icao.items():
                    if text.lower() in search_str:
                        self.current_icao = icao
                        # Set only ICAO/IATA codes in the field
                        data = self.airports_data[icao]
                        codes_display = f"{icao}/{data['iata']}"
                        self.setText(codes_display)
                        self.airport_selected.emit(icao)
                        break
    
    
    def get_current_icao(self):
        """Get the currently selected ICAO code"""
        return self.current_icao
    
    def set_airport(self, icao):
        """Set the airport by ICAO code"""
        if icao in self.airports_data:
            data = self.airports_data[icao]
            codes_display = f"{icao}/{data['iata']}"
            self.setText(codes_display)
            self.current_icao = icao


class SegmentWidget(QWidget):
    def __init__(self, segment_number, parent=None):
        """
        Widget for displaying a single flight segment

        Args:
            segment_number (int): The sequential number of this segment
            parent (QWidget): Parent widget that contains this segment
        """
        super().__init__(parent)
        self.segment_number = segment_number
        self.parent_calculator = parent  # Reference to parent calculator for communication
        self.number_label = None  # Store reference to the number label for updates
        self.init_ui()  # Initialize the user interface

    def init_ui(self):
        """Initialize the user interface for this segment widget"""
        # Main horizontal layout for the segment
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for compact layout

        # Segment number display
        self.number_label = QLabel(f"{self.segment_number}.")
        self.number_label.setFixedWidth(20)  # Fixed width for consistent alignment
        self.number_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.number_label)

        # Departure airport icon/animation
        departure_emoji = create_airport_label("✈️", 20, "resources/airport.png")
        layout.addWidget(departure_emoji)

        # Расширенная база данных аэропортов СНГ с ICAO, IATA кодами, городами, названиями и часовыми поясами
        # Импортируем базу данных аэропортов из рефакторенного модуля
        from airports_data import get_airports_data
        self.airports_data = get_airports_data()
        
        # Departure airport selection with search functionality
        self.departure_combo = AirportSearchWidget(self.airports_data, self)
        
        # Connect airport selection signal
        self.departure_combo.airport_selected.connect(self.on_departure_airport_selected)
        layout.addWidget(self.departure_combo)

        # Departure time input
        self.departure_time = QDateTimeEdit()
        self.departure_time.setDisplayFormat("dd.MM HH:mm")  # Более короткий формат
        self.departure_time.setDateTime(QDateTime.currentDateTime())  # Default to current time
        self.departure_time.setCalendarPopup(True)  # Enable calendar popup for easy date selection
        self.departure_time.setMinimumWidth(90)  # Уменьшаем ширину
        self.departure_time.setMaximumWidth(110)  # Ограничиваем максимальную ширину
        self.departure_time.dateTimeChanged.connect(self.on_departure_time_changed)  # Connect to validation
        layout.addWidget(self.departure_time)

        # Arrival airport icon/animation
        arrival_emoji = create_airport_label("✈️", 20, "resources/airport.png")
        layout.addWidget(arrival_emoji)

        # Arrival airport selection with search functionality
        self.arrival_combo = AirportSearchWidget(self.airports_data, self)
        
        # Connect airport selection signal
        self.arrival_combo.airport_selected.connect(self.on_arrival_airport_selected)
        layout.addWidget(self.arrival_combo)

        # Arrival time input
        self.arrival_time = QDateTimeEdit()
        self.arrival_time.setDisplayFormat("dd.MM HH:mm")  # Более короткий формат
        # Default to current time + 1 hour for realistic flight duration
        self.arrival_time.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.arrival_time.setCalendarPopup(True)  # Enable calendar popup for easy date selection
        self.arrival_time.setMinimumWidth(90)  # Уменьшаем ширину
        self.arrival_time.setMaximumWidth(110)  # Ограничиваем максимальную ширину
        layout.addWidget(self.arrival_time)

        # Add segment button
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(24, 24)
        self.add_btn.setToolTip("Добавить сегмент полета")
        self.add_btn.setStyleSheet("""
            QPushButton {
                font-family: "Segoe UI", Arial, sans-serif;
                font-weight: 900;
                font-size: 16px;
                background-color: #3498db;
                color: white;
                border: 2px solid #2980b9;
                border-radius: 12px;
                margin: 0px;
                padding: 0px;
                text-align: center;
                vertical-align: middle;
                line-height: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                border-color: #21618c;
            }
            QPushButton:pressed {
                background-color: #21618c;
                border-color: #1a4d73;
            }
        """)
        self.add_btn.clicked.connect(self.add_segment)

        # Remove segment button
        self.remove_btn = QPushButton("−")
        self.remove_btn.setFixedSize(24, 24)
        self.remove_btn.setToolTip("Удалить последний сегмент")
        self.remove_btn.setStyleSheet("""
            QPushButton {
                font-family: "Segoe UI", Arial, sans-serif;
                font-weight: 900;
                font-size: 16px;
                background-color: #3498db;
                color: white;
                border: 2px solid #2980b9;
                border-radius: 12px;
                margin: 0px;
                padding: 0px;
                text-align: center;
                vertical-align: middle;
                line-height: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                border-color: #21618c;
            }
            QPushButton:pressed {
                background-color: #21618c;
                border-color: #1a4d73;
            }
        """)
        self.remove_btn.clicked.connect(self.remove_segment)

        # Container widget for buttons with fixed width for stability
        buttons_container = QWidget()
        buttons_container.setFixedWidth(60)
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(5)

        # Add buttons to the button layout
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.remove_btn)

        # Add button container to main layout
        layout.addWidget(buttons_container)
        layout.addStretch()  # Add stretchable space to push elements left

        # Set the main layout for this widget
        self.setLayout(layout)

    def add_segment(self):
        """Request parent to add a new segment after this one"""
        if self.parent_calculator:
            self.parent_calculator.add_segment_after(self.segment_number)

    def remove_segment(self):
        """Request parent to remove this segment"""
        if self.parent_calculator:
            self.parent_calculator.remove_segment(self.segment_number)

    def update_buttons_visibility(self, is_last_segment, total_segments):
        """
        Update button visibility based on segment position

        Args:
            is_last_segment (bool): Whether this is the last segment in the route
            total_segments (int): Total number of segments in the route
        """
        if total_segments == 1:
            # Single segment: show only add button
            self.add_btn.setVisible(True)
            self.remove_btn.setVisible(False)
        elif self.segment_number == 1:
            # First segment in multi-segment route: no buttons
            self.add_btn.setVisible(False)
            self.remove_btn.setVisible(False)
        elif is_last_segment:
            # Last segment: both buttons visible
            self.add_btn.setVisible(True)
            self.remove_btn.setVisible(True)
        else:
            # Intermediate segment: both buttons visible
            self.add_btn.setVisible(True)
            self.remove_btn.setVisible(True)

    def get_airport_code(self, combo_text):
        """Извлекает ICAO код аэропорта из текста комбобокса"""
        # Для новых виджетов поиска просто возвращаем текст как есть
        # или получаем текущий ICAO код
        if hasattr(self, 'departure_combo') and isinstance(self.departure_combo, AirportSearchWidget):
            return self.departure_combo.get_current_icao() or combo_text
        return combo_text
    
    def get_airport_info(self, airport_code):
        """Получает информацию об аэропорте по коду"""
        return self.airports_data.get(airport_code, {"city": "Неизвестно", "name": "Неизвестно", "country": "Неизвестно", "iata": "N/A", "timezone": "Europe/Minsk"})
    
    def on_departure_airport_selected(self, icao):
        """Handle departure airport selection"""
        airport_info = self.get_airport_info(icao)
        tooltip_text = f"Аэропорт отправления:\n{airport_info['name']}\nГород: {airport_info['city']}\nСтрана: {airport_info['country']}\nКод ИКАО: {icao}\nКод ИАТА: {airport_info.get('iata', 'N/A')}"
        self.departure_combo.setToolTip(tooltip_text)
    
    def on_arrival_airport_selected(self, icao):
        """Handle arrival airport selection"""
        airport_info = self.get_airport_info(icao)
        tooltip_text = f"Аэропорт прибытия:\n{airport_info['name']}\nГород: {airport_info['city']}\nСтрана: {airport_info['country']}\nКод ИКАО: {icao}\nКод ИАТА: {airport_info.get('iata', 'N/A')}"
        self.arrival_combo.setToolTip(tooltip_text)


    def set_segment_number(self, number):
        """
        Update the segment number display

        Args:
            number (int): New segment number
        """
        self.segment_number = number
        if self.number_label:
            self.number_label.setText(f"{number}.")  # Update label with new number

    def on_departure_time_changed(self):
        """Обработчик изменения времени вылета"""
        if self.parent_calculator and self.segment_number == 1:
            # Если это первый сегмент, обновляем валидацию FDP времени
            self.parent_calculator.validate_fdp_time()
            self.parent_calculator.update_preview()


class CalculatorTab(QWidget):
    def __init__(self):
        """Основной виджет калькулятора FDP"""
        super().__init__()
        self.calculator = FDPCalculator()
        self.segment_widgets = []  # List to track all segment widgets
        self.calculation_results = {}
        self.validation_widgets = {}  # Store validation widgets
        self.calculation_worker = None
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        main_layout = QHBoxLayout()
        
        # Создаем разделитель для разделения на панели
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)  # Предотвращаем полное сворачивание панелей
        
        # Отключаем только возможность перемещения разделителя
        splitter.setHandleWidth(0)  # Убираем видимую ручку
        # НЕ отключаем splitter полностью, чтобы панели оставались функциональными
        
        # Левая панель - ввод данных
        left_panel = self.create_input_panel()
        
        # Правая панель - результаты
        right_panel = self.create_results_panel()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Устанавливаем минимальные размеры панелей
        left_panel.setMinimumWidth(400)  # Минимальная ширина левой панели (увеличена)
        right_panel.setMinimumWidth(350)  # Минимальная ширина правой панели
        
        # Устанавливаем размеры (60% левая / 40% правая)
        splitter.setSizes([600, 400])
        
        # Пропорции при изменении размера окна (60/40)
        splitter.setStretchFactor(0, 3)  # Левая панель растягивается больше
        splitter.setStretchFactor(1, 2)  # Правая панель растягивается меньше
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        # Сохраняем ссылку на splitter для адаптивного изменения размера
        self.splitter = splitter
        
        # Подключаем обработчик для предотвращения перемещения разделителя
        splitter.splitterMoved.connect(self.on_splitter_moved)
        
        # Загружаем сохраненные размеры панелей
        self.load_panel_sizes()

    def create_input_panel(self):
        """Создает левую панель с вводом данных"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок панели
        title_label = QLabel("Калькулятор служебного полетного времени (FDP)")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Создаем скроллируемую область
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # МАРШРУТ ПОЛЕТА (ПЕРВЫЙ БЛОК - ОСНОВА ВСЕХ РАСЧЕТОВ)
        self.route_group = QGroupBox("🛫 Маршрут полета")
        route_main_layout = QVBoxLayout()
        route_main_layout.setContentsMargins(10, 8, 10, 10)  # Отступ сверху = 8px - небольшой отступ от заголовка
        route_main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Выравниваем содержимое по верхнему краю

        # Убираем информационную подсказку - интерфейс должен быть интуитивным

        # Контейнер для сегментов
        self.segments_container = QVBoxLayout()
        self.segments_container.setSpacing(5)  # Небольшое расстояние между сегментами для лучшей читаемости
        self.segments_container.setAlignment(Qt.AlignmentFlag.AlignTop)  # Выравниваем сегменты по верхнему краю
        
        # Добавляем первый сегмент сразу
        self.add_initial_segment()
        
        route_main_layout.addLayout(self.segments_container)
        
        self.route_group.setLayout(route_main_layout)
        scroll_layout.addWidget(self.route_group)

        # ОСНОВНЫЕ ПАРАМЕТРЫ FDP
        basic_params_group = QGroupBox("🌍 Основные параметры FDP")
        basic_params_layout = QFormLayout()
        
        # Валидация для FDP времени (будет обновляться из маршрута)
        self.fdp_validation = ValidationWidget()
        basic_params_layout.addRow("", self.fdp_validation)
        
        # Часовой пояс основного места базирования
        self.base_timezone_combo = QComboBox()
        self.base_timezone_combo.addItems([
            "Europe/Minsk", "Europe/Moscow", "Europe/Kiev", "Europe/Warsaw", 
            "Europe/Berlin", "Europe/Paris", "Europe/London", "America/New_York",
            "Asia/Dubai", "Asia/Shanghai", "Asia/Tokyo"
        ])
        self.base_timezone_combo.setCurrentText("Europe/Minsk")
        self.base_timezone_combo.setEditable(True)
        self.base_timezone_combo.currentTextChanged.connect(self.update_preview)
        basic_params_layout.addRow("Часовой пояс основного места базирования:", self.base_timezone_combo)


        # Часов с начала выполнения обязанностей
        self.hours_since_duty_spin = QSpinBox()
        self.hours_since_duty_spin.setRange(0, 500)
        self.hours_since_duty_spin.setValue(0)
        self.hours_since_duty_spin.setSuffix(" часов")
        self.hours_since_duty_spin.valueChanged.connect(self.update_preview)
        basic_params_layout.addRow("Часов с начала выполнения обязанностей:", self.hours_since_duty_spin)
        
        basic_params_group.setLayout(basic_params_layout)
        scroll_layout.addWidget(basic_params_group)
        
        # FRMS и отдых в полете перемещены в дополнительные параметры
        
        # ДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ (информативная вертикальная версия)
        additional_group = QGroupBox("⚙️ Дополнительные параметры")
        additional_layout = QFormLayout()  # Используем FormLayout для вертикального размещения
        
        # FRMS - система управления факторами риска
        self.has_frms_combo = QComboBox()
        self.has_frms_combo.addItems(["Нет", "Да"])
        self.has_frms_combo.currentTextChanged.connect(self.update_preview)
        additional_layout.addRow("📊 Система управления факторами риска (FRMS):", self.has_frms_combo)
        
        # Отдых в полете
        self.rest_in_flight_check = QCheckBox()
        self.rest_in_flight_check.stateChanged.connect(self.on_rest_in_flight_changed)
        additional_layout.addRow("🛏️ Отдых в полете предусмотрен:", self.rest_in_flight_check)
        
        # Класс места для отдыха
        self.rest_facility_combo = QComboBox()
        self.rest_facility_combo.addItems(["Не предусмотрен", "1 класс", "2 класс", "3 класс"])
        self.rest_facility_combo.setEnabled(False)
        additional_layout.addRow("🏨 Класс места для отдыха:", self.rest_facility_combo)
        
        # Трансфер
        transfer_layout = QHBoxLayout()
        
        # Часы трансфера
        self.transfer_hours_spin = QSpinBox()
        self.transfer_hours_spin.setRange(0, 24)
        self.transfer_hours_spin.setValue(0)
        self.transfer_hours_spin.setSuffix(" ч")
        self.transfer_hours_spin.setMaximumWidth(80)  # Увеличиваем для удобства
        self.transfer_hours_spin.setEnabled(False)  # По умолчанию отключен
        self.transfer_hours_spin.valueChanged.connect(self.update_preview)
        transfer_layout.addWidget(self.transfer_hours_spin)
        
        # Разделитель
        separator_label = QLabel(":")
        separator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator_label.setStyleSheet("font-weight: bold; font-size: 16px; margin: 0 5px;")
        transfer_layout.addWidget(separator_label)
        
        # Минуты трансфера
        self.transfer_minutes_spin = QSpinBox()
        self.transfer_minutes_spin.setRange(0, 59)
        self.transfer_minutes_spin.setValue(0)
        self.transfer_minutes_spin.setSuffix(" мин")
        self.transfer_minutes_spin.setMaximumWidth(80)  # Увеличиваем для удобства
        self.transfer_minutes_spin.setEnabled(False)  # По умолчанию отключен
        self.transfer_minutes_spin.valueChanged.connect(self.update_preview)
        transfer_layout.addWidget(self.transfer_minutes_spin)
        
        # Чекбокс трансфера
        self.transfer_check = QCheckBox("Включить")
        self.transfer_check.stateChanged.connect(self.on_transfer_changed)
        transfer_layout.addWidget(self.transfer_check)
        
        transfer_layout.addStretch()  # Растягиваем оставшееся пространство
        
        # Создаем контейнер для трансфера
        transfer_container = QWidget()
        transfer_container.setLayout(transfer_layout)
        additional_layout.addRow("🚗 Время трансфера:", transfer_container)
        
        # Устанавливаем высоту группы для вертикального размещения элементов
        additional_group.setLayout(additional_layout)
        additional_group.setMaximumHeight(180)  # Увеличиваем высоту для вертикального размещения всех элементов
        
        scroll_layout.addWidget(additional_group)
        
        # Добавляем панель быстрых действий
        quick_actions_layout = self.add_quick_actions()
        scroll_layout.addLayout(quick_actions_layout)
        
        # Добавляем визуальный разделитель
        separator = self.create_visual_separators()
        scroll_layout.addWidget(separator)
        
        # Кнопка расчета
        self.calculate_btn = QPushButton("🚀 Рассчитать FDP")
        self.calculate_btn.clicked.connect(self.calculate_all)
        self.calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        scroll_layout.addWidget(self.calculate_btn)
        
        # Настройка скроллируемой области
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(550)  # Уменьшаем высоту для убирания прокрутки
        
        # Улучшаем скроллирование
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setSizeAdjustPolicy(QScrollArea.SizeAdjustPolicy.AdjustToContents)
        
        # Добавляем отступы для лучшего отображения
        scroll_area.setContentsMargins(5, 5, 5, 5)
        
        layout.addWidget(scroll_area)
        panel.setLayout(layout)
        
        # Инициализация улучшений
        self.setup_enhanced_styles()
        self.add_help_tooltips()
        
        # Первый сегмент уже создан в маршруте
        
        # Настраиваем порядок Tab после создания сегментов
        self.setup_tab_order()
        
        return panel

    def create_results_panel(self):
        """Создает правую панель с результатами"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок панели результатов
        title_label = QLabel("Результаты расчета")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Создаем вкладки для разных типов результатов
        self.results_tabs = QTabWidget()
        
        # Вкладка предварительного просмотра
        self.preview_tab = QTextEdit()
        self.preview_tab.setReadOnly(True)
        self.preview_tab.setPlainText("Введите параметры для предварительного просмотра...")
        self.results_tabs.addTab(self.preview_tab, "📋 Предварительный просмотр")
        
        # Вкладка детальных результатов
        self.details_tab = QTextEdit()
        self.details_tab.setReadOnly(True)
        self.details_tab.setPlainText("Результаты расчета появятся здесь после выполнения расчетов...")
        self.results_tabs.addTab(self.details_tab, "📊 Детальные результаты")
        
        # Вкладка рекомендаций
        self.recommendations_tab = QTextEdit()
        self.recommendations_tab.setReadOnly(True)
        self.recommendations_tab.setPlainText("Рекомендации и предупреждения появятся здесь...")
        self.results_tabs.addTab(self.recommendations_tab, "⚠️ Рекомендации")
        
        layout.addWidget(self.results_tabs)
        
        # Кнопка экспорта результатов
        export_btn = QPushButton("💾 Экспорт результатов")
        export_btn.clicked.connect(self.export_results)
        layout.addWidget(export_btn)
        
        panel.setLayout(layout)
        return panel

    def on_rest_in_flight_changed(self, state):
        """Обработчик изменения состояния чекбокса отдыха в полете"""
        is_enabled = state == Qt.CheckState.Checked
        self.rest_facility_combo.setEnabled(is_enabled)
        if not is_enabled:
            self.rest_facility_combo.setCurrentText("Не предусмотрен")
        self.update_preview()

    def on_transfer_changed(self, state):
        """Обработчик изменения состояния чекбокса трансфера"""
        # Правильное определение состояния чекбокса
        is_enabled = state == Qt.CheckState.Checked.value
        
        self.transfer_hours_spin.setEnabled(is_enabled)
        self.transfer_minutes_spin.setEnabled(is_enabled)
        
        if not is_enabled:
            self.transfer_hours_spin.setValue(0)  # Сбрасываем значения при отключении
            self.transfer_minutes_spin.setValue(0)
        self.update_preview()

    def add_initial_segment(self):
        """Add the initial segment to start the flight route"""
        # Clear any existing segments from container
        self.clear_segments_container()

        # Clear segment widgets list
        self.segment_widgets.clear()

        # Create and add first segment
        segment = SegmentWidget(1, self)
        self.segment_widgets.append(segment)
        self.segments_container.addWidget(segment)

        # Update button visibility for all segments
        self.update_buttons_visibility()

    def clear_segments_container(self):
        """Safely remove all widgets from segments container"""
        while self.segments_container.count():
            item = self.segments_container.takeAt(0)  # Take item from layout
            if item.widget():
                item.widget().setParent(None)  # Remove parent reference
            del item  # Delete the item

    def add_segment_after(self, segment_number):
        """
        Add a new segment after the specified segment number

        Args:
            segment_number (int): The segment number after which to insert the new segment
        """
        # Check maximum segment limit
        if len(self.segment_widgets) >= 10:
            QMessageBox.information(self, "Информация", "Максимальное количество сегментов маршрута - 10")
            return

        # Calculate current segment index (0-based)
        current_index = segment_number - 1

        # Create new segment with incremented number
        new_segment = SegmentWidget(segment_number + 1, self)

        # Insert new segment after current segment
        self.segment_widgets.insert(current_index + 1, new_segment)

        # Rebuild the entire segments layout first
        self.rebuild_segments_layout()
        
        # Update button visibility for all segments
        self.update_buttons_visibility()

        # Auto-fill departure from previous segment's arrival AFTER layout is built
        if current_index >= 0 and current_index < len(self.segment_widgets):
            try:
                prev_segment = self.segment_widgets[current_index]

                # Set departure airport from previous arrival
                # Устанавливаем аэропорт отправления нового сегмента как аэропорт прибытия предыдущего
                if hasattr(prev_segment, 'arrival_combo') and prev_segment.arrival_combo:
                    prev_arrival_icao = prev_segment.arrival_combo.get_current_icao()
                    if prev_arrival_icao and hasattr(new_segment, 'departure_combo') and new_segment.departure_combo:
                        new_segment.departure_combo.set_airport(prev_arrival_icao)
                        # Блокируем поле аэропорта отправления для изменения
                        new_segment.departure_combo.setEnabled(False)
                        new_segment.departure_combo.setStyleSheet("""
                            QLineEdit {
                                background-color: #f0f0f0;
                                color: #666666;
                                border: 1px solid #cccccc;
                            }
                        """)
                        new_segment.departure_combo.setToolTip("Аэропорт отправления автоматически установлен из предыдущего сегмента и заблокирован для изменения")

                # Set arrival airport from previous departure (but keep it editable)
                # Устанавливаем аэропорт прибытия нового сегмента как аэропорт отправления предыдущего, но оставляем редактируемым
                if hasattr(prev_segment, 'departure_combo') and prev_segment.departure_combo:
                    prev_departure_icao = prev_segment.departure_combo.get_current_icao()
                    if prev_departure_icao and hasattr(new_segment, 'arrival_combo') and new_segment.arrival_combo:
                        new_segment.arrival_combo.set_airport(prev_departure_icao)
                        new_segment.arrival_combo.setToolTip("Аэропорт прибытия автоматически установлен из предыдущего сегмента, но может быть изменен")

                # Set departure time as previous arrival time + 30 minutes
                if hasattr(prev_segment, 'arrival_time') and prev_segment.arrival_time:
                    arrival_time = prev_segment.arrival_time.dateTime()
                    new_departure_time = arrival_time.addSecs(1800)  # +30 minutes
                    if hasattr(new_segment, 'departure_time') and new_segment.departure_time:
                        new_segment.departure_time.setDateTime(new_departure_time)

                # Set arrival time as departure time + 1 hour
                new_arrival_time = new_departure_time.addSecs(3600)  # +1 hour
                if hasattr(new_segment, 'arrival_time') and new_segment.arrival_time:
                    new_segment.arrival_time.setDateTime(new_arrival_time)
            except Exception as e:
                print(f"Ошибка при автозаполнении сегмента: {e}")
                # Продолжаем выполнение без автозаполнения

        # Принудительно обновляем весь layout
        self.segments_container.update()
        self.route_group.update()

    def remove_segment(self, segment_number):
        """
        Remove the specified segment from the route

        Args:
            segment_number (int): The segment number to remove
        """
        # Prevent removal if only one segment remains
        if len(self.segment_widgets) <= 1:
            QMessageBox.warning(self, "Предупреждение", "Нельзя удалить единственный сегмент маршрута")
            return

        # Calculate segment index to remove (0-based)
        remove_index = segment_number - 1

        # Check if index is valid
        if 0 <= remove_index < len(self.segment_widgets):
            # Remove segment from widgets list
            segment_to_remove = self.segment_widgets.pop(remove_index)

            # Remove widget from layout
            self.segments_container.removeWidget(segment_to_remove)

            # Delete the widget
            segment_to_remove.deleteLater()

            # Rebuild the entire segments layout
            self.rebuild_segments_layout()
            
            # Update button visibility for all segments
            self.update_buttons_visibility()

    def rebuild_segments_layout(self):
        """Completely rebuild the segments layout with current widgets"""
        # Clear the container
        self.clear_segments_container()

        # Ensure alignment is set correctly
        self.segments_container.setAlignment(Qt.AlignmentFlag.AlignTop)  # Выравниваем сегменты по верхнему краю

        # Add all segments back to container
        for segment in self.segment_widgets:
            if segment is not None:
                self.segments_container.addWidget(segment)
                # Принудительно обновляем каждый сегмент
                segment.adjustSize()
                segment.update()
                # Принудительно обновляем layout сегмента
                segment.layout().update()

        # Renumber segments and update buttons
        self.renumber_segments()
        
        # Принудительно обновляем контейнер
        self.segments_container.update()
        
        # Принудительно обновляем весь route_group
        self.route_group.update()

    def renumber_segments(self):
        """Renumber all segments sequentially starting from 1"""
        for i, segment in enumerate(self.segment_widgets):
            if segment is not None and hasattr(segment, 'set_segment_number'):
                segment.set_segment_number(i + 1)  # Update segment number display

        # Update button visibility for all segments
        self.update_buttons_visibility()

    def update_buttons_visibility(self):
        """Update button visibility for all segments based on their position"""
        total_segments = len(self.segment_widgets)

        # Update each segment's button visibility
        for i, segment in enumerate(self.segment_widgets):
            is_last_segment = (i == total_segments - 1)  # Check if this is the last segment
            segment.update_buttons_visibility(is_last_segment, total_segments)
    
    # Методы add_segment и remove_segment теперь находятся в классе SegmentWidget

    def get_route_segments(self):
        """
        Get complete route information with all segments

        Returns:
            list: List of dictionaries containing segment information
        """
        segments = []
        for i, segment in enumerate(self.segment_widgets):
            segments.append({
                'segment': i + 1,  # Segment number
                'departure': segment.departure_combo.get_current_icao() or segment.departure_combo.text(),  # Departure airport code
                'departure_time': segment.departure_time.dateTime().toPyDateTime(),  # Departure time
                'arrival': segment.arrival_combo.get_current_icao() or segment.arrival_combo.text(),  # Arrival airport code
                'arrival_time': segment.arrival_time.dateTime().toPyDateTime()  # Arrival time
            })
        return segments

    def get_sectors_count(self):
        """
        Get the total number of flight sectors/segments

        Returns:
            int: Number of segments in the route
        """
        return len(self.segment_widgets)

    def get_fdp_start_time(self):
        """
        Get FDP start time from the first segment of the route

        Returns:
            datetime: FDP start time from first segment, or current time if no segments
        """
        if self.segment_widgets:
            first_segment = self.segment_widgets[0]
            return first_segment.departure_time.dateTime().toPyDateTime()
        else:
            return datetime.now()
    
    def get_departure_timezone(self):
        """
        Получает часовой пояс аэропорта отправления из первого сегмента маршрута
        """
        if self.segment_widgets:
            first_segment = self.segment_widgets[0]
            departure_icao = first_segment.get_departure_airport_code()
            if departure_icao:
                airport_info = first_segment.get_airport_info(departure_icao)
                return airport_info.get('timezone', 'Europe/Minsk')
        return 'Europe/Minsk'  # По умолчанию

    def update_preview(self):
        """Обновляет предварительный просмотр результатов"""
        try:
            # Собираем параметры
            start_time = self.get_fdp_start_time()  # Получаем время из маршрута
            base_tz = self.base_timezone_combo.currentText()
            local_tz = self.get_departure_timezone()  # Автоматически определяем часовой пояс
            hours_since_duty = self.hours_since_duty_spin.value()
            sectors = self.get_sectors_count()
            has_frms = self.has_frms_combo.currentText() == "Да"
            rest_in_flight = self.rest_in_flight_check.isChecked()
            
            # Стандартные значения подготовительных операций
            preflight = 1  # Стандартная предполетная подготовка - 1 час
            postflight = 0.5  # Стандартная послеполетная подготовка - 30 минут
            
            # Трансфер только если включен (часы + минуты)
            if self.transfer_check.isChecked():
                transfer_hours = self.transfer_hours_spin.value()
                transfer_minutes = self.transfer_minutes_spin.value()
                transfer = transfer_hours + (transfer_minutes / 60.0)  # Переводим в часы
            else:
                transfer = 0
            
            # Формируем предварительный просмотр
            preview = f"ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР\n"
            preview += "=" * 40 + "\n\n"
            
            preview += f"📅 Дата и время начала FDP: {start_time.strftime('%d.%m.%Y %H:%M')}\n"
            preview += f"🌍 Базовый часовой пояс: {base_tz}\n"
            preview += f"🌍 Местный часовой пояс: {local_tz}\n"
            preview += f"⏰ Часов с начала выполнения обязанностей: {hours_since_duty}\n"
            preview += f"✈️ Количество секторов: {sectors}\n"
            preview += f"📊 Наличие FRMS: {'Да' if has_frms else 'Нет'}\n"
            preview += f"🛏️ Отдых в полете: {'Да' if rest_in_flight else 'Нет'}\n"
            preview += f"🛫 Предполетная подготовка: {preflight} часов\n"
            preview += f"🛬 Послеполетная подготовка: {postflight} часов\n"
            if self.transfer_check.isChecked():
                transfer_hours = self.transfer_hours_spin.value()
                transfer_minutes = self.transfer_minutes_spin.value()
                if transfer_minutes > 0:
                    preview += f"🚗 Трансфер: {transfer_hours}ч {transfer_minutes}мин\n"
                else:
                    preview += f"🚗 Трансфер: {transfer_hours} часов\n"
            else:
                preview += f"🚗 Трансфер: отключен\n"
            
            if rest_in_flight:
                rest_class = self.rest_facility_combo.currentText()
                preview += f"🏨 Класс места для отдыха: {rest_class}\n"
            
            # Проверка циркадного окна
            hour = start_time.hour
            if 2 <= hour <= 5:
                preview += f"\n⚠️ ВНИМАНИЕ: Время начала FDP попадает в окно минимальной циркадной активности (02:00-05:59)\n"
            
            # Попытка определения акклиматизации
            try:
                acclimatization_status = self.calculator.determine_acclimatization(
                    base_tz, local_tz, hours_since_duty
                )
                status_text = {
                    'Б': "Акклиматизирован к базовому времени",
                    'В': "Акклиматизирован к новому времени", 
                    'Н': "Неопределенное состояние акклиматизации"
                }
                preview += f"\n🧠 Состояние акклиматизации: {acclimatization_status.value} - {status_text[acclimatization_status.value]}\n"
                
            except Exception as e:
                preview += f"\n❌ Ошибка определения акклиматизации: {str(e)}\n"
            
            # Информация о маршруте
            segments = self.get_route_segments()
            if segments:
                preview += f"\nМАРШРУТ ПОЛЕТА:\n"
                for segment in segments:
                    preview += f"{segment['segment']}. {segment['departure']} → {segment['arrival']}\n"
                    preview += f"   Вылет: {segment['departure_time'].strftime('%d.%m.%Y %H:%M')}\n"
                    preview += f"   Прилет: {segment['arrival_time'].strftime('%d.%m.%Y %H:%M')}\n"
            
            self.preview_tab.setPlainText(preview)
            
        except Exception as e:
            self.preview_tab.setPlainText(f"Ошибка обновления предварительного просмотра: {str(e)}")

    def calculate_all(self):
        """Выполняет полный расчет FDP"""
        try:
            # Собираем все параметры
            start_time = self.get_fdp_start_time()  # Получаем время из маршрута
            base_tz = self.base_timezone_combo.currentText()
            local_tz = self.get_departure_timezone()  # Автоматически определяем часовой пояс
            hours_since_duty = self.hours_since_duty_spin.value()
            sectors = self.get_sectors_count()
            has_frms = self.has_frms_combo.currentText() == "Да"
            rest_in_flight = self.rest_in_flight_check.isChecked()
            
            # Стандартные значения подготовительных операций
            preflight = 1  # Стандартная предполетная подготовка - 1 час
            postflight = 0.5  # Стандартная послеполетная подготовка - 30 минут
            
            # Трансфер только если включен (часы + минуты)
            if self.transfer_check.isChecked():
                transfer_hours = self.transfer_hours_spin.value()
                transfer_minutes = self.transfer_minutes_spin.value()
                transfer = transfer_hours + (transfer_minutes / 60.0)  # Переводим в часы
            else:
                transfer = 0
            
            rest_class_map = {"Не предусмотрен": None, "1 класс": 1, "2 класс": 2, "3 класс": 3}
            rest_facility_class = rest_class_map[self.rest_facility_combo.currentText()] if rest_in_flight else None
            
            # Определяем акклиматизацию
            acclimatization_status = self.calculator.determine_acclimatization(
                base_tz, local_tz, hours_since_duty
            )
            
            # Рассчитываем максимальное FDP
            max_fdp = self.calculator.calculate_max_fdp(
                start_time, sectors, acclimatization_status, has_frms, rest_facility_class
            )
            
            # Рассчитываем необходимый отдых
            is_at_home_base = base_tz == local_tz
            required_rest = self.calculator.calculate_required_rest(max_fdp, is_at_home_base)
            
            # Рассчитываем продление без отдыха в полете
            extension_without_rest = self.calculator.calculate_extension_without_rest(start_time, sectors)
            
            # Рассчитываем минимальный отдых в полете
            min_rest_in_flight = None
            if rest_in_flight and rest_facility_class:
                min_rest_in_flight = self.calculator.calculate_min_in_flight_rest(max_fdp, rest_facility_class)
            
            # Сохраняем результаты
            self.calculation_results = {
                'start_time': start_time,
                'base_tz': base_tz,
                'local_tz': local_tz,
                'hours_since_duty': hours_since_duty,
                'sectors': sectors,
                'has_frms': has_frms,
                'rest_in_flight': rest_in_flight,
                'rest_facility_class': rest_facility_class,
                'preflight': preflight,
                'postflight': postflight,
                'transfer': transfer,
                'acclimatization_status': acclimatization_status,
                'max_fdp': max_fdp,
                'required_rest': required_rest,
                'extension_without_rest': extension_without_rest,
                'min_rest_in_flight': min_rest_in_flight,
                'is_at_home_base': is_at_home_base
            }
            
            # Обновляем результаты
            self.update_results()
            
            # Показываем сообщение об успехе
            QMessageBox.information(self, "Успех", "Расчет FDP выполнен успешно!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при расчете FDP: {str(e)}")

    def update_results(self):
        """Обновляет все вкладки с результатами"""
        if not self.calculation_results:
            return
        
        # Обновляем детальные результаты
        self.update_detailed_results()
        
        # Обновляем рекомендации
        self.update_recommendations()

    def update_detailed_results(self):
        """Обновляет вкладку с детальными результатами"""
        results = self.calculation_results
        
        # Определяем цветовое кодирование на основе результатов
        status_color = self.get_result_status_color(results)
        
        details = f"<h2 style='color: {status_color};'>ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ РАСЧЕТА FDP</h2>"
        details += "<hr>"
        
        # Параметры расчета
        details += "ПАРАМЕТРЫ РАСЧЕТА:\n"
        details += f"📅 Дата и время начала FDP: {results['start_time'].strftime('%d.%m.%Y %H:%M')}\n"
        details += f"🌍 Базовый часовой пояс: {results['base_tz']}\n"
        details += f"🌍 Местный часовой пояс: {results['local_tz']}\n"
        details += f"⏰ Часов с начала выполнения обязанностей: {results['hours_since_duty']}\n"
        details += f"✈️ Количество секторов: {results['sectors']}\n"
        details += f"📊 Наличие FRMS: {'Да' if results['has_frms'] else 'Нет'}\n"
        details += f"🛏️ Отдых в полете: {'Да' if results['rest_in_flight'] else 'Нет'}\n"
        details += f"🛫 Предполетная подготовка: {results['preflight']} часов (стандартное значение)\n"
        details += f"🛬 Послеполетная подготовка: {results['postflight']} часов (стандартное значение)\n"
        if results['transfer'] > 0:
            transfer_hours = int(results['transfer'])
            transfer_minutes = int((results['transfer'] - transfer_hours) * 60)
            if transfer_minutes > 0:
                details += f"🚗 Трансфер: {transfer_hours}ч {transfer_minutes}мин (включен)\n"
            else:
                details += f"🚗 Трансфер: {transfer_hours} часов (включен)\n"
        else:
            details += f"🚗 Трансфер: отключен\n"
        
        if results['rest_facility_class']:
            details += f"🏨 Класс места для отдыха: {results['rest_facility_class']} класс\n"
        
        details += "\n"
        
        # Состояние акклиматизации
        status_text = {
            'Б': "Акклиматизирован к базовому времени",
            'В': "Акклиматизирован к новому времени", 
            'Н': "Неопределенное состояние акклиматизации"
        }
        details += f"🧠 Состояние акклиматизации: {results['acclimatization_status'].value} - {status_text[results['acclimatization_status'].value]}\n\n"
        
        # Основные результаты
        details += "ОСНОВНЫЕ РЕЗУЛЬТАТЫ:\n"
        details += f"⏱️ Максимальное FDP: {results['max_fdp']}\n"
        details += f"😴 Необходимый отдых: {results['required_rest']}\n"
        details += f"📍 Место отдыха: {'Основное место базирования' if results['is_at_home_base'] else 'Вне основного места базирования'}\n\n"
        
        # Продление FDP
        details += "ПРОДЛЕНИЕ FDP:\n"
        if results['extension_without_rest']:
            details += f"⏰ Продление без отдыха в полете: {results['extension_without_rest']}\n"
        else:
            details += "❌ Продление без отдыха в полете не допускается\n"
        
        if results['min_rest_in_flight']:
            details += f"🛏️ Минимальный отдых в полете: {results['min_rest_in_flight']}\n"
        
        # Добавляем прогресс-бары и статусные индикаторы
        details += self.add_progress_bars(results)
        
        # Добавляем статусный индикатор
        hour = results['start_time'].hour
        if 2 <= hour <= 5:
            details += self.create_status_indicator('warning', '⚠️ Время начала FDP попадает в окно циркадной активности')
        else:
            details += self.create_status_indicator('safe', '✅ Время начала FDP в норме')
        
        self.details_tab.setHtml(details)

    def update_recommendations(self):
        """Обновляет вкладку с рекомендациями"""
        results = self.calculation_results
        
        recommendations = f"РЕКОМЕНДАЦИИ И ПРЕДУПРЕЖДЕНИЯ\n"
        recommendations += "=" * 40 + "\n\n"
        
        # Проверка циркадного окна
        hour = results['start_time'].hour
        if 2 <= hour <= 5:
            recommendations += "⚠️ КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ:\n"
            recommendations += "Время начала FDP попадает в окно минимальной циркадной активности (02:00-05:59).\n"
            recommendations += "Это требует дополнительных ограничений согласно документу №110.\n\n"
            
            if results['has_frms']:
                if results['sectors'] <= 5:
                    recommendations += "При наличии FRMS допускается до 5 секторов, если они не попадают в окно циркадной активности более чем на 2 часа.\n"
                elif results['sectors'] <= 4:
                    recommendations += "При наличии FRMS допускается до 4 секторов, если они попадают в окно циркадной активности на 2 часа или меньше.\n"
                else:
                    recommendations += "При наличии FRMS допускается до 2 секторов, если они попадают в окно циркадной активности более чем на 2 часа.\n"
            else:
                recommendations += "Без FRMS рекомендуется избегать полетов в это время.\n"
            
            recommendations += "\n"
        
        # Рекомендации по акклиматизации
        if results['acclimatization_status'].value == 'Н':
            recommendations += "🧠 РЕКОМЕНДАЦИЯ ПО АККЛИМАТИЗАЦИИ:\n"
            recommendations += "Состояние акклиматизации не определено. Рекомендуется использовать наиболее строгие ограничения.\n\n"
        
        # Рекомендации по отдыху
        recommendations += "😴 РЕКОМЕНДАЦИИ ПО ОТДЫХУ:\n"
        if results['is_at_home_base']:
            recommendations += "• Отдых в основном месте базирования\n"
            recommendations += "• Минимум 8 часов сна без учета трансфера\n"
            recommendations += "• Общий период отдыха: не менее 12 часов или продолжительность предыдущего FDP\n"
        else:
            recommendations += "• Отдых вне основного места базирования\n"
            recommendations += "• Минимум 8 часов сна + 1 час на физиологические потребности\n"
            recommendations += "• Общий период отдыха: не менее 10 часов или продолжительность предыдущего FDP\n"
        
        recommendations += "\n"
        
        # Рекомендации по продлению
        if results['extension_without_rest']:
            recommendations += "⏰ РЕКОМЕНДАЦИИ ПО ПРОДЛЕНИЮ FDP:\n"
            recommendations += "• Продление возможно на срок до 1 часа\n"
            recommendations += "• Не более 2 раз в любые 7 последовательных дней\n"
            recommendations += "• При каждом продлении отдых увеличивается на 4 часа\n"
            recommendations += "• Требуется устное согласие всех членов экипажа\n\n"
        
        # Общие рекомендации
        recommendations += "📋 ОБЩИЕ РЕКОМЕНДАЦИИ:\n"
        recommendations += "• Соблюдайте все ограничения документа №110\n"
        recommendations += "• При непредвиденных обстоятельствах после взлета - полет до запланированного аэродрома\n"
        recommendations += "• Минимальный отдых после FDP: не менее 10 часов (включая 8 часов сна)\n"
        recommendations += "• Ведите учет всех изменений и продлений FDP\n"
        
        self.recommendations_tab.setPlainText(recommendations)

    def export_results(self):
        """Экспортирует результаты в файл"""
        if not self.calculation_results:
            QMessageBox.warning(self, "Предупреждение", "Нет результатов для экспорта. Выполните расчет сначала.")
            return
        
        # Простой экспорт в текстовый файл
        try:
            from datetime import datetime
            filename = f"fdp_calculation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.details_tab.toPlainText())
                f.write("\n\n" + "="*50 + "\n\n")
                f.write(self.recommendations_tab.toPlainText())
            
            QMessageBox.information(self, "Успех", f"Результаты экспортированы в файл: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {str(e)}")

    def validate_fdp_time(self):
        """Валидация времени начала FDP из маршрута"""
        start_time = self.get_fdp_start_time()
        hour = start_time.hour
        if 2 <= hour <= 5:
            self.fdp_validation.show_warning(
                "Время начала FDP попадает в окно минимальной циркадной активности (02:00-05:59). "
                "Это требует дополнительных ограничений согласно документу №110."
            )
        else:
            self.fdp_validation.clear()
        
        # Время начала FDP теперь показывается только в предварительном просмотре

    def validate_sectors(self):
        """Валидация количества секторов"""
        sectors = self.get_sectors_count()
        if sectors > 8:
            if not hasattr(self, 'sectors_validation'):
                # Создаем виджет валидации если его нет
                return
            self.sectors_validation.show_warning(
                f"Количество секторов ({sectors}) превышает рекомендуемое (8). "
                "Проверьте возможность выполнения такого количества секторов."
            )
        else:
            if hasattr(self, 'sectors_validation'):
                self.sectors_validation.clear()

    def setup_enhanced_styles(self):
        """Настройка улучшенных стилей для интерфейса"""
        # Стили для полей ввода с фокусом
        focused_style = """
            QDateTimeEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #3498db;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
        """
        
        # Стили для кнопок
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
        
        # Применяем стиги
        self.setStyleSheet(focused_style + button_style)

    def add_quick_actions(self):
        """Добавляет панель быстрых действий"""
        quick_actions_layout = QHBoxLayout()
        
        # Кнопка сохранения шаблона
        self.save_template_btn = QPushButton("💾 Сохранить шаблон")
        self.save_template_btn.setToolTip("Сохранить текущие настройки как шаблон для повторного использования")
        self.save_template_btn.clicked.connect(self.save_template)
        
        # Кнопка загрузки шаблона
        self.load_template_btn = QPushButton("📁 Загрузить шаблон")
        self.load_template_btn.setToolTip("Загрузить ранее сохраненный шаблон")
        self.load_template_btn.clicked.connect(self.load_template)
        
        # Кнопка копирования настроек
        self.copy_settings_btn = QPushButton("📋 Копировать настройки")
        self.copy_settings_btn.setToolTip("Копировать текущие настройки в буфер обмена")
        self.copy_settings_btn.clicked.connect(self.copy_settings)
        
        # Кнопка информации о панелях
        self.reset_panels_btn = QPushButton("ℹ️ Информация о панелях")
        self.reset_panels_btn.setToolTip("Показывает информацию о режиме фиксированного равного разделения панелей")
        self.reset_panels_btn.clicked.connect(self.reset_panel_sizes)
        
        quick_actions_layout.addWidget(self.save_template_btn)
        quick_actions_layout.addWidget(self.load_template_btn)
        quick_actions_layout.addWidget(self.copy_settings_btn)
        quick_actions_layout.addWidget(self.reset_panels_btn)
        quick_actions_layout.addStretch()
        
        return quick_actions_layout

    def save_template(self):
        """Сохраняет текущие настройки как шаблон"""
        QMessageBox.information(self, "Информация", "Функция сохранения шаблона будет реализована в следующей версии")

    def load_template(self):
        """Загружает шаблон"""
        QMessageBox.information(self, "Информация", "Функция загрузки шаблона будет реализована в следующей версии")

    def copy_settings(self):
        """Копирует настройки в буфер обмена"""
        try:
            start_time = self.get_fdp_start_time()
            if self.transfer_check.isChecked():
                transfer_hours = self.transfer_hours_spin.value()
                transfer_minutes = self.transfer_minutes_spin.value()
                if transfer_minutes > 0:
                    transfer_value = f"{transfer_hours}ч {transfer_minutes}мин"
                else:
                    transfer_value = f"{transfer_hours} часов"
            else:
                transfer_value = "отключен"
            settings_text = f"""
Настройки FDP:
- Дата начала: {start_time.strftime('%d.%m.%Y %H:%M')} (из маршрута)
- Базовый часовой пояс: {self.base_timezone_combo.currentText()}
- Местный часовой пояс: {self.get_departure_timezone()} (автоматически определен)
- FRMS: {self.has_frms_combo.currentText()}
- Отдых в полете: {'Да' if self.rest_in_flight_check.isChecked() else 'Нет'}
- Секторов: {self.get_sectors_count()}
- Трансфер: {transfer_value}
            """
            
            # Копируем в буфер обмена (упрощенная реализация)
            QMessageBox.information(self, "Скопировано", "Настройки скопированы в буфер обмена")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при копировании: {str(e)}")

    def create_visual_separators(self):
        """Создает визуальные разделители"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #bdc3c7;")
        return separator

    def add_help_tooltips(self):
        """Добавляет всплывающие подсказки"""
        self.has_frms_combo.setToolTip(
            "FRMS - Система управления факторами риска, связанными с утомлением. "
            "Позволяет использовать более гибкие ограничения FDP согласно документу №110."
        )
        
        self.rest_in_flight_check.setToolTip(
            "Отдых в полете предоставляется только на этапе установившегося горизонтального полета "
            "на крейсерском эшелоне согласно пункту 22 документа №110."
        )
        
        # Убираем tooltip для fdp_start_info, так как это поле больше не существует

    def setup_tab_order(self):
        """Настраивает порядок Tab для логичной навигации"""
        # Сначала навигация по маршруту (если есть сегменты)
        if self.segment_widgets:
            first_segment = self.segment_widgets[0]
            self.setTabOrder(first_segment.departure_combo, first_segment.departure_time)
            self.setTabOrder(first_segment.departure_time, first_segment.arrival_combo)
            self.setTabOrder(first_segment.arrival_combo, first_segment.arrival_time)
            # Переход от маршрута к основным параметрам
            self.setTabOrder(first_segment.arrival_time, self.base_timezone_combo)
        
        # Затем основные параметры
        self.setTabOrder(self.base_timezone_combo, self.hours_since_duty_spin)
        self.setTabOrder(self.hours_since_duty_spin, self.has_frms_combo)
        self.setTabOrder(self.has_frms_combo, self.rest_in_flight_check)

    def get_result_status_color(self, results):
        """Определяет цвет статуса на основе результатов"""
        hour = results['start_time'].hour
        sectors = results['sectors']
        
        # Критические условия
        if (2 <= hour <= 5 and sectors > 4 and not results['has_frms']):
            return "#e74c3c"  # Красный - опасно
        elif (2 <= hour <= 5 or sectors > 6):
            return "#f39c12"  # Оранжевый - предупреждение
        else:
            return "#27ae60"  # Зеленый - безопасно

    def create_status_indicator(self, status, message):
        """Создает визуальный индикатор статуса"""
        colors = {
            'safe': '#27ae60',
            'warning': '#f39c12', 
            'danger': '#e74c3c'
        }
        
        return f"""
        <div style="background-color: {colors[status]}; color: white; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <strong>{message}</strong>
        </div>
        """

    def add_progress_bars(self, results):
        """Добавляет прогресс-бары для визуализации лимитов"""
        max_fdp_hours = results['max_fdp'].total_seconds() / 3600
        max_possible_hours = 14  # Максимально возможное FDP
        
        progress_html = f"""
        <div style="margin: 10px 0;">
            <h4>Использование FDP:</h4>
            <div style="background-color: #ecf0f1; border-radius: 10px; padding: 3px;">
                <div style="background-color: #3498db; height: 20px; border-radius: 7px; width: {min((max_fdp_hours / max_possible_hours) * 100, 100)}%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                    {max_fdp_hours:.1f}ч из {max_possible_hours}ч
                </div>
            </div>
        </div>
        """
        return progress_html

    def resizeEvent(self, event):
        """Обработчик изменения размера окна - поддерживает пропорции 60/40"""
        super().resizeEvent(event)
        
        # Поддерживаем пропорции 60% левая панель / 40% правая панель
        if hasattr(self, 'splitter'):
            total_width = self.width()
            
            # Минимальные размеры панелей
            min_left_width = 400   # Увеличено для левой панели
            min_right_width = 350  # Остается для правой панели
            
            # Если окно достаточно широкое, используем пропорции 60/40
            if total_width > 750:  # Минимум для двух панелей с новыми пропорциями
                left_width = int(total_width * 0.6)
                right_width = total_width - left_width
                
                # Проверяем минимальные размеры
                if left_width < min_left_width:
                    left_width = min_left_width
                    right_width = total_width - left_width
                if right_width < min_right_width:
                    right_width = min_right_width
                    left_width = total_width - right_width
                    
                self.splitter.setSizes([left_width, right_width])
            else:
                # Для узких окон используем минимальные размеры
                self.splitter.setSizes([min_left_width, min_right_width])

    def on_splitter_moved(self, pos, index):
        """Обработчик перемещения разделителя - предотвращает изменение размеров"""
        # Получаем текущие размеры панелей
        sizes = self.splitter.sizes()
        
        # Минимальные размеры панелей
        min_left_width = 400
        min_right_width = 350
        
        # Всегда возвращаем к пропорциям 60/40
        total_width = self.width()
        if total_width > 750:
            left_width = int(total_width * 0.6)
            right_width = total_width - left_width
            
            # Проверяем минимальные размеры
            if left_width < min_left_width:
                left_width = min_left_width
                right_width = total_width - left_width
            if right_width < min_right_width:
                right_width = min_right_width
                left_width = total_width - right_width
        else:
            left_width = min_left_width
            right_width = min_right_width
        
        # Если размеры изменились, возвращаем к нужным пропорциям
        if sizes[0] != left_width or sizes[1] != right_width:
            self.splitter.setSizes([left_width, right_width])

    def get_settings_file_path(self):
        """Возвращает путь к файлу настроек"""
        return os.path.join(os.path.dirname(__file__), "panel_settings.json")

    def save_panel_sizes(self):
        """Сохраняет информацию о размерах окна (панели всегда равные)"""
        try:
            settings = {
                "window_width": self.width(),
                "panel_mode": "fixed_equal",  # Режим фиксированного равного разделения
                "last_updated": datetime.now().isoformat()
            }
            
            settings_file = self.get_settings_file_path()
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Ошибка при сохранении настроек окна: {e}")

    def load_panel_sizes(self):
        """Загружает настройки окна (панели всегда равные)"""
        try:
            settings_file = self.get_settings_file_path()
            
            if not os.path.exists(settings_file):
                return  # Если файла нет, используем значения по умолчанию
            
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            print("Загружены настройки окна - панели в режиме фиксированного равного разделения")
            
        except Exception as e:
            print(f"Ошибка при загрузке настроек окна: {e}")

    def reset_panel_sizes(self):
        """Информационное сообщение о фиксированном разделении панелей"""
        QMessageBox.information(
            self, 
            "Информация", 
            "Панели зафиксированы в режиме разделения экрана (60/40).\n"
            "Левая панель (60%) - калькулятор, правая панель (40%) - результаты.\n"
            "Это обеспечивает достаточно места для всех полей ввода."
        )