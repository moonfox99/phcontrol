#!/usr/bin/env python3
"""
PhotoControl v2.0 - Оновлені константи
Всі розміри, кольори та налаштування програми
"""

# ===============================
# UI КОНСТАНТИ
# ===============================

class UI:
    """Константи інтерфейсу користувача"""
    
    # Розміри вікна
    DEFAULT_WINDOW_WIDTH = 1400
    DEFAULT_WINDOW_HEIGHT = 900
    MIN_WINDOW_WIDTH = 1000
    MIN_WINDOW_HEIGHT = 700
    
    # Розміри панелей
    CONTROL_PANEL_WIDTH = 250      # Ліва панель управління
    DATA_PANEL_WIDTH = 300         # Права панель даних
    THUMBNAIL_PANEL_WIDTH = 260    # Браузер мініатюр (збільшено з 160px до 260px)
    
    # Розміри мініатюр
    THUMBNAIL_SIZE = 200           # Розмір мініатюр (збільшено з 150px)
    THUMBNAIL_MARGIN = 8           # Відступи між мініатюрами
    
    # Кольори
    BACKGROUND_COLOR = "#f5f5f5"
    PANEL_BORDER_COLOR = "#ccc"
    BUTTON_COLOR = "#e1e1e1"
    BUTTON_HOVER_COLOR = "#d1d1d1"
    BUTTON_PRESSED_COLOR = "#c1c1c1"
    
    # Кольори стану мініатюр
    THUMBNAIL_NORMAL_COLOR = "#ffffff"
    THUMBNAIL_SELECTED_COLOR = "#007bff"
    THUMBNAIL_PROCESSED_COLOR = "#28a745"
    THUMBNAIL_ERROR_COLOR = "#dc3545"
    
    # Шрифти
    MAIN_FONT_SIZE = 11
    HEADER_FONT_SIZE = 14
    SMALL_FONT_SIZE = 9


# ===============================
# КОНСТАНТИ АЗИМУТАЛЬНОЇ СІТКИ
# ===============================

class GRID:
    """Константи азимутальної сітки"""
    
    # Доступні масштаби (як в legacy версії)
    AVAILABLE_SCALES = [
        1000, 2000, 3000, 4000, 5000,
        6000, 7000, 8000, 9000, 10000,
        12000, 15000, 20000, 25000, 30000,
        40000, 50000, 75000, 100000
    ]
    
    # Масштаб за замовчуванням
    DEFAULT_SCALE = 5000
    
    # Кольори сітки
    GRID_COLOR = "#FF0000"           # Червоний для ліній сітки
    CENTER_COLOR = "#00FF00"         # Зелений для центру
    ANALYSIS_POINT_COLOR = "#0000FF" # Синій для точки аналізу
    SCALE_EDGE_COLOR = "#FFD700"     # Золотий для краю масштабу
    
    # Товщина ліній
    GRID_LINE_WIDTH = 1
    CENTER_POINT_SIZE = 8
    ANALYSIS_POINT_SIZE = 6
    
    # Параметри азимутальних ліній
    AZIMUTH_LINES_COUNT = 36         # Кількість азимутальних ліній (через 10°)
    RANGE_CIRCLES_COUNT = 10         # Кількість кіл дальності
    
    # Переміщення центру клавішами
    MOVE_STEP_NORMAL = 1             # Звичайне переміщення
    MOVE_STEP_FAST = 10              # Швидке переміщення (Shift)
    MOVE_STEP_PRECISE = 0.5          # Точне переміщення (Ctrl)


# ===============================
# КОНСТАНТИ ФАЙЛІВ
# ===============================

class FILES:
    """Константи роботи з файлами"""
    
    # Підтримувані формати зображень
    SUPPORTED_IMAGE_FORMATS = [
        '.jpg', '.jpeg', '.png', '.bmp', 
        '.gif', '.tiff', '.tif'
    ]
    
    # Формати для збереження
    SAVE_FORMATS = {
        'JPEG': ['.jpg', '.jpeg'],
        'PNG': ['.png'],
        'BMP': ['.bmp'],
        'TIFF': ['.tiff', '.tif']
    }
    
    # Налаштування JPEG
    JPEG_QUALITY = 95
    
    # Розміри зображень для обробки
    MAX_IMAGE_SIZE = (4000, 4000)   # Максимальний розмір для обробки
    THUMBNAIL_SIZE = (200, 200)     # Розмір мініатюр
    
    # Директорії
    USER_DATA_DIR = "PhotoControl_Data"
    TEMPLATES_DIR = "templates"
    TEMP_DIR = "temp"
    DOCS_DIR = "docs"


