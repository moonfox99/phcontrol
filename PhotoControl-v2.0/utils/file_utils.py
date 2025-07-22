#!/usr/bin/env python3
"""
Утиліти для роботи з файлами та ресурсами
"""

import os
import sys
import tempfile
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from core.constants import FILES, IMAGE


def get_resource_path(relative_path: str) -> str:
    """
    Отримання шляху до ресурсу (працює як в режимі розробки, так і в PyInstaller)
    
    Args:
        relative_path: Відносний шлях до ресурсу
        
    Returns:
        Абсолютний шлях до ресурсу
    """
    try:
        # PyInstaller створює тимчасову папку та зберігає шлях в _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Режим розробки - використовуємо папку проекту
        base_path = Path(__file__).parent.parent
    
    return os.path.join(base_path, relative_path)


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Переконатися що директорія існує, створити якщо потрібно
    
    Args:
        directory_path: Шлях до директорії
        
    Returns:
        True якщо директорія існує або була створена успішно
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError) as e:
        print(f"Помилка створення директорії {directory_path}: {e}")
        return False


def get_user_data_directory(folder_name: str) -> str:
    """
    Отримання шляху до папки користувача для збереження даних програми
    
    Args:
        folder_name: Назва папки в домашній директорії користувача
        
    Returns:
        Абсолютний шлях до папки даних
    """
    home_dir = Path.home()
    data_dir = home_dir / folder_name
    
    # Створюємо папку якщо не існує
    ensure_directory_exists(str(data_dir))
    
    return str(data_dir)


def get_templates_directory() -> str:
    """Отримання шляху до папки шаблонів"""
    return get_user_data_directory(FILES.TEMPLATES_FOLDER)


def get_documentation_directory() -> str:
    """Отримання шляху до папки документації"""
    return get_user_data_directory(FILES.DOCS_FOLDER)


def is_image_file(file_path: str) -> bool:
    """
    Перевірка чи є файл зображенням за розширенням
    
    Args:
        file_path: Шлях до файлу
        
    Returns:
        True якщо файл є зображенням
    """
    if not os.path.isfile(file_path):
        return False
    
    return file_path.lower().endswith(IMAGE.SUPPORTED_FORMATS)


def get_images_in_directory(directory_path: str) -> List[str]:
    """
    Отримання списку всіх зображень в директорії
    
    Args:
        directory_path: Шлях до директорії
        
    Returns:
        Відсортований список шляхів до зображень
    """
    if not os.path.isdir(directory_path):
        return []
    
    image_files = []
    
    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if is_image_file(file_path):
                image_files.append(file_path)
    except (OSError, PermissionError) as e:
        print(f"Помилка читання директорії {directory_path}: {e}")
        return []
    
    return sorted(image_files)


def save_json_file(data: Dict[Any, Any], file_path: str) -> bool:
    """
    Збереження даних у JSON файл
    
    Args:
        data: Дані для збереження
        file_path: Шлях до файлу
        
    Returns:
        True якщо збереження успішне
    """
    try:
        # Переконуємося що директорія існує
        directory = os.path.dirname(file_path)
        if directory:
            ensure_directory_exists(directory)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except (OSError, PermissionError, json.JSONEncodeError) as e:
        print(f"Помилка збереження JSON файлу {file_path}: {e}")
        return False


