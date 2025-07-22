#!/usr/bin/env python3
"""
Панель браузера зображень з мініатюрами
Відображає список зображень з візуальними індикаторами статусу обробки
"""

import os
from typing import List, Optional, Set, Dict
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QLabel, 
                             QFrame, QPushButton, QSizePolicy, QHBoxLayout)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, pyqtSlot, QTimer
from PyQt5.QtGui import QPixmap, QFont, QPainter, QPen, QBrush, QColor

from core.constants import UI, IMAGE
from utils.file_utils import is_image_file


class ImageThumbnailWidget(QFrame):
    """
    Віджет мініатюри зображення з індикаторами статусу
    
    Статуси:
    - normal: звичайне зображення (сірий бордер)
    - selected: вибране зображення (синій бордер)
    - processed: оброблене зображення (зелений бордер)
    - error: помилка завантаження (червоний бордер)
    """
    
    clicked = pyqtSignal(str)  # Клік по мініатюрі
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        
        self.image_path = image_path
        self.filename = os.path.basename(image_path)
        self.status = 'normal'
        self.is_selected = False
        
        # Налаштування розмірів
        self.thumbnail_size = QSize(UI.THUMBNAIL_SIZE, UI.THUMBNAIL_SIZE)
        self.setFixedSize(UI.THUMBNAIL_WIDTH, UI.THUMBNAIL_HEIGHT)
        
        # Налаштування стилів
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        self.setCursor(Qt.PointingHandCursor)
        
        self.init_ui()
        self.update_style()
        
        # Асинхронне завантаження мініатюри
        QTimer.singleShot(0, self.load_thumbnail)
    
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        self.setLayout(layout)
        
        # Мініатюра зображення
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(self.thumbnail_size)
        self.image_label.setMaximumSize(self.thumbnail_size)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.image_label)
        
        # Назва файлу
        self.filename_label = QLabel(self.filename)
        self.filename_label.setFont(QFont("Arial", 8))
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.filename_label.setWordWrap(True)
        self.filename_label.setMaximumHeight(30)
        self.filename_label.setStyleSheet("""
            QLabel {
                color: #333;
                background: none;
                border: none;
                padding: 1px;
            }
        """)
        layout.addWidget(self.filename_label)
        
        # Індикатор статусу
        self.status_label = QLabel("●")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMaximumHeight(16)
        layout.addWidget(self.status_label)
    
    def load_thumbnail(self):
        """Завантаження мініатюри зображення"""
        try:
            if not os.path.exists(self.image_path):
                self.set_status('error')
                self.image_label.setText("Файл\nне знайдено")
                return
            
            # Завантаження зображення
            pixmap = QPixmap(self.image_path)
            
            if pixmap.isNull():
                self.set_status('error')
                self.image_label.setText("Помилка\nзавантаження")
                return
            
            # Масштабування зображення з збереженням пропорцій
            scaled_pixmap = pixmap.scaled(
                self.thumbnail_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            print(f"❌ Помилка завантаження мініатюри {self.filename}: {e}")
            self.set_status('error')
            self.image_label.setText("Помилка")
    
    def set_status(self, status: str):
        """Встановлення статусу мініатюри"""
        self.status = status
        self.update_style()
    
    def set_selected(self, selected: bool):
        """Встановлення стану вибору"""
        self.is_selected = selected
        self.update_style()
    
    def update_style(self):
        """Оновлення стилів в залежності від статусу"""
        # Кольори бордерів
        border_colors = {
            'normal': '#dee2e6',
            'selected': '#007bff',
            'processed': '#28a745',
            'error': '#dc3545'
        }
        
        # Кольори індикаторів
        indicator_colors = {
            'normal': '#6c757d',
            'selected': '#007bff',
            'processed': '#28a745',
            'error': '#dc3545'
        }
        
        # Отримання кольорів
        border_color = border_colors.get(self.status, '#dee2e6')
        indicator_color = indicator_colors.get(self.status, '#6c757d')
        
        # Якщо вибрано, використовуємо синій колір
        if self.is_selected:
            border_color = border_colors['selected']
            indicator_color = indicator_colors['selected']
        
        # Застосування стилів
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {border_color};
                border-radius: 6px;
                background-color: white;
            }}
            QFrame:hover {{
                border: 2px solid {indicator_color};
                background-color: #f8f9fa;
            }}
        """)
        
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {indicator_color};
                background: none;
                border: none;
            }}
        """)
    
    def mousePressEvent(self, event):
        """Обробка кліка по мініатюрі"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path)
        super().mousePressEvent(event)


class BrowserPanel(QWidget):
    """
    Панель браузера зображень
    
    Функціональність:
    - Відображення мініатюр зображень з папки
    - Візуальні індикатори статусу обробки
    - Вибір зображення для роботи
    - Швидка навігація між зображеннями
    """
    
    # Сигнали для зв'язку з головним вікном
    image_selected = pyqtSignal(str)  # Вибране зображення
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Стан панелі
        self.current_images: List[str] = []
        self.processed_images: Set[str] = set()
        self.selected_image: Optional[str] = None
        self.thumbnail_widgets: Dict[str, ImageThumbnailWidget] = {}
        
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
        
        # Панель інформації
        self.create_info_panel(layout)
    
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
        self.scroll_area.setWidgetResizable(True)
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
        self.thumbnails_container = QWidget()
        self.thumbnails_layout = QVBoxLayout()
        self.thumbnails_layout.setContentsMargins(5, 5, 5, 5)
        self.thumbnails_layout.setSpacing(8)
        self.thumbnails_layout.setAlignment(Qt.AlignTop)
        self.thumbnails_container.setLayout(self.thumbnails_layout)
        
        self.scroll_area.setWidget(self.thumbnails_container)
        layout.addWidget(self.scroll_area)
    
    def create_info_panel(self, layout: QVBoxLayout):
        """Створення панелі інформації"""
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        info_frame.setMaximumHeight(80)
        
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(8, 8, 8, 8)
        info_layout.setSpacing(4)
        info_frame.setLayout(info_layout)
        
        # Загальна кількість
        self.total_label = QLabel("Всього: 0")
        self.total_label.setFont(QFont("Arial", 9))
        self.total_label.setStyleSheet("color: #666; background: none; border: none;")
        info_layout.addWidget(self.total_label)
        
        # Оброблені
        self.processed_label = QLabel("Оброблено: 0")
        self.processed_label.setFont(QFont("Arial", 9))
        self.processed_label.setStyleSheet("color: #28a745; background: none; border: none;")
        info_layout.addWidget(self.processed_label)
        
        # Залишилось
        self.remaining_label = QLabel("Залишилось: 0")
        self.remaining_label.setFont(QFont("Arial", 9))
        self.remaining_label.setStyleSheet("color: #dc3545; background: none; border: none;")
        info_layout.addWidget(self.remaining_label)
        
        layout.addWidget(info_frame)
    
    def load_images(self, image_paths: List[str]):
        """
        Завантаження списку зображень
        
        Args:
            image_paths: Список шляхів до зображень
        """
        # Очищення попередніх мініатюр
        self.clear_thumbnails()
        
        # Збереження списку
        self.current_images = image_paths.copy()
        
        # Створення мініатюр
        for image_path in image_paths:
            self.add_thumbnail(image_path)
        
        # Оновлення інформації
        self.update_info_panel()
        
        print(f"✅ Завантажено {len(image_paths)} зображень в браузер")
    
    def add_thumbnail(self, image_path: str):
        """Додавання мініатюри зображення"""
        # Створення віджета мініатюри
        thumbnail = ImageThumbnailWidget(image_path, self)
        thumbnail.clicked.connect(self.on_thumbnail_clicked)
        
        # Додавання до layout
        self.thumbnails_layout.addWidget(thumbnail)
        
        # Збереження посилання
        self.thumbnail_widgets[image_path] = thumbnail
    
    def clear_thumbnails(self):
        """Очищення всіх мініатюр"""
        # Видалення віджетів з layout
        for i in reversed(range(self.thumbnails_layout.count())):
            child = self.thumbnails_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Очищення словника
        self.thumbnail_widgets.clear()
        self.current_images.clear()
        self.selected_image = None
        
        # Оновлення інформації
        self.update_info_panel()
    
    def on_thumbnail_clicked(self, image_path: str):
        """Обробка кліка по мініатюрі"""
        # Зняття виділення з попередньої мініатюри
        if self.selected_image and self.selected_image in self.thumbnail_widgets:
            self.thumbnail_widgets[self.selected_image].set_selected(False)
        
        # Встановлення нового виділення
        self.selected_image = image_path
        if image_path in self.thumbnail_widgets:
            self.thumbnail_widgets[image_path].set_selected(True)
        
        # Сигнал про вибір зображення
        self.image_selected.emit(image_path)
        
        print(f"🖼️ Вибрано зображення: {os.path.basename(image_path)}")
    
    def mark_as_processed(self, image_path: str):
        """Позначення зображення як обробленого"""
        if image_path not in self.processed_images:
            self.processed_images.add(image_path)
            
            # Оновлення стилю мініатюри
            if image_path in self.thumbnail_widgets:
                thumbnail = self.thumbnail_widgets[image_path]
                if not thumbnail.is_selected:  # Не змінюємо колір якщо вибрано
                    thumbnail.set_status('processed')
            
            # Оновлення інформації
            self.update_info_panel()
            
            print(f"✅ Зображення позначено як оброблене: {os.path.basename(image_path)}")
    
    def mark_as_unprocessed(self, image_path: str):
        """Зняття позначки обробки з зображення"""
        if image_path in self.processed_images:
            self.processed_images.remove(image_path)
            
            # Оновлення стилю мініатюри
            if image_path in self.thumbnail_widgets:
                thumbnail = self.thumbnail_widgets[image_path]
                if not thumbnail.is_selected:  # Не змінюємо колір якщо вибрано
                    thumbnail.set_status('normal')
            
            # Оновлення інформації
            self.update_info_panel()
            
            print(f"↩️ З зображення знято позначку обробки: {os.path.basename(image_path)}")
    
    def get_next_image(self) -> Optional[str]:
        """Отримання наступного зображення в списку"""
        if not self.current_images or not self.selected_image:
            return None
        
        try:
            current_index = self.current_images.index(self.selected_image)
            if current_index < len(self.current_images) - 1:
                return self.current_images[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def get_previous_image(self) -> Optional[str]:
        """Отримання попереднього зображення в списку"""
        if not self.current_images or not self.selected_image:
            return None
        
        try:
            current_index = self.current_images.index(self.selected_image)
            if current_index > 0:
                return self.current_images[current_index - 1]
        except ValueError:
            pass
        
        return None
    
    def select_next_image(self):
        """Вибір наступного зображення"""
        next_image = self.get_next_image()
        if next_image:
            self.on_thumbnail_clicked(next_image)
    
    def select_previous_image(self):
        """Вибір попереднього зображення"""
        previous_image = self.get_previous_image()
        if previous_image:
            self.on_thumbnail_clicked(previous_image)
    
    def update_info_panel(self):
        """Оновлення панелі інформації"""
        total_count = len(self.current_images)
        processed_count = len(self.processed_images)
        remaining_count = total_count - processed_count
        
        self.total_label.setText(f"Всього: {total_count}")
        self.processed_label.setText(f"Оброблено: {processed_count}")
        self.remaining_label.setText(f"Залишилось: {remaining_count}")
    
    def scroll_to_selected(self):
        """Прокручування до вибраного зображення"""
        if self.selected_image and self.selected_image in self.thumbnail_widgets:
            widget = self.thumbnail_widgets[self.selected_image]
            self.scroll_area.ensureWidgetVisible(widget)
    
    def get_processed_images(self) -> List[str]:
        """Отримання списку оброблених зображень"""
        return list(self.processed_images)
    
    def get_unprocessed_images(self) -> List[str]:
        """Отримання списку необроблених зображень"""
        return [img for img in self.current_images if img not in self.processed_images]
    
    def clear_processed_status(self):
        """Очищення статусу обробки всіх зображень"""
        self.processed_images.clear()
        
        # Оновлення всіх мініатюр
        for thumbnail in self.thumbnail_widgets.values():
            if not thumbnail.is_selected:
                thumbnail.set_status('normal')
        
        self.update_info_panel()
        print("🔄 Статус обробки всіх зображень очищено")


# ===== ТЕСТУВАННЯ МОДУЛЯ =====

if __name__ == "__main__":
    print("=== Тестування BrowserPanel ===")
    print("Модуль BrowserPanel готовий до використання")