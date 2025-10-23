"""
Виджет для поиска аэропортов с автокомплитом
"""

from PyQt6.QtWidgets import QLineEdit, QCompleter
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont
from ..data.airports import get_airports_data


class AirportSearchWidget(QLineEdit):
    """Виджет для поиска аэропортов с автокомплитом"""
    
    airport_selected = pyqtSignal(str)  # Сигнал с ICAO кодом выбранного аэропорта
    
    def __init__(self, airports_data=None, parent=None):
        super().__init__(parent)
        self.airports_data = airports_data or get_airports_data()
        self.current_icao = None
        self.search_to_icao = {}  # Словарь для поиска ICAO кода по тексту
        
        self.setup_ui()
        self.setup_autocomplete()
        
        # Подключаем сигналы
        self.textChanged.connect(self.on_text_changed)
        self.returnPressed.connect(self.on_return_pressed)
        self.completer.activated.connect(self.on_completer_activated)
        
        # Connect to popup selection change to handle mouse clicks
        popup = self.completer.popup()
        popup.selectionModel().selectionChanged.connect(self.on_popup_selection_changed)
        
        # Connect to focus events to clean up text when field loses focus
        self.focusOutEvent = self.on_focus_out
        
        # Override key press event to prevent automatic text insertion
        self.keyPressEvent = self.on_key_press
        
        # Устанавливаем размеры поля поиска
        self.setMinimumWidth(160)
        self.setMaximumWidth(160)
        
        # Устанавливаем размеры popup
        popup.setMinimumWidth(280)
        popup.setMaximumWidth(300)
        
        # Настройка шрифта
        font = QFont()
        font.setPointSize(9)
        self.setFont(font)
        
        # Устанавливаем placeholder
        self.setPlaceholderText("ICAO/IATA/город/аэропорт")
        
        # Устанавливаем tooltip
        self.setToolTip("Введите ICAO код, IATA код, название города или аэропорта")
    
    def setup_ui(self):
        """Настройка интерфейса виджета"""
        # Устанавливаем стиль
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #007acc;
            }
        """)
    
    def setup_autocomplete(self):
        """Настройка автокомплита"""
        # Создаем список для автокомплита
        search_strings = []
        
        for icao, data in self.airports_data.items():
            # Создаем основной формат отображения
            display_format = f"{icao}/{data['iata']} - {data['city']}, {data['name']}"
            search_strings.append(display_format)
            self.search_to_icao[display_format.lower()] = icao
            
            # Add individual search terms for matching
            search_terms = [
                icao.lower(),  # ICAO code
                data['iata'].lower(),  # IATA code
                data['city'].lower(),  # City name
                data['name'].lower(),  # Airport name
            ]
            
            # Добавляем индивидуальные термины поиска
            for term in search_terms:
                if term not in self.search_to_icao:
                    self.search_to_icao[term] = icao
        
        # Создаем completer
        self.completer = QCompleter(search_strings, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.setCompleter(self.completer)
        
        # Настройка popup
        popup = self.completer.popup()
        popup.setMinimumWidth(280)
        popup.setMaximumWidth(300)
    
    def on_text_changed(self, text):
        """Обработка изменения текста"""
        if text:
            # Обновляем префикс для автокомплита
            self.completer.setCompletionPrefix(text)
            # Показываем popup
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
        """Обработка нажатия Enter"""
        text = self.text().strip()
        if text:
            # Ищем точное совпадение
            for search_text, icao in self.search_to_icao.items():
                if text.lower() == search_text.lower():
                    self.current_icao = icao
                    data = self.airports_data[icao]
                    codes_display = f"{icao}/{data['iata']}"
                    self.setText(codes_display)
                    self.airport_selected.emit(icao)
                    break
    
    def on_popup_selection_changed(self):
        """Handle selection change in popup (for mouse clicks)"""
        # Get selected text from popup
        index = self.completer.popup().currentIndex()
        if index.isValid():
            text = self.completer.completionModel().data(index)
            if text:
                # Extract ICAO code from selected text
                icao = self.search_to_icao.get(text.lower())
                if icao:
                    self.current_icao = icao
                    # Set only ICAO/IATA codes in the field immediately
                    data = self.airports_data[icao]
                    codes_display = f"{icao}/{data['iata']}"
                    self.setText(codes_display)
                    self.airport_selected.emit(icao)
                    # Hide popup immediately after selection
                    self.completer.popup().hide()
    
    def on_focus_out(self, event):
        """Handle focus out event to clean up text format"""
        # Check if current text contains the full format
        current_text = self.text()
        if current_text and " - " in current_text:
            # Extract ICAO code from full format text
            icao = self.search_to_icao.get(current_text.lower())
            if icao:
                # Set only ICAO/IATA codes in the field
                data = self.airports_data[icao]
                codes_display = f"{icao}/{data['iata']}"
                self.setText(codes_display)
                self.current_icao = icao
                self.airport_selected.emit(icao)
        
        # Call the original focusOutEvent
        super().focusOutEvent(event)
    
    def on_key_press(self, event):
        """Handle key press events to prevent automatic text insertion"""
        # Handle Enter key
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.on_return_pressed()
            return
        
        # Handle other keys normally
        super().keyPressEvent(event)
    
    def get_current_icao(self):
        """Возвращает текущий ICAO код"""
        return self.current_icao
    
    def set_airport(self, icao_code):
        """Устанавливает аэропорт по ICAO коду"""
        if icao_code in self.airports_data:
            self.current_icao = icao_code
            data = self.airports_data[icao_code]
            codes_display = f"{icao_code}/{data['iata']}"
            self.setText(codes_display)
            self.airport_selected.emit(icao_code)
