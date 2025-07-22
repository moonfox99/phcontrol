#!/usr/bin/env python3
"""
Панель браузера зображень з вертикальними мініатюрами
"""

import os
from typing import List, Optional, Set
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QLabel, 
                             QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QPixmap, QFont, QCursor

from core.constants import UI
from utils.file_utils import is_image_file


class ThumbnailLabel(QLabel):
    """
    Інтерактивна мініатюра зображення з підтримкою станів
    """
    
    clicked = pyqtSignal(str)  # Сигнал з шляхом до файлу
    
    def __init__(self, image_path: str, width: int = 240, height: int = 180):
        super().__init__()
        
        self.image_path = image_path
        self.is_processed = False
        self.is_selected = False
        
        # Налаштування розміру
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Завантаження та масштабування зображення
        self.load_and_scale_image(width, height)
        
        # Встановлення початкового стилю
        self.update_style()
    
    def load_and_scale_image(self, width: int, height: int):
        """Завантаження та масштабування зображення"""
        try:
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                # Масштабування з збереженням пропорцій
                scaled_pixmap = pixmap.scaled(
                    width - 4, height - 4,  # Відступ для рамки
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.setPixmap(scaled_pixmap)
            else:
                # Помилка завантаження
                self.setText(f"Помилка\n{os.path.basename(self.image_path)}")
                self.setFont(QFont("Arial", 10))
                
        except Exception as e:
            # Обробка виключень
            self.setText(f"Помилка\n{os.path.basename(self.image_path)}")
            self.setFont(QFont("Arial", 10))
            print(f"Помилка завантаження мініатюри {self.image_path}: {e}")
    
    def update_style(self):
        """Оновлення стилю залежно від стану"""
        if self.is_selected:
            # Обране зображення - синя товста рамка
            self.setStyleSheet("""
                QLabel {
                    border: 4px solid #007bff;
                    border-radius: 8px;
                    background-color: #e3f2fd;
                    padding: 2px;
                    margin: 2px;
                }
            """)
        elif self.is_processed:
            # Оброблене зображення - зелена рамка
            self.setStyleSheet("""
                QLabel {
                    border: 3px solid #28a745;
                    border-radius: 8px;
                    background-color: #d4f6d4;
                    padding: 2px;
                    margin: 2px;
                }
                QLabel:hover {
                    border: 3px solid #218838;
                    background-color: #c3e6cb;
                }
            """)
        else:
            # Звичайне зображення
            self.setStyleSheet("""
                QLabel {
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    background-color: white;
                    padding: 2px;
                    margin: 2px;
                }
                QLabel:hover {
                    border: 2px solid #6c757d;
                    background-color: #f8f9fa;
                }
            """)
    
    def set_processed(self, processed: bool):
        """Встановлення стану обробки"""
        self.is_processed = processed
        self.update_style()
    
    def set_selected(self, selected: bool):
        """Встановлення стану виділення"""
        self.is_selected = selected
        self.update_style()
    
    def mousePressEvent(self, event):
        """Обробка кліка миші"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path)


class ThumbnailContainer(QWidget):
    """
    Контейнер для вертикального списку мініатюр
    """
    
    def __init__(self, thumbnail_width: int = 240):
        super().__init__()
        
        self.thumbnail_width = thumbnail_width
        self.thumbnail_height = int(thumbnail_width * 0.75)  # Пропорції 4:3
        self.thumbnails: List[ThumbnailLabel] = []
        self.image_paths: List[str] = []
        
        # Основний layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(8)
        self.setLayout(self.layout)
        
        # Встановлення розміру контейнера
        self.setFixedWidth(thumbnail_width + 20)  # +20 для відступів
    
    def add_thumbnail(self, image_path: str) -> bool:
        """
        Додавання мініатюри до контейнера
        
        Args:
            image_path: Шлях до зображення
            
        Returns:
            True якщо додавання успішне
        """
        try:
            # Перевірка чи зображення вже є
            if image_path in self.image_paths:
                return False
            
            # Створення мініатюри
            thumbnail = ThumbnailLabel(
                image_path, 
                self.thumbnail_width - 20,  # Відступ для рамок
                self.thumbnail_height - 20
            )
            
            # Додавання до списків
            self.thumbnails.append(thumbnail)
            self.image_paths.append(image_path)
            self.layout.addWidget(thumbnail)
            
            # Оновлення висоти контейнера
            self.update_container_height()
            
            print(f"✓ Мініатюра додана: {os.path.basename(image_path)}")
            return True
            
        except Exception as e:
            print(f"✗ Помилка додавання мініатюри: {e}")
            return False
    
    def clear_thumbnails(self):
        """Очищення всіх мініатюр"""
        try:
            # Видалення всіх віджетів з layout
            while self.layout.count():
                child = self.layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Очищення списків
            self.thumbnails.clear()
            self.image_paths.clear()
            
            # Оновлення висоти
            self.update_container_height()
            
            print("✓ Всі мініатюри очищено")
            
        except Exception as e:
            print(f"✗ Помилка очищення мініатюр: {e}")
    
    def update_container_height(self):
        """Оновлення висоти контейнера"""
        thumbnail_count = len(self.thumbnails)
        if thumbnail_count == 0:
            new_height = 100  # Мінімальна висота
        else:
            new_height = thumbnail_count * (self.thumbnail_height + 8) + 20  # +8 spacing, +20 margins
        
        self.setMinimumHeight(new_height)
        self.resize(self.thumbnail_width + 20, new_height)
    
    def mark_as_processed(self, image_path: str):
        """Позначити зображення як оброблене"""
        try:
            if image_path in self.image_paths:
                index = self.image_paths.index(image_path)
                if index < len(self.thumbnails):
                    self.thumbnails[index].set_processed(True)
                    print(f"✓ Позначено як оброблене: {os.path.basename(image_path)}")
        except Exception as e:
            print(f"✗ Помилка позначення як оброблене: {e}")
    
    def mark_as_unprocessed(self, image_path: str):
        """Позначити зображення як необроблене"""
        try:
            if image_path in self.image_paths:
                index = self.image_paths.index(image_path)
                if index < len(self.thumbnails):
                    self.thumbnails[index].set_processed(False)
                    print(f"✓ Позначено як необроблене: {os.path.basename(image_path)}")
        except Exception as e:
            print(f"✗ Помилка позначення як необроблене: {e}")
    
    def set_selected_image(self, image_path: str):
        """Встановити обране зображення"""
        try:
            # Скидаємо виділення з всіх мініатюр
            for thumbnail in self.thumbnails:
                thumbnail.set_selected(False)
            
            # Встановлюємо виділення для обраного
            if image_path in self.image_paths:
                index = self.image_paths.index(image_path)
                if index < len(self.thumbnails):
                    self.thumbnails[index].set_selected(True)
                    print(f"✓ Обрано зображення: {os.path.basename(image_path)}")
        except Exception as e:
            print(f"✗ Помилка виділення зображення: {e}")
    
    def clear_all_processed_status(self):
        """Очистити стан обробки для всіх зображень"""
        try:
            for thumbnail in self.thumbnails:
                thumbnail.set_processed(False)
            print("✓ Стан обробки очищено для всіх зображень")
        except Exception as e:
            print(f"✗ Помилка очищення стану обробки: {e}")


class BrowserPanel(QWidget):
    """
    Панель браузера зображень з вертикальними мініатюрами
    
    Функціональність:
    - Відображення мініатюр зображень у вертикальному списку
    - Візуальні індикатори стану (оброблено/необроблено/обрано)
    - Прокручування для великої кількості зображень
    - Клік для вибору зображення
    """
    
    # Сигнали
    image_selected = pyqtSignal(str)  # Обране зображення
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Стан панелі
        self.current_images: List[str] = []
        self.processed_images: Set[str] = set()
        self.selected_image: Optional[str] = None
        
        # Налаштування панелі
        self.setFixedWidth(UI.BROWSER_PANEL_WIDTH)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                border-right: 1px solid #ccc;
                border-left: 1px solid #ccc;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 15, 0, 15)
        layout.setSpacing(10)
        self.setLayout(layout)
        
        # Заголовок браузера
        self.create_header(layout)
        
        # Область прокручування для мініатюр
        self.create_scroll_area(layout)
    
    def create_header(self, layout: QVBoxLayout):
        """Створення заголовку браузера"""
        header_label = QLabel("Перегляд зображень")
        header_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_label.setStyleSheet("""
            QLabel {
                color: #666;
                margin-bottom: 5px;
                padding: 0 10px;
                background: none;
                border: none;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
    
    def create_scroll_area(self, layout: QVBoxLayout):
        """Створення області прокручування"""
        # Scroll area для мініатюр
        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
        # Контейнер для мініатюр
        self.thumbnail_container = ThumbnailContainer(UI.BROWSER_PANEL_WIDTH - 20)
        self.scroll_area.setWidget(self.thumbnail_container)
        
        layout.addWidget(self.scroll_area)
        
        # Початкове повідомлення
        self.show_no_images_message()
    
    def show_no_images_message(self):
        """Показ повідомлення коли немає зображень"""
        no_images_label = QLabel("Немає зображень")
        no_images_label.setAlignment(Qt.AlignCenter)
        no_images_label.setStyleSheet("""
            QLabel {
                color: gray;
                font-size: 14px;
                padding: 20px;
                background: none;
                border: none;
            }
        """)
        no_images_label.setWordWrap(True)
        
        # Очищуємо контейнер та додаємо повідомлення
        self.thumbnail_container.clear_thumbnails()
        self.thumbnail_container.layout.addWidget(no_images_label)
    
    def load_images(self, image_paths: List[str]):
        """
        Завантаження списку зображень
        
        Args:
            image_paths: Список шляхів до зображень
        """
        try:
            print(f"🔄 Завантаження {len(image_paths)} зображень до браузера...")
            
            # Очищення попередніх мініатюр
            self.thumbnail_container.clear_thumbnails()
            
            # Фільтрація та валідація зображень
            valid_images = []
            for path in image_paths:
                if is_image_file(path) and os.path.exists(path):
                    valid_images.append(path)
                else:
                    print(f"⚠️ Пропуск невалідного файлу: {path}")
            
            if not valid_images:
                self.show_no_images_message()
                return
            
            # Створення мініатюр
            success_count = 0
            for image_path in valid_images:
                if self.thumbnail_container.add_thumbnail(image_path):
                    success_count += 1
                    
                    # Підключення сигналу кліка
                    thumbnail = self.thumbnail_container.thumbnails[-1]
                    thumbnail.clicked.connect(self.on_thumbnail_clicked)
            
            # Оновлення стану
            self.current_images = valid_images
            
            print(f"✅ Успішно завантажено {success_count}/{len(valid_images)} мініатюр")
            
        except Exception as e:
            print(f"✗ Помилка завантаження зображень: {e}")
            self.show_no_images_message()
    
    def on_thumbnail_clicked(self, image_path: str):
        """Обробка кліка по мініатюрі"""
        try:
            self.selected_image = image_path
            self.thumbnail_container.set_selected_image(image_path)
            self.image_selected.emit(image_path)
            
            print(f"🖱️ Обрано зображення: {os.path.basename(image_path)}")
            
        except Exception as e:
            print(f"✗ Помилка обробки кліка: {e}")
    
    def mark_image_as_processed(self, image_path: str):
        """Позначити зображення як оброблене"""
        self.processed_images.add(image_path)
        self.thumbnail_container.mark_as_processed(image_path)
    
    def mark_image_as_unprocessed(self, image_path: str):
        """Позначити зображення як необроблене"""
        self.processed_images.discard(image_path)
        self.thumbnail_container.mark_as_unprocessed(image_path)
    
    def set_selected_image(self, image_path: str):
        """Встановити обране зображення ззовні"""
        self.selected_image = image_path
        self.thumbnail_container.set_selected_image(image_path)
    
    def clear_all_processed_status(self):
        """Очистити стан обробки для всіх зображень"""
        self.processed_images.clear()
        self.thumbnail_container.clear_all_processed_status()
    
    def clear(self):
        """Повне очищення браузера"""
        try:
            self.current_images.clear()
            self.processed_images.clear()
            self.selected_image = None
            self.thumbnail_container.clear_thumbnails()
            self.show_no_images_message()
            
            print("✓ Браузер зображень очищено")
            
        except Exception as e:
            print(f"✗ Помилка очищення браузера: {e}")
    
    def get_processed_count(self) -> int:
        """Отримання кількості оброблених зображень"""
        return len(self.processed_images)
    
    def get_total_count(self) -> int:
        """Отримання загальної кількості зображень"""
        return len(self.current_images)