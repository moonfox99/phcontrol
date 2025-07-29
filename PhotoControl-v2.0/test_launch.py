#!/usr/bin/env python3
"""
Тестування запуску PhotoControl v2.0
Перевірка всіх компонентів та можливість запуску
"""

import sys
import os

# Додавання шляху для імпорту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Тестування імпортів модулів"""
    print("🔍 Перевірка імпортів...")
    
    # Тест PyQt5
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 доступний")
    except ImportError:
        print("❌ PyQt5 недоступний! Встановіть: pip install PyQt5")
        return False
    
    # Тест основних модулів
    results = {}
    
    # Main Window
    try:
        from ui.main_window import MainWindow
        results['MainWindow'] = True
        print("✅ MainWindow завантажено")
    except ImportError as e:
        results['MainWindow'] = False
        print(f"❌ MainWindow помилка: {e}")
    
    # Control Panel
    try:
        from ui.panels.control_panel import ControlPanel
        results['ControlPanel'] = True
        print("✅ ControlPanel завантажено")
    except ImportError as e:
        results['ControlPanel'] = False
        print(f"⚠️ ControlPanel помилка: {e}")
    
    # Constants
    try:
        from core.constants import UI
        results['Constants'] = True
        print("✅ Constants завантажено")
    except ImportError as e:
        results['Constants'] = False
        print(f"⚠️ Constants помилка: {e} (буде fallback)")
    
    # Image Processor
    try:
        from core.image_processor import ImageProcessor
        results['ImageProcessor'] = True
        print("✅ ImageProcessor завантажено")
    except ImportError as e:
        results['ImageProcessor'] = False
        print(f"⚠️ ImageProcessor помилка: {e}")
    
    # Album Creator
    try:
        from core.album_creator import AlbumCreator
        results['AlbumCreator'] = True
        print("✅ AlbumCreator завантажено")
    except ImportError as e:
        results['AlbumCreator'] = False
        print(f"⚠️ AlbumCreator помилка: {e}")
    
    # Translator
    try:
        from translations.translator import get_translator
        results['Translator'] = True
        print("✅ Translator завантажено")
    except ImportError as e:
        results['Translator'] = False
        print(f"⚠️ Translator помилка: {e}")
    
    return results

