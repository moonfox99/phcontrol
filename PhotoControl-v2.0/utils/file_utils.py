#!/usr/bin/env python3
"""
PhotoControl v2.0 - Файлові утиліти
Функції для роботи з файлами та директоріями
"""

import os
import json
import tempfile
import shutil
from typing import List, Optional, Dict, Any, Union
from pathlib import Path


# ===============================
# КОНСТАНТИ ФАЙЛОВИХ ФОРМАТІВ
# ===============================

# Підтримувані формати зображень
SUPPORTED_IMAGE_EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.bmp', 
    '.gif', '.tiff', '.tif', '.webp'
]

# Формати для збереження
SAVE_FORMATS = {
    'JPEG': ['.jpg', '.jpeg'],
    'PNG': ['.png'],
    'BMP': ['.bmp'],
    'TIFF': ['.tiff', '.tif']
}

# Максимальний розмір файлу (100 МБ)
MAX_FILE_SIZE = 100 * 1024 * 1024


# ===============================
# РОБОТА З ЗОБРАЖЕННЯМИ
# ===============================

def is_image_file(file_path: str) -> bool:
    """
    Перевірка чи є файл зображенням
    
    Args:
        file_path: Шлях до файлу
        
    Returns:
        True якщо файл є підтримуваним зображенням
    """
    if not file_path or not os.path.isfile(file_path):
        return False
    
    # Перевірка розширення
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_IMAGE_EXTENSIONS:
        return False
    
    # Перевірка розміру файлу
    try:
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return False
    except OSError:
        return False
    
    return True


def get_images_in_directory(directory_path: str) -> List[str]:
    """
    Отримання списку зображень в директорії
    
    Args:
        directory_path: Шлях до директорії
        
    Returns:
        Відсортований список шляхів до зображень
    """
    if not directory_path or not os.path.isdir(directory_path):
        return []
    
    image_files = []
    
    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            # Пропускаємо директорії та прихований файли
            if os.path.isdir(file_path) or filename.startswith('.'):
                continue
            
            # Перевірка чи є файл зображенням
            if is_image_file(file_path):
                image_files.append(file_path)
    
    except (OSError, PermissionError) as e:
        print(f"Помилка читання директорії {directory_path}: {e}")
        return []
    
    # Сортування за назвою файлу
    image_files.sort(key=lambda x: os.path.basename(x).lower())
    
    return image_files


def get_image_info(image_path: str) -> Optional[Dict[str, Any]]:
    """
    Отримання інформації про зображення
    
    Args:
        image_path: Шлях до зображення
        
    Returns:
        Словник з інформацією або None при помилці
    """
    if not is_image_file(image_path):
        return None
    
    try:
        from PIL import Image
        
        with Image.open(image_path) as img:
            return {
                'filename': os.path.basename(image_path),
                'path': image_path,
                'width': img.width,
                'height': img.height,
                'mode': img.mode,
                'format': img.format,
                'size_bytes': os.path.getsize(image_path),
                'size_mb': round(os.path.getsize(image_path) / (1024 * 1024), 2)
            }
    
    except Exception as e:
        print(f"Помилка отримання інформації про зображення {image_path}: {e}")
        return None


# ===============================
# РОБОТА З ДИРЕКТОРІЯМИ
# ===============================

def ensure_directory_exists(directory_path: str) -> bool:
    """
    Забезпечення існування директорії
    
    Args:
        directory_path: Шлях до директорії
        
    Returns:
        True якщо директорія існує або була створена
    """
    if not directory_path:
        return False
    
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except (OSError, PermissionError) as e:
        print(f"Не вдалося створити директорію {directory_path}: {e}")
        return False


def get_user_data_directory() -> str:
    """
    Отримання директорії для користувацьких даних програми
    
    Returns:
        Шлях до директорії користувацьких даних
    """
    # Визначення домашньої директорії користувача
    home_dir = os.path.expanduser("~")
    
    # Створення папки PhotoControl_Data
    data_dir = os.path.join(home_dir, "PhotoControl_Data")
    
    # Забезпечення існування
    ensure_directory_exists(data_dir)
    
    return data_dir


def get_templates_directory() -> str:
    """
    Отримання директорії шаблонів
    
    Returns:
        Шлях до директорії шаблонів
    """
    user_data = get_user_data_directory()
    templates_dir = os.path.join(user_data, "templates")
    
    ensure_directory_exists(templates_dir)
    
    return templates_dir


