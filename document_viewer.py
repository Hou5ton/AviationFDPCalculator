# document_viewer.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QLabel, QComboBox, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QFile, QTextStream
from PyQt6.QtGui import QFont
try:
    import docx  # Library for reading .docx files
except Exception:  # Handle missing or faulty python-docx gracefully
    docx = None


class DocumentViewer(QWidget):
    def load_document_from_file(self):
        """
        Loads document content from a .docx file

        Attempts to read the document_110.docx file using python-docx library.
        If file is not found or other errors occur, displays appropriate error message.
        """
        try:
            if docx is None:
                # python-docx is not installed
                self.document_content = (
                    "Библиотека python-docx не установлена. Установите пакет 'python-docx' или откройте файл вручную."
                )
            else:
                # Create a Document object from the .docx file
                doc = docx.Document('document_110.docx')

                # Extract text from all paragraphs in the document
                full_text = []
                for paragraph in doc.paragraphs:
                    full_text.append(paragraph.text)

                # Join all paragraphs with newline characters
                self.document_content = '\n'.join(full_text)

        except FileNotFoundError:
            # Handle case when document file doesn't exist
            self.document_content = "Файл с документом не найден. Разместите файл 'document_110.docx' в папке с приложением."
        except Exception as e:
            # Handle any other unexpected errors during file loading
            self.document_content = f"Ошибка загрузки документа: {str(e)}"

        # Display the loaded content in the text editor widget
        self.text_edit.setPlainText(self.document_content)

    def __init__(self):
        """
        Constructor for DocumentViewer class

        Initializes the widget, sets up the user interface,
        and loads the document content from file.
        """
        super().__init__()  # Call parent class constructor
        self.document_content = ""  # Initialize empty document content
        self.init_ui()  # Set up the user interface
        self.load_document_from_file()  # Load document content from file

    def init_ui(self):
        """
        Initializes and sets up the user interface components

        Creates all GUI elements including:
        - Title label
        - Control panel with search and navigation
        - Text display area
        - Font controls
        """
        # Main vertical layout that will contain all UI elements
        main_layout = QVBoxLayout()

        # Document title label
        title_label = QLabel("Нормативный документ №110 от 29.12.2022")
        # Apply CSS-like styling to the title
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the text
        main_layout.addWidget(title_label)  # Add title to main layout

        # Control panel layout (horizontal)
        control_layout = QHBoxLayout()

        # Search functionality components
        search_label = QLabel("Поиск:")  # Search label
        control_layout.addWidget(search_label)  # Add to control panel

        # Search combo box (editable for text input)
        self.search_edit = QComboBox()
        self.search_edit.setEditable(True)  # Allow typing in the combo box
        self.search_edit.setPlaceholderText("Введите текст для поиска...")  # Hint text
        self.search_edit.setMinimumWidth(200)  # Set minimum width
        control_layout.addWidget(self.search_edit)  # Add to control panel

        # Search button
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.search_text)  # Connect button click to search method
        control_layout.addWidget(search_btn)  # Add to control panel

        # Chapter navigation components
        chapter_label = QLabel("Глава:")  # Chapter label
        control_layout.addWidget(chapter_label)  # Add to control panel

        # Chapter selection combo box
        self.chapter_combo = QComboBox()
        # Add all available chapters to the dropdown
        self.chapter_combo.addItems([
            "Все содержание",  # Show entire document
            "Глава 1: ОБЩИЕ ПОЛОЖЕНИЯ",
            "Глава 2: УЧЕТ И ПЛАНИРОВАНИЕ РАБОЧЕГО ВРЕМЕНИ",
            "Глава 3: ОГРАНИЧЕНИЕ СЛУЖЕБНОГО ПОЛЕТНОГО ВРЕМЕНИ И ВРЕМЕНИ ОТДЫХА",
            "Глава 4: РЕЖИМ ОЖИДАНИЯ И НАХОЖДЕНИЕ В РЕЗЕРВЕ",
            "Глава 5: ОСОБЕННОСТИ РАБОЧЕГО ВРЕМЕНИ ДЛЯ СПЕЦИАЛИЗИРОВАННЫХ ОПЕРАЦИЙ",
            "Приложения 1-7"  # Appendices section
        ])
        # Connect chapter selection change to navigation method
        self.chapter_combo.currentTextChanged.connect(self.navigate_to_chapter)
        control_layout.addWidget(self.chapter_combo)  # Add to control panel

        control_layout.addStretch()  # Add stretchable space to push next elements to the right

        # Font size control buttons
        font_plus_btn = QPushButton("А+")  # Increase font size button
        font_plus_btn.clicked.connect(self.increase_font)  # Connect to font increase method
        font_plus_btn.setFixedSize(40, 30)  # Set fixed button size
        control_layout.addWidget(font_plus_btn)  # Add to control panel

        font_minus_btn = QPushButton("А-")  # Decrease font size button
        font_minus_btn.clicked.connect(self.decrease_font)  # Connect to font decrease method
        font_minus_btn.setFixedSize(40, 30)  # Set fixed button size
        control_layout.addWidget(font_minus_btn)  # Add to control panel

        main_layout.addLayout(control_layout)  # Add control panel to main layout

        # Horizontal separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)  # Horizontal line
        separator.setFrameShadow(QFrame.Shadow.Sunken)  # Sunken shadow effect
        main_layout.addWidget(separator)  # Add to main layout

        # Main text display area
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)  # Make text area read-only
        self.text_edit.setPlainText(self.document_content)  # Set initial content

        # Configure default font for text display
        font = QFont()
        font.setPointSize(10)  # Set initial font size
        font.setFamily("Arial")  # Set font family
        self.text_edit.setFont(font)  # Apply font to text editor

        main_layout.addWidget(self.text_edit)  # Add text editor to main layout

        self.setLayout(main_layout)  # Set main layout for the widget

    def search_text(self):
        """
        Searches for text in the document

        Gets search text from the combo box and highlights the first occurrence.
        If text is not found, displays an information message.
        """
        search_text = self.search_edit.currentText()  # Get text from search box
        if not search_text:  # Check if search text is empty
            return

        # Reset cursor to beginning of document to start search from top
        cursor = self.text_edit.textCursor()
        cursor.setPosition(0)
        self.text_edit.setTextCursor(cursor)

        # Search for the text in the document
        if not self.text_edit.find(search_text):
            # Show message if text is not found
            QMessageBox.information(self, "Поиск", "Текст не найден")

    def navigate_to_chapter(self, chapter):
        """
        Navigates to specific chapter in the document

        Maps chapter names from dropdown to actual text markers in the document
        and scrolls to the beginning of the selected chapter.

        Args:
            chapter (str): The selected chapter name from dropdown
        """
        # Dictionary mapping dropdown items to actual text markers in document
        chapters = {
            "Глава 1: ОБЩИЕ ПОЛОЖЕНИЯ": "ГЛАВА 1\nОБЩИЕ ПОЛОЖЕНИЯ",
            "Глава 2: УЧЕТ И ПЛАНИРОВАНИЕ РАБОЧЕГО ВРЕМЕНИ": "ГЛАВА 2\nУЧЕТ И ПЛАНИРОВАНИЕ РАБОЧЕГО ВРЕМЕНИ",
            "Глава 3: ОГРАНИЧЕНИЕ СЛУЖЕБНОГО ПОЛЕТНОГО ВРЕМЕНИ И ВРЕМЕНИ ОТДЫХА": "ГЛАВА 3\nОГРАНИЧЕНИЕ СЛУЖЕБНОГО ПОЛЕТНОГО ВРЕМЕНИ И ВРЕМЕНИ ОТДЫХА",
            "Глава 4: РЕЖИМ ОЖИДАНИЯ И НАХОЖДЕНИЕ В РЕЗЕРВЕ": "ГЛАВА 4\nРЕЖИМ ОЖИДАНИЯ И НАХОЖДЕНИЕ В РЕЗЕРВЕ",
            "Глава 5: ОСОБЕННОСТИ РАБОЧЕГО ВРЕМЕНИ ДЛЯ СПЕЦИАЛИЗИРОВАННЫХ ОПЕРАЦИЙ": "ГЛАВА 5\nОСОБЕННОСТИ РАБОЧЕГО ВРЕМЕНИ",
            "Приложения 1-7": "Приложение 1"  # Navigate to first appendix
        }

        if chapter in chapters:  # Check if selected chapter exists in mapping
            search_text = chapters[chapter]  # Get corresponding document marker

            # Reset cursor to beginning of document
            cursor = self.text_edit.textCursor()
            cursor.setPosition(0)
            self.text_edit.setTextCursor(cursor)

            # Search for the chapter marker text
            if self.text_edit.find(search_text):
                # If found, scroll up a bit for better visibility
                cursor = self.text_edit.textCursor()
                cursor.movePosition(cursor.MoveOperation.Up, cursor.MoveMode.MoveAnchor, 5)
                self.text_edit.setTextCursor(cursor)

    def increase_font(self):
        """
        Increases the font size in the text display

        Gets current font and increases its point size by 1
        """
        font = self.text_edit.font()  # Get current font
        font.setPointSize(font.pointSize() + 1)  # Increase font size by 1
        self.text_edit.setFont(font)  # Apply new font

    def decrease_font(self):
        """
        Decreases the font size in the text display

        Gets current font and decreases its point size by 1,
        but not below the minimum size of 8 points
        """
        font = self.text_edit.font()  # Get current font
        if font.pointSize() > 8:  # Check minimum font size limit
            font.setPointSize(font.pointSize() - 1)  # Decrease font size by 1
            self.text_edit.setFont(font)  # Apply new font