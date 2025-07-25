#!/usr/bin/env python3
"""
PhotoControl v2.0 - Azimuth Image Processor
Професійний інтерфейс для обробки зображень з азимутальною сіткою

Основна точка входу програми
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Додаємо поточну директорію до шляху Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def get_resource_path(relative_path):
    """Отримати абсолютний шлях до ресурсу"""
    try:
        # PyInstaller тимчасова папка
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


def setup_application():
    """Налаштування QApplication"""
    # Налаштування для високої роздільної здатності
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Встановлення іконки програми
    icon_path = get_resource_path("netaz.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Налаштування програми
    app.setApplicationName("PhotoControl")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("PhotoControl Team")
    
    return app


def main():
    """Головна функція програми"""
    try:
        # Створення та налаштування додатку
        app = setup_application()
        
        # Створення головного вікна
        window = MainWindow()
        window.show()
        
        print("PhotoControl v2.0 запущено успішно")
        print(f"Python версія: {sys.version}")
        print(f"Qt версія: {app.applicationVersion()}")
        
        # Запуск основного циклу
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Помилка запуску програми: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()