#!/usr/bin/env python3
"""
Система перекладів PhotoControl v2.0
Підтримка української та англійської мов з автоматичним переключенням
"""

from typing import Dict, Optional, Any, Callable
from enum import Enum
from PyQt5.QtCore import QObject, pyqtSignal


class Language(Enum):
    """Підтримувані мови"""
    UKRAINIAN = "uk"
    ENGLISH = "en"


class TranslationKeys:
    """Ключі перекладів для типобезпеки"""
    
    # Основний інтерфейс
    WINDOW_TITLE = "window_title"
    CONTROLS = "controls"
    REPORT_DATA = "report_data"
    PHOTO_BROWSER = "photo_browser"
    RESULTS = "results"
    
    # Кнопки
    OPEN_IMAGE = "open_image"
    OPEN_FOLDER = "open_folder"
    SAVE_CURRENT_IMAGE = "save_current_image"
    CREATE_NEW_ALBUM = "create_new_album"
    SET_SCALE_EDGE = "set_scale_edge"
    SET_CENTER = "set_center"
    NEXT = "next"
    PREVIOUS = "previous"
    TODAY = "today"
    
    # Секції інтерфейсу
    FILE_OPERATIONS = "file_operations"
    BATCH_PROCESSING = "batch_processing"
    AZIMUTH_GRID = "azimuth_grid"
    MOVE_CENTER = "move_center"
    SCALE_SETTING = "scale_setting"
    TITLE_PAGE = "title_page"
    DOCUMENT_DATE = "document_date"
    TEMPLATE_SELECTION = "template_selection"
    
    # Діалоги файлів
    SELECT_IMAGE = "select_image"
    SELECT_FOLDER = "select_folder"
    IMAGE_FILES = "image_files"
    ALL_FILES = "all_files"
    JPEG_FILES = "jpeg_files"
    PNG_FILES = "png_files"
    SAVE_PROCESSED_IMAGE = "save_processed_image"
    
    # Повідомлення
    LOADED_FOLDER = "loaded_folder"
    FOUND_IMAGES = "found_images"
    NO_IMAGES_FOUND = "no_images_found"
    LOADED_FROM_BROWSER = "loaded_from_browser"
    LOADED = "loaded"
    SAVED = "saved"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    
    # Інструкції
    OPEN_INSTRUCTION = "open_instruction"
    CLICK_TO_PLACE = "click_to_place"
    DRAG_TO_MOVE = "drag_to_move"
    LINE_CONNECTS = "line_connects"
    CLICK_ON_IMAGE = "click_on_image"
    
    # Дані звіту
    KM_UNIT = "km_unit"
    NO_OBSTACLES = "no_obstacles"
    WITH_OBSTACLES = "with_obstacles"
    DETECTION = "detection"
    TRACKING = "tracking"
    LOSS = "loss"
    TARGET_NUMBER = "target_number"
    HEIGHT = "height"
    OBSTACLES = "obstacles"
    
    # Результати аналізу
    IMAGE_INFO = "image_info"
    SIZE = "size"
    SCALE_INFO = "scale_info"
    CENTER_INFO = "center_info"
    BOTTOM_EDGE = "bottom_edge"
    PIXELS_SOUTH = "pixels_south"
    ANALYSIS_POINT = "analysis_point"
    POSITION = "position"
    AZIMUTH = "azimuth"
    RANGE = "range"
    
    # Помилки
    NO_IMAGE_FIRST = "no_image_first"
    NO_ANALYSIS_POINT = "no_analysis_point"
    COULD_NOT_LOAD = "could_not_load"
    COULD_NOT_SAVE = "could_not_save"
    IMAGE_NOT_SUPPORTED = "image_not_supported"
    DOCX_NOT_AVAILABLE = "docx_not_available"
    LOAD_IMAGE_AND_POINT = "load_image_and_point"
    
    # Налаштування
    SETTINGS = "settings"
    LANGUAGE = "language"
    GRID_SETTINGS_APPLIED = "grid_settings_applied"
    CHANGES_SAVED = "changes_saved"
    CHANGES_CANCELLED = "changes_cancelled"
    ALL_CHANGES_CLEARED = "all_changes_cleared"


