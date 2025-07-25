#!/usr/bin/env python3
"""
Браузер мініатюр з візуальними індикаторами обробки
Вертикальний віджет для перегляду та навігації по зображеннях в папці
"""

import os
from typing import List, Optional, Set
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QLabel, 
                             QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont
from PIL import Image
from PIL.ImageQt import ImageQt


class ThumbnailItem(QLabel):
    """
    Окремий елемент мініатюри з індикатором стану обробки
    
    Функціональність:
    - Відображення мініатюри зображення
    - Візуальний індикатор обробки (зелена галочка)
    - Індикатор обраного зображення (синя рамка)
    - Клік для вибору зображення
    - Hover ефекти
    """
    
    clicked = pyqtSignal(str)  # Сигнал з шляхом до зображення
    
    def __init__(self, image_path: str, width: int = 240, height: int = 180, parent=None):
        super().__init__(parent)
        
        # Основні властивості
        self.image_path = image_path
        self.image_name = os.path.basename(image_path)
        self.thumbnail_width = width
        self.thumbnail_height = height
        
        # Стан мініатюри
        self.is_processed = False
        self.is_selected = False
        self.is_hovered = False
        
        # Налаштування віджету
        self._setup_widget()
        self._load_thumbnail()
    
    def _setup_widget(self):
        """Налаштування основних властивостей віджету"""
        # Розміри
        self.setFixedSize(self.thumbnail_width, self.thumbnail_height + 30)  # +30 для тексту
        
        # Стилі та поведінка
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(self._get_base_style())
        
        # Курсор
        self.setCursor(Qt.PointingHandCursor)
        
        # Включаємо відстеження миші для hover ефектів
        self.setMouseTracking(True)
    
    def _get_base_style(self) -> str:
        """Базові стилі для мініатюри"""
        return """
            ThumbnailItem {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
                margin: 2px;
                padding: 4px;
            }
            ThumbnailItem:hover {
                border-color: #007ACC;
                background-color: #f8f9fa;
            }
        """
    
    def _load_thumbnail(self):
        """Завантаження та створення мініатюри зображення"""
        try:
            # Завантаження оригінального зображення
            with Image.open(self.image_path) as image:
                # Конвертація в RGB якщо потрібно
                if image.mode != 'RGB':
                    if image.mode == 'RGBA':
                        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                        rgb_image.paste(image, mask=image.split()[-1])
                        image = rgb_image
                    else:
                        image = image.convert('RGB')
                
                # Створення мініатюри зі збереженням пропорцій
                thumbnail = self._create_proportional_thumbnail(image)
                
                # Конвертація в QPixmap
                qt_image = ImageQt(thumbnail)
                pixmap = QPixmap.fromImage(qt_image)
                
                # Встановлення як базової мініатюри
                self.base_pixmap = pixmap
                self.setPixmap(pixmap)
                
                print(f"Мініатюра створена: {self.image_name}")
        
        except Exception as e:
            print(f"Помилка створення мініатюри для {self.image_name}: {e}")
            self._create_error_thumbnail()
    
    def _create_proportional_thumbnail(self, image: Image.Image) -> Image.Image:
        """
        Створення мініатюри зі збереженням пропорцій та центруванням
        
        Args:
            image: Оригінальне зображення
            
        Returns:
            PIL Image мініатюри
        """
        # Розрахунок розмірів для збереження пропорцій
        original_width, original_height = image.size
        target_width = self.thumbnail_width - 8  # Відступи
        target_height = self.thumbnail_height - 28  # Відступи + місце для тексту
        
        # Розрахунок масштабу
        scale_x = target_width / original_width
        scale_y = target_height / original_height
        scale = min(scale_x, scale_y)
        
        # Нові розміри
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # Зміна розміру з високою якістю
        thumbnail = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Створення фінальної мініатюри з центруванням на білому фоні
        final_thumbnail = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        
        # Розрахунок позиції для центрування
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        
        final_thumbnail.paste(thumbnail, (paste_x, paste_y))
        
        return final_thumbnail
    
    def _create_error_thumbnail(self):
        """Створення мініатюри для помилки завантаження"""
        # Створюємо сірий квадрат з текстом помилки
        error_image = Image.new('RGB', 
                               (self.thumbnail_width - 8, self.thumbnail_height - 28), 
                               (200, 200, 200))
        
        qt_image = ImageQt(error_image)
        pixmap = QPixmap.fromImage(qt_image)
        
        self.base_pixmap = pixmap
        self.setPixmap(pixmap)
    
    def paintEvent(self, event):
        """Перемалювання з додатковими елементами"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        try:
            # Малювання рамки обраного елементу
            if self.is_selected:
                self._draw_selection_border(painter)
            
            # Малювання індикатора обробки
            if self.is_processed:
                self._draw_processed_indicator(painter)
            
            # Малювання назви файлу
            self._draw_filename(painter)
        
        finally:
            painter.end()
    
    def _draw_selection_border(self, painter: QPainter):
        """Малювання рамки для обраного елементу"""
        # Синя рамка
        painter.setPen(QPen(QColor(0, 123, 255), 3))
        painter.drawRect(1, 1, self.width() - 3, self.height() - 3)
        
        # Напівпрозорий синій фон
        painter.setBrush(QBrush(QColor(0, 123, 255, 30)))
        painter.drawRect(1, 1, self.width() - 3, self.height() - 3)
    
    def _draw_processed_indicator(self, painter: QPainter):
        """Малювання індикатора обробленого зображення"""
        # Зелене коло в правому верхньому куті
        circle_size = 24
        circle_x = self.width() - circle_size - 8
        circle_y = 8
        
        # Фон кола
        painter.setBrush(QBrush(QColor(40, 167, 69)))
        painter.setPen(QPen(QColor(33, 136, 56), 2))
        painter.drawEllipse(circle_x, circle_y, circle_size, circle_size)
        
        # Біла галочка
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        check_points = [
            (circle_x + 6, circle_y + 12),
            (circle_x + 10, circle_y + 16),
            (circle_x + 18, circle_y + 8)
        ]
        
        # Малюємо галочку лініями
        painter.drawLine(check_points[0][0], check_points[0][1],
                        check_points[1][0], check_points[1][1])
        painter.drawLine(check_points[1][0], check_points[1][1],
                        check_points[2][0], check_points[2][1])
    
    def _draw_filename(self, painter: QPainter):
        """Малювання назви файлу внизу мініатюри"""
        # Налаштування шрифту
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        # Колір тексту
        if self.is_selected:
            text_color = QColor(0, 123, 255)
        else:
            text_color = QColor(68, 68, 68)
        
        painter.setPen(QPen(text_color))
        
        # Область для тексту
        text_rect = self.rect()
        text_rect.setTop(self.thumbnail_height - 22)
        text_rect.setBottom(self.height() - 4)
        
        # Скорочення назви файлу якщо потрібно
        metrics = painter.fontMetrics()
        available_width = text_rect.width() - 8
        elided_text = metrics.elidedText(self.image_name, Qt.ElideMiddle, available_width)
        
        # Малювання тексту
        painter.drawText(text_rect, Qt.AlignCenter, elided_text)
    
    def mousePressEvent(self, event):
        """Обробка кліку на мініатюрі"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path)
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """Обробка входу миші (hover)"""
        self.is_hovered = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Обробка виходу миші"""
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)
    
    # ===============================
    # ПУБЛІЧНІ МЕТОДИ
    # ===============================
    
    def mark_as_processed(self):
        """Позначити зображення як оброблене"""
        if not self.is_processed:
            self.is_processed = True
            self.update()
            print(f"Мініатюра позначена як оброблена: {self.image_name}")
    
    def mark_as_unprocessed(self):
        """Позначити зображення як необроблене"""
        if self.is_processed:
            self.is_processed = False
            self.update()
            print(f"Мініатюра позначена як необроблена: {self.image_name}")
    
    def set_selected(self, selected: bool):
        """Встановити стан обраності"""
        if self.is_selected != selected:
            self.is_selected = selected
            self.update()
    
    def get_image_path(self) -> str:
        """Отримати шлях до зображення"""
        return self.image_path
    
    def get_image_name(self) -> str:
        """Отримати назву файлу"""
        return self.image_name
    
    def is_image_processed(self) -> bool:
        """Перевірити чи зображення оброблене"""
        return self.is_processed


class ThumbnailBrowser(QWidget):
    """
    Браузер мініатюр з вертикальним прокручуванням
    
    Функціональність:
    - Вертикальне розташування мініатюр
    - Прокручування для великої кількості зображень
    - Відстеження обраного зображення
    - Масове позначення як оброблені/необроблені
    - Фільтрація за статусом обробки
    - Завантаження мініатюр у фоновому режимі
    """
    
    # Сигнали
    image_selected = pyqtSignal(str)      # Обране нове зображення
    processing_status_changed = pyqtSignal(str, bool)  # Зміна статусу обробки
    
    def __init__(self, width: int = 280, parent=None):
        super().__init__(parent)
        
        # Основні властивості
        self.thumbnail_width = width - 40  # Відступи для скролбару
        self.thumbnail_height = int(self.thumbnail_width * 0.75)  # Співвідношення 4:3
        
        # Дані
        self.image_paths: List[str] = []
        self.thumbnail_items: List[ThumbnailItem] = []
        self.processed_images: Set[str] = set()
        self.selected_image_path: Optional[str] = None
        
        # Налаштування віджету
        self.setFixedWidth(width)
        self._setup_layout()
        
        # Таймер для фонового завантаження
        self.loading_timer = QTimer()
        self.loading_timer.setSingleShot(True)
        self.loading_timer.timeout.connect(self._load_next_thumbnail)
        self.loading_queue: List[str] = []
        self.loading_index = 0
    
    def _setup_layout(self):
        """Налаштування макету віджету"""
        # Основний layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        # Область прокручування
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                background-color: #f1f1f1;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8a8a8;
            }
        """)
        main_layout.addWidget(self.scroll_area)
        
        # Контейнер для мініатюр
        self.thumbnails_widget = QWidget()
        self.thumbnails_layout = QVBoxLayout()
        self.thumbnails_layout.setContentsMargins(5, 5, 5, 5)
        self.thumbnails_layout.setSpacing(8)
        self.thumbnails_layout.setAlignment(Qt.AlignTop)
        self.thumbnails_widget.setLayout(self.thumbnails_layout)
        
        self.scroll_area.setWidget(self.thumbnails_widget)
        
        # Початковий стан
        self._show_empty_state()
    
    def _show_empty_state(self):
        """Відображення пустого стану"""
        empty_label = QLabel("Зображення не завантажено")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 40px 20px;
                background-color: transparent;
            }
        """)
        self.thumbnails_layout.addWidget(empty_label)
    
    # ===============================
    # ЗАВАНТАЖЕННЯ ЗОБРАЖЕНЬ
    # ===============================
    
    def load_images(self, image_paths: List[str]):
        """
        Завантаження списку зображень для відображення
        
        Args:
            image_paths: Список шляхів до зображень
        """
        print(f"Завантаження {len(image_paths)} зображень...")
        
        # Очищення поточного вмісту
        self.clear_thumbnails()
        
        if not image_paths:
            self._show_empty_state()
            return
        
        # Збереження списку зображень
        self.image_paths = image_paths.copy()
        self.loading_queue = image_paths.copy()
        self.loading_index = 0
        
        # Початок фонового завантаження
        self._start_background_loading()
    
    def _start_background_loading(self):
        """Початок фонового завантаження мініатюр"""
        if self.loading_queue:
            print("Початок фонового завантаження мініатюр...")
            self.loading_timer.start(50)  # 50мс затримка між завантаженнями
    
    def _load_next_thumbnail(self):
        """Завантаження наступної мініатюри у фоновому режимі"""
        if self.loading_index < len(self.loading_queue):
            image_path = self.loading_queue[self.loading_index]
            self._create_and_add_thumbnail(image_path)
            self.loading_index += 1
            
            # Продовження завантаження
            if self.loading_index < len(self.loading_queue):
                self.loading_timer.start(50)
            else:
                print(f"Завантаження завершено: {len(self.thumbnail_items)} мініатюр")
                self._finalize_loading()
    
    def _create_and_add_thumbnail(self, image_path: str):
        """
        Створення та додавання окремої мініатюри
        
        Args:
            image_path: Шлях до зображення
        """
        try:
            # Створення мініатюри
            thumbnail_item = ThumbnailItem(
                image_path, 
                self.thumbnail_width, 
                self.thumbnail_height
            )
            
            # Встановлення статусу обробки
            if image_path in self.processed_images:
                thumbnail_item.mark_as_processed()
            
            # Підключення сигналів
            thumbnail_item.clicked.connect(self._on_thumbnail_clicked)
            
            # Додавання до layout
            self.thumbnails_layout.addWidget(thumbnail_item)
            self.thumbnail_items.append(thumbnail_item)
            
            # Оновлення розмірів контейнера
            self._update_container_size()
            
        except Exception as e:
            print(f"Помилка створення мініатюри {os.path.basename(image_path)}: {e}")
    
    def _finalize_loading(self):
        """Завершення процесу завантаження"""
        # Додавання еластичного простору в кінці
        self.thumbnails_layout.addStretch()
        
        # Автоматичний вибір першого зображення якщо немає вибору
        if self.thumbnail_items and not self.selected_image_path:
            first_item = self.thumbnail_items[0]
            self.select_image(first_item.get_image_path())
    
    def _update_container_size(self):
        """Оновлення розміру контейнера для правильного прокручування"""
        if self.thumbnail_items:
            # Розрахунок необхідної висоти
            item_height = self.thumbnail_height + 38  # +38 для тексту та відступів
            total_height = len(self.thumbnail_items) * item_height + 20
            
            self.thumbnails_widget.setMinimumHeight(total_height)
    
    # ===============================
    # УПРАВЛІННЯ ВИБОРОМ
    # ===============================
    
    def select_image(self, image_path: str):
        """
        Вибір зображення за шляхом
        
        Args:
            image_path: Шлях до зображення для вибору
        """
        if image_path == self.selected_image_path:
            return
        
        # Скидання попереднього вибору
        if self.selected_image_path:
            self._set_item_selected(self.selected_image_path, False)
        
        # Встановлення нового вибору
        self.selected_image_path = image_path
        self._set_item_selected(image_path, True)
        
        # Прокручування до обраного елементу
        self._scroll_to_selected()
        
        print(f"Обрано зображення: {os.path.basename(image_path)}")
    
    def _on_thumbnail_clicked(self, image_path: str):
        """Обробка кліку на мініатюрі"""
        self.select_image(image_path)
        self.image_selected.emit(image_path)
    
    def _set_item_selected(self, image_path: str, selected: bool):
        """Встановлення стану вибору для конкретної мініатюри"""
        for item in self.thumbnail_items:
            if item.get_image_path() == image_path:
                item.set_selected(selected)
                break
    
    def _scroll_to_selected(self):
        """Прокручування до обраного елементу"""
        if not self.selected_image_path:
            return
        
        # Знаходимо індекс обраного елементу
        selected_index = -1
        for i, item in enumerate(self.thumbnail_items):
            if item.get_image_path() == self.selected_image_path:
                selected_index = i
                break
        
        if selected_index >= 0:
            # Розрахунок позиції для прокручування
            item_height = self.thumbnail_height + 38
            scroll_position = selected_index * item_height
            
            # Прокручування з урахуванням видимої області
            scroll_bar = self.scroll_area.verticalScrollBar()
            visible_height = self.scroll_area.height()
            
            # Центрування обраного елементу
            center_position = scroll_position - (visible_height // 2) + (item_height // 2)
            scroll_bar.setValue(max(0, center_position))
    
    # ===============================
    # УПРАВЛІННЯ СТАТУСОМ ОБРОБКИ
    # ===============================
    
    def mark_image_as_processed(self, image_path: str):
        """
        Позначити зображення як оброблене
        
        Args:
            image_path: Шлях до зображення
        """
        if image_path not in self.processed_images:
            self.processed_images.add(image_path)
            
            # Оновлення мініатюри
            for item in self.thumbnail_items:
                if item.get_image_path() == image_path:
                    item.mark_as_processed()
                    break
            
            self.processing_status_changed.emit(image_path, True)
            print(f"Зображення позначено як оброблене: {os.path.basename(image_path)}")
    
    def mark_image_as_unprocessed(self, image_path: str):
        """
        Позначити зображення як необроблене
        
        Args:
            image_path: Шлях до зображення
        """
        if image_path in self.processed_images:
            self.processed_images.discard(image_path)
            
            # Оновлення мініатюри
            for item in self.thumbnail_items:
                if item.get_image_path() == image_path:
                    item.mark_as_unprocessed()
                    break
            
            self.processing_status_changed.emit(image_path, False)
            print(f"Зображення позначено як необроблене: {os.path.basename(image_path)}")
    
    def clear_all_processed_status(self):
        """Очистити статус обробки для всіх зображень"""
        print("Очищення статусу обробки для всіх зображень...")
        
        # Очищення набору оброблених
        self.processed_images.clear()
        
        # Оновлення всіх мініатюр
        for item in self.thumbnail_items:
            item.mark_as_unprocessed()
        
        print("Статус обробки очищено для всіх зображень")
    
    def get_processed_images(self) -> List[str]:
        """Отримати список оброблених зображень"""
        return list(self.processed_images)
    
    def get_unprocessed_images(self) -> List[str]:
        """Отримати список необроблених зображень"""
        return [path for path in self.image_paths if path not in self.processed_images]
    
    # ===============================
    # НАВІГАЦІЯ
    # ===============================
    
    def select_next_image(self) -> Optional[str]:
        """
        Вибір наступного зображення
        
        Returns:
            Шлях до наступного зображення або None
        """
        if not self.image_paths or not self.selected_image_path:
            return None
        
        try:
            current_index = self.image_paths.index(self.selected_image_path)
            next_index = (current_index + 1) % len(self.image_paths)
            next_image = self.image_paths[next_index]
            
            self.select_image(next_image)
            self.image_selected.emit(next_image)
            
            return next_image
        except ValueError:
            return None
    
    def select_previous_image(self) -> Optional[str]:
        """
        Вибір попереднього зображення
        
        Returns:
            Шлях до попереднього зображення або None
        """
        if not self.image_paths or not self.selected_image_path:
            return None
        
        try:
            current_index = self.image_paths.index(self.selected_image_path)
            prev_index = (current_index - 1) % len(self.image_paths)
            prev_image = self.image_paths[prev_index]
            
            self.select_image(prev_image)
            self.image_selected.emit(prev_image)
            
            return prev_image
        except ValueError:
            return None
    
    def get_current_image_index(self) -> int:
        """Отримати індекс поточного зображення"""
        if not self.selected_image_path or not self.image_paths:
            return -1
        
        try:
            return self.image_paths.index(self.selected_image_path)
        except ValueError:
            return -1
    
    def get_total_images_count(self) -> int:
        """Отримати загальна кількість зображень"""
        return len(self.image_paths)
    
    # ===============================
    # ОЧИЩЕННЯ ТА УТИЛІТИ
    # ===============================
    
    def clear_thumbnails(self):
        """Очищення всіх мініатюр"""
        print("Очищення мініатюр...")
        
        # Зупинка завантаження
        self.loading_timer.stop()
        self.loading_queue.clear()
        self.loading_index = 0
        
        # Видалення всіх віджетів
        while self.thumbnails_layout.count():
            child = self.thumbnails_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Очищення списків
        self.thumbnail_items.clear()
        self.image_paths.clear()
        self.selected_image_path = None
        
        print("Мініатюри очищено")
    
    def get_browser_info(self) -> dict:
        """Отримання інформації про браузер"""
        return {
            'total_images': len(self.image_paths),
            'processed_images': len(self.processed_images),
            'unprocessed_images': len(self.image_paths) - len(self.processed_images),
            'selected_image': self.selected_image_path,
            'current_index': self.get_current_image_index(),
            'thumbnails_loaded': len(self.thumbnail_items),
            'is_loading': self.loading_timer.isActive()
        }
    
    def refresh_thumbnails(self):
        """Оновлення всіх мініатюр"""
        if self.image_paths:
            current_selection = self.selected_image_path
            processed_backup = self.processed_images.copy()
            
            self.load_images(self.image_paths)
            
            # Відновлення статусу обробки
            self.processed_images = processed_backup
            
            # Відновлення вибору
            if current_selection and current_selection in self.image_paths:
                # Затримка для завершення завантаження
                QTimer.singleShot(100, lambda: self.select_image(current_selection))
    
    def is_empty(self) -> bool:
        """Перевірка чи браузер порожній"""
        return len(self.image_paths) == 0
    
    def has_selected_image(self) -> bool:
        """Перевірка чи є обране зображення"""
        return self.selected_image_path is not None
    
    def get_selected_image(self) -> Optional[str]:
        """Отримання шляху до обраного зображення"""
        return self.selected_image_path


if __name__ == "__main__":
    # Тестування браузера мініатюр
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QPushButton
    from PIL import Image, ImageDraw
    import tempfile
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Тест ThumbnailBrowser")
            self.setGeometry(100, 100, 1200, 800)
            
            # Центральний віджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QHBoxLayout(central_widget)
            
            # Браузер мініатюр
            self.thumbnail_browser = ThumbnailBrowser(width=300)
            layout.addWidget(self.thumbnail_browser)
            
            # Панель управління
            control_panel = self.create_control_panel()
            layout.addWidget(control_panel)
            
            # Підключення сигналів
            self.thumbnail_browser.image_selected.connect(self.on_image_selected)
            self.thumbnail_browser.processing_status_changed.connect(self.on_status_changed)
            
            # Створення тестових зображень
            self.test_images = self.create_test_images()
            
            print("Тестове вікно ThumbnailBrowser створено")
            print(f"Створено {len(self.test_images)} тестових зображень")
        
        def create_control_panel(self):
            """Створення панелі управління для тестування"""
            panel = QWidget()
            layout = QVBoxLayout(panel)
            
            # Кнопки управління
            load_btn = QPushButton("Завантажити тестові зображення")
            load_btn.clicked.connect(self.load_test_images)
            layout.addWidget(load_btn)
            
            next_btn = QPushButton("Наступне зображення")
            next_btn.clicked.connect(self.thumbnail_browser.select_next_image)
            layout.addWidget(next_btn)
            
            prev_btn = QPushButton("Попереднє зображення")
            prev_btn.clicked.connect(self.thumbnail_browser.select_previous_image)
            layout.addWidget(prev_btn)
            
            mark_processed_btn = QPushButton("Позначити як оброблене")
            mark_processed_btn.clicked.connect(self.mark_current_as_processed)
            layout.addWidget(mark_processed_btn)
            
            mark_unprocessed_btn = QPushButton("Позначити як необроблене")
            mark_unprocessed_btn.clicked.connect(self.mark_current_as_unprocessed)
            layout.addWidget(mark_unprocessed_btn)
            
            clear_all_btn = QPushButton("Очистити всі статуси")
            clear_all_btn.clicked.connect(self.thumbnail_browser.clear_all_processed_status)
            layout.addWidget(clear_all_btn)
            
            refresh_btn = QPushButton("Оновити мініатюри")
            refresh_btn.clicked.connect(self.thumbnail_browser.refresh_thumbnails)
            layout.addWidget(refresh_btn)
            
            clear_btn = QPushButton("Очистити браузер")
            clear_btn.clicked.connect(self.thumbnail_browser.clear_thumbnails)
            layout.addWidget(clear_btn)
            
            # Інформаційна панель
            info_label = QLabel("Інформація про браузер:")
            info_label.setFont(QFont("Arial", 10, QFont.Bold))
            layout.addWidget(info_label)
            
            self.info_text = QLabel()
            self.info_text.setStyleSheet("""
                QLabel {
                    border: 1px solid #ccc;
                    padding: 8px;
                    background-color: #f9f9f9;
                    font-family: 'Courier New', monospace;
                    font-size: 9px;
                }
            """)
            self.info_text.setWordWrap(True)
            layout.addWidget(self.info_text)
            
            layout.addStretch()
            
            # Оновлення інформації кожні 500мс
            self.info_timer = QTimer()
            self.info_timer.timeout.connect(self.update_info)
            self.info_timer.start(500)
            
            return panel
        
        def create_test_images(self):
            """Створення тестових зображень"""
            test_images = []
            temp_dir = tempfile.mkdtemp(prefix="thumbnail_test_")
            
            colors = [
                (255, 100, 100, "Червоний"),
                (100, 255, 100, "Зелений"),
                (100, 100, 255, "Синій"),
                (255, 255, 100, "Жовтий"),
                (255, 100, 255, "Магента"),
                (100, 255, 255, "Бірюзовий"),
                (255, 150, 100, "Помаранчевий"),
                (150, 100, 255, "Фіолетовий"),
                (200, 200, 200, "Сірий"),
                (255, 200, 150, "Персиковий")
            ]
            
            for i, (r, g, b, name) in enumerate(colors):
                # Створення зображення
                width, height = 400, 300
                image = Image.new('RGB', (width, height), (r, g, b))
                draw = ImageDraw.Draw(image)
                
                # Додавання тексту та геометричних фігур
                draw.rectangle([50, 50, width-50, height-50], outline=(0, 0, 0), width=3)
                draw.ellipse([100, 100, width-100, height-100], outline=(255, 255, 255), width=2)
                
                # Номер зображення
                draw.text((20, 20), f"#{i+1:02d}", fill=(255, 255, 255))
                draw.text((20, height-40), name, fill=(255, 255, 255))
                
                # Збереження
                file_path = os.path.join(temp_dir, f"test_image_{i+1:02d}_{name.lower()}.jpg")
                image.save(file_path, 'JPEG', quality=85)
                test_images.append(file_path)
            
            print(f"Тестові зображення створено в: {temp_dir}")
            return test_images
        
        def load_test_images(self):
            """Завантаження тестових зображень в браузер"""
            self.thumbnail_browser.load_images(self.test_images)
            print("Тестові зображення завантажено")
        
        def mark_current_as_processed(self):
            """Позначити поточне зображення як оброблене"""
            current = self.thumbnail_browser.get_selected_image()
            if current:
                self.thumbnail_browser.mark_image_as_processed(current)
        
        def mark_current_as_unprocessed(self):
            """Позначити поточне зображення як необроблене"""
            current = self.thumbnail_browser.get_selected_image()
            if current:
                self.thumbnail_browser.mark_image_as_unprocessed(current)
        
        def on_image_selected(self, image_path):
            """Обробка вибору зображення"""
            print(f"Обрано зображення: {os.path.basename(image_path)}")
        
        def on_status_changed(self, image_path, is_processed):
            """Обробка зміни статусу обробки"""
            status = "оброблене" if is_processed else "необроблене"
            print(f"Статус змінено - {os.path.basename(image_path)}: {status}")
        
        def update_info(self):
            """Оновлення інформаційної панелі"""
            info = self.thumbnail_browser.get_browser_info()
            
            current_name = "Немає"
            if info['selected_image']:
                current_name = os.path.basename(info['selected_image'])
            
            info_text = f"""
