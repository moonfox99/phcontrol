#!/usr/bin/env python3
"""
Enhanced widgets with zoom functionality for precise scale edge setting
"""

import os
import tempfile
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QFrame, QSizePolicy
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QFont, QCursor, QPainter, QPen
from PIL import Image, ImageDraw

class ZoomWidget(QLabel):
    """Small zoom window that shows magnified area around cursor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)  # Small square zoom window
        self.setStyleSheet("""
            QLabel {
                border: 3px solid #4CAF50;
                border-radius: 8px;
                background-color: white;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setText("ZOOM")
        self.setFont(QFont("Arial", 10, QFont.Bold))
        
        # Zoom parameters
        self.zoom_factor = 4  # 4x magnification
        self.zoom_radius = 30  # Radius around cursor to capture
        
        # Image data
        self.source_pixmap = None
        self.cursor_x = 0
        self.cursor_y = 0
        
        # Position in top-left corner
        self.move(10, 10)
        self.hide()  # Initially hidden
    
    def set_source_image(self, pixmap):
        """Set the source image to zoom from"""
        self.source_pixmap = pixmap
    
    def update_cursor_position(self, x, y):
        """Update cursor position and refresh zoom view"""
        if not self.source_pixmap:
            return
            
        self.cursor_x = x
        self.cursor_y = y
        self.update_zoom_view()
    
    def update_zoom_view(self):
        """Update the zoomed view around cursor position"""
        if not self.source_pixmap:
            self.setText("NO IMAGE")
            return
        
        # Calculate crop area around cursor
        crop_size = self.zoom_radius
        left = max(0, self.cursor_x - crop_size)
        top = max(0, self.cursor_y - crop_size)
        right = min(self.source_pixmap.width(), self.cursor_x + crop_size)
        bottom = min(self.source_pixmap.height(), self.cursor_y + crop_size)
        
        # Crop the area
        crop_rect = (left, top, right - left, bottom - top)
        cropped = self.source_pixmap.copy(*crop_rect)
        
        if cropped.isNull():
            self.setText("OUT OF BOUNDS")
            return
        
        # Scale up the cropped area
        zoomed_size = min(110, 110)  # Fit within widget minus border
        scaled = cropped.scaled(zoomed_size, zoomed_size, 
                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Draw crosshairs on the zoomed image
        painter = QPainter(scaled)
        painter.setPen(QPen(Qt.red, 2))
        
        # Calculate center of the zoomed view
        center_x = scaled.width() // 2
        center_y = scaled.height() // 2
        
        # Draw crosshairs
        painter.drawLine(center_x - 10, center_y, center_x + 10, center_y)
        painter.drawLine(center_x, center_y - 10, center_x, center_y + 10)
        
        # Draw small circle at center
        painter.setPen(QPen(Qt.red, 1))
        painter.drawEllipse(center_x - 3, center_y - 3, 6, 6)
        
        painter.end()
        
        self.setPixmap(scaled)
    
    def show_zoom(self):
        """Show the zoom widget"""
        self.show()
        self.raise_()  # Bring to front
    
    def hide_zoom(self):
        """Hide the zoom widget"""
        self.hide()

class ClickableLabel(QLabel):
    """Custom QLabel that maintains strict 15:13 aspect ratio with accurate coordinate handling"""
    clicked = pyqtSignal(int, int)
    dragged = pyqtSignal(int, int)
    mouse_moved = pyqtSignal(int, int)
    
    def __init__(self):
        super().__init__()
        # Set minimum size with 15:13 aspect ratio
        self.setMinimumSize(450, 390)  # 450 * 13/15 = 390
        self.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.setAlignment(Qt.AlignCenter)
        self.setText("Open an image or folder to start")
        self.setScaledContents(False)  # We'll handle scaling manually
        self.dragging = False
        self.setMouseTracking(True)
        self.scale_edge_mode = False
        
        # ВСТАНОВЛЮЄМО ПОЛІТИКУ ФОКУСУ ДЛЯ ОТРИМАННЯ КЛАВІАТУРНИХ ПОДІЙ
        self.setFocusPolicy(Qt.ClickFocus)
        
        # Critical: Store the target aspect ratio
        self.target_aspect_ratio = 15.0 / 13.0
        
        # Initialize display area variables - these will be updated properly
        self.image_display_width = 450
        self.image_display_height = 390
        self.image_offset_x = 0
        self.image_offset_y = 0
        
        # Create zoom widget as child
        self.zoom_widget = ZoomWidget(self)
        
        # Timer for smooth zoom updates
        self.zoom_update_timer = QTimer()
        self.zoom_update_timer.setSingleShot(True)
        self.zoom_update_timer.timeout.connect(self.update_zoom_delayed)
        
    def set_scale_edge_mode(self, enabled):
        """Enable/disable scale edge setting mode"""
        self.scale_edge_mode = enabled
        if enabled:
            self.setCursor(Qt.CrossCursor)
            self.zoom_widget.show_zoom()
        else:
            self.setCursor(Qt.ArrowCursor)
            # Only hide zoom if center mode is also disabled
            if not getattr(self, 'center_setting_mode', False):
                self.zoom_widget.hide_zoom()

    def set_center_setting_mode(self, enabled):
        """Enable/disable center setting mode"""
        self.center_setting_mode = enabled
        if enabled:
            self.setCursor(Qt.CrossCursor)
            self.zoom_widget.show_zoom()
        else:
            self.setCursor(Qt.ArrowCursor)
            # Only hide zoom if scale edge mode is also disabled
            if not getattr(self, 'scale_edge_mode', False):
                self.zoom_widget.hide_zoom()
    
    def update_image_geometry(self, image_width, image_height, scale_factor_x, scale_factor_y, offset_x, offset_y):
        """Update image geometry from the main application"""
        self.image_display_width = int(image_width * scale_factor_x)
        self.image_display_height = int(image_height * scale_factor_y)
        self.image_offset_x = offset_x
        self.image_offset_y = offset_y
        self.scale_factor_x = scale_factor_x
        self.scale_factor_y = scale_factor_y
        self.original_image_width = image_width
        self.original_image_height = image_height
        
        print(f"ClickableLabel geometry updated: display({self.image_display_width}x{self.image_display_height}) "
              f"offset({self.image_offset_x}, {self.image_offset_y}) scale({scale_factor_x:.3f}, {scale_factor_y:.3f})")
    
    def set_zoom_source_image(self, pixmap):
        """Set the source image for zoom widget"""
        self.zoom_widget.set_source_image(pixmap)
    
    def update_zoom_delayed(self):
        """Update zoom with a slight delay for performance"""
        if (self.scale_edge_mode or getattr(self, 'center_setting_mode', False)) and hasattr(self, 'last_mouse_x'):
            # Convert widget coordinates to pixmap coordinates for zoom
            pixmap_x = (self.last_mouse_x - self.image_offset_x) / self.scale_factor_x
            pixmap_y = (self.last_mouse_y - self.image_offset_y) / self.scale_factor_y
            
            # Ensure coordinates are within bounds
            if (0 <= pixmap_x < self.original_image_width and 
                0 <= pixmap_y < self.original_image_height):
                self.zoom_widget.update_cursor_position(int(pixmap_x), int(pixmap_y))

    def update_zoom_immediately(self):
        """Update zoom immediately without delay"""
        if (self.scale_edge_mode or getattr(self, 'center_setting_mode', False)) and hasattr(self, 'last_mouse_x'):
            # Convert widget coordinates to pixmap coordinates for zoom
            pixmap_x = (self.last_mouse_x - self.image_offset_x) / self.scale_factor_x
            pixmap_y = (self.last_mouse_y - self.image_offset_y) / self.scale_factor_y
            
            # Ensure coordinates are within bounds
            if (0 <= pixmap_x < self.original_image_width and 
                0 <= pixmap_y < self.original_image_height):
                self.zoom_widget.update_cursor_position(int(pixmap_x), int(pixmap_y))
    
    def widget_to_image_coords(self, widget_x, widget_y):
        """Convert widget coordinates to original image coordinates"""
        if not hasattr(self, 'scale_factor_x'):
            # Fallback if geometry not set yet
            return widget_x, widget_y
        
        # Remove offsets and scale back to original image coordinates
        image_x = (widget_x - self.image_offset_x) / self.scale_factor_x
        image_y = (widget_y - self.image_offset_y) / self.scale_factor_y
        
        # Ensure coordinates are within image bounds
        image_x = max(0, min(int(image_x), self.original_image_width - 1))
        image_y = max(0, min(int(image_y), self.original_image_height - 1))
        
        return image_x, image_y
    
    def is_click_on_image(self, widget_x, widget_y):
        """Check if click is within the actual image area"""
        if not hasattr(self, 'image_offset_x'):
            return True  # Fallback
        
        return (self.image_offset_x <= widget_x <= self.image_offset_x + self.image_display_width and
                self.image_offset_y <= widget_y <= self.image_offset_y + self.image_display_height)
    
    def sizeHint(self):
        """Provide size hint that maintains 15:13 ratio"""
        # Always suggest a size that maintains the aspect ratio
        width = max(450, self.width())
        height = int(width * 13 / 15)
        return QSize(width, height)
    
    def heightForWidth(self, width):
        """Maintain aspect ratio: height should be width * 13/15"""
        return int(width * 13 / 15)
    
    def hasHeightForWidth(self):
        """Indicate that this widget maintains aspect ratio"""
        return True
    
    def paintEvent(self, event):
        """Custom paint - removed debug border for cleaner look"""
        super().paintEvent(event)
        # Debug border removed for production use
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            widget_x, widget_y = event.x(), event.y()
            
            # Check if click is within the actual image
            if self.is_click_on_image(widget_x, widget_y):
                # Convert to image coordinates immediately
                image_x, image_y = self.widget_to_image_coords(widget_x, widget_y)
                
                print(f"Click: widget({widget_x}, {widget_y}) -> image({image_x}, {image_y})")
                print(f"Scale edge mode: {self.scale_edge_mode}")
                print(f"Center setting mode: {getattr(self, 'center_setting_mode', False)}")
                
                # ONLY emit click signal if NOT in special modes
                if not self.scale_edge_mode and not getattr(self, 'center_setting_mode', False):
                    self.clicked.emit(image_x, image_y)
                    self.dragging = True
                elif self.scale_edge_mode or getattr(self, 'center_setting_mode', False):
                    # In special modes, emit click directly to handle the special function
                    self.clicked.emit(image_x, image_y)
    
    def mouseMoveEvent(self, event):
        widget_x, widget_y = event.x(), event.y()

        # Store last mouse position for zoom
        self.last_mouse_x = widget_x
        self.last_mouse_y = widget_y

        # Update zoom if in scale edge mode OR center setting mode
        if (self.scale_edge_mode or getattr(self, 'center_setting_mode', False)) and self.is_click_on_image(widget_x, widget_y):
            self.update_zoom_immediately()
        
        # Always emit mouse move for hover effects
        if hasattr(self, 'scale_factor_x'):
            image_x, image_y = self.widget_to_image_coords(widget_x, widget_y)
            self.mouse_moved.emit(image_x, image_y)
        
        # ЕМІТИМО DRAG ТІЛЬКИ ЯКЩО ПЕРЕТЯГУЄМО І НЕ В СПЕЦІАЛЬНИХ РЕЖИМАХ
        if (self.dragging and event.buttons() & Qt.LeftButton and 
            not self.scale_edge_mode and not getattr(self, 'center_setting_mode', False) and 
            self.is_click_on_image(widget_x, widget_y)):
            
            image_x, image_y = self.widget_to_image_coords(widget_x, widget_y)
            print(f"Drag: widget({widget_x}, {widget_y}) -> image({image_x}, {image_y})")
            self.dragged.emit(image_x, image_y)

    def mouseReleaseEvent(self, event):
        # ЗАВЕРШУЄМО ПЕРЕТЯГУВАННЯ
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def keyPressEvent(self, event):
        """Передача клавіатурних подій головному вікну"""
        # Передаємо події клавіатури батьківському віджету (головному вікну)
        parent = self.parent()
        while parent and not hasattr(parent, 'center_setting_mode'):
            parent = parent.parent()
        
        if parent:
            parent.keyPressEvent(event)
        else:
            super().keyPressEvent(event)

# Оновлення для widgets.py

class VerticalThumbnailWidget(QWidget):
    image_selected = pyqtSignal(str)
    
    def __init__(self, thumbnail_width=260, parent=None):
        super().__init__(parent)
        self.thumbnail_width = thumbnail_width
        self.thumbnail_height = int(thumbnail_width * 0.75)
        self.thumbnails = []
        self.image_paths = []
        self.processed_paths = set()
        self.selected_path = None  # НОВЕ: шлях до обраного зображення
        
        # Основний layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(8)
        self.setLayout(self.layout)
        
        # Встановлюємо розмір віджета
        self.setFixedWidth(thumbnail_width)
        
        print(f"📐 VerticalThumbnailWidget initialized: {thumbnail_width}x{self.thumbnail_height}")

    def set_selected_image(self, image_path):
        """Встановити обране зображення"""
        old_selected = self.selected_path
        self.selected_path = image_path
        
        # Оновлюємо стилі для старого та нового обраного зображення
        for i, path in enumerate(self.image_paths):
            if i < len(self.thumbnails):
                thumbnail = self.thumbnails[i]
                if path == old_selected:
                    thumbnail.set_selected(False)
                elif path == image_path:
                    thumbnail.set_selected(True)
    
    def mark_image_as_unprocessed(self, image_path):
        """Позначити зображення як необроблене"""
        try:
            # Видаляємо з множини оброблених
            self.processed_paths.discard(image_path)
            
            # Знаходимо відповідну мініатюру і оновлюємо її стиль
            for i, path in enumerate(self.image_paths):
                if path == image_path and i < len(self.thumbnails):
                    thumbnail = self.thumbnails[i]
                    if hasattr(thumbnail, 'mark_as_unprocessed'):
                        thumbnail.mark_as_unprocessed()
                    break
                    
            print(f"❌ Marked as unprocessed: {os.path.basename(image_path)}")
            
        except Exception as e:
            print(f"❌ Error marking image as unprocessed: {e}")

    def clear_all_processed_status(self):
        """Очистити статус обробки для всіх зображень"""
        try:
            # Очищуємо множину оброблених
            self.processed_paths.clear()
            
            # Оновлюємо всі мініатюри
            for thumbnail in self.thumbnails:
                if hasattr(thumbnail, 'mark_as_unprocessed'):
                    thumbnail.mark_as_unprocessed()
                    
            print("🗑️ Cleared processed status for all images")
            
        except Exception as e:
            print(f"❌ Error clearing all processed status: {e}")

    def add_thumbnail(self, image_path):
        """Додавання мініатюри з оновленими розмірами"""
        try:
            print(f"🔨 Creating thumbnail for: {os.path.basename(image_path)}")
            
            # Перевіряємо чи зображення оброблене
            is_processed = image_path in self.processed_paths
            print(f"📋 Image processed status: {is_processed}")
            
            # Створюємо мініатюру
            thumbnail_label = ClickableThumbnail(image_path, 
                                               width=self.thumbnail_width-20,  # Відступ для бордерів
                                               height=self.thumbnail_height-20,
                                               is_processed=is_processed)
            
            # Підключаємо сигнал
            thumbnail_label.clicked.connect(lambda path=image_path: self.image_selected.emit(path))
            
            print("✓ Successfully created thumbnail image")
            
            # Додаємо до layout та списків
            self.layout.addWidget(thumbnail_label)
            self.thumbnails.append(thumbnail_label)
            self.image_paths.append(image_path)
            
            widget_count = len(self.thumbnails)
            print(f"✅ Added to layout. Total widgets: {widget_count}")
            
            # Оновлюємо висоту віджета
            new_height = widget_count * (self.thumbnail_height + 8) + 20
            self.setMinimumHeight(new_height)
            print(f"📏 Updated widget height to: {new_height}px")
            
        except Exception as e:
            print(f"❌ Error creating thumbnail: {e}")
            import traceback
            traceback.print_exc()

    def clear_thumbnails(self):
        """Очищення всіх мініатюр"""
        try:
            print(f"Clearing {len(self.thumbnails)} existing thumbnails")
            
            # Видаляємо всі віджети з layout
            while self.layout.count():
                child = self.layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Очищуємо списки
            self.thumbnails.clear()
            self.image_paths.clear()
            self.processed_paths.clear()
            
            print("Thumbnails and references cleared")
            
        except Exception as e:
            print(f"Error clearing thumbnails: {e}")

    def mark_image_as_processed(self, image_path):
        """Позначити зображення як оброблене"""
        try:
            # Додаємо до множини оброблених
            self.processed_paths.add(image_path)
            
            # Знаходимо відповідну мініатюру і оновлюємо її стиль
            for i, path in enumerate(self.image_paths):
                if path == image_path and i < len(self.thumbnails):
                    thumbnail = self.thumbnails[i]
                    if hasattr(thumbnail, 'mark_as_processed'):
                        thumbnail.mark_as_processed()
                    break
                    
            print(f"✅ Marked as processed: {os.path.basename(image_path)}")
            
        except Exception as e:
            print(f"❌ Error marking image as processed: {e}")

class ClickableThumbnail(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, image_path, width=240, height=180, is_processed=False, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.is_processed = is_processed
        self.is_selected = False  # НОВЕ: чи обране зображення
        
        # Встановлюємо розмір
        self.setFixedSize(width, height)
        
        # Завантажуємо і масштабуємо зображення
        self.load_and_scale_image(width, height)
        
        # Встановлюємо стиль
        self.update_style()
        
        # Налаштування взаємодії
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)
    
    def set_selected(self, selected):
        """Встановити стан обраного зображення"""
        self.is_selected = selected
        self.update_style()

    def mark_as_unprocessed(self):
        """Позначити зображення як необроблене"""
        self.is_processed = False
        self.update_style()
    
    def load_and_scale_image(self, width, height):
        """Завантаження та масштабування зображення"""
        try:
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                # Масштабуємо зберігаючи пропорції
                scaled_pixmap = pixmap.scaled(width-4, height-4, 
                                            Qt.KeepAspectRatio, 
                                            Qt.SmoothTransformation)
                self.setPixmap(scaled_pixmap)
            else:
                self.setText(f"Error loading\n{os.path.basename(self.image_path)}")
        except Exception as e:
            self.setText(f"Error\n{os.path.basename(self.image_path)}")
    
    def update_style(self):
        """Оновлення стилю з урахуванням всіх станів"""
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
    
    def mark_as_processed(self):
        """Позначити зображення як оброблене"""
        self.is_processed = True
        self.update_style()
    
    def mousePressEvent(self, event):
        """Обробка кліка миші - ВИПРАВЛЕНА ВЕРСІЯ"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        # НЕ викликаємо super() для уникнення конфліктів


    