class UkrainianTranslations:
    """Українські переклади"""
    
    TRANSLATIONS = {
        # Основний інтерфейс
        TranslationKeys.WINDOW_TITLE: "PhotoControl - Обробка азимутальних зображень",
        TranslationKeys.CONTROLS: "Управління",
        TranslationKeys.REPORT_DATA: "Дані звіту",
        TranslationKeys.PHOTO_BROWSER: "Браузер зображень:",
        TranslationKeys.RESULTS: "Результати",
        
        # Кнопки
        TranslationKeys.OPEN_IMAGE: "Відкрити зображення",
        TranslationKeys.OPEN_FOLDER: "Відкрити папку",
        TranslationKeys.SAVE_CURRENT_IMAGE: "Зберегти поточне зображення",
        TranslationKeys.CREATE_NEW_ALBUM: "Створити новий альбом",
        TranslationKeys.SET_SCALE_EDGE: "Встановити край масштабу",
        TranslationKeys.SET_CENTER: "Встановити центр",
        TranslationKeys.NEXT: "Наступне",
        TranslationKeys.PREVIOUS: "Попереднє",
        TranslationKeys.TODAY: "Сьогодні",
        
        # Секції інтерфейсу
        TranslationKeys.FILE_OPERATIONS: "Файлові операції",
        TranslationKeys.BATCH_PROCESSING: "Пакетна обробка",
        TranslationKeys.AZIMUTH_GRID: "Азимутальна сітка",
        TranslationKeys.MOVE_CENTER: "Переміщення центру",
        TranslationKeys.SCALE_SETTING: "Налаштування масштабу",
        TranslationKeys.TITLE_PAGE: "Титульна сторінка",
        TranslationKeys.DOCUMENT_DATE: "Дата документу",
        TranslationKeys.TEMPLATE_SELECTION: "Вибір шаблону",
        
        # Діалоги файлів
        TranslationKeys.SELECT_IMAGE: "Виберіть зображення",
        TranslationKeys.SELECT_FOLDER: "Виберіть папку",
        TranslationKeys.IMAGE_FILES: "Файли зображень",
        TranslationKeys.ALL_FILES: "Всі файли",
        TranslationKeys.JPEG_FILES: "JPEG файли",
        TranslationKeys.PNG_FILES: "PNG файли",
        TranslationKeys.SAVE_PROCESSED_IMAGE: "Зберегти оброблене зображення",
        
        # Повідомлення
        TranslationKeys.LOADED_FOLDER: "Завантажено папку",
        TranslationKeys.FOUND_IMAGES: "Знайдено зображень: {count}",
        TranslationKeys.NO_IMAGES_FOUND: "У цій папці не знайдено зображень",
        TranslationKeys.LOADED_FROM_BROWSER: "Завантажено з браузера: {name}",
        TranslationKeys.LOADED: "Завантажено",
        TranslationKeys.SAVED: "Збережено",
        TranslationKeys.SUCCESS: "Успіх",
        TranslationKeys.ERROR: "Помилка",
        TranslationKeys.WARNING: "Попередження",
        
        # Інструкції
        TranslationKeys.OPEN_INSTRUCTION: "Відкрийте зображення або папку для початку",
        TranslationKeys.CLICK_TO_PLACE: "Клікніть для розміщення точки",
        TranslationKeys.DRAG_TO_MOVE: "Перетягніть для переміщення",
        TranslationKeys.LINE_CONNECTS: "Лінія з'єднується з правим краєм",
        TranslationKeys.CLICK_ON_IMAGE: "Клікніть на зображенні",
        
        # Дані звіту
        TranslationKeys.KM_UNIT: "км",
        TranslationKeys.NO_OBSTACLES: "без перешкод",
        TranslationKeys.WITH_OBSTACLES: "з перешкодами",
        TranslationKeys.DETECTION: "Виявлення",
        TranslationKeys.TRACKING: "Супроводження",
        TranslationKeys.LOSS: "Втрата",
        TranslationKeys.TARGET_NUMBER: "Номер цілі",
        TranslationKeys.HEIGHT: "Висота",
        TranslationKeys.OBSTACLES: "Перешкоди",
        
        # Результати аналізу
        TranslationKeys.IMAGE_INFO: "Зображення: {name}",
        TranslationKeys.SIZE: "Розмір: {width} x {height}",
        TranslationKeys.SCALE_INFO: "Масштаб: 1:{scale}",
        TranslationKeys.CENTER_INFO: "Центр: ({x}, {y})",
        TranslationKeys.BOTTOM_EDGE: "Нижній край = {scale} одиниць",
        TranslationKeys.PIXELS_SOUTH: "Пікселів на південь: {pixels}",
        TranslationKeys.ANALYSIS_POINT: "Точка аналізу:",
        TranslationKeys.POSITION: "Позиція",
        TranslationKeys.AZIMUTH: "Азимут",
        TranslationKeys.RANGE: "Дальність",
        
        # Помилки
        TranslationKeys.NO_IMAGE_FIRST: "Спочатку завантажте зображення",
        TranslationKeys.NO_ANALYSIS_POINT: "Немає точки аналізу для збереження",
        TranslationKeys.COULD_NOT_LOAD: "Не вдалося завантажити: {error}",
        TranslationKeys.COULD_NOT_SAVE: "Не вдалося зберегти: {error}",
        TranslationKeys.IMAGE_NOT_SUPPORTED: "Формат зображення не підтримується",
        TranslationKeys.DOCX_NOT_AVAILABLE: "Бібліотека python-docx не встановлена",
        TranslationKeys.LOAD_IMAGE_AND_POINT: "Завантажте зображення та встановіть точку аналізу",
        
        # Налаштування
        TranslationKeys.SETTINGS: "Налаштування",
        TranslationKeys.LANGUAGE: "Мова",
        TranslationKeys.GRID_SETTINGS_APPLIED: "Налаштування сітки застосовано",
        TranslationKeys.CHANGES_SAVED: "Зміни збережено",
        TranslationKeys.CHANGES_CANCELLED: "Зміни скасовано",
        TranslationKeys.ALL_CHANGES_CLEARED: "Всі зміни очищено",
    }


