#!/usr/bin/env python3
"""
ZoomWidget - Повний функціонал збільшення
Завершений віджет для детального перегляду області зображення
"""

from typing import Optional, Tuple
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt


class ZoomWidget(QWidget):
    """
    ЗАВЕРШЕНИЙ віджет для відображення збільшеної області зображення
    
    Функціональність:
    - Збільшення області навколо курсора або центру сітки (2x-8x)
    - Відображення координат поточної позиції
    - Хрестик в центрі для точного позиціонування
    - Автоматичне приховування/показ
    - Плавне оновлення при русі миші
    - Кешування для оптимізації продуктивності
    - Підтримка різних режимів (center, scale, normal)
    - Розумне позиціонування відносно курсора
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Параметри зуму
        self.zoom_factor = 4  # Коефіцієнт збільшення
        self.zoom_size = 100  # Розмір області для збільшення (в пікселях оригіналу)
        self.widget_size = 200  # Розмір віджету на екрані
        
        # Дані зображення
        self.source_image: Optional[Image.Image] = None
        self.current_x = 0
        self.current_y = 0
        
        # Кеш для оптимізації
        self.cached_zoom: Optional[QPixmap] = None
        self.cache_position = (-1, -1)
        self.cache_factor = -1
        
        # Стан віджету
        self.is_visible = False
        self.current_mode = "normal"  # normal, center, scale
        
        # Таймери
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide_zoom)
        
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._delayed_update)
        
        # Налаштування віджету
        self._setup_widget()
        self._setup_layout()
    
    def _setup_widget(self):
        """Налаштування основних властивостей віджету"""
        # Розміри та позиція
        self.setFixedSize(self.widget_size + 40, self.widget_size + 60)
        
        # Стилі з кращою видимістю
        self.setStyleSheet("""
            ZoomWidget {
                background-color: rgba(248, 249, 250, 240);
                border: 2px solid #495057;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
        """)
        
        # Завжди зверху без рамки
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Ігнорування подій миші (щоб не заважати взаємодії)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        # Початково приховано
        self.hide()
    
    def _setup_layout(self):
        """Налаштування макету віджету"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        self.setLayout(layout)
        
        # Заголовок з режимом
        self.title_label = QLabel("Зум x4")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 12px;
                color: #212529;
                background-color: transparent;
                padding: 4px;
                border-radius: 4px;
                background-color: rgba(255, 255, 255, 150);
            }
        """)
        layout.addWidget(self.title_label)
        
        # Область зображення з рамкою
        self.image_label = QLabel()
        self.image_label.setFixedSize(self.widget_size, self.widget_size)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #6c757d;
                background-color: white;
                border-radius: 6px;
            }
        """)
        # Placeholder
        self.image_label.setText("Зум\nнедоступний")
        self.image_label.setWordWrap(True)
        layout.addWidget(self.image_label)
        
        # Координати з кращим стилем
        self.coords_label = QLabel("(0, 0)")
        self.coords_label.setAlignment(Qt.AlignCenter)
        self.coords_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: bold;
                color: #495057;
                background-color: rgba(255, 255, 255, 150);
                padding: 3px 8px;
                border-radius: 4px;
                border: 1px solid #adb5bd;
            }
        """)
        layout.addWidget(self.coords_label)
    
    # ===============================
    # ОСНОВНІ МЕТОДИ УПРАВЛІННЯ
    # ===============================
    
    def set_image(self, image: Image.Image):
        """
        Встановлення вихідного зображення для зуму
        
        Args:
            image: PIL Image для збільшення
        """
        self.source_image = image
        self._clear_cache()
        
        if image:
            # Ініціалізація центру зображення
            self.current_x = image.width // 2
            self.current_y = image.height // 2
            self.coords_label.setText(f"({self.current_x}, {self.current_y})")
            print(f"Зум встановлено для зображення: {image.width}×{image.height}")
        else:
            self.image_label.setText("Зум\nнедоступний")
            print("Зображення для зуму очищено")
    
    def set_zoom_factor(self, factor: int):
        """
        Встановлення коефіцієнта збільшення
        
        Args:
            factor: Коефіцієнт збільшення (2-8x)
        """
        if 2 <= factor <= 8:
            self.zoom_factor = factor
            self._clear_cache()
            self.title_label.setText(f"Зум x{factor}")
            
            # Оновлення зуму якщо потрібно
            if self.is_visible and self.source_image:
                self._update_zoom_display()
            
            print(f"Коефіцієнт зуму змінено на: x{factor}")
    
    def set_zoom_size(self, size: int):
        """
        Встановлення розміру області для збільшення
        
        Args:
            size: Розмір в пікселях оригінального зображення
        """
        if 50 <= size <= 200:
            self.zoom_size = size
            self._clear_cache()
            
            # Оновлення зуму якщо потрібно
            if self.is_visible and self.source_image:
                self._update_zoom_display()
            
            print(f"Розмір області зуму змінено на: {size}px")
    
    def set_mode(self, mode: str):
        """
        Встановлення режиму роботи зуму
        
        Args:
            mode: 'normal', 'center' або 'scale'
        """
        self.current_mode = mode
        
        # Оновлення заголовка відповідно до режиму
        mode_names = {
            'normal': 'Зум',
            'center': 'Центр',
            'scale': 'Масштаб'
        }
        
        mode_name = mode_names.get(mode, 'Зум')
        self.title_label.setText(f"{mode_name} x{self.zoom_factor}")
        
        # Оновлення стилів відповідно до режиму
        mode_colors = {
            'normal': '#6c757d',
            'center': '#dc3545',  # Червоний для режиму центру
            'scale': '#007bff'    # Синій для режиму масштабу
        }
        
        border_color = mode_colors.get(mode, '#6c757d')
        self.image_label.setStyleSheet(f"""
            QLabel {{
                border: 2px solid {border_color};
                background-color: white;
                border-radius: 6px;
            }}
        """)
    
    def update_position(self, x: int, y: int):
        """
        Оновлення позиції для збільшення
        
        Args:
            x, y: Координати в оригінальному зображенні
        """
        if not self.source_image:
            return
        
        # Обмеження координат межами зображення
        x = max(0, min(x, self.source_image.width - 1))
        y = max(0, min(y, self.source_image.height - 1))
        
        # Перевірка чи змінилась позиція (з допуском для оптимізації)
        if abs(self.current_x - x) < 2 and abs(self.current_y - y) < 2:
            return
        
        self.current_x = x
        self.current_y = y
        
        # Оновлення відображення координат
        self.coords_label.setText(f"({x}, {y})")
        
        # Відкладене оновлення для оптимізації
        if self.is_visible:
            self.update_timer.start(16)  # ~60 FPS
    
    def show_zoom(self):
        """Показати віджет зуму"""
        if not self.source_image:
            return
        
        self.is_visible = True
        self._update_zoom_display()
        self._position_widget()
        self.show()
        self.raise_()
        
        # Скасування автоматичного приховування
        self.auto_hide_timer.stop()
        
        print("Зум показано")
    
    def show_zoom_at_center(self):
        """Показати зум в центрі сітки"""
        if self.source_image:
            center_x = self.source_image.width // 2
            center_y = self.source_image.height // 2
            self.update_position(center_x, center_y)
            self.set_mode('center')
            self.show_zoom()
    
    def hide_zoom(self):
        """Приховати віджет зуму"""
        self.is_visible = False
        self.hide()
        print("Зум приховано")
    
    def show_zoom_temporarily(self, duration_ms: int = 3000):
        """
        Показати зум на певний час
        
        Args:
            duration_ms: Тривалість показу в мілісекундах
        """
        self.show_zoom()
        self.auto_hide_timer.start(duration_ms)
    
    # ===============================
    # ВНУТРІШНІ МЕТОДИ ВІДОБРАЖЕННЯ
    # ===============================
    
    def _update_zoom_display(self):
        """Оновлення відображення збільшеної області"""
        if not self.source_image:
            return
        
        # Перевірка кешу
        cache_key = (self.current_x, self.current_y, self.zoom_factor)
        if (self.cached_zoom and 
            self.cache_position == (self.current_x, self.current_y) and
            self.cache_factor == self.zoom_factor):
            self.image_label.setPixmap(self.cached_zoom)
            return
        
        try:
            # Створення збільшеної області
            zoomed_image = self._create_zoomed_region()
            
            if zoomed_image:
                # Конвертація в QPixmap
                qt_image = ImageQt(zoomed_image)
                pixmap = QPixmap.fromImage(qt_image)
                
                # Масштабування до розміру віджету
                scaled_pixmap = pixmap.scaled(
                    self.widget_size, self.widget_size,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                
                # Кешування
                self.cached_zoom = scaled_pixmap
                self.cache_position = (self.current_x, self.current_y)
                self.cache_factor = self.zoom_factor
                
                # Відображення
                self.image_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            print(f"Помилка оновлення зуму: {e}")
            self.image_label.setText("Помилка\nзуму")
    
    def _delayed_update(self):
        """Відкладене оновлення для оптимізації"""
        self._update_zoom_display()
    
    def _create_zoomed_region(self) -> Optional[Image.Image]:
        """
        Створення збільшеної області зображення
        
        Returns:
            PIL Image зі збільшеною областю
        """
        if not self.source_image:
            return None
        
        # Розрахунок області для вирізки
        half_size = self.zoom_size // 2
        
        # Координати області (з обмеженням межами зображення)
        left = max(0, self.current_x - half_size)
        top = max(0, self.current_y - half_size)
        right = min(self.source_image.width, self.current_x + half_size)
        bottom = min(self.source_image.height, self.current_y + half_size)
        
        # Перевірка валідності області
        if right <= left or bottom <= top:
            return None
        
        # Вирізка області
        region = self.source_image.crop((left, top, right, bottom))
        
        # Збільшення області
        new_size = (
            int(region.width * self.zoom_factor),
            int(region.height * self.zoom_factor)
        )
        
        zoomed_region = region.resize(new_size, Image.LANCZOS)
        
        # Додавання хрестика в центрі
        self._add_crosshair(zoomed_region)
        
        return zoomed_region
    
    def _add_crosshair(self, image: Image.Image):
        """
        Додавання хрестика в центрі збільшеної області
        
        Args:
            image: PIL Image для додавання хрестика
        """
        draw = ImageDraw.Draw(image)
        
        center_x = image.width // 2
        center_y = image.height // 2
        
        # Розмір хрестика залежно від режиму
        crosshair_size = {
            'normal': 15,
            'center': 20,
            'scale': 18
        }.get(self.current_mode, 15)
        
        # Колір хрестика залежно від режиму
        crosshair_color = {
            'normal': (255, 0, 0),     # Червоний
            'center': (255, 0, 0),     # Червоний для центру
            'scale': (0, 0, 255)       # Синій для масштабу
        }.get(self.current_mode, (255, 0, 0))
        
        # Товщина ліній
        line_width = max(2, self.zoom_factor // 2)
        
        # Горизонтальна лінія
        draw.line([
            (center_x - crosshair_size, center_y),
            (center_x + crosshair_size, center_y)
        ], fill=crosshair_color, width=line_width)
        
        # Вертикальна лінія
        draw.line([
            (center_x, center_y - crosshair_size),
            (center_x, center_y + crosshair_size)
        ], fill=crosshair_color, width=line_width)
        
        # Коло навколо центру для кращої видимості
        circle_radius = crosshair_size // 2
        draw.ellipse([
            center_x - circle_radius, center_y - circle_radius,
            center_x + circle_radius, center_y + circle_radius
        ], outline=crosshair_color, width=max(1, line_width // 2))
    
    def _position_widget(self):
        """Розумне позиціонування віджету відносно батьківського віджету"""
        if not self.parent():
            return
        
        parent_widget = self.parent()
        parent_rect = parent_widget.rect()
        
        # Позиція курсора в батьківському віджеті
        cursor_pos = parent_widget.mapFromGlobal(parent_widget.cursor().pos())
        
        # Розміри цього віджету
        widget_width = self.width()
        widget_height = self.height()
        
        # Відступи від країв
        margin = 20
        
        # Початкова позиція (справа від курсора)
        x = cursor_pos.x() + 30
        y = cursor_pos.y() - widget_height // 2
        
        # Корекція якщо виходить за межі справа
        if x + widget_width > parent_rect.width() - margin:
            x = cursor_pos.x() - widget_width - 30  # Ліворуч від курсора
        
        # Корекція якщо виходить за межі зверху
        if y < margin:
            y = margin
        
        # Корекція якщо виходить за межі знизу
        if y + widget_height > parent_rect.height() - margin:
            y = parent_rect.height() - widget_height - margin
        
        # Корекція якщо виходить за межі ліворуч
        if x < margin:
            x = margin
        
        # Встановлення позиції
        self.move(x, y)
    
    def _clear_cache(self):
        """Очищення кешу"""
        self.cached_zoom = None
        self.cache_position = (-1, -1)
        self.cache_factor = -1
    
    # ===============================
    # ПУБЛІЧНІ МЕТОДИ ДЛЯ ІНТЕГРАЦІЇ
    # ===============================
    
    def get_zoom_info(self) -> dict:
        """
        Отримання інформації про поточний стан зуму
        
        Returns:
            Словник з інформацією про зум
        """
        return {
            'is_visible': self.is_visible,
            'zoom_factor': self.zoom_factor,
            'zoom_size': self.zoom_size,
            'current_position': (self.current_x, self.current_y),
            'mode': self.current_mode,
            'has_image': self.source_image is not None,
            'widget_size': self.widget_size
        }
    
    def get_zoom_region_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Отримання меж поточної області зуму
        
        Returns:
            Кортеж (left, top, right, bottom) або None
        """
        if not self.source_image:
            return None
        
        half_size = self.zoom_size // 2
        
        left = max(0, self.current_x - half_size)
        top = max(0, self.current_y - half_size)
        right = min(self.source_image.width, self.current_x + half_size)
        bottom = min(self.source_image.height, self.current_y + half_size)
        
        return (left, top, right, bottom)


