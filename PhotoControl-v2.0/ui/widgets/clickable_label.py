#!/usr/bin/env python3
"""
ClickableLabel - Доповнення відсутніх методів малювання
Додаємо візуальні індикатори центру, точки аналізу та спеціальних режимів
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
    ДОПОВНЕНИЙ візуальними індикаторами
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
        self.scale_edge_point: Optional[Tuple[int, int]] = None
        
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
        self.scale_edge_point = None
        
        self.setText("Відкрийте зображення або папку для початку")
        self.zoom_widget.hide()
    
    def _update_display(self):
        """Оновлення відображення зображення з масштабуванням"""
        if not self.current_image:
            return
        
        # Конвертація PIL Image в QPixmap
        qt_image = ImageQt(self.current_image)
        self.current_pixmap = QPixmap.fromImage(qt_image)
        
        # Розрахунок масштабу для підгонки під віджет
        widget_size = self.size()
        pixmap_size = self.current_pixmap.size()
        
        scale_x = widget_size.width() / pixmap_size.width()
        scale_y = widget_size.height() / pixmap_size.height()
        self.image_scale_factor = min(scale_x, scale_y, 1.0)  # Не збільшуємо понад оригінал
        
        # Масштабування pixmap
        if self.image_scale_factor < 1.0:
            scaled_size = pixmap_size * self.image_scale_factor
            self.current_pixmap = self.current_pixmap.scaled(
                scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        
        # Встановлення pixmap
        self.setPixmap(self.current_pixmap)
    
    # ===============================
    # МАЛЮВАННЯ ВІЗУАЛЬНИХ ІНДИКАТОРІВ (НОВІ МЕТОДИ)
    # ===============================
    
    def paintEvent(self, event):
        """
        ДОПОВНЕНИЙ paintEvent з візуальними індикаторами
        """
        # Спочатку стандартне малювання QLabel
        super().paintEvent(event)
        
        # Якщо немає зображення, не малюємо індикатори
        if not self.current_image or not self.current_pixmap:
            return
        
        # Створюємо painter для додаткових елементів
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        try:
            # Малювання центру сітки
            self._draw_grid_center(painter)
            
            # Малювання точки масштабу
            if self.scale_edge_point:
                self._draw_scale_edge_point(painter)
            
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
    
    def _draw_scale_edge_point(self, painter: QPainter):
        """Малювання точки масштабу"""
        if not self.scale_edge_point:
            return
        
        x, y = self.scale_edge_point
        widget_coords = self._image_to_widget_coords(x, y)
        if not widget_coords:
            return
        
        widget_x, widget_y = widget_coords
        
        # Синій квадрат для точки масштабу
        painter.setPen(QPen(QColor(0, 0, 255), 2))
        painter.setBrush(QBrush(QColor(0, 0, 255, 100)))
        painter.drawRect(widget_x - 6, widget_y - 6, 12, 12)
        
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
        painter.drawText(10, 35, "Клікніть на точку з відомою відстанню")
    
    # ===============================
    # КООРДИНАТНІ ПЕРЕТВОРЕННЯ
    # ===============================
    
    def _widget_to_image_coords(self, widget_x: int, widget_y: int) -> Optional[Tuple[int, int]]:
        """
        Перетворення координат віджету в координати зображення
        
        Args:
            widget_x, widget_y: Координати в віджеті
            
        Returns:
            Координати в зображенні або None якщо поза межами
        """
        if not self.current_pixmap:
            return None
        
        # Отримуємо розміри для центрування
        pixmap_rect = self.current_pixmap.rect()
        widget_rect = self.rect()
        
        # Розрахунок зміщення для центрування
        x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
        y_offset = (widget_rect.height() - pixmap_rect.height()) // 2
        
        # Координати відносно pixmap
        pixmap_x = widget_x - x_offset
        pixmap_y = widget_y - y_offset
        
        # Перевірка чи координати в межах pixmap
        if (pixmap_x < 0 or pixmap_x >= pixmap_rect.width() or
            pixmap_y < 0 or pixmap_y >= pixmap_rect.height()):
            return None
        
        # Перетворення в координати оригінального зображення
        image_x = int(pixmap_x / self.image_scale_factor)
        image_y = int(pixmap_y / self.image_scale_factor)
        
        # Обмеження координат зображення
        image_x = max(0, min(image_x, self.current_image.width - 1))
        image_y = max(0, min(image_y, self.current_image.height - 1))
        
        return (image_x, image_y)
    
    def _image_to_widget_coords(self, image_x: int, image_y: int) -> Optional[Tuple[int, int]]:
        """
        Перетворення координат зображення в координати віджету
        
        Args:
            image_x, image_y: Координати в зображенні
            
        Returns:
            Координати в віджеті або None якщо поза межами
        """
        if not self.current_pixmap or not self.current_image:
            return None
        
        # Перевірка меж
        if (image_x < 0 or image_x >= self.current_image.width or
            image_y < 0 or image_y >= self.current_image.height):
            return None
        
        # Масштабування до pixmap
        pixmap_x = int(image_x * self.image_scale_factor)
        pixmap_y = int(image_y * self.image_scale_factor)
        
        # Отримуємо розміри для центрування
        pixmap_rect = self.current_pixmap.rect()
        widget_rect = self.rect()
        
        # Розрахунок зміщення для центрування
        x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
        y_offset = (widget_rect.height() - pixmap_rect.height()) // 2
        
        # Координати в віджеті
        widget_x = pixmap_x + x_offset
        widget_y = pixmap_y + y_offset
        
        return (widget_x, widget_y)
    
    # ===============================
    # ОБРОБКА ПОДІЙ МИШІ
    # ===============================
    
    def mousePressEvent(self, event):
        """Обробка натискання миші"""
        if event.button() == Qt.LeftButton and self.current_image:
            widget_x, widget_y = event.x(), event.y()
            image_coords = self._widget_to_image_coords(widget_x, widget_y)
            
            if image_coords:
                image_x, image_y = image_coords
                
                if self.center_setting_mode:
                    # Режим налаштування центру - встановлюємо новий центр
                    self.set_grid_center(image_x, image_y)
                    self.center_moved.emit(image_x, image_y)
                    
                elif self.scale_edge_mode:
                    # Режим налаштування масштабу - встановлюємо точку масштабу
                    self.scale_edge_point = (image_x, image_y)
                    self.scale_edge_set.emit(image_x, image_y)
                    self.update()
                    
                else:
                    # Звичайний режим - встановлюємо точку аналізу
                    self.current_analysis_point = (image_x, image_y)
                    self.clicked.emit(image_x, image_y)
                    
                    # Підготовка до можливого перетягування
                    self.dragging = False
                    self.drag_start_pos = event.pos()
                    
                self.update()
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Обробка руху миші"""
        if self.current_image:
            widget_x, widget_y = event.x(), event.y()
            image_coords = self._widget_to_image_coords(widget_x, widget_y)
            
            if image_coords:
                image_x, image_y = image_coords
                
                # Сигнал руху миші для підказок
                self.mouse_moved.emit(image_x, image_y)
                
                # Перетягування точки аналізу
                if (event.buttons() & Qt.LeftButton and 
                    self.current_analysis_point and 
                    not self.center_setting_mode and 
                    not self.scale_edge_mode):
                    
                    # Перевірка початку перетягування
                    if not self.dragging:
                        drag_distance = (event.pos() - self.drag_start_pos).manhattanLength()
                        if drag_distance > 3:  # Мінімальна відстань для початку перетягування
                            self.dragging = True
                    
                    if self.dragging:
                        self.current_analysis_point = (image_x, image_y)
                        self.dragged.emit(image_x, image_y)
                        self.update()
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Обробка відпускання миші"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
        
        super().mouseReleaseEvent(event)
    
    # ===============================
    # КЛАВІАТУРНЕ УПРАВЛІННЯ
    # ===============================
    
    def keyPressEvent(self, event):
        """Обробка натискання клавіш"""
        if not self.center_setting_mode or not self.current_image:
            super().keyPressEvent(event)
            return
        
        # Визначення швидкості руху
        if event.modifiers() & Qt.ShiftModifier:
            speed = self.move_speed_fast
        elif event.modifiers() & Qt.ControlModifier:
            speed = self.move_speed_slow
        else:
            speed = self.move_speed_normal
        
        # Рух центру сітки
        dx, dy = 0, 0
        if event.key() == Qt.Key_Left:
            dx = -speed
        elif event.key() == Qt.Key_Right:
            dx = speed
        elif event.key() == Qt.Key_Up:
            dy = -speed
        elif event.key() == Qt.Key_Down:
            dy = speed
        elif event.key() == Qt.Key_Escape:
            # Вихід з режиму налаштування
            self.set_center_setting_mode(False)
            return
        
        if dx != 0 or dy != 0:
            # Переміщення центру
            new_x = max(0, min(self.grid_center_x + dx, self.current_image.width - 1))
            new_y = max(0, min(self.grid_center_y + dy, self.current_image.height - 1))
            
            self.set_grid_center(new_x, new_y)
            self.center_moved.emit(new_x, new_y)
            
            # Налаштування повторення клавіш
            self.current_key_action = (dx, dy)
            if not self.key_repeat_timer.isActive():
                self.key_repeat_timer.start(50)  # Повторення кожні 50мс
        
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Обробка відпускання клавіш"""
        # Зупинка повторення клавіш
        self.key_repeat_timer.stop()
        self.current_key_action = None
        super().keyReleaseEvent(event)
    
    def _handle_key_repeat(self):
        """Обробка повторення клавіш"""
        if not self.current_key_action or not self.current_image:
            self.key_repeat_timer.stop()
            return
        
        dx, dy = self.current_key_action
        
        # Переміщення центру
        new_x = max(0, min(self.grid_center_x + dx, self.current_image.width - 1))
        new_y = max(0, min(self.grid_center_y + dy, self.current_image.height - 1))
        
        self.set_grid_center(new_x, new_y)
        self.center_moved.emit(new_x, new_y)
    
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
    
    def set_scale_edge_point(self, x: int, y: int):
        """Встановлення точки масштабу програмно"""
        if self.current_image:
            self.scale_edge_point = (x, y)
            self.update()
    
    def clear_scale_edge_point(self):
        """Очищення точки масштабу"""
        self.scale_edge_point = None
        self.update()
    
    def set_center_setting_mode(self, enabled: bool):
        """Увімкнення/вимкнення режиму налаштування центру"""
        self.center_setting_mode = enabled
        if enabled:
            self.scale_edge_mode = False
            self.setFocus()  # Для клавіатурного управління
        self.update()
    
    def set_scale_edge_mode(self, enabled: bool):
        """Увімкнення/вимкнення режиму налаштування масштабу"""
        self.scale_edge_mode = enabled
        if enabled:
            self.center_setting_mode = False
        self.update()
    
    def get_current_analysis_point(self) -> Optional[Tuple[int, int]]:
        """Отримання поточної точки аналізу"""
        return self.current_analysis_point
    
    def get_grid_center(self) -> Tuple[int, int]:
        """Отримання координат центру сітки"""
        return (self.grid_center_x, self.grid_center_y)
    
    def get_scale_edge_point(self) -> Optional[Tuple[int, int]]:
        """Отримання координат точки масштабу"""
        return self.scale_edge_point
    
    def has_image(self) -> bool:
        """Перевірка чи завантажено зображення"""
        return self.current_image is not None
    
    def resizeEvent(self, event):
        """Обробка зміни розміру віджету"""
        super().resizeEvent(event)
        
        # Перерахунок масштабування при зміні розміру
        if self.current_image:
            self._update_display()
    
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
            'has_scale_edge': self.scale_edge_point is not None,
            'center_mode': self.center_setting_mode,
            'scale_mode': self.scale_edge_mode
        }


# ===============================
# ТЕСТУВАННЯ
# ===============================

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
    from PIL import Image, ImageDraw
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Тест ClickableLabel з візуальними індикаторами")
            self.setGeometry(100, 100, 1200, 800)
            
            # Центральний віджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QHBoxLayout(central_widget)
            
            # Створення тестового зображення
            test_image = self.create_test_image()
            
            # ClickableLabel
            self.clickable_label = ClickableLabel()
            self.clickable_label.set_image(test_image)
            layout.addWidget(self.clickable_label)
            
            # Панель кнопок
            buttons_widget = QWidget()
            buttons_widget.setFixedWidth(200)
            buttons_layout = QVBoxLayout(buttons_widget)
            
            # Кнопки управління
            self.center_mode_btn = QPushButton("Режим налаштування центру")
            self.center_mode_btn.setCheckable(True)
            self.center_mode_btn.toggled.connect(self.toggle_center_mode)
            buttons_layout.addWidget(self.center_mode_btn)
            
            self.scale_mode_btn = QPushButton("Режим налаштування масштабу")
            self.scale_mode_btn.setCheckable(True)
            self.scale_mode_btn.toggled.connect(self.toggle_scale_mode)
            buttons_layout.addWidget(self.scale_mode_btn)
            
            clear_analysis_btn = QPushButton("Очистити точку аналізу")
            clear_analysis_btn.clicked.connect(self.clickable_label.clear_analysis_point)
            buttons_layout.addWidget(clear_analysis_btn)
            
            clear_scale_btn = QPushButton("Очистити точку масштабу")
            clear_scale_btn.clicked.connect(self.clickable_label.clear_scale_edge_point)
            buttons_layout.addWidget(clear_scale_btn)
            
            set_center_btn = QPushButton("Встановити центр (400, 300)")
            set_center_btn.clicked.connect(lambda: self.clickable_label.set_grid_center(400, 300))
            buttons_layout.addWidget(set_center_btn)
            
            set_analysis_btn = QPushButton("Встановити точку аналізу")
            set_analysis_btn.clicked.connect(lambda: self.clickable_label.set_analysis_point(300, 200))
            buttons_layout.addWidget(set_analysis_btn)
            
            info_btn = QPushButton("Показати інформацію")
            info_btn.clicked.connect(self.show_info)
            buttons_layout.addWidget(info_btn)
            
            buttons_layout.addStretch()
            
            layout.addWidget(buttons_widget)
            
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
            
            # Кола різних розмірів від центру
            for radius in [50, 100, 150, 200]:
                draw.ellipse([center_x-radius, center_y-radius, center_x+radius, center_y+radius], 
                            outline=(100, 100, 100), width=1)
            
            # Додаємо текст з координатами
            draw.text((10, 10), f"Розмір: {width} x {height}", fill=(0, 0, 0))
            draw.text((10, 30), f"Центр: ({center_x}, {center_y})", fill=(0, 0, 0))
            
            return image
        
        def toggle_center_mode(self, checked):
            """Перемикання режиму налаштування центру"""
            self.clickable_label.set_center_setting_mode(checked)
            if checked:
                self.scale_mode_btn.setChecked(False)
                print("Режим налаштування центру УВІМКНЕНО")
                print("Використовуйте стрілки для переміщення центру")
            else:
                print("Режим налаштування центру ВИМКНЕНО")
        
        def toggle_scale_mode(self, checked):
            """Перемикання режиму налаштування масштабу"""
            self.clickable_label.set_scale_edge_mode(checked)
            if checked:
                self.center_mode_btn.setChecked(False)
                print("Режим налаштування масштабу УВІМКНЕНО")
                print("Клікніть на точку з відомою відстанню")
            else:
                print("Режим налаштування масштабу ВИМКНЕНО")
        
        def on_image_clicked(self, x, y):
            """Обробка кліку на зображенні"""
            print(f"🖱️  Клік на зображенні: ({x}, {y})")
        
        def on_image_dragged(self, x, y):
            """Обробка перетягування на зображенні"""
            print(f"🔄 Перетягування: ({x}, {y})")
        
        def on_mouse_moved(self, x, y):
            """Обробка руху миші"""
            # Показуємо координати в заголовку вікна
            self.setWindowTitle(f"Тест ClickableLabel - Координати: ({x}, {y})")
        
        def on_center_moved(self, x, y):
            """Обробка переміщення центру"""
            print(f"🎯 Центр переміщено: ({x}, {y})")
        
        def on_scale_edge_set(self, x, y):
            """Обробка встановлення точки масштабу"""
            print(f"📏 Точка масштабу встановлена: ({x}, {y})")
        
        def show_info(self):
            """Показ інформації про поточний стан"""
            info = self.clickable_label.get_image_info()
            print("\n=== ІНФОРМАЦІЯ ПРО СТАН ===")
            for key, value in info.items():
                print(f"{key}: {value}")
            print("=" * 30)
    
    # Запуск тесту
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("=== Тестування ClickableLabel з ВІЗУАЛЬНИМИ ІНДИКАТОРАМИ ===")
    print("\nФункції для тестування:")
    print("1. 🖱️  Клік лівою кнопкою - встановлення точки аналізу (ЧЕРВОНЕ КОЛО)")
    print("2. 🔄 Перетягування - переміщення точки аналізу")
    print("3. 🎯 Кнопка 'Режим центру' + стрілки = переміщення ЗЕЛЕНОГО ХРЕСТИКА")
    print("4. 📏 Кнопка 'Режим масштабу' + клік = встановлення СИНЬОГО КВАДРАТА")
    print("5. ⚡ Shift+стрілки = швидке переміщення центру")
    print("6. 🐌 Ctrl+стрілки = повільне переміщення центру")
    print("7. 🚪 Esc = вихід з режиму")
    print("\nВізуальні індикатори:")
    print("🟢 ЗЕЛЕНИЙ ХРЕСТИК = центр азимутальної сітки")
    print("🔴 ЧЕРВОНЕ КОЛО = точка аналізу цілі")
    print("🔵 СИНІЙ КВАДРАТ = точка масштабу")
    print("🔴 ЧЕРВОНИЙ ХРЕСТИК = центр в режимі налаштування")
    
    sys.exit(app.exec_())