class EnglishTranslations:
    """Англійські переклади"""
    
    TRANSLATIONS = {
        # Основний інтерфейс
        TranslationKeys.WINDOW_TITLE: "PhotoControl - Azimuth Image Processor",
        TranslationKeys.CONTROLS: "Controls",
        TranslationKeys.REPORT_DATA: "Report Data",
        TranslationKeys.PHOTO_BROWSER: "Photo Browser:",
        TranslationKeys.RESULTS: "Results",
        
        # Кнопки
        TranslationKeys.OPEN_IMAGE: "Open Image",
        TranslationKeys.OPEN_FOLDER: "Open Folder",
        TranslationKeys.SAVE_CURRENT_IMAGE: "Save Current Image",
        TranslationKeys.CREATE_NEW_ALBUM: "Create New Album",
        TranslationKeys.SET_SCALE_EDGE: "Set Scale Edge",
        TranslationKeys.SET_CENTER: "Set Center",
        TranslationKeys.NEXT: "Next",
        TranslationKeys.PREVIOUS: "Previous",
        TranslationKeys.TODAY: "Today",
        
        # Секції інтерфейсу
        TranslationKeys.FILE_OPERATIONS: "File Operations",
        TranslationKeys.BATCH_PROCESSING: "Batch Processing",
        TranslationKeys.AZIMUTH_GRID: "Azimuth Grid",
        TranslationKeys.MOVE_CENTER: "Move Center",
        TranslationKeys.SCALE_SETTING: "Scale Setting",
        TranslationKeys.TITLE_PAGE: "Title Page",
        TranslationKeys.DOCUMENT_DATE: "Document Date",
        TranslationKeys.TEMPLATE_SELECTION: "Template Selection",
        
        # Діалоги файлів
        TranslationKeys.SELECT_IMAGE: "Select Image",
        TranslationKeys.SELECT_FOLDER: "Select Folder",
        TranslationKeys.IMAGE_FILES: "Image Files",
        TranslationKeys.ALL_FILES: "All Files",
        TranslationKeys.JPEG_FILES: "JPEG Files",
        TranslationKeys.PNG_FILES: "PNG Files",
        TranslationKeys.SAVE_PROCESSED_IMAGE: "Save Processed Image",
        
        # Повідомлення
        TranslationKeys.LOADED_FOLDER: "Loaded folder",
        TranslationKeys.FOUND_IMAGES: "Found {count} images",
        TranslationKeys.NO_IMAGES_FOUND: "No images found in this folder",
        TranslationKeys.LOADED_FROM_BROWSER: "Loaded from browser: {name}",
        TranslationKeys.LOADED: "Loaded",
        TranslationKeys.SAVED: "Saved",
        TranslationKeys.SUCCESS: "Success",
        TranslationKeys.ERROR: "Error",
        TranslationKeys.WARNING: "Warning",
        
        # Інструкції
        TranslationKeys.OPEN_INSTRUCTION: "Open an image or folder to start",
        TranslationKeys.CLICK_TO_PLACE: "Click to place point",
        TranslationKeys.DRAG_TO_MOVE: "Drag to move",
        TranslationKeys.LINE_CONNECTS: "Line connects to right edge",
        TranslationKeys.CLICK_ON_IMAGE: "Click on image",
        
        # Дані звіту
        TranslationKeys.KM_UNIT: "km",
        TranslationKeys.NO_OBSTACLES: "no obstacles",
        TranslationKeys.WITH_OBSTACLES: "with obstacles",
        TranslationKeys.DETECTION: "Detection",
        TranslationKeys.TRACKING: "Tracking",
        TranslationKeys.LOSS: "Loss",
        TranslationKeys.TARGET_NUMBER: "Target Number",
        TranslationKeys.HEIGHT: "Height",
        TranslationKeys.OBSTACLES: "Obstacles",
        
        # Результати аналізу
        TranslationKeys.IMAGE_INFO: "Image: {name}",
        TranslationKeys.SIZE: "Size: {width} x {height}",
        TranslationKeys.SCALE_INFO: "Scale: 1:{scale}",
        TranslationKeys.CENTER_INFO: "Center: ({x}, {y})",
        TranslationKeys.BOTTOM_EDGE: "Bottom edge = {scale} units",
        TranslationKeys.PIXELS_SOUTH: "Pixels south: {pixels}",
        TranslationKeys.ANALYSIS_POINT: "Analysis point:",
        TranslationKeys.POSITION: "Position",
        TranslationKeys.AZIMUTH: "Azimuth",
        TranslationKeys.RANGE: "Range",
        
        # Помилки
        TranslationKeys.NO_IMAGE_FIRST: "Load an image first",
        TranslationKeys.NO_ANALYSIS_POINT: "No analysis point to save",
        TranslationKeys.COULD_NOT_LOAD: "Could not load: {error}",
        TranslationKeys.COULD_NOT_SAVE: "Could not save: {error}",
        TranslationKeys.IMAGE_NOT_SUPPORTED: "Image format not supported",
        TranslationKeys.DOCX_NOT_AVAILABLE: "python-docx library not available",
        TranslationKeys.LOAD_IMAGE_AND_POINT: "Load an image and set analysis point",
        
        # Налаштування
        TranslationKeys.SETTINGS: "Settings",
        TranslationKeys.LANGUAGE: "Language",
        TranslationKeys.GRID_SETTINGS_APPLIED: "Grid settings applied",
        TranslationKeys.CHANGES_SAVED: "Changes saved",
        TranslationKeys.CHANGES_CANCELLED: "Changes cancelled",
        TranslationKeys.ALL_CHANGES_CLEARED: "All changes cleared",
    }


