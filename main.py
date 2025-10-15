# main.py
import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

def main():
    # Создаем экземпляр QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Aviation FDP Calculator")
    app.setApplicationVersion("1.0")


    # Создаем и показываем главное окно
    window = MainWindow()
    window.setWindowTitle("Aviation FDP Calculator - Beta")
    window.resize(800, 600)
    window.show()

    # Запускаем цикл обработки событий
    sys.exit(app.exec())    

if __name__ == "__main__":
    main()