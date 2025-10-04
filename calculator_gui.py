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

        # Segment number display (simple number instead of emoji for compatibility)
        self.number_label = QLabel(f"{self.segment_number}.")
        self.number_label.setFixedWidth(20)  # Fixed width for consistent alignment
        self.number_label.setStyleSheet("font-weight: bold;")  # Bold for emphasis
        layout.addWidget(self.number_label)

        # Departure emoji
        departure_emoji = QLabel("🛫")
        departure_emoji.setFixedWidth(30)
        layout.addWidget(departure_emoji)

        # Departure airport selection combo box
        self.departure_combo = QComboBox()
        self.departure_combo.setEditable(True)  # Allow custom airport codes
        # Predefined list of common airport codes
        self.departure_combo.addItems(["UMMS", "UEEE", "UWKD", "UUDD", "URSS", "EKCH", "EDDF", "LFPG"])
        self.departure_combo.setMinimumWidth(120)  # Ensure adequate width for text
        layout.addWidget(self.departure_combo)

        # Departure time input
        self.departure_time = QDateTimeEdit()
        self.departure_time.setDisplayFormat("dd.MM.yyyy HH:mm")  # Date/time format
        self.departure_time.setDateTime(QDateTime.currentDateTime())  # Default to current time
        self.departure_time.setCalendarPopup(True)  # Enable calendar popup for easy date selection
        self.departure_time.setMinimumWidth(140)  # Ensure adequate width
        layout.addWidget(self.departure_time)

        # Arrival emoji
        arrival_emoji = QLabel("🛬")
        arrival_emoji.setFixedWidth(30)
        layout.addWidget(arrival_emoji)

        # Arrival airport selection combo box
        self.arrival_combo = QComboBox()
        self.arrival_combo.setEditable(True)  # Allow custom airport codes
        # Predefined list of common airport codes
        self.arrival_combo.addItems(["UMMS", "UEEE", "UWKD", "UUDD", "URSS", "EKCH", "EDDF", "LFPG"])
        self.arrival_combo.setMinimumWidth(120)  # Ensure adequate width for text
        layout.addWidget(self.arrival_combo)

        # Arrival time input
        self.arrival_time = QDateTimeEdit()
        self.arrival_time.setDisplayFormat("dd.MM.yyyy HH:mm")  # Date/time format
        # Default to current time + 1 hour for realistic flight duration
        self.arrival_time.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.arrival_time.setCalendarPopup(True)  # Enable calendar popup for easy date selection
        self.arrival_time.setMinimumWidth(140)  # Ensure adequate width
        layout.addWidget(self.arrival_time)

        # Add segment button
        self.add_btn = QPushButton("➕")
        self.add_btn.setFixedSize(30, 30)  # Fixed size for consistent appearance
        self.add_btn.clicked.connect(self.add_segment)  # Connect click to add method

        # Remove segment button
        self.remove_btn = QPushButton("➖")
        self.remove_btn.setFixedSize(30, 30)  # Fixed size for consistent appearance
        self.remove_btn.clicked.connect(self.remove_segment)  # Connect click to remove method

        # Container widget for buttons with fixed width for stability
        buttons_container = QWidget()
        buttons_container.setFixedWidth(70)  # Fixed width prevents layout shifts
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        buttons_layout.setSpacing(5)  # Small spacing between buttons

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

    def set_segment_number(self, number):
        """
        Update the segment number display

        Args:
            number (int): New segment number
        """
        self.segment_number = number
        if self.number_label:
            self.number_label.setText(f"{number}.")  # Update label with new number