class Translator(QObject):
    """
    Головний клас системи перекладів
    
    Функціональність:
    - Переключення між українською та англійською мовами
    - Підстановка параметрів у переклади (format)
    - Автоматичне збереження обраної мови
    - Сигнали для оновлення інтерфейсу при зміні мови
    - Резервні переклади (fallback) при відсутності ключа
    """
    
    # Сигнал про зміну мови
    language_changed = pyqtSignal(Language)
    
    def __init__(self):
        super().__init__()
        
        # Поточна мова (за замовчуванням українська)
        self._current_language = Language.UKRAINIAN
        
        # Словники перекладів
        self._translations = {
            Language.UKRAINIAN: UkrainianTranslations.TRANSLATIONS,
            Language.ENGLISH: EnglishTranslations.TRANSLATIONS
        }
        
        # Кеш для покращення продуктивності
        self._translation_cache: Dict[str, str] = {}
        
        # Функції зворотного виклику для динамічного оновлення
        self._update_callbacks: Dict[str, Callable] = {}
        
        print(f"Translator ініціалізовано. Поточна мова: {self._current_language.value}")
    
    # ===============================
    # ОСНОВНІ МЕТОДИ ПЕРЕКЛАДУ
    # ===============================
    
    def tr(self, key: str, **kwargs) -> str:
        """
        Основний метод перекладу
        
        Args:
            key: Ключ перекладу (рекомендується використовувати TranslationKeys)
            **kwargs: Параметри для підстановки в текст
            
        Returns:
            Перекладений текст
        """
        # Створення ключа кешу
        cache_key = f"{self._current_language.value}:{key}:{str(sorted(kwargs.items()))}"
        
        # Перевірка кешу
        if cache_key in self._translation_cache:
            return self._translation_cache[cache_key]
        
        # Отримання базового перекладу
        translation = self._get_translation(key)
        
        # Підстановка параметрів
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError) as e:
                print(f"Помилка підстановки параметрів для ключа '{key}': {e}")
                # Повертаємо базовий переклад без підстановки
        
        # Збереження в кеш
        self._translation_cache[cache_key] = translation
        
        return translation
    
    def _get_translation(self, key: str) -> str:
        """
        Отримання базового перекладу для ключа
        
        Args:
            key: Ключ перекладу
            
        Returns:
            Перекладений текст або fallback
        """
        current_translations = self._translations.get(self._current_language)
        
        if current_translations and key in current_translations:
            return current_translations[key]
        
        # Fallback на англійську якщо переклад не знайдено
        if self._current_language != Language.ENGLISH:
            english_translations = self._translations.get(Language.ENGLISH)
            if english_translations and key in english_translations:
                print(f"Використано fallback переклад для ключа: {key}")
                return english_translations[key]
        
        # Якщо переклад не знайдено взагалі
        print(f"Переклад не знайдено для ключа: {key}")
        return f"[{key}]"  # Відображення ключа в квадратних дужках
    
    # ===============================
    # УПРАВЛІННЯ МОВОЮ
    # ===============================
    
    def set_language(self, language: Language):
        """
        Встановлення поточної мови
        
        Args:
            language: Нова мова
        """
        if language != self._current_language:
            old_language = self._current_language
            self._current_language = language
            
            # Очищення кешу при зміні мови
            self._translation_cache.clear()
            
            print(f"Мова змінена: {old_language.value} → {language.value}")
            
            # Сповіщення про зміну мови
            self.language_changed.emit(language)
            
            # Виклик зареєстрованих callback функцій
            self._call_update_callbacks()
    
    def get_current_language(self) -> Language:
        """Отримання поточної мови"""
        return self._current_language
    
    def get_available_languages(self) -> Dict[Language, str]:
        """
        Отримання списку доступних мов
        
        Returns:
            Словник {Language: Назва_мови_українською}
        """
        return {
            Language.UKRAINIAN: "Українська",
            Language.ENGLISH: "English"
        }
    
    def toggle_language(self):
        """Переключення між мовами"""
        if self._current_language == Language.UKRAINIAN:
            self.set_language(Language.ENGLISH)
        else:
            self.set_language(Language.UKRAINIAN)
    
    # ===============================
    # СИСТЕМИ ОНОВЛЕННЯ ІНТЕРФЕЙСУ
    # ===============================
    
    def register_update_callback(self, callback_id: str, callback_func: Callable):
        """
        Реєстрація функції для оновлення при зміні мови
        
        Args:
            callback_id: Унікальний ідентифікатор callback
            callback_func: Функція для виклику при зміні мови
        """
        self._update_callbacks[callback_id] = callback_func
        print(f"Зареєстровано callback для оновлення: {callback_id}")
    
    def unregister_update_callback(self, callback_id: str):
        """
        Відміна реєстрації callback функції
        
        Args:
            callback_id: Ідентифікатор callback для видалення
        """
        if callback_id in self._update_callbacks:
            del self._update_callbacks[callback_id]
            print(f"Callback відмінено: {callback_id}")
    
    def _call_update_callbacks(self):
        """Виклик всіх зареєстрованих callback функцій"""
        for callback_id, callback_func in self._update_callbacks.items():
            try:
                callback_func()
                print(f"Callback викликано успішно: {callback_id}")
            except Exception as e:
                print(f"Помилка виклику callback {callback_id}: {e}")
    
    # ===============================
    # СПЕЦІАЛЬНІ МЕТОДИ ПЕРЕКЛАДУ
    # ===============================
    
    def tr_file_filter(self, filter_type: str) -> str:
        """
        Спеціальний метод для фільтрів файлових діалогів
        
        Args:
            filter_type: Тип фільтру ('images', 'jpeg', 'png', 'all', 'docx')
            
        Returns:
            Рядок фільтру для QFileDialog
        """
        filters = {
            'images': f"{self.tr(TranslationKeys.IMAGE_FILES)} (*.jpg *.jpeg *.png *.bmp *.tiff *.tif)",
            'jpeg': f"{self.tr(TranslationKeys.JPEG_FILES)} (*.jpg *.jpeg)",
            'png': f"{self.tr(TranslationKeys.PNG_FILES)} (*.png)",
            'all': f"{self.tr(TranslationKeys.ALL_FILES)} (*.*)",
            'docx': "Word Documents (*.docx)"
        }
        
        return filters.get(filter_type, filters['all'])
    
    def tr_message_box(self, message_type: str, title: str, text: str) -> tuple:
        """
        Переклад для повідомлень QMessageBox
        
        Args:
            message_type: Тип повідомлення ('success', 'error', 'warning')
            title: Заголовок повідомлення
            text: Текст повідомлення
            
        Returns:
            Кортеж (перекладений_заголовок, перекладений_текст)
        """
        type_translations = {
            'success': self.tr(TranslationKeys.SUCCESS),
            'error': self.tr(TranslationKeys.ERROR),
            'warning': self.tr(TranslationKeys.WARNING)
        }
        
        translated_title = type_translations.get(message_type, title)
        translated_text = self.tr(text) if text in [k for k in dir(TranslationKeys) if not k.startswith('_')] else text
        
        return translated_title, translated_text
    
    def tr_format_numbers(self, number: float, unit_key: str = None) -> str:
        """
        Форматування чисел з урахуванням локалізації
        
        Args:
            number: Число для форматування
            unit_key: Ключ одиниці вимірювання (опціонально)
            
        Returns:
            Відформатоване число з одиницею
        """
        # Форматування числа залежно від мови
        if self._current_language == Language.UKRAINIAN:
            # Українське форматування: кома як десятковий роздільник
            formatted = f"{number:.1f}".replace('.', ',')
        else:
            # Англійське форматування: крапка як десятковий роздільник
            formatted = f"{number:.1f}"
        
        # Додавання одиниці вимірювання
        if unit_key:
            unit = self.tr(unit_key)
            formatted = f"{formatted} {unit}"
        
        return formatted
    
    # ===============================
    # УТИЛІТАРНІ МЕТОДИ
    # ===============================
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """
        Отримання статистики перекладів
        
        Returns:
            Словник з інформацією про переклади
        """
        stats = {
            'current_language': self._current_language.value,
            'available_languages': len(self._translations),
            'cache_size': len(self._translation_cache),
            'callbacks_registered': len(self._update_callbacks)
        }
        
        # Статистика по мовах
        for lang, translations in self._translations.items():
            stats[f'{lang.value}_translations_count'] = len(translations)
        
        return stats
    
    def clear_cache(self):
        """Очищення кешу перекладів"""
        cache_size = len(self._translation_cache)
        self._translation_cache.clear()
        print(f"Кеш перекладів очищено. Видалено {cache_size} записів")
    
    def validate_translations(self) -> Dict[str, list]:
        """
        Валідація повноти перекладів
        
        Returns:
            Словник з відсутніми ключами для кожної мови
        """
        # Отримання всіх можливих ключів з TranslationKeys
        all_keys = {getattr(TranslationKeys, attr) 
                   for attr in dir(TranslationKeys) 
                   if not attr.startswith('_')}
        
        missing_keys = {}
        
        for language, translations in self._translations.items():
            missing = all_keys - set(translations.keys())
            if missing:
                missing_keys[language.value] = list(missing)
        
        return missing_keys
    
    def is_rtl_language(self) -> bool:
        """Перевірка чи поточна мова читається справа наліво"""
        # Українська та англійська читаються зліва направо
        return False
    
    def get_language_direction(self) -> str:
        """Отримання напрямку тексту для CSS"""
        return "rtl" if self.is_rtl_language() else "ltr"