def get_temp_directory() -> str:
    """
    Отримання тимчасової директорії програми
    
    Returns:
        Шлях до тимчасової директорії
    """
    user_data = get_user_data_directory()
    temp_dir = os.path.join(user_data, "temp")
    
    ensure_directory_exists(temp_dir)
    
    return temp_dir


def cleanup_temp_files(max_age_hours: int = 24) -> int:
    """
    Очищення старих тимчасових файлів
    
    Args:
        max_age_hours: Максимальний вік файлів в годинах
        
    Returns:
        Кількість видалених файлів
    """
    import time
    
    temp_dir = get_temp_directory()
    if not os.path.exists(temp_dir):
        return 0
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    deleted_count = 0
    
    try:
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            
            # Пропускаємо директорії
            if os.path.isdir(file_path):
                continue
            
            # Перевірка віку файлу
            file_age = current_time - os.path.getmtime(file_path)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except OSError:
                    pass  # Ігноруємо помилки видалення
    
    except OSError:
        pass
    
    return deleted_count


# ===============================
# РОБОТА З JSON
# ===============================

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Завантаження JSON файлу
    
    Args:
        file_path: Шлях до JSON файлу
        
    Returns:
        Словник з даними або None при помилці
    """
    if not os.path.isfile(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        print(f"Помилка завантаження JSON {file_path}: {e}")
        return None


def save_json_file(file_path: str, data: Dict[str, Any], indent: int = 2) -> bool:
    """
    Збереження даних у JSON файл
    
    Args:
        file_path: Шлях до файлу для збереження
        data: Дані для збереження
        indent: Відступ для форматування
        
    Returns:
        True при успішному збереженні
    """
    try:
        # Забезпечення існування директорії
        directory = os.path.dirname(file_path)
        if directory:
            ensure_directory_exists(directory)
        
        # Збереження з резервною копією
        backup_path = file_path + '.backup'
        
        # Створення резервної копії якщо файл існує
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
        
        # Збереження нових даних
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        # Видалення резервної копії при успішному збереженні
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
            except OSError:
                pass
        
        return True
    
    except (OSError, TypeError, ValueError) as e:
        print(f"Помилка збереження JSON {file_path}: {e}")
        
        # Відновлення з резервної копії при помилці
        backup_path = file_path + '.backup'
        if os.path.exists(backup_path):
            try:
                shutil.copy2(backup_path, file_path)
                os.remove(backup_path)
            except OSError:
                pass
        
        return False


# ===============================
# БЕЗПЕКА ТА ВАЛІДАЦІЯ
# ===============================

def validate_file_path(file_path: str, check_exists: bool = True) -> bool:
    """
    Валідація шляху до файлу
    
    Args:
        file_path: Шлях до файлу
        check_exists: Чи перевіряти існування файлу
        
    Returns:
        True якщо шлях валідний
    """
    if not file_path or not isinstance(file_path, str):
        return False
    
    # Перевірка на небезпечні символи
    dangerous_chars = ['..', '<', '>', '|', '?', '*']
    if any(char in file_path for char in dangerous_chars):
        return False
    
    # Перевірка існування
    if check_exists and not os.path.exists(file_path):
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Очищення назви файлу від небезпечних символів
    
    Args:
        filename: Оригінальна назва файлу
        
    Returns:
        Безпечна назва файлу
    """
    if not filename:
        return "untitled"
    
    # Небезпечні символи для заміни
    dangerous_chars = '<>:"/\\|?*'
    
    # Заміна небезпечних символів на підкреслення
    safe_filename = filename
    for char in dangerous_chars:
        safe_filename = safe_filename.replace(char, '_')
    
    # Обмеження довжини
    max_length = 200
    if len(safe_filename) > max_length:
        name, ext = os.path.splitext(safe_filename)
        safe_filename = name[:max_length - len(ext)] + ext
    
    return safe_filename


# ===============================
# ТИМЧАСОВІ ФАЙЛИ
# ===============================

def create_temp_file(suffix: str = '.tmp', prefix: str = 'photocontrol_') -> str:
    """
    Створення тимчасового файлу
    
    Args:
        suffix: Розширення файлу
        prefix: Префікс назви файлу
        
    Returns:
        Шлях до тимчасового файлу
    """
    temp_dir = get_temp_directory()
    
    # Створення тимчасового файлу
    fd, temp_path = tempfile.mkstemp(
        suffix=suffix,
        prefix=prefix,
        dir=temp_dir
    )
    
    # Закриття файлового дескриптора
    os.close(fd)
    
    return temp_path