# ===============================
# КОНСТАНТИ WORD АЛЬБОМІВ
# ===============================

class ALBUM:
    """Константи створення Word альбомів"""
    
    # Розміри сторінки (мм)
    PAGE_WIDTH = 210          # A4 ширина
    PAGE_HEIGHT = 297         # A4 висота
    
    # Поля сторінок (мм)
    # ⚠️ КРИТИЧНО ВАЖЛИВІ РОЗМІРИ для таблиць!
    TABLE_PAGES_LEFT_MARGIN = 2.5    # 2.5мм ліво для таблиць!
    TABLE_PAGES_RIGHT_MARGIN = 5     # 5мм справа
    TABLE_PAGES_TOP_MARGIN = 20      # 20мм зверху
    TABLE_PAGES_BOTTOM_MARGIN = 5    # 5мм знизу
    
    # Розміри таблиць (мм)
    # ⚠️ КРИТИЧНО ВАЖЛИВІ РОЗМІРИ!
    TABLE_WIDTH = 205         # 205мм ширина таблиці
    TABLE_HEIGHT = 130        # 130мм висота таблиці
    
    # Висота параграфів-розділювачів
    PARAGRAPH_HEIGHT = 5      # 5мм висота параграфу
    
    # Пропорції опису РЛС
    # ⚠️ КРИТИЧНО ВАЖЛИВІ ПРОПОРЦІЇ!
    RADAR_DESCRIPTION_WIDTH_PERCENT = 28.60   # 28.60% від ширини зображення
    RADAR_DESCRIPTION_HEIGHT_PERCENT = 19.54  # 19.54% від висоти зображення
    
    # Шрифти для документів
    DEFAULT_FONT = "Times New Roman"
    DEFAULT_FONT_SIZE = 12
    TABLE_FONT_SIZE = 10
    HEADER_FONT_SIZE = 14
    
    # Кольори
    TABLE_BORDER_COLOR = "#000000"
    TABLE_HEADER_COLOR = "#f0f0f0"


# ===============================
# КОНСТАНТИ ОБРОБКИ ЗОБРАЖЕНЬ
# ===============================

class IMAGE_PROCESSING:
    """Константи обробки зображень"""
    
    # Налаштування обробки
    DPI = 300                 # DPI для високої якості
    ANTIALIAS = True          # Згладжування
    
    # Кольори для накладання
    OVERLAY_OPACITY = 0.8     # Прозорість накладення
    
    # Зум
    ZOOM_FACTOR = 2.0         # Коефіцієнт збільшення зуму
    ZOOM_WINDOW_SIZE = 150    # Розмір вікна зуму (пікселів)
    
    # Обрізка зображень
    AUTO_CROP_ENABLED = False
    CROP_MARGIN = 10          # Відступ при обрізці


# ===============================
# КОНСТАНТИ ПЕРЕКЛАДІВ
# ===============================

class TRANSLATIONS:
    """Константи системи перекладів"""
    
    # Мови за замовчуванням
    DEFAULT_LANGUAGE = "uk"   # Українська за замовчуванням
    FALLBACK_LANGUAGE = "uk"  # Українська як резервна
    
    # Доступні мови
    AVAILABLE_LANGUAGES = ["uk", "en"]
    
    # Назви мов для UI
    LANGUAGE_NAMES = {
        "uk": "🇺🇦 Українська",
        "en": "🇺🇸 English"
    }


# ===============================
# КОНСТАНТИ НАЛАШТУВАНЬ
# ===============================

class SETTINGS:
    """Константи збереження налаштувань"""
    
    # Ключі налаштувань
    GEOMETRY_KEY = "geometry"
    SPLITTER_STATE_KEY = "splitter_state"
    LANGUAGE_KEY = "language"
    THUMBNAILS_VISIBLE_KEY = "thumbnails_visible"
    DATA_PANEL_VISIBLE_KEY = "data_panel_visible"
    LAST_FOLDER_KEY = "last_folder"
    RECENT_FILES_KEY = "recent_files"
    
    # Максимальна кількість нещодавніх файлів
    MAX_RECENT_FILES = 10
    
    # Автозбереження
    AUTO_SAVE_ENABLED = True
    AUTO_SAVE_INTERVAL = 300  # 5 хвилин в секундах