# ===============================
# ГЛОБАЛЬНИЙ ЕКЗЕМПЛЯР TRANSLATOR
# ===============================

# Створення глобального екземпляру для використання в усій програмі
_translator_instance: Optional[Translator] = None


def get_translator() -> Translator:
    """
    Отримання глобального екземпляру Translator (Singleton pattern)
    
    Returns:
        Глобальний екземпляр Translator
    """
    global _translator_instance
    
    if _translator_instance is None:
        _translator_instance = Translator()
    
    return _translator_instance


def tr(key: str, **kwargs) -> str:
    """
    Скорочена функція для перекладу (глобальна)
    
    Args:
        key: Ключ перекладу
        **kwargs: Параметри для підстановки
        
    Returns:
        Перекладений текст
    """
    return get_translator().tr(key, **kwargs)


# ===============================
# ДОПОМІЖНІ ФУНКЦІЇ
# ===============================

def setup_translator_for_widget(widget, update_callback: Callable):
    """
    Налаштування перекладів для віджету
    
    Args:
        widget: Віджет Qt для налаштування
        update_callback: Функція оновлення перекладів віджету
    """
    translator = get_translator()
    widget_id = f"{widget.__class__.__name__}_{id(widget)}"
    
    # Реєстрація callback для оновлення при зміні мови
    translator.register_update_callback(widget_id, update_callback)
    
    # Видалення callback при знищенні віджету
    def cleanup():
        translator.unregister_update_callback(widget_id)
    
    # Підключення до сигналу destroyed якщо це QObject
    if hasattr(widget, 'destroyed'):
        widget.destroyed.connect(cleanup)