📊 Статистика браузера:
• Всього зображень: {info['total_images']}
• Оброблено: {info['processed_images']}
• Не оброблено: {info['unprocessed_images']}
• Мініатюр завантажено: {info['thumbnails_loaded']}

🖼️ Поточне зображення:
• Назва: {current_name}
• Індекс: {info['current_index'] + 1 if info['current_index'] >= 0 else 'N/A'}

⚙️ Стан:
• Завантаження: {'Так' if info['is_loading'] else 'Ні'}
• Порожній: {'Так' if self.thumbnail_browser.is_empty() else 'Ні'}
            """.strip()
            
            self.info_text.setText(info_text)
        
        def closeEvent(self, event):
            """Очищення при закритті"""
            # Видалення тестових файлів
            import shutil
            for image_path in self.test_images:
                temp_dir = os.path.dirname(image_path)
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    break
            
            super().closeEvent(event)
    
    # Запуск тесту
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("=== Тестування ThumbnailBrowser ===")
    print("Функції для тестування:")
    print("1. 'Завантажити тестові зображення' - створення 10 тестових зображень")
    print("2. 'Наступне/Попереднє зображення' - навігація")
    print("3. 'Позначити як оброблене/необроблене' - зміна статусу")
    print("4. 'Очистити всі статуси' - скидання всіх індикаторів")
    print("5. Клік на мініатюрі - вибір зображення")
    print("6. Зелена галочка - оброблене зображення")
    print("7. Синя рамка - обране зображення")
    print("8. Автоматичне прокручування до обраного")
    print("9. Фонове завантаження мініатюр")
    
    sys.exit(app.exec_())