class CalculatorTab(QWidget):
    def __init__(self):
        """
        Main calculator tab widget for flight duty period calculations
        """
        super().__init__()
        self.calculator = FDPCalculator()  # Backend calculator instance
        self.segment_widgets = []  # List to track all segment widgets
        self.init_ui()  # Initialize the user interface

    def init_ui(self):
        """Initialize the main user interface"""
        # Main vertical layout
        main_layout = QVBoxLayout()

        # Create scrollable area for content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()  # Widget that will be scrolled
        scroll_layout = QVBoxLayout(scroll_widget)  # Layout for scrollable content

        # Flight route section
        route_group = QGroupBox("Маршрут полета")  # "Flight Route" in Russian
        route_main_layout = QVBoxLayout()

        # Pre-flight preparation label
        pre_flight_label = QLabel("Предполетная подготовка - 60 мин")  # "Pre-flight preparation - 60 min"
        pre_flight_label.setStyleSheet("font-weight: bold; color: #2c3e50; padding: 5px;")
        route_main_layout.addWidget(pre_flight_label)

        # Container for segment widgets - segments will be displayed here
        self.segments_container = QVBoxLayout()
        route_main_layout.addLayout(self.segments_container)

        # Post-flight preparation label
        post_flight_label = QLabel("Послеполетная подготовка - 30 мин")  # "Post-flight preparation - 30 min"
        post_flight_label.setStyleSheet("font-weight: bold; color: #2c3e50; padding: 5px;")
        route_main_layout.addWidget(post_flight_label)

        # Set the main layout for route group and add to scroll layout
        route_group.setLayout(route_main_layout)
        scroll_layout.addWidget(route_group)

        # Create initial segment
        self.add_initial_segment()

        """
        # COMMENTED OUT: CALCULATION PARAMETERS BLOCK
        # This section is commented out but preserved for future use
        # Main calculation parameters group
        params_group = QGroupBox("Параметры расчета")
        params_layout = QFormLayout()

        # Base timezone selection
        self.base_timezone_combo = QComboBox()
        self.base_timezone_combo.addItems(pytz.all_timezones)
        self.base_timezone_combo.setCurrentText("Europe/Minsk")
        self.base_timezone_combo.setEditable(True)
        params_layout.addRow("Базовый часовой пояс:", self.base_timezone_combo)

        # Local timezone selection
        self.local_timezone_combo = QComboBox()
        self.local_timezone_combo.addItems(pytz.all_timezones)
        self.local_timezone_combo.setCurrentText("Europe/Minsk")
        self.local_timezone_combo.setEditable(True)
        params_layout.addRow("Часовой пояс места начала FDP:", self.local_timezone_combo)

        # Hours since duty start
        self.hours_since_duty_spin = QSpinBox()
        self.hours_since_duty_spin.setRange(0, 500)
        self.hours_since_duty_spin.setValue(0)
        params_layout.addRow("Часов с начала выполнения обязанностей:", self.hours_since_duty_spin)

        # FDP start date and time
        self.fdp_start_edit = QDateTimeEdit()
        self.fdp_start_edit.setDateTime(QDateTime.currentDateTime())
        self.fdp_start_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        params_layout.addRow("Дата и время начала FDP:", self.fdp_start_edit)

        # FRMS availability
        self.has_frms_combo = QComboBox()
        self.has_frms_combo.addItems(["Нет", "Да"])
        params_layout.addRow("Наличие FRMS:", self.has_frms_combo)

        # Rest facility class
        self.rest_facility_combo = QComboBox()
        self.rest_facility_combo.addItems(["Не предусмотрен", "1 класс", "2 класс", "3 класс"])
        params_layout.addRow("Класс места для отдыха:", self.rest_facility_combo)

        params_group.setLayout(params_layout)
        scroll_layout.addWidget(params_group)

        # COMMENTED OUT: CALCULATION BUTTONS BLOCK
        # Calculation buttons layout
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
        """

        # Results display text area
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)  # Make it read-only
        self.result_text.setMinimumHeight(200)  # Ensure adequate height for results
        scroll_layout.addWidget(self.result_text)

        # Configure scroll area
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)  # Allow widget to resize with content
        scroll_area.setMinimumHeight(600)  # Set minimum height

        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)  # Set main layout for this widget

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

        # Auto-fill departure from previous segment's arrival
        if current_index >= 0 and current_index < len(self.segment_widgets):
            prev_segment = self.segment_widgets[current_index]

            # Set departure airport from previous arrival
            new_segment.departure_combo.setCurrentText(prev_segment.arrival_combo.currentText())

            # Set departure time as previous arrival time + 30 minutes
            arrival_time = prev_segment.arrival_time.dateTime()
            new_departure_time = arrival_time.addSecs(1800)  # +30 minutes
            new_segment.departure_time.setDateTime(new_departure_time)

            # Set arrival time as departure time + 1 hour
            new_arrival_time = new_departure_time.addSecs(3600)  # +1 hour
            new_segment.arrival_time.setDateTime(new_arrival_time)

        # Insert new segment after current segment
        self.segment_widgets.insert(current_index + 1, new_segment)

        # Rebuild the entire segments layout
        self.rebuild_segments_layout()

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

    def rebuild_segments_layout(self):
        """Completely rebuild the segments layout with current widgets"""
        # Clear the container
        self.clear_segments_container()

        # Add all segments back to container
        for segment in self.segment_widgets:
            self.segments_container.addWidget(segment)

        # Renumber segments and update buttons
        self.renumber_segments()

    def renumber_segments(self):
        """Renumber all segments sequentially starting from 1"""
        for i, segment in enumerate(self.segment_widgets):
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
                'departure': segment.departure_combo.currentText(),  # Departure airport
                'departure_time': segment.departure_time.dateTime().toPyDateTime(),  # Departure time
                'arrival': segment.arrival_combo.currentText(),  # Arrival airport
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

    """
    # COMMENTED OUT: CALCULATION METHODS
    # These methods are preserved but commented out for future implementation

    def calculate_acclimatization(self):
        # Method to calculate crew acclimatization status
        pass

    def calculate_fdp(self):
        # Method to calculate Flight Duty Period
        pass

    def calculate_rest(self):
        # Method to calculate required rest periods
        pass

    def calculate_extension(self):
        # Method to calculate duty period extensions
        pass
    """