def load_json_file(file_path: str) -> Optional[Dict[Any, Any]]:
    """
    Завантаження даних з JSON файлу
    
    Args:
        file_path: Шлях до файлу
        
    Returns:
        Дані з файлу або None якщо помилка
    """
    if not os.path.isfile(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    except (OSError, PermissionError, json.JSONDecodeError) as e:
        print(f"Помилка завантаження JSON файлу {file_path}: {e}")
        return None


def create_temp_file(suffix: str = '.tmp', delete: bool = False) -> str:
    """
    Створення тимчасового файлу
    
    Args:
        suffix: Розширення файлу
        delete: Чи видаляти файл при закритті
        
    Returns:
        Шлях до тимчасового файлу
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=delete)
    
    if delete:
        return temp_file.name
    else:
        # Закриваємо файл але не видаляємо
        temp_path = temp_file.name
        temp_file.close()
        return temp_path


def safe_remove_file(file_path: str) -> bool:
    """
    Безпечне видалення файлу
    
    Args:
        file_path: Шлях до файлу
        
    Returns:
        True якщо файл видалено або не існував
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except (OSError, PermissionError) as e:
        print(f"Помилка видалення файлу {file_path}: {e}")
        return False


def get_file_size_mb(file_path: str) -> float:
    """
    Отримання розміру файлу в мегабайтах
    
    Args:
        file_path: Шлях до файлу
        
    Returns:
        Розмір файлу в MB або 0 якщо файл не існує
    """
    try:
        if os.path.isfile(file_path):
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)  # Конвертація в MB
        return 0.0
    except OSError:
        return 0.0


def list_template_files() -> List[str]:
    """
    Отримання списку файлів шаблонів
    
    Returns:
        Список назв шаблонів (без розширення)
    """
    templates_dir = get_templates_directory()
    template_files = []
    
    try:
        for filename in os.listdir(templates_dir):
            if filename.endswith(FILES.TEMPLATE_EXTENSION):
                # Прибираємо розширення .json
                template_name = filename[:-len(FILES.TEMPLATE_EXTENSION)]
                template_files.append(template_name)
    except (OSError, PermissionError):
        pass  # Директорія може не існувати
    
    return sorted(template_files)


def validate_file_path(file_path: str, must_exist: bool = True) -> bool:
    """
    Валідація шляху до файлу
    
    Args:
        file_path: Шлях до файлу
        must_exist: Чи повинен файл існувати
        
    Returns:
        True якщо шлях валідний
    """
    if not file_path or not isinstance(file_path, str):
        return False
    
    if must_exist:
        return os.path.isfile(file_path)
    else:
        # Перевіряємо чи батьківська директорія існує або може бути створена
        parent_dir = os.path.dirname(file_path)
        if not parent_dir:  # Поточна директорія
            return True
        
        return os.path.isdir(parent_dir) or ensure_directory_exists(parent_dir)


def get_backup_filename(original_path: str) -> str:
    """
    Генерація імені файлу резервної копії
    
    Args:
        original_path: Оригінальний шлях до файлу
        
    Returns:
        Шлях до файлу резервної копії
    """
    path = Path(original_path)
    backup_name = f"{path.stem}_backup{path.suffix}"
    return str(path.parent / backup_name)


# Константи фільтрів для діалогів відкриття файлів
IMAGE_FILTERS = f"Файли зображень ({' '.join('*' + ext for ext in IMAGE.SUPPORTED_FORMATS)});;Всі файли (*.*)"
DOCX_FILTERS = f"Документи Word (*{FILES.DOC_EXTENSION});;Всі файли (*.*)"
JSON_FILTERS = f"JSON файли (*{FILES.TEMPLATE_EXTENSION});;Всі файли (*.*)"


if __name__ == "__main__":
    # Тестування утиліт
    print("=== Тестування file_utils ===")
    
    # Тест шляхів
    print(f"Папка шаблонів: {get_templates_directory()}")
    print(f"Папка документації: {get_documentation_directory()}")
    
    # Тест перевірки зображень
    test_files = ["test.jpg", "test.png", "test.txt", "test.docx"]
    for file in test_files:
        print(f"Чи є {file} зображенням: {file.lower().endswith(IMAGE.SUPPORTED_FORMATS)}")
    
    # Тест фільтрів
    print(f"Фільтр зображень: {IMAGE_FILTERS}")
    print(f"Фільтр DOCX: {DOCX_FILTERS}")
    
    print("=== Тест завершено ===")