# ===============================
# ІНТЕГРАЦІЯ З CLICKABLE LABEL
# ===============================

class ClickableLabelZoomExtension:
    """
    Розширення ClickableLabel для інтеграції з ZoomWidget
    Ці методи потрібно додати до ClickableLabel
    """
    
    def show_zoom_at_center(self):
        """Показати зум в центрі сітки"""
        if self.zoom_widget and self.current_image:
            self.zoom_widget.update_position(self.grid_center_x, self.grid_center_y)
            self.zoom_widget.set_mode('center')
            self.zoom_widget.show_zoom()
    
    def show_zoom_at_mouse(self, x: int, y: int):
        """Показати зум в позиції миші"""
        if self.zoom_widget:
            self.zoom_widget.update_position(x, y)
            self.zoom_widget.set_mode('normal')
            self.zoom_widget.show_zoom_temporarily(2000)
    
    def update_zoom_position(self, x: int, y: int):
        """Оновити позицію зуму під час руху миші"""
        if self.zoom_widget and self.zoom_widget.is_visible:
            self.zoom_widget.update_position(x, y)
    
    def hide_zoom(self):
        """Приховати зум"""
        if self.zoom_widget:
            self.zoom_widget.hide_zoom()
    
    # Доповнення до mouseMoveEvent
    def mouseMoveEvent_with_zoom(self, event):
        """
        ДОПОВНЕНИЙ mouseMoveEvent з підтримкою зуму
        Замінити в ClickableLabel
        """
        if self.current_image:
            widget_x, widget_y = event.x(), event.y()
            image_coords = self._widget_to_image_coords(widget_x, widget_y)
            
            if image_coords:
                image_x, image_y = image_coords
                
                # Сигнал руху миші для підказок
                self.mouse_moved.emit(image_x, image_y)
                
                # Оновлення зуму в спеціальних режимах
                if self.center_setting_mode or self.scale_edge_mode:
                    self.update_zoom_position(image_x, image_y)
                
                # Перетягування точки аналізу
                if (event.buttons() & Qt.LeftButton and 
                    self.current_analysis_point and 
                    not self.center_setting_mode and 
                    not self.scale_edge_mode):
                    
                    if not self.dragging:
                        drag_distance = (event.pos() - self.drag_start_pos).manhattanLength()
                        if drag_distance > 3:
                            self.dragging = True
                    
                    if self.dragging:
                        self.current_analysis_point = (image_x, image_y)
                        self.dragged.emit(image_x, image_y)
                        self.update()
        
        super().mouseMoveEvent(event)


