#!/usr/bin/env python3
"""
Центральна панель для відображення та обробки зображень
"""

import os
import tempfile
from typing import Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QPixmap, QFont, QCursor

from core.constants import UI, IMAGE
from core.image_processor import ImageProcessor


class ClickableImageLabel(QLabel):
    """Інтерактивна мітка для зображення з підтримкою кліків та перетягування"""
    
    point_clicked = pyqtSignal(int, int)
    mouse_moved = pyqtSignal(int, int)
    
    def __init__(self):
        super().__init__()
        
        self.setMinimumSize(450, 390)  # Пропорції 15:13
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 1px solid #dee2e6;
                background-color: white;
                border-radius: 6px;
            }
        """)
        
        self.setMouseTracking(True)
        self.dragging = False
        
        # Параметри масштабування
        self.scale_factor_x = 1.0
        self.scale_factor_y = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.original_image_width = 0
        self.original_image_height = 0
        
        # Початковий стан
        self.setText("Відкрийте зображення для початку роботи")
        self.setFont(QFont("Arial", 14))
        self.setStyleSheet(self.styleSheet() + "color: #6c757d;")
    
    def update_image_geometry(self, image_width: int, image_height: int, 
                            scale_factor_x: float, scale_factor_y: float, 
                            offset_x: int, offset_y: int):
        """Оновлення геометрії зображення для правильної обробки кліків"""
        self.original_image_width = image_width
        self.original_image_height = image_height
        self.scale_factor_x = scale_factor_x
        self.scale_factor_y = scale_factor_y
        self.offset_x = offset_x
        self.offset_y = offset_y
    
    def widget_to_image_coords(self, widget_x: int, widget_y: int) -> tuple:
        """Перетворення координат віджету в координати зображення"""
        image_x = (widget_x - self.offset_x) / self.scale_factor_x
        image_y = (widget_y - self.offset_y) / self.scale_factor_y
        
        image_x = max(0, min(int(image_x), self.original_image_width - 1))
        image_y = max(0, min(int(image_y), self.original_image_height - 1))
        
        return image_x, image_y
    
    def is_click_on_image(self, widget_x: int, widget_y: int) -> bool:
        """Перевірка чи клік знаходиться в межах зображення"""
        display_width = int(self.original_image_width * self.scale_factor_x)
        display_height = int(self.original_image_height * self.scale_factor_y)
        
        return (self.offset_x <= widget_x <= self.offset_x + display_width and
                self.offset_y <= widget_y <= self.offset_y + display_height)
    
    def mousePressEvent(self, event):
        """Обробка натискання миші"""
        if event.button() == Qt.LeftButton:
            widget_x, widget_y = event.x(), event.y()
            
            if self.is_click_on_image(widget_x, widget_y):
                image_x, image_y = self.widget_to_image_coords(widget_x, widget_y)
                self.point_clicked.emit(image_x, image_y)
                self.dragging = True
    
    def mouseMoveEvent(self, event):
        """Обробка руху миші"""
        widget_x, widget_y = event.x(), event.y()
        
        if self.is_click_on_image(widget_x, widget_y):
            image_x, image_y = self.widget_to_image_coords(widget_x, widget_y)
            self.mouse_moved.emit(image_x, image_y)
            
            if self.dragging and event.buttons() & Qt.LeftButton:
                self.point_clicked.emit(image_x, image_y)
    
    def mouseReleaseEvent(self, event):
        """Обробка відпускання миші"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
    
    def sizeHint(self):
        """Підказка розміру з підтримкою пропорцій 15:13"""
        width = max(450, self.width())
        height = int(width * 13 / 15)
        return QSize(width, height)