# ===============================
# КОНСТАНТИ ПРОДУКТИВНОСТІ
# ===============================

class PERFORMANCE:
    """Константи оптимізації продуктивності"""
    
    # Мініатюри
    THUMBNAIL_CACHE_SIZE = 100        # Кількість мініатюр в кеші
    THUMBNAIL_LOAD_TIMEOUT = 5        # Таймаут завантаження мініатюр (сек)
    
    # Обробка зображень
    MAX_THREADS = 4                   # Максимальна кількість потоків
    PROCESSING_TIMEOUT = 30           # Таймаут обробки (сек)
    
    # Пам'ять
    MAX_MEMORY_USAGE = 1024           # Максимальне використання пам'яті (МБ)
    GARBAGE_COLLECTION_INTERVAL = 60  # Інтервал збирання сміття (сек)


# ===============================
# КОНСТАНТИ ЛОГУВАННЯ
# ===============================

class LOGGING:
    """Константи системи логування"""
    
    # Рівні логування
    LOG_LEVEL = "INFO"
    
    # Файли логів
    LOG_FILE = "photocontrol.log"
    MAX_LOG_SIZE = 10 * 1024 * 1024   # 10 МБ
    BACKUP_COUNT = 5
    
    # Формат логів
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ===============================
# КОНСТАНТИ ВАЛІДАЦІЇ
# ===============================

class VALIDATION:
    """Константи валідації даних"""
    
    # Обмеження полів
    MAX_TARGET_NUMBER_LENGTH = 50
    MAX_HEIGHT_VALUE = 9999
    MIN_HEIGHT_VALUE = 0
    
    # Регулярні вирази
    HEIGHT_PATTERN = r"^\d+(\.\d+)?\s*(м|m|метр.*)?$"
    TARGET_NUMBER_PATTERN = r"^[А-Яа-яA-Za-z0-9\-\s]+$"
    
    # Обмеження зображень
    MIN_IMAGE_SIZE = (100, 100)
    MAX_IMAGE_SIZE = (10000, 10000)


# ===============================
# КОНСТАНТИ ТЕСТУВАННЯ
# ===============================

class TESTING:
    """Константи для тестування"""
    
    # Тестові дані
    TEST_IMAGE_SIZE = (800, 600)
    TEST_TARGET_COUNT = 5
    
    # Тестові кольори
    TEST_IMAGE_COLORS = [
        (100, 150, 200),  # Блакитний
        (150, 100, 200),  # Фіолетовий
        (200, 150, 100),  # Помаранчевий
        (100, 200, 150),  # Зелений
        (200, 100, 150),  # Рожевий
    ]
    
    # Таймаути для тестів
    TEST_TIMEOUT = 10             # Максимальний час виконання тесту (сек)
    UI_TEST_DELAY = 0.1           # Затримка між діями в UI тестах (сек)


# ===============================
# СИСТЕМНІ КОНСТАНТИ
# ===============================

class SYSTEM:
    """Системні константи"""
    
    # Версія програми
    VERSION = "2.0.0"
    VERSION_DATE = "2025-01-01"
    
    # Інформація про програму
    APP_NAME = "PhotoControl"
    APP_TITLE = "Фотоконтроль - Обробка азимутальних зображень"
    ORGANIZATION = "PhotoControl Team"
    
    # Підтримка
    SUPPORT_EMAIL = "support@photocontrol.ua"
    WEBSITE = "https://photocontrol.ua"
    
    # Сумісність
    MIN_PYTHON_VERSION = (3, 7)
    MIN_QT_VERSION = "5.12"
    
    # Платформи
    SUPPORTED_PLATFORMS = ["Windows", "Linux", "macOS"]


# ===============================
# КОНСТАНТИ ПОМИЛОК
# ===============================

class ERRORS:
    """Константи обробки помилок"""
    
    # Коди помилок
    SUCCESS = 0
    GENERAL_ERROR = 1
    FILE_NOT_FOUND = 2
    INVALID_FORMAT = 3
    PROCESSING_ERROR = 4
    MEMORY_ERROR = 5
    PERMISSION_ERROR = 6
    
    # Повідомлення про помилки
    ERROR_MESSAGES = {
        GENERAL_ERROR: "Загальна помилка програми",
        FILE_NOT_FOUND: "Файл не знайдено",
        INVALID_FORMAT: "Невідомий формат файлу",
        PROCESSING_ERROR: "Помилка обробки зображення",
        MEMORY_ERROR: "Недостатньо пам'яті",
        PERMISSION_ERROR: "Недостатньо прав доступу"
    }