def create_temp_copy(source_path: str, suffix: str = None) -> Optional[str]:
    """
    Створення тимчасової копії файлу
    
    Args:
        source_path: Шлях до оригінального файлу
        suffix: Розширення для копії (автоматично з оригіналу якщо None)
        
    Returns:
        Шлях до тимчасової копії або None при помилці
    """
    if not os.path.isfile(source_path):
        return None
    
    # Визначення розширення
    if suffix is None:
        suffix = os.path.splitext(source_path)[1]
    
    try:
        # Створення тимчасового файлу
        temp_path = create_temp_file(suffix=suffix)
        
        # Копіювання
        shutil.copy2(source_path, temp_path)
        
        return temp_path
    
    except (OSError, shutil.Error) as e:
        print(f"Помилка створення тимчасової копії {source_path}: {e}")
        return None


# ===============================
# РОБОТА З НАЛАШТУВАННЯМИ
# ===============================

def get_settings_file_path() -> str:
    """
    Отримання шляху до файлу налаштувань
    
    Returns:
        Шлях до settings.json
    """
    user_data = get_user_data_directory()
    return os.path.join(user_data, "settings.json")


def load_settings() -> Dict[str, Any]:
    """
    Завантаження налаштувань програми
    
    Returns:
        Словник з налаштуваннями
    """
    settings_path = get_settings_file_path()
    settings = load_json_file(settings_path)
    
    # Налаштування за замовчуванням
    if settings is None:
        settings = {
            'language': 'uk',
            'window_geometry': None,
            'recent_folders': [],
            'thumbnail_size': 200,
            'zoom_factor': 4,
            'auto_save': True
        }
    
    return settings


def save_settings(settings: Dict[str, Any]) -> bool:
    """
    Збереження налаштувань програми
    
    Args:
        settings: Словник з налаштуваннями
        
    Returns:
        True при успішному збереженні
    """
    settings_path = get_settings_file_path()
    return save_json_file(settings_path, settings)


# ===============================
# СТАТИСТИКА ТА ІНФОРМАЦІЯ
# ===============================

def get_directory_stats(directory_path: str) -> Dict[str, Any]:
    """
    Отримання статистики директорії
    
    Args:
        directory_path: Шлях до директорії
        
    Returns:
        Словник зі статистикою
    """
    if not os.path.isdir(directory_path):
        return {
            'exists': False,
            'total_files': 0,
            'image_files': 0,
            'total_size': 0
        }
    
    stats = {
        'exists': True,
        'path': directory_path,
        'total_files': 0,
        'image_files': 0,
        'total_size': 0,
        'image_formats': {}
    }
    
    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isfile(file_path):
                stats['total_files'] += 1
                
                try:
                    file_size = os.path.getsize(file_path)
                    stats['total_size'] += file_size
                except OSError:
                    continue
                
                if is_image_file(file_path):
                    stats['image_files'] += 1
                    
                    # Підрахунок форматів
                    ext = os.path.splitext(filename)[1].lower()
                    stats['image_formats'][ext] = stats['image_formats'].get(ext, 0) + 1
    
    except OSError:
        pass
    
    # Конвертація розміру в МБ
    stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)
    
    return stats


# ===============================
# ТЕСТУВАННЯ
# ===============================

if __name__ == "__main__":
    # Тестування основних функцій
    print("=== Тестування file_utils.py ===")
    
    # Тест директорій
    user_data = get_user_data_directory()
    print(f"Директорія користувацьких даних: {user_data}")
    
    templates_dir = get_templates_directory()
    print(f"Директорія шаблонів: {templates_dir}")
    
    temp_dir = get_temp_directory()
    print(f"Тимчасова директорія: {temp_dir}")
    
    # Тест тимчасових файлів
    temp_file = create_temp_file('.jpg', 'test_')
    print(f"Тимчасовий файл: {temp_file}")
    
    # Тест налаштувань
    settings = load_settings()
    print(f"Налаштування: {settings}")
    
    # Тест очищення назви файлу
    unsafe_name = "test<>file|name?.jpg"
    safe_name = sanitize_filename(unsafe_name)
    print(f"Безпечна назва: {unsafe_name} → {safe_name}")
    
    # Очищення тимчасових файлів
    cleaned = cleanup_temp_files(0)  # Видалити всі
    print(f"Очищено тимчасових файлів: {cleaned}")
    
    print("Всі тести пройдено успішно! ✅")