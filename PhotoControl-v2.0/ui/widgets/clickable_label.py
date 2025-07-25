#!/usr/bin/env python3
"""
Клікабельне зображення з підтримкою азимутальної сітки
Основний віджет для відображення та взаємодії з зображеннями
"""

from typing import Optional, Tuple
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont, QCursor
from PIL import Image
from PIL.ImageQt import ImageQt

from ui.widgets.zoom_widget import ZoomWidget


class ClickableLabel(QLabel):
    """
    Клікабельний віджет для відображення зображень з азимутальною сіткою
    
    Функціональність:
    - Клік лівою кнопкою миші - встановлення точки аналізу
    - Перетягування - зміщення точки аналізу
    - Клавіатурне управління центром сітки (стрілки + Shift/Ctrl)
    - Режими: звичайний, налаштування центру, налаштування масштабу
    - Зум-функціональність з точними розмірами
    - Візуальні підказки та індикатори
    """
    
    # Сигнали для взаємодії з головним вікном
    clicked = pyqtSignal(int, int)                    # Клік на зображенні
    dragged = pyqtSignal(int, int)                    # Перетягування точки
    mouse_moved = pyqtSignal(int, int)                # Рух миші (для підказок)
    center_moved = pyqtSignal(int, int)               # Зміщення центру клавіатурою
    scale_edge_set = pyqtSignal(int, int)             # Встановлення точки масштабу
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Основні властивості
        self.current_image: Optional[Image.Image] = None
        self.current_pixmap: Optional[QPixmap] = None
        self.image_scale_factor = 1.0
        
        # Стан взаємодії
        self.dragging = False
        self.drag_start_pos = QPoint()
        self.current_analysis_point: Optional[Tuple[int, int]] = None
        
        # Режими роботи
        self.center_setting_mode = False
        self.scale_edge_mode = False
        
        # Координати сітки
        self.grid_center_x = 0
        self.grid_center_y = 0
        
        # Зум-функціональність
        self.zoom_widget = ZoomWidget(self)
        self.zoom_widget.hide()
        
        # Налаштування віджету
        self._setup_widget()
        self._setup_keyboard()
    
    def _setup_widget(self):
        """Налаштування основних властивостей віджету"""
        # Розміри та вигляд
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #ccc;
                background-color: white;
                border-radius: 4px;
            }
            QLabel:focus {
                border: 2px solid #007ACC;
            }
        """)
        
        # Вирівнювання та масштабування
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(False)  # Ручне масштабування
        
        # Підтримка фокусу для клавіатури
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Відстеження миші для підказок
        self.setMouseTracking(True)
        
        # Початковий текст
        self.setText("Відкрийте зображення або папку для початку")
    
    def _setup_keyboard(self):
        """Налаштування клавіатурних скорочень"""
        # Таймер для повторення клавіш
        self.key_repeat_timer = QTimer()
        self.key_repeat_timer.timeout.connect(self._handle_key_repeat)
        self.current_key_action = None
        
        # Швидкість переміщення
        self.move_speed_normal = 1
        self.move_speed_fast = 5
        self.move_speed_slow = 0.2
    
    # ===============================
    # ЗАВАНТАЖЕННЯ ТА ВІДОБРАЖЕННЯ ЗОБРАЖЕНЬ
    # ===============================
    
    def set_image(self, image: Image.Image, grid_center: Tuple[int, int] = None):
        """
        Встановлення нового зображення для відображення
        
        Args:
            image: PIL Image для відображення
            grid_center: Координати центру сітки (x, y)
        """
        if not image:
            self.clear_image()
            return
        
        self.current_image = image
        self.current_analysis_point = None
        
        # Встановлення центру сітки
        if grid_center:
            self.grid_center_x, self.grid_center_y = grid_center
        else:
            self.grid_center_x = image.width // 2
            self.grid_center_y = image.height // 2
        
        # Конвертація в QPixmap та відображення
        self._update_display()
        
        print(f"Зображення встановлено: {image.width}×{image.height}")
        print(f"Центр сітки: ({self.grid_center_x}, {self.grid_center_y})")
    
    def clear_image(self):
        """Очищення поточного зображення"""
        self.current_image = None
        self.current_pixmap = None
        self.current_analysis_point = None
        self.grid_center_x = 0
        self.grid_center_y = 0
        
        self.setText("Відкрийте зображення або папку для початку")
        self.zoom_widget.hide()
    
    def _update_display(self):
        """Оновлення відображення зображення з масштабуванням"""
        if not self.current_image:
            return
        
        # Конвертація PIL Image в QPixmap
        qt_image = ImageQt(self.current_image)
        self.current_pixmap = QPixmap.fromImage(qt_image)
        
        # Розрахунок масштабу для вміщення в віджет
        self.image_scale_factor = self._calculate_scale_factor()
        
        # Масштабування та відображення
        if self.image_scale_factor != 1.0:
            scaled_pixmap = self.current_pixmap.scaled(
                int(self.current_image.width * self.image_scale_factor),
                int(self.current_image.height * self.image_scale_factor),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        else:
            self.setPixmap(self.current_pixmap)
        
        # Оновлення зуму
        self._update_zoom_widget()
    
    def _calculate_scale_factor(self) -> float:
        """
        Розрахунок коефіцієнта масштабування для вміщення зображення
        
        Returns:
            Коефіцієнт масштабування (1.0 = оригінальний розмір)
        """
        if not self.current_image:
            return 1.0
        
        # Доступний простір (з відступами)
        available_width = self.width() - 20
        available_height = self.height() - 20
        
        # Коефіцієнти масштабування по осях
        scale_x = available_width / self.current_image.width
        scale_y = available_height / self.current_image.height
        
        # Вибираємо менший коефіцієнт для вміщення
        scale_factor = min(scale_x, scale_y, 1.0)  # Не збільшуємо більше оригіналу
        
        return scale_factor
    
    # ===============================
    # ОБРОБКА ПОДІЙ МИШІ
    # ===============================
    
    def mousePressEvent(self, event):
        """Обробка натискання кнопки миші"""
        if event.button() == Qt.LeftButton and self.current_image:
            # Конвертація координат віджету в координати зображення
            image_coords = self._widget_to_image_coords(event.x(), event.y())
            
            if image_coords and self._is_click_on_image(event.x(), event.y()):
                image_x, image_y = image_coords
                
                if self.center_setting_mode:
                    # Режим налаштування центру сітки
                    self._handle_center_setting(image_x, image_y)
                elif self.scale_edge_mode:
                    # Режим налаштування масштабу
                    self._handle_scale_edge_setting(image_x, image_y)
                else:
                    # Звичайний режим - встановлення точки аналізу
                    self._handle_analysis_point_setting(image_x, image_y, event)
            
            # Встановлюємо фокус для клавіатурного управління
            self.setFocus()
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Обробка руху миші"""
        # Завжди відправляємо координати для підказок
        image_coords = self._widget_to_image_coords(event.x(), event.y())
        if image_coords:
            self.mouse_moved.emit(image_coords[0], image_coords[1])
        
        # Оновлення зуму при русі миші
        if self.current_image and self._is_click_on_image(event.x(), event.y()):
            self._update_zoom_at_position(event.x(), event.y())
        
        # Перетягування точки аналізу
        if (self.dragging and event.buttons() & Qt.LeftButton and 
            not self.scale_edge_mode and not self.center_setting_mode):
            
            image_coords = self._widget_to_image_coords(event.x(), event.y())
            if image_coords and self._is_click_on_image(event.x(), event.y()):
                image_x, image_y = image_coords
                self.current_analysis_point = (image_x, image_y)
                self.dragged.emit(image_x, image_y)
                self.update()  # Перемалювання для відображення нової позиції
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Обробка відпускання кнопки миші"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
        
        super().mouseReleaseEvent(event)
    
    def _handle_center_setting(self, x: int, y: int):
        """Обробка встановлення центру сітки"""
        self.grid_center_x = x
        self.grid_center_y = y
        self.update()  # Перемалювання для відображення нового центру
        print(f"Центр сітки встановлено: ({x}, {y})")
    
    def _handle_scale_edge_setting(self, x: int, y: int):
        """Обробка встановлення точки масштабу"""
        self.scale_edge_set.emit(x, y)
        print(f"Точка масштабу встановлена: ({x}, {y})")
    
    def _handle_analysis_point_setting(self, x: int, y: int, event):
        """Обробка встановлення точки аналізу"""
        self.current_analysis_point = (x, y)
        self.drag_start_pos = event.pos()
        self.dragging = True
        
        self.clicked.emit(x, y)
        self.update()  # Перемалювання для відображення точки
    
    # ===============================
    # ОБРОБКА КЛАВІАТУРИ
    # ===============================
    
    def keyPressEvent(self, event):
        """Обробка натискання клавіш для управління центром сітки"""
        if not self.current_image or not self.center_setting_mode:
            super().keyPressEvent(event)
            return
        
        key = event.key()
        modifiers = event.modifiers()
        
        # Визначення швидкості переміщення
        if modifiers & Qt.ControlModifier:
            speed = self.move_speed_slow
        elif modifiers & Qt.ShiftModifier:
            speed = self.move_speed_fast
        else:
            speed = self.move_speed_normal
        
        # Обробка клавіш стрілок
        move_actions = {
            Qt.Key_Left: (-speed, 0),
            Qt.Key_Right: (speed, 0),
            Qt.Key_Up: (0, -speed),
            Qt.Key_Down: (0, speed)
        }
        
        if key in move_actions:
            dx, dy = move_actions[key]
            self._move_grid_center(dx, dy)
            
            # Запуск таймера для повторення
            self.current_key_action = (dx, dy)
            if not self.key_repeat_timer.isActive():
                self.key_repeat_timer.start(100)  # Повторення кожні 100мс
        
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Обробка відпускання клавіш"""
        # Зупинка повторення клавіш
        self.key_repeat_timer.stop()
        self.current_key_action = None
        
        super().keyReleaseEvent(event)
    
    def _handle_key_repeat(self):
        """Обробка повторення натиснутої клавіші"""
        if self.current_key_action and self.center_setting_mode:
            dx, dy = self.current_key_action
            self._move_grid_center(dx, dy)
    
    def _move_grid_center(self, dx: int, dy: int):
        """
        Переміщення центру сітки на вказану відстань
        
        Args:
            dx, dy: Зміщення в пікселях
        """
        new_x = max(0, min(self.current_image.width - 1, self.grid_center_x + dx))
        new_y = max(0, min(self.current_image.height - 1, self.grid_center_y + dy))
        
        if new_x != self.grid_center_x or new_y != self.grid_center_y:
            self.grid_center_x = new_x
            self.grid_center_y = new_y
            
            self.center_moved.emit(new_x, new_y)
            self.update()  # Перемалювання
    
    # ===============================
    # РЕЖИМИ РОБОТИ
    # ===============================
    
    def set_center_setting_mode(self, enabled: bool):
        """
        Увімкнення/вимкнення режиму налаштування центру сітки
        
        Args:
            enabled: True для увімкнення режиму
        """
        self.center_setting_mode = enabled
        
        if enabled:
            self.setCursor(Qt.CrossCursor)
            self.setToolTip("Клікніть для встановлення центру сітки\n"
                          "Стрілки: переміщення (Shift=швидко, Ctrl=повільно)")
            print("Режим налаштування центру увімкнено")
        else:
            self.setCursor(Qt.ArrowCursor)
            self.setToolTip("")
            print("Режим налаштування центру вимкнено")
        
        self.update()
    
    def set_scale_edge_mode(self, enabled: bool):
        """
        Увімкнення/вимкнення режиму налаштування масштабу
        
        Args:
            enabled: True для увімкнення режиму
        """
        self.scale_edge_mode = enabled
        
        if enabled:
            self.setCursor(Qt.CrossCursor)
            self.setToolTip("Клікніть на крайню точку для встановлення масштабу")
            print("Режим налаштування масштабу увімкнено")
        else:
            self.setCursor(Qt.ArrowCursor)
            self.setToolTip("")
            print("Режим налаштування масштабу вимкнено")
        
        self.update()
    
    # ===============================
    # ЗУМІНГ ТА ВІЗУАЛІЗАЦІЯ
    # ===============================
    
    def _update_zoom_widget(self):
        """Оновлення зум-віджету при зміні зображення"""
        if self.current_image and hasattr(self, 'zoom_widget'):
            self.zoom_widget.set_image(self.current_image)
    
    def _update_zoom_at_position(self, widget_x: int, widget_y: int):
        """
        Оновлення зуму для вказаної позиції
        
        Args:
            widget_x, widget_y: Координати в віджеті
        """
        image_coords = self._widget_to_image_coords(widget_x, widget_y)
        if image_coords and hasattr(self, 'zoom_widget'):
            image_x, image_y = image_coords
            self.zoom_widget.update_position(image_x, image_y)
    
    def show_zoom_at_center(self):
        """Показати зум в області центру сітки"""
        if self.current_image and hasattr(self, 'zoom_widget'):
            self.zoom_widget.update_position(self.grid_center_x, self.grid_center_y)
            self.zoom_widget.show_zoom()
    
    def hide_zoom(self):
        """Сховати зум-віджет"""
        if hasattr(self, 'zoom_widget'):
            self.zoom_widget.hide_zoom()
    
    # ===============================
    # МАЛЮВАННЯ ТА ВІЗУАЛІЗАЦІЯ
    # ===============================
    
    def paintEvent(self, event):
        """Перемалювання віджету з додатковими елементами"""
        # Спочатку малюємо базове зображення
        super().paintEvent(event)
        
        if not self.current_image:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        try:
            # Малювання центру сітки
            self._draw_grid_center(painter)
            
            # Малювання точки аналізу
            if self.current_analysis_point:
                self._draw_analysis_point(painter)
            
            # Додаткові індикатори для спеціальних режимів
            if self.center_setting_mode:
                self._draw_center_mode_indicators(painter)
            elif self.scale_edge_mode:
                self._draw_scale_mode_indicators(painter)
        
        finally:
            painter.end()
    
    def _draw_grid_center(self, painter: QPainter):
        """Малювання центру азимутальної сітки"""
        widget_coords = self._image_to_widget_coords(self.grid_center_x, self.grid_center_y)
        if not widget_coords:
            return
        
        widget_x, widget_y = widget_coords
        
        # Колір та розмір залежно від режиму
        if self.center_setting_mode:
            color = QColor(255, 0, 0)  # Червоний в режимі налаштування
            size = 20
        else:
            color = QColor(0, 255, 0)  # Зелений в звичайному режимі
            size = 15
        
        # Хрестик центру
        painter.setPen(QPen(color, 2))
        painter.drawLine(widget_x - size//2, widget_y, widget_x + size//2, widget_y)
        painter.drawLine(widget_x, widget_y - size//2, widget_x, widget_y + size//2)
        
        # Коло навколо центру
        painter.setPen(QPen(color, 1))
        painter.drawEllipse(widget_x - size//2, widget_y - size//2, size, size)
    
    def _draw_analysis_point(self, painter: QPainter):
        """Малювання точки аналізу"""
        if not self.current_analysis_point:
            return
        
        x, y = self.current_analysis_point
        widget_coords = self._image_to_widget_coords(x, y)
        if not widget_coords:
            return
        
        widget_x, widget_y = widget_coords
        
        # Червоне коло для точки аналізу
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.setBrush(QBrush(QColor(255, 0, 0, 100)))
        painter.drawEllipse(widget_x - 8, widget_y - 8, 16, 16)
        
        # Біла точка в центрі
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(widget_x - 2, widget_y - 2, 4, 4)
    
    def _draw_center_mode_indicators(self, painter: QPainter):
        """Додаткові індикатори для режиму налаштування центру"""
        # Підказка в лівому верхньому куті
        painter.setPen(QPen(QColor(255, 0, 0), 1))
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(10, 20, "РЕЖИМ НАЛАШТУВАННЯ ЦЕНТРУ")
        painter.drawText(10, 35, "Стрілки: переміщення | Shift: швидко | Ctrl: повільно")
    
    def _draw_scale_mode_indicators(self, painter: QPainter):
        """Додаткові індикатори для режиму налаштування масштабу"""
        # Підказка в лівому верхньому куті
        painter.setPen(QPen(QColor(0, 0, 255), 1))
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(10, 20, "РЕЖИМ НАЛАШТУВАННЯ МАСШТАБУ")
        painter.drawText(10, 35, "Клікніть на крайню точку відомої відстані")
    
    # ===============================
    # КОНВЕРТАЦІЯ КООРДИНАТ
    # ===============================
    
    def _widget_to_image_coords(self, widget_x: int, widget_y: int) -> Optional[Tuple[int, int]]:
        """
        Конвертація координат віджету в координати зображення
        
        Args:
            widget_x, widget_y: Координати в віджеті
            
        Returns:
            Кортеж (image_x, image_y) або None якщо конвертація неможлива
        """
        if not self.current_pixmap or not self.current_image:
            return None
        
        # Отримуємо розміри відображуваного зображення
        pixmap_rect = self.pixmap().rect()
        widget_rect = self.rect()
        
        # Розрахунок зміщення для центрування
        x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
        y_offset = (widget_rect.height() - pixmap_rect.height()) // 2
        
        # Координати відносно pixmap
        pixmap_x = widget_x - x_offset
        pixmap_y = widget_y - y_offset
        
        # Перевірка меж
        if (pixmap_x < 0 or pixmap_x >= pixmap_rect.width() or
            pixmap_y < 0 or pixmap_y >= pixmap_rect.height()):
            return None
        
        # Конвертація в координати оригінального зображення
        image_x = int(pixmap_x / self.image_scale_factor)
        image_y = int(pixmap_y / self.image_scale_factor)
        
        # Обмеження межами зображення
        image_x = max(0, min(image_x, self.current_image.width - 1))
        image_y = max(0, min(image_y, self.current_image.height - 1))
        
        return (image_x, image_y)
    
    def _image_to_widget_coords(self, image_x: int, image_y: int) -> Optional[Tuple[int, int]]:
        """
        Конвертація координат зображення в координати віджету
        
        Args:
            image_x, image_y: Координати в зображенні
            
        Returns:
            Кортеж (widget_x, widget_y) або None якщо конвертація неможлива
        """
        if not self.current_pixmap or not self.current_image:
            return None
        
        # Конвертація в координати pixmap
        pixmap_x = int(image_x * self.image_scale_factor)
        pixmap_y = int(image_y * self.image_scale_factor)
        
        # Отримуємо розміри для центрування
        pixmap_rect = self.pixmap().rect()
        widget_rect = self.rect()
        
        # Розрахунок зміщення для центрування
        x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
        y_offset = (widget_rect.height() - pixmap_rect.height()) // 2
        
        # Координати в віджеті
        widget_x = pixmap_x + x_offset
        widget_y = pixmap_y + y_offset
        
        return (widget_x, widget_y)
    
    def _is_click_on_image(self, widget_x: int, widget_y: int) -> bool:
        """
        Перевірка чи клік знаходиться на зображенні
        
        Args:
            widget_x, widget_y: Координати кліку в віджеті
            
        Returns:
            True якщо клік на зображенні
        """
        return self._widget_to_image_coords(widget_x, widget_y) is not None
    
    # ===============================
    # ПУБЛІЧНІ МЕТОДИ ДЛЯ ЗОВНІШНЬОГО УПРАВЛІННЯ
    # ===============================
    
    def set_grid_center(self, x: int, y: int):
        """Встановлення центру сітки програмно"""
        if self.current_image:
            self.grid_center_x = max(0, min(x, self.current_image.width - 1))
            self.grid_center_y = max(0, min(y, self.current_image.height - 1))
            self.update()
    
    def set_analysis_point(self, x: int, y: int):
        """Встановлення точки аналізу програмно"""
        if self.current_image:
            self.current_analysis_point = (x, y)
            self.update()
    
    def clear_analysis_point(self):
        """Очищення точки аналізу"""
        self.current_analysis_point = None
        self.update()
    
    def get_current_analysis_point(self) -> Optional[Tuple[int, int]]:
        """Отримання поточної точки аналізу"""
        return self.current_analysis_point
    
    def get_grid_center(self) -> Tuple[int, int]:
        """Отримання координат центру сітки"""
        return (self.grid_center_x, self.grid_center_y)
    
    def resizeEvent(self, event):
        """Обробка зміни розміру віджету"""
        super().resizeEvent(event)
        
        # Перерахунок масштабування при зміні розміру
        if self.current_image:
            self._update_display()
    
    def has_image(self) -> bool:
        """Перевірка чи завантажено зображення"""
        return self.current_image is not None
    
    def get_image_info(self) -> dict:
        """Отримання інформації про поточне зображення"""
        if not self.current_image:
            return {}
        
        return {
            'width': self.current_image.width,
            'height': self.current_image.height,
            'scale_factor': self.image_scale_factor,
            'grid_center': (self.grid_center_x, self.grid_center_y),
            'has_analysis_point': self.current_analysis_point is not None,
            'center_mode': self.center_setting_mode,
            'scale_mode': self.scale_edge_mode
        }


if __name__ == "__main__":
    # Тестування віджету
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
    from PIL import Image, ImageDraw
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Тест ClickableLabel")
            self.setGeometry(100, 100, 1000, 700)
            
            # Центральний віджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Створення тестового зображення
            test_image = self.create_test_image()
            
            # ClickableLabel
            self.clickable_label = ClickableLabel()
            self.clickable_label.set_image(test_image)
            layout.addWidget(self.clickable_label)
            
            # Кнопки управління
            buttons_layout = QVBoxLayout()
            
            self.center_mode_btn = QPushButton("Режим налаштування центру")
            self.center_mode_btn.setCheckable(True)
            self.center_mode_btn.toggled.connect(self.toggle_center_mode)
            buttons_layout.addWidget(self.center_mode_btn)
            
            self.scale_mode_btn = QPushButton("Режим налаштування масштабу")
            self.scale_mode_btn.setCheckable(True)
            self.scale_mode_btn.toggled.connect(self.toggle_scale_mode)
            buttons_layout.addWidget(self.scale_mode_btn)
            
            clear_btn = QPushButton("Очистити точку аналізу")
            clear_btn.clicked.connect(self.clickable_label.clear_analysis_point)
            buttons_layout.addWidget(clear_btn)
            
            layout.addLayout(buttons_layout)
            
            # Підключення сигналів
            self.clickable_label.clicked.connect(self.on_image_clicked)
            self.clickable_label.dragged.connect(self.on_image_dragged)
            self.clickable_label.mouse_moved.connect(self.on_mouse_moved)
            self.clickable_label.center_moved.connect(self.on_center_moved)
            self.clickable_label.scale_edge_set.connect(self.on_scale_edge_set)
        
        def create_test_image(self):
            """Створення тестового зображення з сіткою"""
            width, height = 800, 600
            image = Image.new('RGB', (width, height), (240, 240, 240))
            draw = ImageDraw.Draw(image)
            
            # Малюємо сітку
            for i in range(0, width, 50):
                draw.line([(i, 0), (i, height)], fill=(200, 200, 200))
            for i in range(0, height, 50):
                draw.line([(0, i), (width, i)], fill=(200, 200, 200))
            
            # Центральні лінії
            center_x, center_y = width // 2, height // 2
            draw.line([(center_x, 0), (center_x, height)], fill=(150, 150, 150), width=2)
            draw.line([(0, center_y), (width, center_y)], fill=(150, 150, 150), width=2)
            
            # Коло в центрі
            draw.ellipse([center_x-30, center_y-30, center_x+30, center_y+30], 
                        outline=(100, 100, 100), width=2)
            
            return image
        
        def toggle_center_mode(self, checked):
            """Перемикання режиму налаштування центру"""
            self.clickable_label.set_center_setting_mode(checked)
            if checked:
                self.scale_mode_btn.setChecked(False)
                self.clickable_label.show_zoom_at_center()
            else:
                self.clickable_label.hide_zoom()
        
        def toggle_scale_mode(self, checked):
            """Перемикання режиму налаштування масштабу"""
            self.clickable_label.set_scale_edge_mode(checked)
            if checked:
                self.center_mode_btn.setChecked(False)
        
        def on_image_clicked(self, x, y):
            """Обробка кліку на зображенні"""
            print(f"Клік на зображенні: ({x}, {y})")
        
        def on_image_dragged(self, x, y):
            """Обробка перетягування на зображенні"""
            print(f"Перетягування: ({x}, {y})")
        
        def on_mouse_moved(self, x, y):
            """Обробка руху миші"""
            # Не виводимо кожен рух, щоб не засмічувати консоль
            pass
        
        def on_center_moved(self, x, y):
            """Обробка переміщення центру"""
            print(f"Центр переміщено: ({x}, {y})")
        
        def on_scale_edge_set(self, x, y):
            """Обробка встановлення точки масштабу"""
            print(f"Точка масштабу встановлена: ({x}, {y})")
    
    # Запуск тесту
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("=== Тестування ClickableLabel ===")
    print("Функції для тестування:")
    print("1. Клік лівою кнопкою - встановлення точки аналізу")
    print("2. Перетягування - переміщення точки аналізу")
    print("3. Кнопка 'Режим налаштування центру' - клавіші стрілок для переміщення")
    print("4. Кнопка 'Режим налаштування масштабу' - клік для встановлення краю")
    print("5. Shift+стрілки - швидке переміщення")
    print("6. Ctrl+стрілки - повільне переміщення")
    
    sys.exit(app.exec_())