def detect_system_language() -> Language:
    """
    Автоматичне визначення мови системи
    
    Returns:
        Language відповідно до налаштувань системи
    """
    import locale
    
    try:
        # Отримання мови системи
        system_locale = locale.getdefaultlocale()[0]
        
        if system_locale:
            # Перевірка на українську мову
            if system_locale.startswith('uk') or 'ukraine' in system_locale.lower():
                return Language.UKRAINIAN
            # За замовчуванням англійська
            else:
                return Language.ENGLISH
    except Exception as e:
        print(f"Помилка визначення системної мови: {e}")
    
    # За замовчуванням українська
    return Language.UKRAINIAN


def load_language_from_config(config_path: str = None) -> Language:
    """
    Завантаження мови з конфігураційного файлу
    
    Args:
        config_path: Шлях до файлу конфігурації
        
    Returns:
        Language з конфігурації або за замовчуванням
    """
    import json
    import os
    
    if not config_path:
        # Використання стандартного шляху
        from utils.file_utils import get_user_data_directory
        config_path = os.path.join(get_user_data_directory(), "settings.json")
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            language_code = config.get('language', 'uk')
            
            # Конвертація коду в Language enum
            for lang in Language:
                if lang.value == language_code:
                    return lang
    
    except Exception as e:
        print(f"Помилка завантаження мови з конфігурації: {e}")
    
    # За замовчуванням визначення системної мови
    return detect_system_language()


