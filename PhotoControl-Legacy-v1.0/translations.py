#!/usr/bin/env python3
"""
Translations module for Azimuth Image Processor
"""

# У файлі translations.py замініть переклади на ці:

class Translations:
    def __init__(self):
        self.translations = {
            'UKRAINIAN': {
                # Основні елементи інтерфейсу
                'window_title': 'Фотоконтроль',
                'controls': 'Керування',
                'report_data': 'Дані цілі',
                'photo_browser': 'Перегляд зображень:',
                'results': 'Інфо',
                
                # Кнопки
                'open_image': 'Відкрити зображення',
                'open_folder': 'Відкрити папку',
                'save_current_image': 'Зберегти зображення',
                'create_new_album': 'Створити новий альбом',  # <-- НОВА КНОПКА
                'set_scale_edge': 'Встановити край',
                'set_center': 'Встановити центр',
                
                # Секції
                'file_operations': 'Операції з файлами',
                'batch_processing': 'Пакетна обробка',
                'azimuth_grid': 'Азимутальна сітка',
                'move_center': 'Переміщення центру',
                'scale_setting': 'Масштаб',
                
                # Пакетна обробка
                'save_current_image_data': 'Додати до альбому',
                
                # Меню
                'settings': 'Налаштування',
                'language': 'Мова',
                
                # Діалоги файлів
                'select_image': 'Виберіть зображення',
                'select_folder': 'Виберіть папку',
                'image_files': 'Файли зображень',
                'all_files': 'Всі файли',
                'jpeg_files': 'JPEG файли',
                'png_files': 'PNG файли',
                'save_processed_image': 'Зберегти оброблене зображення',
                
                # Повідомлення
                'loaded_folder': 'Завантажена папка',
                'found_images': 'Знайдено зображень: {count}',
                'no_images_found': 'Зображення не знайдені',
                'loaded_from_browser': 'Завантажено з браузера: {name}',
                'loaded': 'Завантажено',
                'saved': 'Збережено',
                'success': 'Успіх',
                'error': 'Помилка',
                'warning': 'Попередження',
                
                # Інструкції
                'open_instruction': 'Відкрийте зображення або папку для початку роботи',
                
                # Дані звіту
                'km_unit': 'м',
                'no_obstacles': 'без перешкод',
                'with_obstacles': 'з перешкодами',
                'detection': 'Виявлення',
                'tracking': 'Супроводження',
                'loss': 'Втрата',
                
                # Результати
                'image_info': 'Зображення: {name}',
                'size': 'Розмір: {width} x {height}',
                'scale_info': 'Масштаб: 1:{scale}',
                'center_info': 'Центр: ({x}, {y})',
                'bottom_edge': 'Нижній край = {scale} одиниць',
                'pixels_south': 'Пікселів на південь: {pixels}',
                'analysis_point': 'Точка аналізу:',
                'position': 'Позиція',
                'azimuth': 'Азимут',
                'range': 'Дальність',
                'click_to_place': 'Клікніть для розміщення точки',
                'drag_to_move': 'Перетягніть для переміщення',
                'line_connects': 'Лінія з\'єднує з правим краєм',
                'click_on_image': 'Клікніть на зображення',
                
                # Повідомлення про помилки
                'no_image_first': 'Спочатку завантажте зображення',
                'no_analysis_point': 'Немає точки аналізу для збереження',
                'could_not_load': 'Не вдалося завантажити: {error}',
                'could_not_save': 'Не вдалося зберегти: {error}',
                'image_saved_successfully': 'Зображення успішно збережено',
                'saved_clean': 'Збережено без міток',
                'docx_not_available': 'Бібліотека python-docx не встановлена',
                'load_image_and_point': 'Завантажте зображення та встановіть точку аналізу',
                
                # Операції з сіткою
                'center_moved': 'Центр переміщено: ({x}, {y})',
                'grid_settings_saved': 'Налаштування сітки збережено',
                'grid_settings_applied': 'Налаштування сітки застосовано',
                'scale_edge_active': 'Режим встановлення краю масштабу активний',
                'scale_edge_set': 'Край масштабу встановлено: {distance:.1f} пікселів',
                'scale_updated': 'Масштаб оновлено до 1:{scale}',

                'radar_description': 'Опис РЛС',
                'add_radar_description': 'Додати опис РЛС',
                'radar_date': 'Дата:',
                'radar_callsign': 'Позивний РЛС',
                'radar_name': 'Назва РЛС',
                'radar_number': 'Номер РЛС',
                'radar_data_added': 'Дані РЛС додано до зображення',

                'document_date': 'Дата документу',
                'set_today': 'Встановити сьогодні',
                'date_updated': 'Дата оновлена',
                'using_document_date': 'Використовується дата документу',
                'using_radar_date': 'Використовується дата РЛС', 
                'using_current_date': 'Використовується поточна дата',
                'cancel_changes': 'Скасувати зміни',
                'clear_all': 'Очистити все',
                'cancel_current_changes': 'Скасувати зміни для поточного зображення',
                'clear_all_changes': 'Очистити всі оброблені зображення',
                'no_image_to_cancel': 'Немає завантаженого зображення',
                'no_processed_images': 'Немає оброблених зображень для очищення',
                'confirm_clear_all': 'Ви впевнені, що хочете очистити всі оброблені зображення?',
                'changes_cancelled': 'Зміни скасовано',
                'all_changes_cleared': 'Всі зміни очищено',
            },
            
            'ENGLISH': {
                # Basic interface elements
                'window_title': 'Azimuth Image Processor',
                'controls': 'Controls',
                'report_data': 'Report Data',
                'photo_browser': 'Photo Browser:',
                'results': 'Results',
                
                # Buttons
                'open_image': 'Open Image',
                'open_folder': 'Open Folder',
                'save_current_image': 'Save Current Image',
                'create_new_album': 'Create New Album',  # <-- NEW BUTTON
                'set_scale_edge': 'Set Scale Edge',
                'set_center': 'Set Center',
                
                # Sections
                'file_operations': 'File Operations',
                'batch_processing': 'Batch Processing',
                'azimuth_grid': 'Azimuth Grid',
                'move_center': 'Move Center',
                'scale_setting': 'Scale',
                
                # Batch processing
                'save_current_image_data': 'Save Current Image Data',
                
                # Меню та решта перекладів залишаються без змін...
                'settings': 'Settings',
                'language': 'Language',
                
                # File dialogs
                'select_image': 'Select Image',
                'select_folder': 'Select Folder',
                'image_files': 'Image Files',
                'all_files': 'All Files',
                'jpeg_files': 'JPEG Files',
                'png_files': 'PNG Files',
                'save_processed_image': 'Save Processed Image',
                
                # Messages
                'loaded_folder': 'Loaded folder',
                'found_images': 'Found {count} images',
                'no_images_found': 'No images found',
                'loaded_from_browser': 'Loaded from browser: {name}',
                'loaded': 'Loaded',
                'saved': 'Saved',
                'success': 'Success',
                'error': 'Error',
                'warning': 'Warning',
                
                # Instructions
                'open_instruction': 'Open an image or folder to start',
                
                # Report data
                'km_unit': 'km',
                'no_obstacles': 'no obstacles',
                'with_obstacles': 'with obstacles',
                'detection': 'Detection',
                'tracking': 'Tracking',
                'loss': 'Loss',
                
                # Results
                'image_info': 'Image: {name}',
                'size': 'Size: {width} x {height}',
                'scale_info': 'Scale: 1:{scale}',
                'center_info': 'Center: ({x}, {y})',
                'bottom_edge': 'Bottom edge = {scale} units',
                'pixels_south': 'Pixels south: {pixels}',
                'analysis_point': 'Analysis point:',
                'position': 'Position',
                'azimuth': 'Azimuth',
                'range': 'Range',
                'click_to_place': 'Click to place point',
                'drag_to_move': 'Drag to move',
                'line_connects': 'Line connects to right edge',
                'click_on_image': 'Click on image',
                
                # Error messages
                'no_image_first': 'Load an image first',
                'no_analysis_point': 'No analysis point to save',
                'could_not_load': 'Could not load: {error}',
                'could_not_save': 'Could not save: {error}',
                'image_saved_successfully': 'Image saved successfully',
                'saved_clean': 'Saved without markers',
                'docx_not_available': 'python-docx library not available',
                'load_image_and_point': 'Load image and set analysis point',
                
                # Grid operations
                'center_moved': 'Center moved: ({x}, {y})',
                'grid_settings_saved': 'Grid settings saved',
                'grid_settings_applied': 'Grid settings applied',
                'scale_edge_active': 'Scale edge setting mode active',
                'scale_edge_set': 'Scale edge set: {distance:.1f} pixels',
                'scale_updated': 'Scale updated to 1:{scale}',

                'radar_description': 'Radar Description',
                'add_radar_description': 'Add Radar Description',
                'radar_date': 'Date:',
                'radar_callsign': 'Radar Callsign',
                'radar_name': 'Radar Name',
                'radar_number': 'Radar Number',
                'radar_data_added': 'Radar data added to image',

                'document_date': 'Document Date',
                'set_today': 'Set Today',
                'date_updated': 'Date Updated',
                'using_document_date': 'Using document date',
                'using_radar_date': 'Using radar date',
                'using_current_date': 'Using current date',

                'cancel_changes': 'Cancel Changes',
                'clear_all': 'Clear All',
                'cancel_current_changes': 'Cancel changes for current image',
                'clear_all_changes': 'Clear all processed images',
                'no_image_to_cancel': 'No loaded image',
                'no_processed_images': 'No processed images to clear',
                'confirm_clear_all': 'Are you sure you want to clear all processed images?',
                'changes_cancelled': 'Changes cancelled',
                'all_changes_cleared': 'All changes cleared',
            }
        }

    def get(self, language, key):
        """Отримати переклад для ключа"""
        try:
            return self.translations[language][key]
        except KeyError:
            # Повертаємо ключ якщо переклад не знайдено
            return key