# ===============================
# КОНСТАНТИ КЛАВІАТУРНИХ СКОРОЧЕНЬ
# ===============================

class SHORTCUTS:
    """Константи клавіатурних скорочень"""
    
    # Файлові операції
    OPEN_IMAGE = "Ctrl+O"
    OPEN_FOLDER = "Ctrl+Shift+O"
    SAVE_IMAGE = "Ctrl+S"
    CREATE_ALBUM = "Ctrl+E"
    EXIT = "Ctrl+Q"
    
    # Режими роботи
    NORMAL_MODE = "Esc"
    CENTER_MODE = "C"
    SCALE_MODE = "S"
    
    # Навігація
    NEXT_IMAGE = "Right"
    PREVIOUS_IMAGE = "Left"
    
    # Зум
    ZOOM_IN = "Ctrl+Plus"
    ZOOM_OUT = "Ctrl+Minus"
    ZOOM_RESET = "Ctrl+0"
    
    # Панелі
    TOGGLE_THUMBNAILS = "F1"
    TOGGLE_DATA_PANEL = "F2"
    
    # Швидкі дії
    SAVE_CURRENT_DATA = "Ctrl+Space"
    REFRESH = "F5"
    
    # Довідка
    HELP = "F1"
    ABOUT = "Ctrl+?"


# ===============================
# КОНСТАНТИ БЕЗПЕКИ
# ===============================

class SECURITY:
    """Константи безпеки"""
    
    # Обмеження файлів
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 МБ
    ALLOWED_EXTENSIONS = FILES.SUPPORTED_IMAGE_FORMATS
    
    # Тимчасові файли
    TEMP_FILE_LIFETIME = 3600          # 1 година в секундах
    AUTO_CLEANUP_ENABLED = True
    
    # Валідація шляхів
    VALIDATE_PATHS = True
    RESTRICT_SYSTEM_PATHS = True


# ===============================
# ЕКСПОРТ КОНСТАНТ
# ===============================

# Створення глобального словника для зручного доступу
CONSTANTS = {
    'UI': UI,
    'GRID': GRID,
    'FILES': FILES,
    'ALBUM': ALBUM,
    'IMAGE_PROCESSING': IMAGE_PROCESSING,
    'TRANSLATIONS': TRANSLATIONS,
    'SETTINGS': SETTINGS,
    'PERFORMANCE': PERFORMANCE,
    'LOGGING': LOGGING,
    'VALIDATION': VALIDATION,
    'TESTING': TESTING,
    'SYSTEM': SYSTEM,
    'ERRORS': ERRORS,
    'SHORTCUTS': SHORTCUTS,
    'SECURITY': SECURITY,
}


# ===============================
# УТИЛІТАРНІ ФУНКЦІЇ
# ===============================

def get_constant(category: str, name: str, default=None):
    """
    Безпечне отримання константи
    
    Args:
        category: Категорія константи (наприклад, 'UI')
        name: Назва константи (наприклад, 'DEFAULT_WINDOW_WIDTH')
        default: Значення за замовчуванням
        
    Returns:
        Значення константи або default
    """
    try:
        category_obj = CONSTANTS.get(category)
        if category_obj and hasattr(category_obj, name):
            return getattr(category_obj, name)
        return default
    except Exception:
        return default


def validate_constants():
    """
    Валідація констант на коректність
    
    Returns:
        Tuple[bool, List[str]]: (успіх, список помилок)
    """
    errors = []
    
    # Перевірка розмірів UI
    if UI.DEFAULT_WINDOW_WIDTH < UI.MIN_WINDOW_WIDTH:
        errors.append("DEFAULT_WINDOW_WIDTH менше ніж MIN_WINDOW_WIDTH")
    
    if UI.DEFAULT_WINDOW_HEIGHT < UI.MIN_WINDOW_HEIGHT:
        errors.append("DEFAULT_WINDOW_HEIGHT менше ніж MIN_WINDOW_HEIGHT")
    
    # Перевірка розмірів панелей
    total_panels_width = UI.CONTROL_PANEL_WIDTH + UI.DATA_PANEL_WIDTH + UI.THUMBNAIL_PANEL_WIDTH
    if total_panels_width > UI.DEFAULT_WINDOW_WIDTH:
        errors.append(f"Сума ширин панелей ({total_panels_width}) більше ширини вікна")
    
    # Перевірка масштабів сітки
    if GRID.DEFAULT_SCALE not in GRID.AVAILABLE_SCALES:
        errors.append("DEFAULT_SCALE відсутній в AVAILABLE_SCALES")
    
    # Перевірка розмірів альбому
    if ALBUM.TABLE_WIDTH > ALBUM.PAGE_WIDTH:
        errors.append("TABLE_WIDTH більше ніж PAGE_WIDTH")
    
    if ALBUM.TABLE_HEIGHT > ALBUM.PAGE_HEIGHT:
        errors.append("TABLE_HEIGHT більше ніж PAGE_HEIGHT")
    
    # Перевірка налаштувань продуктивності
    if PERFORMANCE.MAX_THREADS < 1:
        errors.append("MAX_THREADS має бути принаймні 1")
    
    return len(errors) == 0, errors


