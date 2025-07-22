#!/usr/bin/env python3
"""
Центральна панель для перегляду та обробки зображень
Відображає зображення з азимутальною сіткою, точками аналізу та інструментами
"""

import math
from typing import Optional, Tuple
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import (QPainter, QPen, QBrush, QColor, QPixmap, 
                         QMouseEvent, QWheelEvent, QKeyEvent, QFont, QPalette)

from core.constants import UI, IMAGE, GRID
from core.image_processor import ImageProcessor, AnalysisPoint


class ImageDisplayWidget(QLabel):
    """
    Віджет для відображення зображення з можливістю масштабування та взаємодії
    
    Функціональність:
    - Відображення зображення з автоматичним масштабуванням
    - Зум колесиком миші
    - Перетягування зображення
    - Клік для встановлення точок
    - Клавіатурне управління
    """
    
    # Сигнали для взаємодії
    point_clicked = pyqtSignal(int, int)  # Клік по зображенню
    center_move_requested = pyqtSignal(int, int)  # Запит переміщення центру
    scale_edge_requested = pyqtSignal(int, int)  # Запит встановлення краю масштабу
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Стан відображення
        self.image_processor: Optional[ImageProcessor] = None
        self.display_pixmap: Optional[QPixmap] = None
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Позиція та перетягування
        self.image_offset = QPoint(0, 0)
        self.last_mouse_pos = QPoint()
        self.is_dragging = False
        
        # Режими взаємодії
        self.center_setting_mode = False
        self.scale_edge_mode = False
        
        # Налаштування віджета
        self.setMinimumSize(400, 300)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border: 1px solid #555;
            }
        """)
        
        # Підтримка фокусу для клавіатури
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Початкове повідомлення
        self.show_placeholder_message()
    
    def show_placeholder_message(self):
        """Показ повідомлення-заглушки"""
        self.setText("Відкрийте зображення для початку роботи")
        self.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                color: #6c757d;
                font-size: 14pt;
                padding: 20px;
            }
        """)
    
    def set_image_processor(self, processor: ImageProcessor):
        """Встановлення процесора зображень"""
        self.image_processor = processor
        
        if processor and processor.is_loaded:
            self.load_image()
            self.setStyleSheet("""
                QLabel {
                    background-color: #2a2a2a;
                    border: 1px solid #555;
                }
            """)
        else:
            self.show_placeholder_message()
    
    def load_image(self):
        """Завантаження зображення для відображення"""
        if not self.image_processor or not self.image_processor.is_loaded:
            return
        
        # Створення зображення з накладеними елементами
        pil_image = self.image_processor.create_preview_image(
            show_grid=True,
            show_analysis=True,
            show_radar_desc=False  # Опис РЛС показуємо тільки при збереженні
        )
        
        if pil_image:
            # Конвертація PIL -> QPixmap
            self.display_pixmap = self.pil_to_qpixmap(pil_image)
            
            # Автоматичне масштабування для вміщення
            self.fit_to_window()
            
            # Оновлення відображення
            self.update_display()
    
    def pil_to_qpixmap(self, pil_image) -> QPixmap:
        """Конвертація PIL Image в QPixmap"""
        # Конвертація в RGB якщо потрібно
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Отримання даних
        width, height = pil_image.size
        bytes_per_line = 3 * width
        
        # Конвертація
        from PyQt5.QtGui import QImage
        qimage = QImage(
            pil_image.tobytes(),
            width, height,
            bytes_per_line,
            QImage.Format_RGB888
        )
        
        return QPixmap.fromImage(qimage)
    
    def update_display(self):
        """Оновлення відображення зображення"""
        if not self.display_pixmap:
            return
        
        # Розрахунок розміру з урахуванням зуму
        scaled_size = self.display_pixmap.size() * self.zoom_factor
        
        # Створення масштабованого зображення
        scaled_pixmap = self.display_pixmap.scaled(
            scaled_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Розрахунок позиції для центрування
        widget_rect = self.rect()
        image_rect = scaled_pixmap.rect()
        
        # Центрування з урахуванням offset
        center_x = (widget_rect.width() - image_rect.width()) // 2 + self.image_offset.x()
        center_y = (widget_rect.height() - image_rect.height()) // 2 + self.image_offset.y()
        
        # Створення фінального зображення
        final_pixmap = QPixmap(widget_rect.size())
        final_pixmap.fill(QColor(42, 42, 42))  # Темний фон
        
        painter = QPainter(final_pixmap)
        painter.drawPixmap(center_x, center_y, scaled_pixmap)
        painter.end()
        
        # Встановлення зображення
        self.setPixmap(final_pixmap)
    
    def fit_to_window(self):
        """Автоматичне масштабування для вміщення в вікно"""
        if not self.display_pixmap:
            return
        
        widget_size = self.size()
        image_size = self.display_pixmap.size()
        
        # Розрахунок масштабу для вміщення
        scale_x = widget_size.width() / image_size.width()
        scale_y = widget_size.height() / image_size.height()
        
        # Використовуємо менший масштаб
        self.zoom_factor = min(scale_x, scale_y) * 0.9  # 90% для відступів
        
        # Скидання offset
        self.image_offset = QPoint(0, 0)
        
        # Оновлення відображення
        self.update_display()
    
    def zoom_in(self):
        """Збільшення масштабу"""
        self.set_zoom(self.zoom_factor * 1.25)
    
    def zoom_out(self):
        """Зменшення масштабу"""
        self.set_zoom(self.zoom_factor / 1.25)
    
    def set_zoom(self, zoom: float):
        """Встановлення конкретного масштабу"""
        self.zoom_factor = max(self.min_zoom, min(self.max_zoom, zoom))
        self.update_display()
    
    def reset_zoom(self):
        """Скидання масштабу до початкового"""
        self.fit_to_window()
    
    # ===== ОБРОБКА ПОДІЙ МИШІ =====
    
    def mousePressEvent(self, event: QMouseEvent):
        """Обробка натискання миші"""
        if event.button() == Qt.LeftButton:
            # Конвертація координат в координати зображення
            image_coords = self.widget_to_image_coords(event.pos())
            
            if image_coords:
                x, y = image_coords
                
                # Перевірка режимів
                if self.center_setting_mode:
                    self.center_move_requested.emit(x, y)
                elif self.scale_edge_mode:
                    self.scale_edge_requested.emit(x, y)
                else:
                    self.point_clicked.emit(x, y)
            
            # Початок перетягування
            self.last_mouse_pos = event.pos()
            self.is_dragging = True
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Обробка переміщення миші"""
        if self.is_dragging and event.buttons() & Qt.LeftButton:
            # Перетягування зображення (тільки якщо не в спеціальному режимі)
            if not self.center_setting_mode and not self.scale_edge_mode:
                delta = event.pos() - self.last_mouse_pos
                self.image_offset += delta
                self.update_display()
            
            self.last_mouse_pos = event.pos()
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Обробка відпускання миші"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
        
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event: QWheelEvent):
        """Обробка колесика миші для зуму"""
        # Зум в точці курсора
        zoom_delta = 1.25 if event.angleDelta().y() > 0 else 1/1.25
        old_zoom = self.zoom_factor
        
        self.set_zoom(self.zoom_factor * zoom_delta)
        
        # Коригування offset для зуму в точці курсора
        if old_zoom != self.zoom_factor:
            cursor_pos = event.pos()
            widget_center = self.rect().center()
            
            # Зміщення для зуму в точці курсора
            offset_delta = (cursor_pos - widget_center) * (self.zoom_factor / old_zoom - 1)
            self.image_offset -= offset_delta
            
            self.update_display()
        
        super().wheelEvent(event)
    
    # ===== ОБРОБКА КЛАВІАТУРИ =====
    
    def keyPressEvent(self, event: QKeyEvent):
        """Обробка натискання клавіш"""
        key = event.key()
        modifiers = event.modifiers()
        
        # Переміщення центру/краю стрілками
        if key in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down]:
            # Розрахунок кроку переміщення
            if modifiers & Qt.ControlModifier:
                step = 1  # Точне переміщення
            elif modifiers & Qt.ShiftModifier:
                step = 10  # Швидке переміщення
            else:
                step = 5  # Звичайне переміщення
            
            # Напрямок переміщення
            dx, dy = 0, 0
            if key == Qt.Key_Left:
                dx = -step
            elif key == Qt.Key_Right:
                dx = step
            elif key == Qt.Key_Up:
                dy = -step
            elif key == Qt.Key_Down:
                dy = step
            
            # Переміщення в залежності від режиму
            if self.center_setting_mode or self.scale_edge_mode:
                # Переміщення центру/краю через процесор
                if self.image_processor:
                    if self.center_setting_mode:
                        current_x = self.image_processor.grid_settings.center_x
                        current_y = self.image_processor.grid_settings.center_y
                        self.center_move_requested.emit(current_x + dx, current_y + dy)
                    elif self.scale_edge_mode:
                        # Переміщення краю масштабу
                        edge_x = self.image_processor.grid_settings.scale_edge_x or 0
                        edge_y = self.image_processor.grid_settings.scale_edge_y or 0
                        self.scale_edge_requested.emit(edge_x + dx, edge_y + dy)
            else:
                # Звичайне переміщення зображення
                self.image_offset += QPoint(dx * 2, dy * 2)
                self.update_display()
            
            event.accept()
            return
        
        # Управління зумом
        elif key == Qt.Key_Plus or key == Qt.Key_Equal:
            self.zoom_in()
            event.accept()
            return
        elif key == Qt.Key_Minus:
            self.zoom_out()
            event.accept()
            return
        elif key == Qt.Key_0:
            self.reset_zoom()
            event.accept()
            return
        
        # Вихід з режимів
        elif key == Qt.Key_Escape:
            if self.center_setting_mode or self.scale_edge_mode:
                self.set_center_setting_mode(False)
                self.set_scale_edge_mode(False)
                event.accept()
                return
        
        super().keyPressEvent(event)
    
    # ===== УТИЛІТАРНІ МЕТОДИ =====
    
    def widget_to_image_coords(self, widget_pos: QPoint) -> Optional[Tuple[int, int]]:
        """Конвертація координат віджета в координати зображення"""
        if not self.display_pixmap or not self.image_processor:
            return None
        
        # Розміри та позиції
        widget_rect = self.rect()
        scaled_size = self.display_pixmap.size() * self.zoom_factor
        
        # Позиція зображення на віджеті
        image_x = (widget_rect.width() - scaled_size.width()) // 2 + self.image_offset.x()
        image_y = (widget_rect.height() - scaled_size.height()) // 2 + self.image_offset.y()
        
        # Перевірка чи клік в межах зображення
        image_rect = QRect(image_x, image_y, scaled_size.width(), scaled_size.height())
        if not image_rect.contains(widget_pos):
            return None
        
        # Конвертація в координати оригінального зображення
        rel_x = widget_pos.x() - image_x
        rel_y = widget_pos.y() - image_y
        
        # Масштабування до оригінального розміру
        orig_x = int(rel_x / self.zoom_factor)
        orig_y = int(rel_y / self.zoom_factor)
        
        return (orig_x, orig_y)
    
    def image_to_widget_coords(self, image_x: int, image_y: int) -> QPoint:
        """Конвертація координат зображення в координати віджета"""
        if not self.display_pixmap:
            return QPoint()
        
        # Розміри та позиції
        widget_rect = self.rect()
        scaled_size = self.display_pixmap.size() * self.zoom_factor
        
        # Позиція зображення на віджеті
        display_x = (widget_rect.width() - scaled_size.width()) // 2 + self.image_offset.x()
        display_y = (widget_rect.height() - scaled_size.height()) // 2 + self.image_offset.y()
        
        # Конвертація координат
        widget_x = display_x + int(image_x * self.zoom_factor)
        widget_y = display_y + int(image_y * self.zoom_factor)
        
        return QPoint(widget_x, widget_y)
    
    # ===== РЕЖИМИ ВЗАЄМОДІЇ =====
    
    def set_center_setting_mode(self, enabled: bool):
        """Включення/виключення режиму встановлення центру"""
        self.center_setting_mode = enabled
        
        if enabled:
            self.setCursor(Qt.CrossCursor)
            self.scale_edge_mode = False  # Вимикаємо інший режим
        else:
            self.setCursor(Qt.ArrowCursor)
    
    def set_scale_edge_mode(self, enabled: bool):
        """Включення/виключення режиму встановлення краю масштабу"""
        self.scale_edge_mode = enabled
        
        if enabled:
            self.setCursor(Qt.CrossCursor)
            self.center_setting_mode = False  # Вимикаємо інший режим
        else:
            self.setCursor(Qt.ArrowCursor)
    
    # ===== ОНОВЛЕННЯ ВІДОБРАЖЕННЯ =====
    
    def refresh_display(self):
        """Оновлення відображення після змін в процесорі"""
        if self.image_processor and self.image_processor.is_loaded:
            self.load_image()
    
    def resizeEvent(self, event):
        """Обробка зміни розміру віджета"""
        super().resizeEvent(event)
        if self.display_pixmap:
            self.update_display()


class ImagePanel(QWidget):
    """
    Центральна панель для перегляду та обробки зображень
    
    Функціональність:
    - Відображення зображення з інструментами
    - Панель управління зумом та режимами
    - Інформація про поточне зображення
    - Координація з основним процесором зображень
    """
    
    # Сигнали для зв'язку з головним вікном
    point_clicked = pyqtSignal(int, int)  # Клік по зображенню
    center_move_requested = pyqtSignal(int, int)  # Переміщення центру
    scale_edge_requested = pyqtSignal(int, int)  # Встановлення краю масштабу
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Стан панелі
        self.image_processor: Optional[ImageProcessor] = None
        
        # Налаштування панелі
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        # Панель інструментів
        self.create_toolbar(layout)
        
        # Область відображення зображення
        self.create_image_area(layout)
        
        # Панель статусу
        self.create_status_bar(layout)
    
    def create_toolbar(self, layout: QVBoxLayout):
        """Створення панелі інструментів"""
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #dee2e6;
                padding: 8px;
            }
        """)
        toolbar.setMaximumHeight(50)
        
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar_layout.setSpacing(10)
        toolbar.setLayout(toolbar_layout)
        
        # Кнопки зуму
        self.zoom_out_btn = QPushButton("🔍−")
        self.zoom_out_btn.setToolTip("Зменшити масштаб")
        self.zoom_out_btn.setFixedSize(32, 32)
        
        self.zoom_reset_btn = QPushButton("🔍")
        self.zoom_reset_btn.setToolTip("Вмістити в вікно")
        self.zoom_reset_btn.setFixedSize(32, 32)
        
        self.zoom_in_btn = QPushButton("🔍+")
        self.zoom_in_btn.setToolTip("Збільшити масштаб")
        self.zoom_in_btn.setFixedSize(32, 32)
        
        # Розділювач
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        
        # Кнопки режимів
        self.center_mode_btn = QPushButton("📍 Центр")
        self.center_mode_btn.setToolTip("Режим встановлення центру сітки")
        self.center_mode_btn.setCheckable(True)
        
        self.edge_mode_btn = QPushButton("📏 Край")
        self.edge_mode_btn.setToolTip("Режим встановлення краю масштабу")
        self.edge_mode_btn.setCheckable(True)
        
        # Розділювач
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        
        # Інформація про зум
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setStyleSheet("""
            QLabel {
                background: none;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px 8px;
                font-family: monospace;
            }
        """)
        
        # Додавання елементів
        toolbar_layout.addWidget(self.zoom_out_btn)
        toolbar_layout.addWidget(self.zoom_reset_btn)
        toolbar_layout.addWidget(self.zoom_in_btn)
        toolbar_layout.addWidget(self.zoom_label)
        toolbar_layout.addWidget(separator1)
        toolbar_layout.addWidget(self.center_mode_btn)
        toolbar_layout.addWidget(self.edge_mode_btn)
        toolbar_layout.addWidget(separator2)
        toolbar_layout.addStretch()
        
        layout.addWidget(toolbar)
    
    def create_image_area(self, layout: QVBoxLayout):
        """Створення області відображення зображення"""
        # Віджет відображення зображення
        self.image_display = ImageDisplayWidget(self)
        layout.addWidget(self.image_display, 1)  # Розтягування
    
    def create_status_bar(self, layout: QVBoxLayout):
        """Створення панелі статусу"""
        status_bar = QFrame()
        status_bar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #dee2e6;
                padding: 4px;
            }
        """)
        status_bar.setMaximumHeight(30)
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 2, 10, 2)
        status_layout.setSpacing(15)
        status_bar.setLayout(status_layout)
        
        # Інформація про зображення
        self.image_info_label = QLabel("Зображення не завантажено")
        self.image_info_label.setStyleSheet("""
            QLabel {
                background: none;
                border: none;
                color: #6c757d;
                font-size: 11pt;
            }
        """)
        
        # Координати курсора
        self.coords_label = QLabel("x: -, y: -")
        self.coords_label.setStyleSheet("""
            QLabel {
                background: none;
                border: none;
                color: #6c757d;
                font-family: monospace;
                font-size: 11pt;
            }
        """)
        
        # Режим роботи
        self.mode_label = QLabel("Звичайний режим")
        self.mode_label.setStyleSheet("""
            QLabel {
                background: none;
                border: none;
                color: #28a745;
                font-weight: bold;
                font-size: 11pt;
            }
        """)
        
        status_layout.addWidget(self.image_info_label)
        status_layout.addStretch()
        status_layout.addWidget(self.coords_label)
        status_layout.addWidget(self.mode_label)
        
        layout.addWidget(status_bar)
    
    def setup_connections(self):
        """Налаштування зв'язків між компонентами"""
        # Кнопки зуму
        self.zoom_out_btn.clicked.connect(self.image_display.zoom_out)
        self.zoom_reset_btn.clicked.connect(self.image_display.reset_zoom)
        self.zoom_in_btn.clicked.connect(self.image_display.zoom_in)
        
        # Кнопки режимів
        self.center_mode_btn.toggled.connect(self.on_center_mode_toggled)
        self.edge_mode_btn.toggled.connect(self.on_edge_mode_toggled)
        
        # Сигнали від віджета зображення
        self.image_display.point_clicked.connect(self.point_clicked.emit)
        self.image_display.center_move_requested.connect(self.center_move_requested.emit)
        self.image_display.scale_edge_requested.connect(self.scale_edge_requested.emit)
        
        # Таймер для оновлення статусу
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(100)  # Оновлення кожні 100мс
    
    # ===== ОСНОВНІ МЕТОДИ =====
    
    def set_image_processor(self, processor: ImageProcessor):
        """Встановлення процесора зображень"""
        self.image_processor = processor
        self.image_display.set_image_processor(processor)
        
        # Оновлення інформації
        self.update_image_info()
    
    def update_display(self):
        """Оновлення відображення"""
        self.image_display.refresh_display()
    
    def update_image_info(self):
        """Оновлення інформації про зображення"""
        if self.image_processor and self.image_processor.is_loaded:
            info = self.image_processor.get_image_info()
            filename = info.get('filename', 'Невідомо')
            width, height = info.get('size', (0, 0))
            file_size = info.get('file_size', 0)
            
            # Форматування розміру файлу
            if file_size > 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.1f} МБ"
            elif file_size > 1024:
                size_str = f"{file_size / 1024:.1f} КБ"
            else:
                size_str = f"{file_size} Б"
            
            info_text = f"{filename} • {width}×{height} • {size_str}"
            self.image_info_label.setText(info_text)
        else:
            self.image_info_label.setText("Зображення не завантажено")
    
    def update_status(self):
        """Оновлення статусної інформації"""
        # Оновлення зуму
        zoom_percent = int(self.image_display.zoom_factor * 100)
        self.zoom_label.setText(f"{zoom_percent}%")
        
        # Оновлення режиму
        if self.image_display.center_setting_mode:
            self.mode_label.setText("🎯 Встановлення центру")
            self.mode_label.setStyleSheet("color: #007bff; font-weight: bold;")
        elif self.image_display.scale_edge_mode:
            self.mode_label.setText("📏 Встановлення краю")
            self.mode_label.setStyleSheet("color: #fd7e14; font-weight: bold;")
        else:
            self.mode_label.setText("👀 Звичайний режим")
            self.mode_label.setStyleSheet("color: #28a745; font-weight: bold;")
    
    # ===== ОБРОБНИКИ ПОДІЙ =====
    
    def on_center_mode_toggled(self, checked: bool):
        """Обробка перемикання режиму центру"""
        self.image_display.set_center_setting_mode(checked)
        
        if checked:
            # Вимикаємо інший режим
            self.edge_mode_btn.setChecked(False)
    
    def on_edge_mode_toggled(self, checked: bool):
        """Обробка перемикання режиму краю"""
        self.image_display.set_scale_edge_mode(checked)
        
        if checked:
            # Вимикаємо інший режим
            self.center_mode_btn.setChecked(False)
    
    # ===== ПУБЛІЧНІ МЕТОДИ ДЛЯ УПРАВЛІННЯ =====
    
    def set_center_mode(self, enabled: bool):
        """Програмне включення режиму встановлення центру"""
        self.center_mode_btn.setChecked(enabled)
    
    def set_edge_mode(self, enabled: bool):
        """Програмне включення режиму встановлення краю"""
        self.edge_mode_btn.setChecked(enabled)
    
    def exit_special_modes(self):
        """Вихід з всіх спеціальних режимів"""
        self.center_mode_btn.setChecked(False)
        self.edge_mode_btn.setChecked(False)
    
    def focus_image(self):
        """Встановлення фокусу на зображення для клавіатурного управління"""
        self.image_display.setFocus()


# ===== ТЕСТУВАННЯ МОДУЛЯ =====

if __name__ == "__main__":
    print("=== Тестування ImagePanel ===")
    print("Модуль ImagePanel готовий до використання")