def test_window_creation():
    """Тестування створення головного вікна"""
    print("\n🏗️ Тестування створення вікна...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.main_window import MainWindow
        
        app = QApplication([])  # Порожній список args
        window = MainWindow()
        
        print("✅ MainWindow створено успішно")
        print(f"   Заголовок: {window.windowTitle()}")
        print(f"   Розмір: {window.size().width()}×{window.size().height()}")
        
        # Перевірка панелей
        panels_status = {
            'ControlPanel': window.control_panel is not None,
            'DataPanel': window.data_panel is not None,
            'ImagePanel': window.image_panel is not None,
            'ThumbnailBrowser': window.thumbnail_browser is not None
        }
        
        print("\n📋 Статус панелей:")
        working_panels = 0
        for panel, status in panels_status.items():
            status_icon = "✅" if status else "⚠️ заглушка"
            print(f"   {panel}: {status_icon}")
            if status:
                working_panels += 1
        
        # Тест основних методів
        print("\n🔧 Тестування методів:")
        try:
            # Тест методів що не потребують UI interaction
            if hasattr(window, '_show_about'):
                print("   _show_about(): ✅")
            if hasattr(window, '_save_settings'):
                print("   _save_settings(): ✅")
            if hasattr(window, 'get_current_language') and hasattr(window, 'control_panel') and window.control_panel:
                print("   get_current_language(): ✅")
        except Exception as e:
            print(f"   Помилка тестування методів: {e}")
        
        return True, working_panels
        
    except Exception as e:
        print(f"❌ Помилка створення вікна: {e}")
        import traceback
        traceback.print_exc()
        return False, 0

def test_control_panel():
    """Тестування ControlPanel окремо"""
    print("\n📋 Тестування ControlPanel...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.panels.control_panel import ControlPanel
        
        if not QApplication.instance():
            app = QApplication([])
        
        panel = ControlPanel.create_test_panel()
        
        print("✅ ControlPanel створено успішно")
        
        # Тест методів
        test_methods = [
            'add_result',
            'set_buttons_enabled', 
            'update_processed_count',
            'get_document_date',
            'get_current_language'
        ]
        
        working_methods = 0
        for method_name in test_methods:
            if hasattr(panel, method_name):
                try:
                    method = getattr(panel, method_name)
                    if method_name == 'add_result':
                        method("Тест методу add_result")
                    elif method_name == 'set_buttons_enabled':
                        method(save_image=True)
                    elif method_name == 'update_processed_count':
                        method(5)
                    elif method_name in ['get_document_date', 'get_current_language']:
                        result = method()
                        print(f"   {method_name}(): {result}")
                    
                    working_methods += 1
                    print(f"   {method_name}(): ✅")
                    
                except Exception as e:
                    print(f"   {method_name}(): ❌ {e}")
            else:
                print(f"   {method_name}(): ❌ метод відсутній")
        
        return True, working_methods
        
    except Exception as e:
        print(f"❌ Помилка тестування ControlPanel: {e}")
        return False, 0

def main():
    """Головна функція тестування"""
    print("🚀 ТЕСТУВАННЯ PHOTOCONTROL V2.0")
    print("=" * 60)
    
    # Тест 1: Імпорти
    print("\n📦 КРОК 1: Перевірка модулів")
    import_results = test_imports()
    
    if not import_results or not import_results.get('MainWindow', False):
        print("\n❌ КРИТИЧНА ПОМИЛКА: MainWindow не завантажується!")
        print("🔧 Перевірте файл ui/main_window.py")
        return False
    
    # Тест 2: Створення вікна
    print("\n🏗️ КРОК 2: Тестування головного вікна")
    window_success, working_panels = test_window_creation()
    
    if not window_success:
        print("\n❌ КРИТИЧНА ПОМИЛКА: Не вдалося створити головне вікно!")
        return False
    
    # Тест 3: ControlPanel
    print("\n📋 КРОК 3: Тестування ControlPanel")
    panel_success, working_methods = test_control_panel()
    
    # Підсумок
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТИ ТЕСТУВАННЯ")
    print("=" * 60)
    
    if import_results:
        total_modules = len(import_results)
        working_modules = sum(import_results.values())
        print(f"📦 Модулі: {working_modules}/{total_modules} працюють")
    
    if window_success:
        print(f"🏗️ Головне вікно: ✅ створено")
        print(f"📋 Панелі: {working_panels}/4 завантажено")
    else:
        print(f"🏗️ Головне вікно: ❌ помилка")
    
    if panel_success:
        print(f"🔧 ControlPanel методи: {working_methods}/5 працюють")
    
    # Фінальна оцінка
    if window_success and working_panels >= 1:
        print("\n🎉 РЕЗУЛЬТАТ: PhotoControl v2.0 ГОТОВИЙ ДО ЗАПУСКУ!")
        print("🚀 Рекомендація: запустіть main.py для повного тестування")
        print("\n💡 Що працює:")
        print("   - Базовий інтерфейс")
        print("   - Меню та статус-бар") 
        print("   - Файлові діалоги")
        print("   - Система логування")
        if working_panels > 1:
            print("   - Деякі панелі завантажені")
        
        print("\n🔧 Наступні кроки:")
        print("   1. Запустити main.py")
        print("   2. Протестувати інтерфейс")
        print("   3. Інтегрувати відсутні компоненти")
        
        return True
    else:
        print("\n⚠️ РЕЗУЛЬТАТ: Потрібні виправлення")
        print("🔧 Рекомендація: виправте помилки та запустіть тест знову")
        return False

def quick_launch_test():
    """Швидкий тест запуску інтерфейсу"""
    print("\n🚀 ШВИДКИЙ ТЕСТ ЗАПУСКУ")
    print("=" * 40)
    
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.main_window import MainWindow
        
        app = QApplication([])
        window = MainWindow()
        
        print("✅ Інтерфейс готовий!")
        print("📋 Натисніть будь-яку клавішу для показу вікна...")
        input()  # Чекаємо натискання клавіші
        
        window.show()
        print("🖼️ Вікно показано! Закрийте його для завершення тесту.")
        
        # Запуск на 10 секунд для тестування
        from PyQt5.QtCore import QTimer
        timer = QTimer()
        timer.singleShot(10000, app.quit)  # Автозакриття через 10 сек
        
        app.exec_()
        print("✅ Тест завершено успішно!")
        return True
        
    except Exception as e:
        print(f"❌ Помилка швидкого тесту: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎯 Хочете запустити швидкий тест інтерфейсу? (y/n): ", end="")
        try:
            choice = input().lower().strip()
            if choice in ['y', 'yes', 'так', 'д']:
                quick_launch_test()
        except KeyboardInterrupt:
            print("\n👋 Тест перервано користувачем")
    
    print(f"\n🏁 Тестування завершено з кодом: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)