def print_constants_summary():
    """Виведення інформації про константи"""
    print("=== PhotoControl v2.0 - Константи ===")
    print(f"Версія: {SYSTEM.VERSION}")
    print(f"Дата версії: {SYSTEM.VERSION_DATE}")
    print()
    
    print("📐 Розміри інтерфейсу:")
    print(f"  Вікно: {UI.DEFAULT_WINDOW_WIDTH}×{UI.DEFAULT_WINDOW_HEIGHT}")
    print(f"  Ліва панель: {UI.CONTROL_PANEL_WIDTH}px")
    print(f"  Права панель: {UI.DATA_PANEL_WIDTH}px")
    print(f"  Мініатюри: {UI.THUMBNAIL_PANEL_WIDTH}px")
    print()
    
    print("🗺️ Азимутальна сітка:")
    print(f"  Масштаб за замовчуванням: 1:{GRID.DEFAULT_SCALE}")
    print(f"  Доступні масштаби: {len(GRID.AVAILABLE_SCALES)} варіантів")
    print(f"  Азимутальні лінії: {GRID.AZIMUTH_LINES_COUNT}")
    print()
    
    print("📄 Word альбоми:")
    print(f"  Розмір таблиці: {ALBUM.TABLE_WIDTH}×{ALBUM.TABLE_HEIGHT} мм")
    print(f"  Поля: ліво {ALBUM.TABLE_PAGES_LEFT_MARGIN}мм, верх {ALBUM.TABLE_PAGES_TOP_MARGIN}мм")
    print(f"  Опис РЛС: {ALBUM.RADAR_DESCRIPTION_WIDTH_PERCENT}%×{ALBUM.RADAR_DESCRIPTION_HEIGHT_PERCENT}%")
    print()
    
    print("🔧 Продуктивність:")
    print(f"  Максимум потоків: {PERFORMANCE.MAX_THREADS}")
    print(f"  Кеш мініатюр: {PERFORMANCE.THUMBNAIL_CACHE_SIZE}")
    print(f"  Максимум пам'яті: {PERFORMANCE.MAX_MEMORY_USAGE} МБ")
    print()
    
    # Валідація
    is_valid, validation_errors = validate_constants()
    if is_valid:
        print("✅ Всі константи валідні")
    else:
        print("❌ Знайдено помилки в константах:")
        for error in validation_errors:
            print(f"  - {error}")


# ===============================
# ТЕСТУВАННЯ КОНСТАНТ
# ===============================

if __name__ == "__main__":
    # Виведення інформації про константи
    print_constants_summary()
    
    # Тестування функції отримання константи
    print("\n=== Тестування get_constant ===")
    
    test_cases = [
        ("UI", "DEFAULT_WINDOW_WIDTH", None),
        ("GRID", "DEFAULT_SCALE", None), 
        ("ALBUM", "TABLE_WIDTH", None),
        ("INVALID", "INVALID", "default_value"),
        ("UI", "INVALID", 999),
    ]
    
    for category, name, default in test_cases:
        result = get_constant(category, name, default)
        print(f"get_constant('{category}', '{name}', {default}) = {result}")
    
    print("\n=== Тестування доступу до константи ===")
    print(f"UI.DEFAULT_WINDOW_WIDTH = {UI.DEFAULT_WINDOW_WIDTH}")
    print(f"GRID.AVAILABLE_SCALES[:5] = {GRID.AVAILABLE_SCALES[:5]}")
    print(f"ALBUM.TABLE_WIDTH = {ALBUM.TABLE_WIDTH}")
    print(f"SYSTEM.VERSION = {SYSTEM.VERSION}")
    
    print("\nКонстанти PhotoControl v2.0 готові до використання! ✅")