def save_language_to_config(language: Language, config_path: str = None):
    """
    Збереження мови в конфігураційний файл
    
    Args:
        language: Мова для збереження
        config_path: Шлях до файлу конфігурації
    """
    import json
    import os
    
    if not config_path:
        # Використання стандартного шляху
        from utils.file_utils import get_user_data_directory, ensure_directory_exists
        config_dir = get_user_data_directory()
        ensure_directory_exists(config_dir)
        config_path = os.path.join(config_dir, "settings.json")
    
    try:
        # Завантаження існуючої конфігурації
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # Оновлення мови
        config['language'] = language.value
        
        # Збереження
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        print(f"Мову збережено в конфігурацію: {language.value}")
        
    except Exception as e:
        print(f"Помилка збереження мови в конфігурацію: {e}")


if __name__ == "__main__":
    # Тестування системи перекладів
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
    from PyQt5.QtCore import QTimer
    
    class TranslatorTestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.translator = get_translator()
            self.setWindowTitle("Тестування системи перекладів")
            self.setGeometry(100, 100, 800, 600)
            
            # Центральний віджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)
            
            # Поточна мова та кнопки перемикання
            lang_layout = QHBoxLayout()
            
            self.current_lang_label = QLabel()
            lang_layout.addWidget(self.current_lang_label)
            
            self.toggle_lang_btn = QPushButton("Переключити мову")
            self.toggle_lang_btn.clicked.connect(self.translator.toggle_language)
            lang_layout.addWidget(self.toggle_lang_btn)
            
            self.ukrainian_btn = QPushButton("Українська")
            self.ukrainian_btn.clicked.connect(lambda: self.translator.set_language(Language.UKRAINIAN))
            lang_layout.addWidget(self.ukrainian_btn)
            
            self.english_btn = QPushButton("English")
            self.english_btn.clicked.connect(lambda: self.translator.set_language(Language.ENGLISH))
            lang_layout.addWidget(self.english_btn)
            
            lang_layout.addStretch()
            main_layout.addLayout(lang_layout)
            
            # Тестові переклади
            self.test_labels = []
            
            # Створення тестових віджетів
            test_keys = [
                TranslationKeys.WINDOW_TITLE,
                TranslationKeys.OPEN_IMAGE,
                TranslationKeys.SAVE_CURRENT_IMAGE,
                TranslationKeys.BATCH_PROCESSING,
                TranslationKeys.NO_IMAGES_FOUND,
                TranslationKeys.ANALYSIS_POINT,
                TranslationKeys.COULD_NOT_LOAD,
                TranslationKeys.SETTINGS
            ]
            
            for key in test_keys:
                label = QLabel()
                self.test_labels.append((label, key))
                main_layout.addWidget(label)
            
            # Тестування з параметрами
            main_layout.addWidget(QLabel("Тестування з параметрами:"))
            
            self.param_test_labels = []
            param_tests = [
                (TranslationKeys.FOUND_IMAGES, {'count': 42}),
                (TranslationKeys.IMAGE_INFO, {'name': 'test.jpg'}),
                (TranslationKeys.SIZE, {'width': 1920, 'height': 1080}),
                (TranslationKeys.SCALE_INFO, {'scale': 300}),
                (TranslationKeys.CENTER_INFO, {'x': 960, 'y': 540})
            ]
            
            for key, params in param_tests:
                label = QLabel()
                self.param_test_labels.append((label, key, params))
                main_layout.addWidget(label)
            
            # Статистика
            main_layout.addWidget(QLabel("Статистика перекладів:"))
            self.stats_text = QTextEdit()
            self.stats_text.setMaximumHeight(150)
            self.stats_text.setStyleSheet("""
                QTextEdit {
                    font-family: 'Courier New', monospace;
                    font-size: 10px;
                    background-color: #f9f9f9;
                    border: 1px solid #ccc;
                }
            """)
            main_layout.addWidget(self.stats_text)
            
            # Кнопки тестування
            test_layout = QHBoxLayout()
            
            clear_cache_btn = QPushButton("Очистити кеш")
            clear_cache_btn.clicked.connect(self.translator.clear_cache)
            test_layout.addWidget(clear_cache_btn)
            
            validate_btn = QPushButton("Валідація перекладів")
            validate_btn.clicked.connect(self.validate_translations)
            test_layout.addWidget(validate_btn)
            
            test_layout.addStretch()
            main_layout.addLayout(test_layout)
            
            # Підключення до сигналу зміни мови
            self.translator.language_changed.connect(self.update_translations)
            
            # Початкове оновлення
            self.update_translations()
            
            # Таймер для оновлення статистики
            self.stats_timer = QTimer()
            self.stats_timer.timeout.connect(self.update_stats)
            self.stats_timer.start(1000)  # Кожну секунду
        
        def update_translations(self):
            """Оновлення всіх перекладів в інтерфейсі"""
            # Поточна мова
            current_lang = self.translator.get_current_language()
            available_langs = self.translator.get_available_languages()
            self.current_lang_label.setText(f"Поточна мова: {available_langs[current_lang]}")
            
            # Основні переклади
            for label, key in self.test_labels:
                translation = self.translator.tr(key)
                label.setText(f"{key}: {translation}")
            
            # Переклади з параметрами
            for label, key, params in self.param_test_labels:
                translation = self.translator.tr(key, **params)
                label.setText(f"{key}: {translation}")
            
            print(f"Інтерфейс оновлено для мови: {current_lang.value}")
        
        def update_stats(self):
            """Оновлення статистики"""
            stats = self.translator.get_translation_stats()
            
            stats_text = f"""
Поточна мова: {stats['current_language']}
Доступно мов: {stats['available_languages']}
Розмір кешу: {stats['cache_size']}
Зареєстровано callbacks: {stats['callbacks_registered']}

Кількість перекладів по мовах:
• Українська: {stats.get('uk_translations_count', 0)}
• Англійська: {stats.get('en_translations_count', 0)}
            """.strip()
            
            self.stats_text.setText(stats_text)
        
        def validate_translations(self):
            """Валідація повноти перекладів"""
            missing_keys = self.translator.validate_translations()
            
            if missing_keys:
                result = "Знайдено відсутні переклади:\n\n"
                for lang, keys in missing_keys.items():
                    result += f"{lang.upper()}:\n"
                    for key in keys:
                        result += f"  - {key}\n"
                    result += "\n"
            else:
                result = "Всі переклади присутні! ✅"
            
            self.stats_text.setText(result)
            print("Валідацію перекладів завершено")
    
    # Запуск тесту
    app = QApplication(sys.argv)
    
    # Ініціалізація мови
    translator = get_translator()
    saved_language = load_language_from_config()
    translator.set_language(saved_language)
    
    # Збереження мови при зміні
    def save_on_change(language):
        save_language_to_config(language)
    
    translator.language_changed.connect(save_on_change)
    
    # Показ тестового вікна
    window = TranslatorTestWindow()
    window.show()
    
    print("=== Тестування системи перекладів ===")
    print("Функції для тестування:")
    print("1. 'Переключити мову' - перемикання між українською та англійською")
    print("2. 'Українська/English' - пряме встановлення мови")
    print("3. 'Очистити кеш' - очищення кешу перекладів")
    print("4. 'Валідація перекладів' - перевірка повноти перекладів")
    print("5. Автоматичне збереження обраної мови")
    print("6. Статистика в реальному часі")
    print("7. Тестування перекладів з параметрами")
    
    sys.exit(app.exec_())