# ===============================
# ТЕСТУВАННЯ
# ===============================

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QSlider
    from PIL import Image, ImageDraw
    
    class ZoomTestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Тест ZoomWidget - Повний функціонал")
            self.setGeometry(100, 100, 800, 600)
            
            # Центральний віджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QHBoxLayout(central_widget)
            
            # Ліва частина - зображення
            left_widget = QWidget()
            left_layout = QVBoxLayout(left_widget)
            
            # Створення тестового зображення
            test_image = self.create_detailed_test_image()
            
            # Основне зображення (імітація ClickableLabel)
            self.main_image_label = QLabel()
            self.main_image_label.setMinimumSize(400, 400)
            self.main_image_label.setStyleSheet("border: 1px solid black;")
            self.main_image_label.setAlignment(Qt.AlignCenter)
            
            # Встановлення зображення
            qt_image = ImageQt(test_image)
            pixmap = QPixmap.fromImage(qt_image).scaled(400, 400, Qt.KeepAspectRatio)
            self.main_image_label.setPixmap(pixmap)
            
            left_layout.addWidget(self.main_image_label)
            layout.addWidget(left_widget)
            
            # Права частина - управління
            right_widget = QWidget()
            right_widget.setFixedWidth(250)
            right_layout = QVBoxLayout(right_widget)
            
            # ZoomWidget
            self.zoom_widget = ZoomWidget(self.main_image_label)
            self.zoom_widget.set_image(test_image)
            
            # Кнопки управління
            show_btn = QPushButton("Показати зум")
            show_btn.clicked.connect(self.zoom_widget.show_zoom)
            right_layout.addWidget(show_btn)
            
            hide_btn = QPushButton("Приховати зум")
            hide_btn.clicked.connect(self.zoom_widget.hide_zoom)
            right_layout.addWidget(hide_btn)
            
            center_btn = QPushButton("Зум в центрі")
            center_btn.clicked.connect(self.zoom_widget.show_zoom_at_center)
            right_layout.addWidget(center_btn)
            
            temp_btn = QPushButton("Тимчасовий зум")
            temp_btn.clicked.connect(lambda: self.zoom_widget.show_zoom_temporarily(5000))
            right_layout.addWidget(temp_btn)
            
            # Слайдери
            right_layout.addWidget(QLabel("Коефіцієнт зуму:"))
            zoom_slider = QSlider(Qt.Horizontal)
            zoom_slider.setRange(2, 8)
            zoom_slider.setValue(4)
            zoom_slider.valueChanged.connect(self.zoom_widget.set_zoom_factor)
            right_layout.addWidget(zoom_slider)
            
            right_layout.addWidget(QLabel("Розмір області:"))
            size_slider = QSlider(Qt.Horizontal)
            size_slider.setRange(50, 200)
            size_slider.setValue(100)
            size_slider.valueChanged.connect(self.zoom_widget.set_zoom_size)
            right_layout.addWidget(size_slider)
            
            # Кнопки режимів
            right_layout.addWidget(QLabel("Режими:"))
            
            normal_btn = QPushButton("Звичайний")
            normal_btn.clicked.connect(lambda: self.zoom_widget.set_mode('normal'))
            right_layout.addWidget(normal_btn)
            
            center_mode_btn = QPushButton("Режим центру")
            center_mode_btn.clicked.connect(lambda: self.zoom_widget.set_mode('center'))
            right_layout.addWidget(center_mode_btn)
            
            scale_mode_btn = QPushButton("Режим масштабу")
            scale_mode_btn.clicked.connect(lambda: self.zoom_widget.set_mode('scale'))
            right_layout.addWidget(scale_mode_btn)
            
            # Інформація
            info_btn = QPushButton("Показати інформацію")
            info_btn.clicked.connect(self.show_zoom_info)
            right_layout.addWidget(info_btn)
            
            right_layout.addStretch()
            layout.addWidget(right_widget)
            
            # Обробка рухів миші для тестування
            self.main_image_label.mouseMoveEvent = self.on_mouse_move
            self.main_image_label.setMouseTracking(True)
        
        def create_detailed_test_image(self):
            """Створення детального тестового зображення"""
            width, height = 800, 600
            image = Image.new('RGB', (width, height), (250, 250, 250))
            draw = ImageDraw.Draw(image)
            
            # Дрібна сітка
            for i in range(0, width, 20):
                draw.line([(i, 0), (i, height)], fill=(220, 220, 220))
            for i in range(0, height, 20):
                draw.line([(0, i), (width, i)], fill=(220, 220, 220))
            
            # Основна сітка
            for i in range(0, width, 100):
                draw.line([(i, 0), (i, height)], fill=(180, 180, 180), width=2)
            for i in range(0, height, 100):
                draw.line([(0, i), (width, i)], fill=(180, 180, 180), width=2)
            
            # Центральні лінії
            center_x, center_y = width // 2, height // 2
            draw.line([(center_x, 0), (center_x, height)], fill=(255, 0, 0), width=3)
            draw.line([(0, center_y), (width, center_y)], fill=(255, 0, 0), width=3)
            
            # Кола з центру
            for radius in [50, 100, 150, 200, 250]:
                draw.ellipse([
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius
                ], outline=(100, 100, 255), width=2)
            
            # Цифри для орієнтації
            try:
                from PIL import ImageFont
                font = ImageFont.load_default()
                for i in range(0, width, 100):
                    for j in range(0, height, 100):
                        draw.text((i + 5, j + 5), f"{i},{j}", fill=(0, 0, 0), font=font)
            except:
                pass
            
            return image
        
        def on_mouse_move(self, event):
            """Обробка руху миші для оновлення позиції зуму"""
            # Перетворення координат з віджету в зображення (спрощено)
            x = int(event.x() * 800 / 400)  # 800/400 = масштаб
            y = int(event.y() * 600 / 400)  # 600/400 = масштаб
            
            self.zoom_widget.update_position(x, y)
        
        def show_zoom_info(self):
            """Показ інформації про зум"""
            info = self.zoom_widget.get_zoom_info()
            print("\n=== ІНФОРМАЦІЯ ПРО ЗУМWIDGET ===")
            for key, value in info.items():
                print(f"{key}: {value}")
            
            bounds = self.zoom_widget.get_zoom_region_bounds()
            if bounds:
                print(f"Межі області: {bounds}")
    
    # Запуск тесту
    app = QApplication(sys.argv)
    window = ZoomTestWindow()
    window.show()
    
    print("=== ТЕСТУВАННЯ ZOOMWIDGET - ПОВНИЙ ФУНКЦІОНАЛ ===")
    print("\n🔍 ОСНОВНІ ФУНКЦІЇ:")
    print("1. ✅ Збільшення області 2x-8x")
    print("2. ✅ Хрестик в центрі для позиціонування")
    print("3. ✅ Відображення координат")
    print("4. ✅ Кешування для оптимізації")
    print("5. ✅ Розумне позиціонування віджету")
    print("6. ✅ Режими: normal, center, scale")
    print("7. ✅ Автоматичне приховування")
    print("8. ✅ Плавне оновлення (60 FPS)")
    
    print("\n⌨️ ТЕСТУВАННЯ:")
    print("- Рухайте мишею над зображенням")
    print("- Використовуйте слайдери для зміни параметрів")
    print("- Тестуйте різні режими роботи")
    print("- Перевіряйте кешування та продуктивність")
    
    sys.exit(app.exec_())