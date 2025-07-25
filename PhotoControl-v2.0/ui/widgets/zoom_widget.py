#!/usr/bin/env python3
"""
Віджет зуму з точними розмірами для детального перегляду
Показує збільшену область навколо курсора або центру сітки
"""

from typing import Optional, Tuple
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt


class ZoomWidget(QWidget):
    """
    Віджет для відображення збільшеної області зображення
    
    Функціональність:
    - Збільшення області навколо курсора або центру сітки
    - Налаштовуваний коефіцієнт зуму (2x, 3x, 4x, 5x)
    - Відображення координат поточної позиції
    - Хрестик в центрі для точного позиціонування
    - Автоматичне приховування/показ
    - Плавне оновлення при русі миші
    - Кешування для оптимізації продуктивності
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
        
        # Стан віджету
        self.is_visible = False
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide_zoom)
        
        # Налаштування віджету
        self._setup_widget()
        self._setup_layout()
    
    def _setup_widget(self):
        """Налаштування основних властивостей віджету"""
        # Розміри та позиція
        self.setFixedSize(self.widget_size + 40, self.widget_size + 60)  # +40 для рамки, +60 для тексту
        
        # Стилі
        self.setStyleSheet("""
            ZoomWidget {
                background-color: rgba(240, 240, 240, 220);
                border: 2px solid #666;
                border-radius: 8px;
            }
        """)
        
        # Завжди зверху
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Ігнорування подій миші (щоб не заважати взаємодії з основним зображенням)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        # Початково приховано
        self.hide()
    
    def _setup_layout(self):
        """Налаштування макету віджету"""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        self.setLayout(layout)
        
        # Заголовок
        self.title_label = QLabel("Зум x4")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 11px;
                color: #333;
                background-color: transparent;
                padding: 2px;
            }
        """)
        layout.addWidget(self.title_label)
        
        # Область зображення
        self.image_label = QLabel()
        self.image_label.setFixedSize(self.widget_size, self.widget_size)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #999;
                background-color: white;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.image_label)
        
        # Координати
        self.coords_label = QLabel("(0, 0)")
        self.coords_label.setAlignment(Qt.AlignCenter)
        self.coords_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #666;
                background-color: transparent;
                padding: 2px;
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
        self.cached_zoom = None  # Очищення кешу
        self.cache_position = (-1, -1)
        
        if image:
            print(f"Зум встановлено для зображення: {image.width}×{image.height}")
        else:
            print("Зображення для зуму очищено")
    
    def set_zoom_factor(self, factor: int):
        """
        Встановлення коефіцієнта збільшення
        
        Args:
            factor: Коефіцієнт збільшення (2-8x)
        """
        if 2 <= factor <= 8:
            self.zoom_factor = factor
            self.cached_zoom = None  # Очищення кешу
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
            self.cached_zoom = None  # Очищення кешу
            
            # Оновлення зуму якщо потрібно
            if self.is_visible and self.source_image:
                self._update_zoom_display()
            
            print(f"Розмір області зуму змінено на: {size}px")
    
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
        
        # Перевірка чи змінилась позиція
        if self.current_x == x and self.current_y == y:
            return
        
        self.current_x = x
        self.current_y = y
        
        # Оновлення відображення координат
        self.coords_label.setText(f"({x}, {y})")
        
        # Оновлення зуму якщо він видимий
        if self.is_visible:
            self._update_zoom_display()
    
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
        current_position = (self.current_x, self.current_y)
        if (self.cached_zoom and 
            self.cache_position == current_position):
            # Використання кешу
            self.image_label.setPixmap(self.cached_zoom)
            return
        
        # Створення нового зуму
        zoomed_pixmap = self._create_zoom_pixmap()
        
        if zoomed_pixmap:
            # Збереження в кеш
            self.cached_zoom = zoomed_pixmap
            self.cache_position = current_position
            
            # Відображення
            self.image_label.setPixmap(zoomed_pixmap)
    
    def _create_zoom_pixmap(self) -> Optional[QPixmap]:
        """
        Створення QPixmap зі збільшеною областю
        
        Returns:
            QPixmap з збільшеною областю або None при помилці
        """
        try:
            # Визначення області для вирізання
            half_size = self.zoom_size // 2
            
            left = max(0, self.current_x - half_size)
            top = max(0, self.current_y - half_size)
            right = min(self.source_image.width, self.current_x + half_size)
            bottom = min(self.source_image.height, self.current_y + half_size)
            
            # Вирізання області
            crop_box = (left, top, right, bottom)
            cropped_image = self.source_image.crop(crop_box)
            
            # Збільшення області
            zoomed_size = (self.widget_size, self.widget_size)
            zoomed_image = cropped_image.resize(zoomed_size, Image.Resampling.NEAREST)
            
            # Додавання хрестика в центрі
            zoomed_with_crosshair = self._add_crosshair(zoomed_image)
            
            # Конвертація в QPixmap
            qt_image = ImageQt(zoomed_with_crosshair)
            pixmap = QPixmap.fromImage(qt_image)
            
            return pixmap
            
        except Exception as e:
            print(f"Помилка створення зуму: {e}")
            return None
    
    def _add_crosshair(self, image: Image.Image) -> Image.Image:
        """
        Додавання хрестика в центр збільшеної області
        
        Args:
            image: Збільшене зображення
            
        Returns:
            Зображення з хрестиком
        """
        # Створення копії для малювання
        image_with_crosshair = image.copy()
        draw = ImageDraw.Draw(image_with_crosshair)
        
        # Координати центру
        center_x = image.width // 2
        center_y = image.height // 2
        
        # Параметри хрестика
        crosshair_size = 20
        line_width = 2
        color = (255, 0, 0)  # Червоний
        
        # Горизонтальна лінія
        draw.line([
            (center_x - crosshair_size//2, center_y),
            (center_x + crosshair_size//2, center_y)
        ], fill=color, width=line_width)
        
        # Вертикальна лінія
        draw.line([
            (center_x, center_y - crosshair_size//2),
            (center_x, center_y + crosshair_size//2)
        ], fill=color, width=line_width)
        
        # Коло навколо центру
        circle_radius = 8
        draw.ellipse([
            center_x - circle_radius, center_y - circle_radius,
            center_x + circle_radius, center_y + circle_radius
        ], outline=color, width=1)
        
        return image_with_crosshair
    
    def _position_widget(self):
        """Позиціонування віджету відносно батьківського віджету"""
        if not self.parent():
            return
        
        parent_widget = self.parent()
        
        # Отримання розмірів батьківського віджету
        parent_rect = parent_widget.rect()
        parent_global = parent_widget.mapToGlobal(parent_rect.topLeft())
        
        # Позиціонування в правому верхньому куті з відступом
        margin = 20
        x = parent_global.x() + parent_rect.width() - self.width() - margin
        y = parent_global.y() + margin
        
        # Перевірка меж екрану
        screen_rect = parent_widget.screen().availableGeometry()
        
        # Корекція якщо виходить за межі
        if x + self.width() > screen_rect.right():
            x = screen_rect.right() - self.width() - margin
        
        if y + self.height() > screen_rect.bottom():
            y = screen_rect.bottom() - self.height() - margin
        
        if x < screen_rect.left():
            x = screen_rect.left() + margin
        
        if y < screen_rect.top():
            y = screen_rect.top() + margin
        
        # Встановлення позиції
        self.move(x, y)
    
    # ===============================
    # РЕЖИМИ РОБОТИ
    # ===============================
    
    def set_mode(self, mode: str):
        """
        Встановлення режиму роботи зуму
        
        Args:
            mode: 'normal', 'center', 'scale' або 'precision'
        """
        mode_configs = {
            'normal': {
                'zoom_factor': 4,
                'zoom_size': 100,
                'title': 'Зум x4'
            },
            'center': {
                'zoom_factor': 6,
                'zoom_size': 80,
                'title': 'Центр x6'
            },
            'scale': {
                'zoom_factor': 5,
                'zoom_size': 120,
                'title': 'Масштаб x5'
            },
            'precision': {
                'zoom_factor': 8,
                'zoom_size': 60,
                'title': 'Точність x8'
            }
        }
        
        config = mode_configs.get(mode, mode_configs['normal'])
        
        self.zoom_factor = config['zoom_factor']
        self.zoom_size = config['zoom_size']
        self.title_label.setText(config['title'])
        
        # Очищення кешу при зміні режиму
        self.cached_zoom = None
        self.cache_position = (-1, -1)
        
        # Оновлення якщо потрібно
        if self.is_visible and self.source_image:
            self._update_zoom_display()
        
        print(f"Режим зуму змінено на: {mode}")
    
    def toggle_zoom(self):
        """Перемикання видимості зуму"""
        if self.is_visible:
            self.hide_zoom()
        else:
            self.show_zoom()
    
    # ===============================
    # УТИЛІТАРНІ МЕТОДИ
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
            'widget_size': self.widget_size,
            'current_position': (self.current_x, self.current_y),
            'has_image': self.source_image is not None,
            'cache_status': self.cached_zoom is not None
        }
    
    def clear_cache(self):
        """Очищення кешу зуму"""
        self.cached_zoom = None
        self.cache_position = (-1, -1)
        print("Кеш зуму очищено")
    
    def save_zoom_as_image(self, file_path: str) -> bool:
        """
        Збереження поточного зуму як зображення
        
        Args:
            file_path: Шлях для збереження
            
        Returns:
            True якщо збереження успішне
        """
        if not self.cached_zoom:
            return False
        
        try:
            # Конвертація QPixmap в PIL Image
            qt_image = self.cached_zoom.toImage()
            
            # Збереження
            qt_image.save(file_path)
            print(f"Зум збережено: {file_path}")
            return True
            
        except Exception as e:
            print(f"Помилка збереження зуму: {e}")
            return False
    
    def update_from_mouse_event(self, widget_x: int, widget_y: int, 
                               to_image_coords_func):
        """
        Оновлення позиції зуму з події миші
        
        Args:
            widget_x, widget_y: Координати в віджеті
            to_image_coords_func: Функція конвертації координат
        """
        try:
            image_coords = to_image_coords_func(widget_x, widget_y)
            if image_coords:
                self.update_position(image_coords[0], image_coords[1])
        except Exception as e:
            print(f"Помилка оновлення зуму з миші: {e}")
    
    # ===============================
    # ОБРОБКА ПОДІЙ
    # ===============================
    
    def paintEvent(self, event):
        """Перемалювання з додатковими елементами"""
        super().paintEvent(event)
        
        # Додаткове малювання якщо потрібно
        if self.is_visible and not self.source_image:
            # Показ повідомлення про відсутність зображення
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Текст в центрі
            painter.setPen(QPen(QColor(100, 100, 100)))
            painter.setFont(QFont("Arial", 10))
            
            rect = self.image_label.geometry()
            painter.drawText(rect, Qt.AlignCenter, "Зображення\nне завантажено")
    
    def mousePressEvent(self, event):
        """Обробка кліку (хоча віджет прозорий для миші)"""
        # Цей метод викликатиметься рідко через WA_TransparentForMouseEvents
        super().mousePressEvent(event)
    
    def resizeEvent(self, event):
        """Обробка зміни розміру"""
        super().resizeEvent(event)
        
        # Очищення кешу при зміні розміру
        self.cached_zoom = None
        self.cache_position = (-1, -1)


# ===============================
# ДОПОМІЖНІ ФУНКЦІЇ
# ===============================

def create_test_zoom_widget(parent=None) -> ZoomWidget:
    """
    Створення тестового віджету зуму
    
    Args:
        parent: Батьківський віджет
        
    Returns:
        Налаштований ZoomWidget для тестування
    """
    zoom_widget = ZoomWidget(parent)
    
    # Створення тестового зображення з шахматною дошкою
    test_image = Image.new('RGB', (400, 300), (255, 255, 255))
    draw = ImageDraw.Draw(test_image)
    
    # Шахматна дошка для перевірки точності зуму
    square_size = 20
    for row in range(0, 300, square_size):
        for col in range(0, 400, square_size):
            if (row // square_size + col // square_size) % 2 == 0:
                draw.rectangle([col, row, col + square_size, row + square_size], 
                             fill=(200, 200, 200))
    
    # Координатна сітка
    for i in range(0, 400, 50):
        draw.line([(i, 0), (i, 300)], fill=(100, 100, 100), width=1)
        if i > 0:
            draw.text((i + 2, 2), str(i), fill=(0, 0, 0))
    
    for i in range(0, 300, 50):
        draw.line([(0, i), (400, i)], fill=(100, 100, 100), width=1)
        if i > 0:
            draw.text((2, i + 2), str(i), fill=(0, 0, 0))
    
    # Центральний хрест
    draw.line([(200, 0), (200, 300)], fill=(255, 0, 0), width=2)
    draw.line([(0, 150), (400, 150)], fill=(255, 0, 0), width=2)
    
    zoom_widget.set_image(test_image)
    zoom_widget.update_position(200, 150)  # Центр зображення
    
    return zoom_widget


if __name__ == "__main__":
    # Тестування віджету зуму
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSlider, QLabel, QCheckBox, QComboBox
    from PyQt5.QtCore import QTimer
    
    class ZoomTestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Тестування ZoomWidget")
            self.setGeometry(100, 100, 800, 600)
            
            # Центральний віджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QHBoxLayout(central_widget)
            
            # Ліва панель управління
            control_panel = self.create_control_panel()
            layout.addWidget(control_panel)
            
            # Основна область
            main_area = QWidget()
            main_area.setMinimumSize(500, 400)
            main_area.setStyleSheet("""
                QWidget {
                    border: 2px solid #ccc;
                    background-color: #f0f0f0;
                    background-image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHZpZXdCb3g9IjAgMCAyMCAyMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3QgeD0iMCIgeT0iMCIgd2lkdGg9IjEwIiBoZWlnaHQ9IjEwIiBmaWxsPSIjZmZmZmZmIiBmaWxsLW9wYWNpdHk9IjAuMSIvPgo8cmVjdCB4PSIxMCIgeT0iMTAiIHdpZHRoPSIxMCIgaGVpZ2h0PSIxMCIgZmlsbD0iI2ZmZmZmZiIgZmlsbC1vcGFjaXR5PSIwLjEiLz4KPC9zdmc+);
                }
            """)
            layout.addWidget(main_area)
            
            # Створення тестового зум віджету
            self.zoom_widget = create_test_zoom_widget(main_area)
            
            # Симуляція руху миші
            self.mouse_timer = QTimer()
            self.mouse_timer.timeout.connect(self.simulate_mouse_movement)
            self.mouse_position = [200, 150]
            self.mouse_direction = [1, 1]
            
            # Показати зум одразу
            self.zoom_widget.show_zoom()
            
            print("ZoomWidget тестове вікно готове")
        
        def create_control_panel(self):
            """Створення панелі управління"""
            panel = QWidget()
            panel.setFixedWidth(280)
            layout = QVBoxLayout(panel)
            
            # Заголовок
            title = QLabel("Управління зумом")
            title.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
            layout.addWidget(title)
            
            # Показати/приховати зум
            self.toggle_btn = QPushButton("Показати/Приховати зум")
            self.toggle_btn.clicked.connect(self.zoom_widget.toggle_zoom)
            layout.addWidget(self.toggle_btn)
            
            # Коефіцієнт зуму
            layout.addWidget(QLabel("Коефіцієнт зуму:"))
            self.zoom_slider = QSlider(Qt.Horizontal)
            self.zoom_slider.setRange(2, 8)
            self.zoom_slider.setValue(4)
            self.zoom_slider.valueChanged.connect(self.change_zoom_factor)
            
            zoom_layout = QHBoxLayout()
            zoom_layout.addWidget(self.zoom_slider)
            self.zoom_value_label = QLabel("x4")
            zoom_layout.addWidget(self.zoom_value_label)
            layout.addLayout(zoom_layout)
            
            # Розмір області зуму
            layout.addWidget(QLabel("Розмір області (px):"))
            self.size_slider = QSlider(Qt.Horizontal)
            self.size_slider.setRange(50, 200)
            self.size_slider.setValue(100)
            self.size_slider.valueChanged.connect(self.change_zoom_size)
            
            size_layout = QHBoxLayout()
            size_layout.addWidget(self.size_slider)
            self.size_value_label = QLabel("100px")
            size_layout.addWidget(self.size_value_label)
            layout.addLayout(size_layout)
            
            # Режим роботи
            layout.addWidget(QLabel("Режим роботи:"))
            self.mode_combo = QComboBox()
            self.mode_combo.addItems([
                "normal - Звичайний x4",
                "center - Центр x6", 
                "scale - Масштаб x5",
                "precision - Точність x8"
            ])
            self.mode_combo.currentTextChanged.connect(self.change_mode)
            layout.addWidget(self.mode_combo)
            
            # Симуляція руху миші
            self.simulate_mouse_cb = QCheckBox("Симуляція руху миші")
            self.simulate_mouse_cb.toggled.connect(self.toggle_mouse_simulation)
            layout.addWidget(self.simulate_mouse_cb)
            
            # Тестові позиції
            layout.addWidget(QLabel("Тестові позиції:"))
            
            positions = [
                ("Центр", 200, 150),
                ("Лівий верх", 50, 50),
                ("Правий верх", 350, 50),
                ("Лівий низ", 50, 250),
                ("Правий низ", 350, 250)
            ]
            
            for name, x, y in positions:
                btn = QPushButton(f"{name} ({x}, {y})")
                btn.clicked.connect(lambda checked, px=x, py=y: self.set_test_position(px, py))
                layout.addWidget(btn)
            
            # Управління кешем
            layout.addWidget(QLabel("Кеш та утиліти:"))
            
            clear_cache_btn = QPushButton("Очистити кеш")
            clear_cache_btn.clicked.connect(self.zoom_widget.clear_cache)
            layout.addWidget(clear_cache_btn)
            
            save_zoom_btn = QPushButton("Зберегти зум")
            save_zoom_btn.clicked.connect(self.save_zoom_image)
            layout.addWidget(save_zoom_btn)
            
            # Інформація про зум
            layout.addWidget(QLabel("Інформація:"))
            self.info_label = QLabel()
            self.info_label.setStyleSheet("""
                QLabel {
                    border: 1px solid #ccc;
                    padding: 8px;
                    background-color: #f9f9f9;
                    font-family: 'Courier New', monospace;
                    font-size: 9px;
                }
            """)
            self.info_label.setWordWrap(True)
            layout.addWidget(self.info_label)
            
            layout.addStretch()
            
            # Таймер для оновлення інформації
            self.info_timer = QTimer()
            self.info_timer.timeout.connect(self.update_info)
            self.info_timer.start(500)  # Кожні 500мс
            
            return panel
        
        def change_zoom_factor(self, value):
            """Зміна коефіцієнта зуму"""
            self.zoom_widget.set_zoom_factor(value)
            self.zoom_value_label.setText(f"x{value}")
        
        def change_zoom_size(self, value):
            """Зміна розміру області зуму"""
            self.zoom_widget.set_zoom_size(value)
            self.size_value_label.setText(f"{value}px")
        
        def change_mode(self, text):
            """Зміна режиму роботи"""
            mode = text.split(' - ')[0]
            self.zoom_widget.set_mode(mode)
            
            # Оновлення слайдерів відповідно до режиму
            info = self.zoom_widget.get_zoom_info()
            self.zoom_slider.setValue(info['zoom_factor'])
            self.zoom_value_label.setText(f"x{info['zoom_factor']}")
            self.size_slider.setValue(info['zoom_size'])
            self.size_value_label.setText(f"{info['zoom_size']}px")
        
        def toggle_mouse_simulation(self, enabled):
            """Увімкнення/вимкнення симуляції руху миші"""
            if enabled:
                self.mouse_timer.start(100)  # Кожні 100мс
                print("Симуляція руху миші увімкнена")
            else:
                self.mouse_timer.stop()
                print("Симуляція руху миші вимкнена")
        
        def simulate_mouse_movement(self):
            """Симуляція руху миші для тестування"""
            # Рух у межах тестового зображення
            self.mouse_position[0] += self.mouse_direction[0] * 2
            self.mouse_position[1] += self.mouse_direction[1] * 1
            
            # Відбивання від меж
            if self.mouse_position[0] <= 50 or self.mouse_position[0] >= 350:
                self.mouse_direction[0] *= -1
            
            if self.mouse_position[1] <= 50 or self.mouse_position[1] >= 250:
                self.mouse_direction[1] *= -1
            
            # Оновлення позиції зуму
            self.zoom_widget.update_position(
                int(self.mouse_position[0]), 
                int(self.mouse_position[1])
            )
        
        def set_test_position(self, x, y):
            """Встановлення тестової позиції"""
            self.zoom_widget.update_position(x, y)
            print(f"Встановлено тестову позицію: ({x}, {y})")
        
        def save_zoom_image(self):
            """Збереження зуму як зображення"""
            import tempfile
            import os
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_file.close()
            
            if self.zoom_widget.save_zoom_as_image(temp_file.name):
                print(f"Зум збережено: {temp_file.name}")
                
                # Спроба відкрити файл
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(temp_file.name)
                    elif os.name == 'posix':  # macOS/Linux
                        os.system(f'open "{temp_file.name}"')
                except Exception as e:
                    print(f"Не вдалося відкрити файл: {e}")
            else:
                print("Помилка збереження зуму")
        
        def update_info(self):
            """Оновлення інформаційної панелі"""
            info = self.zoom_widget.get_zoom_info()
            
            info_text = f"""
Статус зуму:
• Видимий: {'Так' if info['is_visible'] else 'Ні'}
• Коефіцієнт: x{info['zoom_factor']}
• Розмір області: {info['zoom_size']}px
• Розмір віджету: {info['widget_size']}px

Позиція:
• X: {info['current_position'][0]}
• Y: {info['current_position'][1]}

Стан:
• Зображення: {'Є' if info['has_image'] else 'Немає'}
• Кеш: {'Активний' if info['cache_status'] else 'Порожній'}

Симуляція:
• Рух миші: {'Увімкнена' if self.mouse_timer.isActive() else 'Вимкнена'}
            """.strip()
            
            self.info_label.setText(info_text)
        
        def mouseMoveEvent(self, event):
            """Оновлення зуму при русі миші по головному вікну"""
            # Конвертація координат віконної системи в координати тестового зображення
            # (спрощена конвертація для демонстрації)
            
            central_widget = self.centralWidget()
            if not central_widget:
                return
            
            # Знаходимо основну область (другий віджет в layout)
            main_area = central_widget.layout().itemAt(1).widget()
            if not main_area:
                return
            
            # Координати відносно основної області
            local_pos = main_area.mapFromGlobal(event.globalPos())
            
            if main_area.rect().contains(local_pos):
                # Масштабування координат до розмірів тестового зображення (400x300)
                scale_x = 400 / main_area.width()
                scale_y = 300 / main_area.height()
                
                image_x = int(local_pos.x() * scale_x)
                image_y = int(local_pos.y() * scale_y)
                
                # Обмеження межами зображення
                image_x = max(0, min(image_x, 399))
                image_y = max(0, min(image_y, 299))
                
                # Оновлення зуму (тільки якщо симуляція вимкнена)
                if not self.mouse_timer.isActive():
                    self.zoom_widget.update_position(image_x, image_y)
            
            super().mouseMoveEvent(event)
        
        def closeEvent(self, event):
            """Очищення при закритті"""
            self.mouse_timer.stop()
            self.info_timer.stop()
            
            # Приховання зуму
            self.zoom_widget.hide_zoom()
            
            super().closeEvent(event)
    
    # Запуск тесту
    app = QApplication(sys.argv)
    window = ZoomTestWindow()
    window.show()
    
    print("=== Тестування ZoomWidget ===")
    print("Функції для тестування:")
    print("1. 'Показати/Приховати зум' - переключення видимості")
    print("2. Слайдер 'Коефіцієнт зуму' - зміна x2-x8")
    print("3. Слайдер 'Розмір області' - зміна 50-200px")
    print("4. Комбобокс 'Режим роботи' - різні налаштування")
    print("5. 'Симуляція руху миші' - автоматичний рух")
    print("6. Кнопки тестових позицій - швидке переміщення")
    print("7. Рух миші по вікну - інтерактивне оновлення")
    print("8. 'Очистити кеш' - скидання кешу")
    print("9. 'Зберегти зум' - експорт поточного зуму")
    print("\nЗум показується в правому верхньому куті основної області")
    print("Червоний хрестик в центрі зуму показує точну позицію")
    
    sys.exit(app.exec_())