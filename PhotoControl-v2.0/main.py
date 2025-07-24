#!/usr/bin/env python3
"""
PhotoControl v2.0 - Головний файл програми
Система аналізу фотографій з азимутальною сіткою та створенням Word альбомів
"""

import sys
import os
from pathlib import Path
from typing import List, Optional

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTranslator, QLocale
from PyQt5.QtGui import QIcon

# Додавання шляху для імпорту наших модулів
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Імпорти наших модулів
from ui.main_window import MainWindow
from utils.file_utils import get_resource_path


def setup_application() -> QApplication:
    """
    Налаштування застосунку
    
    Returns:
        Налаштований QApplication
    """
    app = QApplication(sys.argv)
    
    # Базові налаштування
    app.setApplicationName("PhotoControl")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("PhotoControl Team")
    
    # Іконка застосунку
    icon_path = get_resource_path("netaz.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Налаштування локалізації (підготовка на майбутнє)
    locale = QLocale.system()
    translator = QTranslator()
    
    # Поки що використовуємо українську за замовчуванням
    # В майбутньому можна додати файли перекладів
    
    return app


def check_dependencies() -> bool:
    """
    Перевірка критичних залежностей
    
    Returns:
        True якщо всі залежності доступні
    """
    missing_deps = []
    
    # Перевірка PyQt5
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        missing_deps.append("PyQt5")
    
    # Перевірка PIL/Pillow
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("Pillow")
    
    # Перевірка python-docx (не критична, але бажана)
    try:
        import docx
    except ImportError:
        print("⚠️  python-docx не встановлено - створення Word альбомів недоступне")
        print("   Встановіть: pip install python-docx")
    
    if missing_deps:
        error_msg = f"Критичні залежності відсутні: {', '.join(missing_deps)}"
        print(f"❌ {error_msg}")
        
        # Показуємо повідомлення користувачу
        if 'PyQt5' not in missing_deps:  # Якщо PyQt5 є, можемо показати діалог
            QMessageBox.critical(None, "Помилка залежностей", 
                               f"{error_msg}\n\nПрограма не може запуститися.")
        
        return False
    
    return True


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Глобальний обробник виключень
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Ctrl+C - нормальне завершення
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Логування помилки
    import traceback
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"❌ Необроблена помилка:\n{error_msg}")
    
    # Показуємо користувачу (якщо можливо)
    try:
        QMessageBox.critical(None, "Критична помилка", 
                           f"Виникла неочікувана помилка:\n\n{exc_value}\n\n"
                           f"Деталі записано в консоль.")
    except:
        pass


def main():
    """Головна функція програми"""
    print("=" * 50)
    print(f"🚀 PhotoControl v2.0")
    print(f"   Система аналізу фотографій з азимутальною сіткою")
    print("=" * 50)
    
    # Встановлення глобального обробника виключень
    sys.excepthook = handle_exception
    
    # Перевірка залежностей
    if not check_dependencies():
        return 1
    
    # Створення застосунку
    try:
        app = setup_application()
        print("✅ Застосунок ініціалізовано")
        
        # Створення головного вікна
        window = MainWindow()
        print("✅ Головне вікно створено")
        
        # Показуємо вікно
        window.show()
        print("✅ Інтерфейс запущено")
        
        # Запуск циклу подій
        print("🎯 PhotoControl готовий до роботи!")
        print("-" * 50)
        
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Критична помилка при запуску: {e}")
        
        try:
            QMessageBox.critical(None, "Помилка запуску", 
                               f"Не вдалося запустити програму:\n\n{e}")
        except:
            pass
        
        return 1
    
    finally:
        print("\n" + "=" * 50)
        print("📋 PhotoControl завершено")
        print("=" * 50)


if __name__ == "__main__":
    # Установка кодування для консолі Windows
    if sys.platform == "win32":
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except:
            pass  # Ігноруємо помилки кодування
    
    exit_code = main()
    sys.exit(exit_code)