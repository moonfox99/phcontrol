#!/usr/bin/env python3
"""
Константи для програми Фотоконтроль
Централізоване зберігання всіх магічних чисел та налаштувань
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AlbumLayout:
    """Константи для створення Word альбомів"""
    # Розміри сторінки A4 в міліметрах
    PAGE_WIDTH: float = 210.0
    PAGE_HEIGHT: float = 297.0
    
    # Стандартні поля для титульної та описової сторінок
    STANDARD_LEFT_MARGIN: float = 25.0
    STANDARD_RIGHT_MARGIN: float = 25.0
    STANDARD_TOP_MARGIN: float = 10.0
    STANDARD_BOTTOM_MARGIN: float = 10.0

    # Поля для сторінок з таблицями (мм)
    TABLE_PAGES_LEFT_MARGIN: float = 2.5    # 2.5мм зліва
    TABLE_PAGES_RIGHT_MARGIN: float = 5.0   # 5мм справа
    TABLE_PAGES_TOP_MARGIN: float = 20.0    # 20мм зверху
    TABLE_PAGES_BOTTOM_MARGIN: float = 5.0  # 5мм знизу
    
    # Параметри таблиць
    TABLE_ROWS: int = 1  # Тільки 1 рядок на таблицю
    TABLE_COLS: int = 3
    TABLE_HEIGHT: float = 130.0  # Висота таблиці 130мм
    PARAGRAPH_HEIGHT: float = 5.0  # Параграф-розділювач 5мм
    
    # Ширини колонок (мм)
    COL_1_WIDTH: float = 25.0   # Перша колонка "Індикатор ЗРЛ"
    COL_2_WIDTH: float = 150.0  # Друга колонка (зображення)
    COL_3_WIDTH: float = 30.0   # Третя колонка (дані)
    
    # Параметри зображень
    IMAGE_ASPECT_RATIO: float = 15/13
    IMAGE_WIDTH_CM: float = 14.9   # Ширина зображення в см (з відступом для границь)
    IMAGE_HEIGHT_CM: float = 12.9  # Висота зображення в см


@dataclass
class UIConstants:
    """Константи інтерфейсу користувача"""
    # Розміри головного вікна
    MIN_WINDOW_WIDTH: int = 1000
    MIN_WINDOW_HEIGHT: int = 700
    DEFAULT_WINDOW_WIDTH: int = 1400
    DEFAULT_WINDOW_HEIGHT: int = 900
    
    # Ширини панелей
    LEFT_PANEL_WIDTH: int = 220
    BROWSER_PANEL_WIDTH: int = 280
    RIGHT_PANEL_WIDTH: int = 220
    
    # Розміри мініатюр
    THUMBNAIL_WIDTH: int = 240
    THUMBNAIL_HEIGHT: int = 180
    BROWSER_WIDGET_WIDTH: int = 260
    
    # Розміри зум-віджету
    ZOOM_WIDGET_SIZE: int = 120
    ZOOM_FACTOR: int = 4
    ZOOM_RADIUS: int = 30
    
    # Відступи та інтервали
    PANEL_MARGIN: int = 15
    WIDGET_SPACING: int = 12
    THUMBNAIL_SPACING: int = 8


@dataclass
class ImageProcessing:
    """Константи обробки зображень"""
    # Підтримувані формати
    SUPPORTED_FORMATS: tuple = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif')
    
    # Обов'язкові пропорції зображень
    REQUIRED_ASPECT_RATIO: float = 15.0 / 13.0
    
    # Параметри якості
    JPEG_QUALITY: int = 95
    
    # Розміри елементів на зображенні
    CROSS_SIZE: int = 15
    LINE_WIDTH: int = 3
    POINT_RADIUS: int = 4
    
    # Кольори
    CENTER_COLOR: str = 'red'
    ANALYSIS_POINT_COLOR: str = 'blue'
    SCALE_EDGE_COLOR: str = 'green'
    LINE_COLOR: str = 'black'


@dataclass
class RadarDescription:
    """Константи для опису РЛС на зображенні"""
    # Розміри таблички РЛС (у відсотках від зображення)
    BOX_WIDTH_PERCENT: float = 28.60   # 4.29см / 15см * 100%
    BOX_HEIGHT_PERCENT: float = 19.54  # 2.54см / 13см * 100%
    
    # Внутрішні відступи (у відсотках від розміру таблички)
    PADDING_HORIZONTAL_PERCENT: float = 5.83  # 0,25см / 4,29см * 100%
    PADDING_VERTICAL_PERCENT: float = 5.12    # 0,13см / 2,54см * 100%
    
    # Позиція таблички
    MARGIN_FROM_EDGE_PERCENT: float = 1.0  # 1% від ширини зображення
    
    # Шрифт
    FONT_SIZE_PERCENT: float = 17.0  # 17% від висоти таблички
    MIN_FONT_SIZE: int = 12
    LINE_HEIGHT_MULTIPLIER: float = 1.2
    
    # Рамка
    BORDER_WIDTH_MULTIPLIER: float = 0.008  # відносно ширини таблички
    MIN_BORDER_WIDTH: int = 2


class AzimuthGrid:
    """Константи азимутальної сітки"""
    
    # Доступні масштаби - ВИПРАВЛЕНО: ініціалізуємо відразу
    AVAILABLE_SCALES = ["25", "35", "50", "75", "80", "90", "100", "150", "200", "250", "300", "350"]
    DEFAULT_SCALE = "300"
    
    # Кроки переміщення клавіатурою
    NORMAL_STEP = 1.0
    FAST_STEP = 5.0      # З Shift
    PRECISE_STEP = 0.5   # З Ctrl
    
    # Точність розрахунків
    AZIMUTH_PRECISION = 0   # Знаків після коми для азимуту
    RANGE_PRECISION = 0     # Знаків після коми для дальності


@dataclass
class StyleConstants:
    """Константи стилів UI"""
    # Кольори
    PRIMARY_COLOR: str = "#495057"
    SECONDARY_COLOR: str = "#6c757d"
    SUCCESS_COLOR: str = "#28a745"
    WARNING_COLOR: str = "#fd7e14"
    DANGER_COLOR: str = "#dc3545"
    
    BACKGROUND_LIGHT: str = "#f8f9fa"
    BACKGROUND_WHITE: str = "#ffffff"
    BORDER_COLOR: str = "#dee2e6"
    
    # Шрифти
    DEFAULT_FONT_FAMILY: str = '"Segoe UI", Arial, sans-serif'
    MONOSPACE_FONT_FAMILY: str = '"Consolas", "Courier New", monospace'
    
    # Розміри шрифтів
    TITLE_FONT_SIZE: str = "16pt"
    NORMAL_FONT_SIZE: str = "12pt"
    SMALL_FONT_SIZE: str = "10pt"
    
    # Радіуси та відступи
    BORDER_RADIUS: str = "6px"
    BUTTON_PADDING: str = "10px 14px"
    INPUT_PADDING: str = "6px 10px"


@dataclass
class FileConstants:
    """Константи файлової системи"""
    # Папки
    TEMPLATES_FOLDER: str = "PhotoControl_Templates"
    DOCS_FOLDER: str = "PhotoControl_Docs"
    
    # Розширення файлів
    TEMPLATE_EXTENSION: str = ".json"
    DOC_EXTENSION: str = ".docx"
    HTML_EXTENSION: str = ".html"
    
    # Імена файлів
    README_FILENAME: str = "README.txt"
    DOCUMENTATION_FILENAME: str = "PhotoControl_Documentation.html"
    
    # Фільтри діалогів
    IMAGE_FILES_FILTER: str = "Image Files (*.jpg *.jpeg *.png *.bmp *.gif *.tiff)"
    WORD_FILES_FILTER: str = "Word Documents (*.docx)"
    ALL_FILES_FILTER: str = "All files (*.*)"


@dataclass
class DefaultTemplateData:
    """Базові дані для шаблонів"""
    UNIT_INFO: str = 'А0000'
    
    COMMANDER: Dict[str, str] = None
    CHIEF_OF_STAFF: Dict[str, str] = None
    SIGNATURE_INFO: Dict[str, str] = None
    
    MARGINS: Dict[str, float] = None
    
    def __post_init__(self):
        if self.COMMANDER is None:
            self.COMMANDER = {'rank': 'полковник', 'name': 'П.П. ПЕТРЕНКО'}
        
        if self.CHIEF_OF_STAFF is None:
            self.CHIEF_OF_STAFF = {'rank': 'підполковник', 'name': 'С.С. СИДОРЕНКО'}
        
        if self.SIGNATURE_INFO is None:
            self.SIGNATURE_INFO = {'rank': 'головний сержант', 'name': 'Анна Петренко'}
        
        if self.MARGINS is None:
            self.MARGINS = {'top': 2.25, 'left': 2.5, 'bottom': 0, 'right': 0.75}


@dataclass
class WordDocumentStyles:
    """Константи стилів Word документа"""
    # Розміри шрифтів (в пунктах)
    TITLE_TOP_SPACER_SIZE: int = 31
    TITLE_MAIN_SIZE: int = 28
    TITLE_SIGNATURE_SIZE: int = 16
    TITLE_SIGNATURE_SPACER_SIZE: int = 9
    TITLE_FINAL_SIZE: int = 16
    
    # Розміри для таблиць
    TABLE_HEADER_SIZE: int = 14
    TABLE_DATA_SIZE: int = 14
    
    # Розміри для опису
    DESCRIPTION_HEADING_SIZE: int = 22
    DESCRIPTION_SPACER_SIZE: int = 28
    DESCRIPTION_SIGNATURE_SIZE: int = 14
    
    # Відступи та інтервали
    LINE_SPACING_MULTIPLE: float = 1.15
    FIRST_LINE_INDENT_CM: float = 1.0
    
    # Висоти рядків таблиць
    TABLE_HEADER_HEIGHT_CM: float = 2.0
    TABLE_DATA_HEIGHT_CM: float = 0.6


@dataclass
class ValidationRules:
    """Правила валідації даних"""
    # Мінімальні розміри зображень
    MIN_IMAGE_WIDTH: int = 300
    MIN_IMAGE_HEIGHT: int = 200
    
    # Максимальні значення
    MAX_SCALE_VALUE: int = 999
    MAX_AZIMUTH: float = 360.0
    MAX_RANGE: float = 9999.0
    
    # Допустимі символи в полях
    ALLOWED_TARGET_CHARS: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    
    # Мінімальні довжини
    MIN_TEMPLATE_NAME_LENGTH: int = 1
    MIN_UNIT_NAME_LENGTH: int = 1


# Глобальні екземпляри для зручності використання
ALBUM = AlbumLayout()
UI = UIConstants()
IMAGE = ImageProcessing()
RADAR = RadarDescription()
GRID = AzimuthGrid()
STYLES = StyleConstants()
FILES = FileConstants()
TEMPLATE_DEFAULTS = DefaultTemplateData()
WORD_STYLES = WordDocumentStyles()
VALIDATION = ValidationRules()


# Утилітні функції для роботи з константами
def mm_to_cm(mm: float) -> float:
    """Перетворення міліметрів в сантиметри"""
    return mm / 10.0


def get_image_files_filter() -> str:
    """Отримання фільтру для діалогу відкриття зображень"""
    return f"{FILES.IMAGE_FILES_FILTER};;{FILES.ALL_FILES_FILTER}"


def get_word_files_filter() -> str:
    """Отримання фільтру для діалогу збереження Word документів"""
    return f"{FILES.WORD_FILES_FILTER};;{FILES.ALL_FILES_FILTER}"


def is_supported_image_format(filename: str) -> bool:
    """Перевірка чи підтримується формат зображення"""
    return filename.lower().endswith(IMAGE.SUPPORTED_FORMATS)


def validate_aspect_ratio(width: int, height: int, tolerance: float = 0.1) -> bool:
    """Перевірка пропорцій зображення (15:13 з допуском)"""
    actual_ratio = width / height
    expected_ratio = IMAGE.REQUIRED_ASPECT_RATIO
    return abs(actual_ratio - expected_ratio) <= tolerance


if __name__ == "__main__":
    # Тестування констант
    print("=== Тестування констант Фотоконтроль ===")
    print(f"Розміри альбому: {ALBUM.PAGE_WIDTH}x{ALBUM.PAGE_HEIGHT}мм")
    print(f"Ширина панелей: {UI.LEFT_PANEL_WIDTH}, {UI.BROWSER_PANEL_WIDTH}, {UI.RIGHT_PANEL_WIDTH}")
    print(f"Підтримувані формати: {IMAGE.SUPPORTED_FORMATS}")
    print(f"Доступні масштаби: {GRID.AVAILABLE_SCALES}")
    print(f"Фільтр зображень: {get_image_files_filter()}")
    print(f"Перевірка пропорцій 450x390: {validate_aspect_ratio(450, 390)}")
    print("=== Тест завершено ===")