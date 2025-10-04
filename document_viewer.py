# document_viewer.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QLabel, QComboBox, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QFile, QTextStream
from PyQt6.QtGui import QFont
import docx  # Добавляем библиотеку для работы с docx файлами


class DocumentViewer(QWidget):
    def load_document_from_file(self):
        """Загружает документ из файла"""
        try:
            doc = docx.Document('document_110.docx')
            full_text = []
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)
            self.document_content = '\n'.join(full_text)
        except FileNotFoundError:
            self.document_content = "Файл с документом не найден. Разместите файл 'document_110.docx' в папке с приложением."
        except Exception as e:
            self.document_content = f"Ошибка загрузки документа: {str(e)}"

        self.text_edit.setPlainText(self.document_content)

    def __init__(self):
        super().__init__()
        self.document_content = ""
        self.init_ui()
        self.load_document_from_file()  # Загружаем из файла

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("Нормативный документ №110 от 29.12.2022")
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
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Панель управления
        control_layout = QHBoxLayout()

        # Поиск
        search_label = QLabel("Поиск:")
        control_layout.addWidget(search_label)

        self.search_edit = QComboBox()
        self.search_edit.setEditable(True)
        self.search_edit.setPlaceholderText("Введите текст для поиска...")
        self.search_edit.setMinimumWidth(200)
        control_layout.addWidget(self.search_edit)

        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.search_text)
        control_layout.addWidget(search_btn)

        # Навигация по главам
        chapter_label = QLabel("Глава:")
        control_layout.addWidget(chapter_label)

        self.chapter_combo = QComboBox()
        self.chapter_combo.addItems([
            "Все содержание",
            "Глава 1: ОБЩИЕ ПОЛОЖЕНИЯ",
            "Глава 2: УЧЕТ И ПЛАНИРОВАНИЕ РАБОЧЕГО ВРЕМЕНИ",
            "Глава 3: ОГРАНИЧЕНИЕ СЛУЖЕБНОГО ПОЛЕТНОГО ВРЕМЕНИ И ВРЕМЕНИ ОТДЫХА",
            "Глава 4: РЕЖИМ ОЖИДАНИЯ И НАХОЖДЕНИЕ В РЕЗЕРВЕ",
            "Глава 5: ОСОБЕННОСТИ РАБОЧЕГО ВРЕМЕНИ ДЛЯ СПЕЦИАЛИЗИРОВАННЫХ ОПЕРАЦИЙ",
            "Приложения 1-7"
        ])
        self.chapter_combo.currentTextChanged.connect(self.navigate_to_chapter)
        control_layout.addWidget(self.chapter_combo)

        control_layout.addStretch()

        # Кнопки управления текстом
        font_plus_btn = QPushButton("А+")
        font_plus_btn.clicked.connect(self.increase_font)
        font_plus_btn.setFixedSize(40, 30)
        control_layout.addWidget(font_plus_btn)

        font_minus_btn = QPushButton("А-")
        font_minus_btn.clicked.connect(self.decrease_font)
        font_minus_btn.setFixedSize(40, 30)
        control_layout.addWidget(font_minus_btn)

        main_layout.addLayout(control_layout)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # Область для отображения документа
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(self.document_content)

        # Настройка шрифта
        font = QFont()
        font.setPointSize(10)
        font.setFamily("Arial")
        self.text_edit.setFont(font)

        main_layout.addWidget(self.text_edit)

        self.setLayout(main_layout)

    def search_text(self):
        """Поиск текста в документе"""
        search_text = self.search_edit.currentText()
        if not search_text:
            return

        # Сбрасываем предыдущее выделение
        cursor = self.text_edit.textCursor()
        cursor.setPosition(0)
        self.text_edit.setTextCursor(cursor)

        # Ищем текст
        if not self.text_edit.find(search_text):
            QMessageBox.information(self, "Поиск", "Текст не найден")

    def navigate_to_chapter(self, chapter):
        """Навигация по главам документа"""
        chapters = {
            "Глава 1: ОБЩИЕ ПОЛОЖЕНИЯ": "ГЛАВА 1\nОБЩИЕ ПОЛОЖЕНИЯ",
            "Глава 2: УЧЕТ И ПЛАНИРОВАНИЕ РАБОЧЕГО ВРЕМЕНИ": "ГЛАВА 2\nУЧЕТ И ПЛАНИРОВАНИЕ РАБОЧЕГО ВРЕМЕНИ",
            "Глава 3: ОГРАНИЧЕНИЕ СЛУЖЕБНОГО ПОЛЕТНОГО ВРЕМЕНИ И ВРЕМЕНИ ОТДЫХА": "ГЛАВА 3\nОГРАНИЧЕНИЕ СЛУЖЕБНОГО ПОЛЕТНОГО ВРЕМЕНИ И ВРЕМЕНИ ОТДЫХА",
            "Глава 4: РЕЖИМ ОЖИДАНИЯ И НАХОЖДЕНИЕ В РЕЗЕРВЕ": "ГЛАВА 4\nРЕЖИМ ОЖИДАНИЯ И НАХОЖДЕНИЕ В РЕЗЕРВЕ",
            "Глава 5: ОСОБЕННОСТИ РАБОЧЕГО ВРЕМЕНИ ДЛЯ СПЕЦИАЛИЗИРОВАННЫХ ОПЕРАЦИЙ": "ГЛАВА 5\nОСОБЕННОСТИ РАБОЧЕГО ВРЕМЕНИ",
            "Приложения 1-7": "Приложение 1"
        }

        if chapter in chapters:
            search_text = chapters[chapter]
            cursor = self.text_edit.textCursor()
            cursor.setPosition(0)
            self.text_edit.setTextCursor(cursor)

            if self.text_edit.find(search_text):
                # Прокручиваем немного вверх для лучшего обзора
                cursor = self.text_edit.textCursor()
                cursor.movePosition(cursor.MoveOperation.Up, cursor.MoveMode.MoveAnchor, 5)
                self.text_edit.setTextCursor(cursor)

    def increase_font(self):
        """Увеличить размер шрифта"""
        font = self.text_edit.font()
        font.setPointSize(font.pointSize() + 1)
        self.text_edit.setFont(font)

    def decrease_font(self):
        """Уменьшить размер шрифта"""
        font = self.text_edit.font()
        if font.pointSize() > 8:
            font.setPointSize(font.pointSize() - 1)
            self.text_edit.setFont(font)