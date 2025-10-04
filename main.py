# main.py
import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

def main():
    # Создаем экземпляр QApplication
    app = QApplication(sys.argv)

    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()

    # Запускаем цикл обработки событий
    sys.exit(app.exec())    

if __name__ == "__main__":
    main()