class ImagePanel(QWidget):
    """Центральна панель для відображення та обробки зображень"""
    
    point_clicked = pyqtSignal(int, int)
    center_move_requested = pyqtSignal(int, int)
    scale_edge_requested = pyqtSignal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.image_processor: Optional[ImageProcessor] = None
        self.center_setting_mode = False
        self.scale_edge_mode = False
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        self.image_label = ClickableImageLabel()
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
        """)
        
        layout.addWidget(scroll_area)
    
    def setup_connections(self):
        """Налаштування зв'язків"""
        self.image_label.point_clicked.connect(self.handle_point_click)
        self.image_label.mouse_moved.connect(self.handle_mouse_move)
    
    def set_image_processor(self, processor: ImageProcessor):
        """Встановлення процесора зображень"""
        self.image_processor = processor
        self.update_display()
    
    def update_display(self):
        """Оновлення відображення зображення"""
        if not self.image_processor or not self.image_processor.is_loaded:
            return
        
        try:
            preview_image = self.image_processor.create_preview_image(
                show_grid=True, 
                show_analysis=True
            )
            
            if not preview_image:
                return
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_path = temp_file.name
                preview_image.save(temp_path, 'JPEG', quality=95)
            
            pixmap = QPixmap(temp_path)
            
            try:
                os.remove(temp_path)
            except:
                pass
            
            self.scale_and_display_image(pixmap)
            
        except Exception as e:
            print(f"Помилка оновлення відображення: {e}")
    
    def scale_and_display_image(self, pixmap: QPixmap):
        """Масштабування та відображення зображення"""
        widget_width = self.image_label.width()
        widget_height = self.image_label.height()
        
        scaled_pixmap = pixmap.scaled(
            widget_width, widget_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        original_width = pixmap.width()
        original_height = pixmap.height()
        scaled_width = scaled_pixmap.width()
        scaled_height = scaled_pixmap.height()
        
        self.scale_factor_x = scaled_width / original_width
        self.scale_factor_y = scaled_height / original_height
        
        self.offset_x = (widget_width - scaled_width) // 2
        self.offset_y = (widget_height - scaled_height) // 2
        
        self.image_label.update_image_geometry(
            original_width, original_height,
            self.scale_factor_x, self.scale_factor_y,
            self.offset_x, self.offset_y
        )
        
        self.image_label.setPixmap(scaled_pixmap)
    
    def handle_point_click(self, x: int, y: int):
        """Обробка кліка по зображенню"""
        if self.center_setting_mode:
            self.center_move_requested.emit(x, y)
        elif self.scale_edge_mode:
            self.scale_edge_requested.emit(x, y)
        else:
            self.point_clicked.emit(x, y)
    
    def handle_mouse_move(self, x: int, y: int):
        """Обробка руху миші по зображенню"""
        pass  # Можна додати логіку для підказок
    
    def set_center_setting_mode(self, enabled: bool):
        """Встановлення режиму налаштування центру"""
        self.center_setting_mode = enabled
        self.scale_edge_mode = False if enabled else self.scale_edge_mode
        
        if enabled:
            self.image_label.setCursor(Qt.CrossCursor)
        else:
            self.image_label.setCursor(Qt.ArrowCursor)
    
    def set_scale_edge_mode(self, enabled: bool):
        """Встановлення режиму налаштування краю масштабу"""
        self.scale_edge_mode = enabled
        self.center_setting_mode = False if enabled else self.center_setting_mode
        
        if enabled:
            self.image_label.setCursor(Qt.CrossCursor)
        else:
            self.image_label.setCursor(Qt.ArrowCursor)
    
    def keyPressEvent(self, event):
        """Обробка клавіатурних команд"""
        if not self.image_processor:
            super().keyPressEvent(event)
            return
        
        # Обробка тільки в спеціальних режимах
        if not (self.center_setting_mode or self.scale_edge_mode):
            super().keyPressEvent(event)
            return
        
        # Визначення кроку
        step = 1
        if event.modifiers() & Qt.ShiftModifier:
            step = 5
        elif event.modifiers() & Qt.ControlModifier:
            step = 0.5
        
        dx, dy = 0, 0
        if event.key() == Qt.Key_Left:
            dx = -step
        elif event.key() == Qt.Key_Right:
            dx = step
        elif event.key() == Qt.Key_Up:
            dy = -step
        elif event.key() == Qt.Key_Down:
            dy = step
        elif event.key() == Qt.Key_Escape:
            self.set_center_setting_mode(False)
            self.set_scale_edge_mode(False)
            return
        else:
            super().keyPressEvent(event)
            return
        
        # Виконання переміщення
        if dx != 0 or dy != 0:
            if self.center_setting_mode:
                self.move_center_with_keyboard(dx, dy)
            elif self.scale_edge_mode:
                self.move_scale_edge_with_keyboard(dx, dy)
        
        event.accept()
    
    def move_center_with_keyboard(self, dx: float, dy: float):
        """Переміщення центру з клавіатури"""
        if self.image_processor:
            success = self.image_processor.move_center(int(dx), int(dy))
            if success:
                self.update_display()
                # Сигнал для оновлення в головному вікні
                self.center_move_requested.emit(int(dx), int(dy))
    
    def move_scale_edge_with_keyboard(self, dx: float, dy: float):
        """Переміщення краю масштабу з клавіатури"""
        if (self.image_processor and 
            self.image_processor.grid_settings.scale_edge_x is not None and
            self.image_processor.grid_settings.scale_edge_y is not None):
            
            new_x = self.image_processor.grid_settings.scale_edge_x + int(dx)
            new_y = self.image_processor.grid_settings.scale_edge_y + int(dy)
            
            # Обмеження межами
            new_x = max(0, min(new_x, self.image_processor.original_image.width - 1))
            new_y = max(0, min(new_y, self.image_processor.original_image.height - 1))
            
            success = self.image_processor.set_scale_edge(new_x, new_y)
            if success:
                self.update_display()
                self.scale_edge_requested.emit(new_x, new_y)
    
    def resizeEvent(self, event):
        """Обробка зміни розміру панелі"""
        super().resizeEvent(event)
        
        # Оновлення відображення з затримкою
        QTimer.singleShot(50, self.update_display_after_resize)
    
    def update_display_after_resize(self):
        """Оновлення відображення після зміни розміру"""
        if self.image_processor and self.image_processor.is_loaded:
            self.update_display()