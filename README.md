# Aviation FDP Calculator

Приложение для расчёта рабочего времени и времени отдыха членов экипажей воздушных судов (ВС) в соответствии с нормативными документами Республики Беларусь.

## 🚀 Запуск проекта (краткая версия)

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/Hou5ton/AviationFDPCalculator.git
    cd AviationFDPCalculator
    ```

2.  **Создайте и активируйте виртуальное окружение:**
    ```bash
    python -m venv venv
    # Для Windows:
    .\venv\Scripts\activate
    # Для macOS/Linux:
    source venv/bin/activate
    ```

3.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Запустите приложение:**
    ```bash
    python main.py
    ```

## 📚 Подробное руководство по установке

### Предварительные требования

*   **Python 3.8+** (рекомендуется 3.8, 3.9, 3.10 или 3.11). Важно: Python 3.12 и новее могут иметь проблемы совместимости с некоторыми библиотеками.
*   **pip** (обычно входит в состав Python).
*   **Git** (для клонирования репозитория).

### Решение известных проблем

#### Ошибка `ImportError: DLL load failed while importing QtCore`

Если при запуске возникает ошибка, связанная с DLL, выполните следующие команды **в активированном виртуальном окружении**:

```bash
# Полностью удаляем потенциально конфликтующие пакеты
pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip pyqt6-plugins pyqt6-tools qt6-applications qt6-tools

# Устанавливаем проверенные совместимые версии
pip install PyQt6==6.5.0 PyQt6-Qt6==6.5.0 PyQt6-sip==13.5.0