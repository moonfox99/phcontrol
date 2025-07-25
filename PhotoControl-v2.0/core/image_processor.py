#!/usr/bin/env python3
"""
Обробка зображень з азимутальною сіткою
Основний модуль для розрахунків азимуту, дальності та візуалізації
"""

import os
import math
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageOps
from PyQt5.QtCore import QObject, pyqtSignal


@dataclass
class AnalysisPoint:
    """Точка аналізу на зображенні"""
    x: int
    y: int
    azimuth: float
    range_value: float
    timestamp: str = ""


@dataclass 
class GridSettings:
    """Налаштування азимутальної сітки"""
    center_x: int
    center_y: int
    scale: int
    rotation_angle: float = 0.0
    offset_x: int = 0
    offset_y: int = 0
    custom_scale_distance: Optional[int] = None
    scale_edge_point: Optional[Tuple[int, int]] = None


class ImageProcessor(QObject):
    """
    Процесор зображень з азимутальною сіткою
    
    Функціональність:
    - Завантаження та обробка зображень
    - Розрахунки азимуту та дальності
    - Налаштування центру та масштабу сітки
    - Поворот та зміщення зображень
    - Візуалізація точок аналізу
    - Збереження налаштувань сітки
    """
    
    # Сигнали для повідомлення про зміни
    image_processed = pyqtSignal(object)  # PIL Image
    settings_changed = pyqtSignal(object)  # GridSettings
    analysis_completed = pyqtSignal(object)  # AnalysisPoint
    
    def __init__(self, image_path: str = None, **kwargs):
        super().__init__()
        
        # Основні властивості
        self.image_path = image_path
        self.original_image: Optional[Image.Image] = None
        self.working_image: Optional[Image.Image] = None
        
        # Налаштування сітки
        self.grid_settings = GridSettings(
            center_x=0,
            center_y=0,
            scale=kwargs.get('scale', 300),
            rotation_angle=0.0,
            offset_x=0,
            offset_y=0
        )
        
        # Стан обробки
        self.current_analysis: Optional[AnalysisPoint] = None
        self.is_modified = False
        
        if image_path:
            self.load_image(image_path)
    
    # ===============================
    # ЗАВАНТАЖЕННЯ ТА ІНІЦІАЛІЗАЦІЯ
    # ===============================
    
    def load_image(self, image_path: str) -> bool:
        """
        Завантаження зображення з файлу
        
        Args:
            image_path: Шлях до файлу зображення
            
        Returns:
            True якщо завантаження успішне
        """
        try:
            self.image_path = image_path
            self.original_image = Image.open(image_path)
            self.working_image = self.original_image.copy()
            
            # Автоматичне виправлення орієнтації EXIF
            self._auto_fix_orientation()
            
            # Ініціалізація центру сітки
            self._initialize_grid_center()
            
            # Конвертація в RGB якщо потрібно
            self._ensure_rgb_format()
            
            self.is_modified = False
            print(f"Зображення завантажено: {os.path.basename(image_path)}")
            print(f"Розмір: {self.working_image.width}x{self.working_image.height}")
            
            self.image_processed.emit(self.working_image)
            return True
            
        except Exception as e:
            print(f"Помилка завантаження зображення: {e}")
            return False
    
    def _auto_fix_orientation(self):
        """Автоматичне виправлення орієнтації за EXIF даними"""
        try:
            if hasattr(self.working_image, '_getexif'):
                exif = self.working_image._getexif()
                if exif is not None:
                    orientation = exif.get(274)  # EXIF Orientation tag
                    if orientation:
                        self.working_image = ImageOps.exif_transpose(self.working_image)
                        self.original_image = self.working_image.copy()
                        print("EXIF орієнтація виправлена")
        except Exception as e:
            print(f"Помилка виправлення EXIF: {e}")
    
    def _initialize_grid_center(self):
        """Ініціалізація центру сітки в центрі зображення"""
        if self.working_image:
            self.grid_settings.center_x = self.working_image.width // 2
            self.grid_settings.center_y = self.working_image.height // 2
    
    def _ensure_rgb_format(self):
        """Конвертація зображення в RGB формат"""
        if self.working_image.mode != 'RGB':
            if self.working_image.mode == 'RGBA':
                # Створюємо білий фон для RGBA
                rgb_image = Image.new('RGB', self.working_image.size, (255, 255, 255))
                rgb_image.paste(self.working_image, mask=self.working_image.split()[-1])
                self.working_image = rgb_image
            else:
                self.working_image = self.working_image.convert('RGB')
            
            self.original_image = self.working_image.copy()
    
    # ===============================
    # НАЛАШТУВАННЯ СІТКИ
    # ===============================
    
    def set_grid_center(self, x: int, y: int):
        """
        Встановлення центру азимутальної сітки
        
        Args:
            x, y: Координати центру в пікселях
        """
        if not self._validate_coordinates(x, y):
            return False
        
        self.grid_settings.center_x = x
        self.grid_settings.center_y = y
        self.is_modified = True
        
        print(f"Центр сітки встановлено: ({x}, {y})")
        self.settings_changed.emit(self.grid_settings)
        return True
    
    def move_center(self, dx: int, dy: int):
        """
        Зміщення центру сітки на вказану відстань
        
        Args:
            dx: Зміщення по X (позитивне = праворуч)
            dy: Зміщення по Y (позитивне = вниз)
        """
        new_x = self.grid_settings.center_x + dx
        new_y = self.grid_settings.center_y + dy
        
        return self.set_grid_center(new_x, new_y)
    
    def set_scale(self, scale: int):
        """
        Встановлення масштабу сітки
        
        Args:
            scale: Масштаб в одиницях до краю зображення
        """
        if scale <= 0:
            return False
        
        self.grid_settings.scale = scale
        self.is_modified = True
        
        print(f"Масштаб встановлено: 1:{scale}")
        self.settings_changed.emit(self.grid_settings)
        return True
    
    def set_scale_edge_point(self, x: int, y: int):
        """
        Встановлення точки краю для кастомного масштабу
        
        Args:
            x, y: Координати точки краю
        """
        if not self._validate_coordinates(x, y):
            return False
        
        # Розрахунок відстані від центру до точки
        distance = self._calculate_pixel_distance(
            self.grid_settings.center_x, self.grid_settings.center_y, x, y
        )
        
        if distance > 0:
            self.grid_settings.scale_edge_point = (x, y)
            self.grid_settings.custom_scale_distance = int(distance)
            self.is_modified = True
            
            print(f"Точка масштабу: ({x}, {y}), відстань: {distance:.1f} пікселів")
            self.settings_changed.emit(self.grid_settings)
            return True
        
        return False
    
    # ===============================
    # ПЕРЕТВОРЕННЯ ЗОБРАЖЕННЯ
    # ===============================
    
    def rotate_image(self, angle: float):
        """
        Поворот зображення на вказаний кут
        
        Args:
            angle: Кут повороту в градусах (позитивний = за годинниковою)
        """
        self.grid_settings.rotation_angle += angle
        self.grid_settings.rotation_angle %= 360
        
        # Поворот зображення (PIL повертає проти годинникової, тому негативний кут)
        self.working_image = self.original_image.rotate(
            -self.grid_settings.rotation_angle, 
            expand=True, 
            fillcolor='white'
        )
        
        # Перерахунок координат центру після повороту
        self._recalculate_center_after_rotation()
        
        self.is_modified = True
        print(f"Зображення повернуто на {angle}°. Загальний поворот: {self.grid_settings.rotation_angle}°")
        
        self.image_processed.emit(self.working_image)
        self.settings_changed.emit(self.grid_settings)
    
    def _recalculate_center_after_rotation(self):
        """Перерахунок координат центру після повороту зображення"""
        if not self.original_image:
            return
        
        # Отримуємо нові розміри після повороту
        original_center_x = self.original_image.width // 2
        original_center_y = self.original_image.height // 2
        
        # Розрахунок нового центру з урахуванням повороту та зміщень
        self.grid_settings.center_x = (self.working_image.width // 2 + 
                                     self.grid_settings.offset_x)
        self.grid_settings.center_y = (self.working_image.height // 2 + 
                                     self.grid_settings.offset_y)
    
    def reset_transformations(self):
        """Скидання всіх перетворень до оригінального стану"""
        if not self.original_image:
            return False
        
        self.working_image = self.original_image.copy()
        self.grid_settings.rotation_angle = 0.0
        self.grid_settings.offset_x = 0
        self.grid_settings.offset_y = 0
        
        self._initialize_grid_center()
        self.is_modified = False
        
        print("Всі перетворення скинуто")
        self.image_processed.emit(self.working_image)
        self.settings_changed.emit(self.grid_settings)
        return True
    
    # ===============================
    # РОЗРАХУНКИ АЗИМУТУ ТА ДАЛЬНОСТІ
    # ===============================
    
    def calculate_azimuth_range(self, x: int, y: int) -> Tuple[float, float]:
        """
        Розрахунок азимуту та дальності для точки
        
        Args:
            x, y: Координати точки на зображенні
            
        Returns:
            Кортеж (азимут_в_градусах, дальність_в_одиницях)
        """
        # Відносні координати від центру сітки
        dx = x - self.grid_settings.center_x
        dy = y - self.grid_settings.center_y
        
        # Розрахунок азимуту (0° = північ, за годинниковою)
        azimuth_rad = math.atan2(dx, -dy)  # -dy тому що Y збільшується вниз
        azimuth_deg = math.degrees(azimuth_rad)
        
        # Нормалізація азимуту до діапазону 0-360°
        if azimuth_deg < 0:
            azimuth_deg += 360
        
        # Розрахунок дальності
        range_value = self._calculate_range(dx, dy)
        
        return azimuth_deg, range_value
    
    def _calculate_range(self, dx: int, dy: int) -> float:
        """
        Розрахунок дальності в одиницях масштабу
        
        Args:
            dx, dy: Відносні координати від центру
            
        Returns:
            Дальність в одиницях масштабу
        """
        pixel_distance = math.sqrt(dx * dx + dy * dy)
        
        if self.grid_settings.custom_scale_distance:
            # Використовуємо кастомний масштаб
            units_per_pixel = self.grid_settings.scale / self.grid_settings.custom_scale_distance
        else:
            # Використовуємо автоматичний масштаб до краю зображення
            max_distance = self._get_max_distance_to_edge()
            units_per_pixel = self.grid_settings.scale / max_distance
        
        return pixel_distance * units_per_pixel
    
    def _get_max_distance_to_edge(self) -> float:
        """Розрахунок максимальної відстані від центру до краю зображення"""
        if not self.working_image:
            return 1.0
        
        distances = [
            self.grid_settings.center_x,  # Ліворуч
            self.working_image.width - self.grid_settings.center_x,  # Праворуч
            self.grid_settings.center_y,  # Вгору
            self.working_image.height - self.grid_settings.center_y  # Вниз
        ]
        
        return max(distances)
    
    # ===============================
    # ОБРОБКА КЛІКІВ ТА АНАЛІЗ
    # ===============================
    
    def process_click(self, x: int, y: int) -> AnalysisPoint:
        """
        Обробка кліку на зображенні - створення точки аналізу
        
        Args:
            x, y: Координати кліку
            
        Returns:
            AnalysisPoint з розрахованими даними
        """
        if not self._validate_coordinates(x, y):
            return None
        
        # Розрахунок азимуту та дальності
        azimuth, range_value = self.calculate_azimuth_range(x, y)
        
        # Створення точки аналізу
        self.current_analysis = AnalysisPoint(
            x=x,
            y=y,
            azimuth=azimuth,
            range_value=range_value,
            timestamp=self._get_current_timestamp()
        )
        
        print(f"Точка аналізу: ({x}, {y}) -> Азимут: {azimuth:.1f}°, Дальність: {range_value:.1f}")
        
        self.analysis_completed.emit(self.current_analysis)
        return self.current_analysis
    
    def create_processed_image(self, line_to_edge: bool = True) -> Image.Image:
        """
        Створення зображення з візуалізацією точки аналізу
        
        Args:
            line_to_edge: Чи малювати лінію до краю
            
        Returns:
            PIL Image з нанесеними елементами
        """
        if not self.working_image or not self.current_analysis:
            return self.working_image
        
        # Створюємо копію для обробки
        processed_image = self.working_image.copy()
        draw = ImageDraw.Draw(processed_image)
        
        # Параметри візуалізації
        point_color = (255, 0, 0)  # Червоний
        line_color = (0, 255, 0)   # Зелений
        circle_radius = 8
        line_width = 3
        
        # Малюємо точку аналізу
        self._draw_analysis_point(draw, self.current_analysis, point_color, circle_radius)
        
        # Малюємо лінію до краю (якщо потрібно)
        if line_to_edge:
            edge_point = self._calculate_edge_point(self.current_analysis)
            self._draw_line_to_edge(draw, self.current_analysis, edge_point, line_color, line_width)
        
        return processed_image
    
    def _draw_analysis_point(self, draw: ImageDraw.Draw, point: AnalysisPoint, 
                           color: Tuple[int, int, int], radius: int):
        """Малювання точки аналізу на зображенні"""
        x, y = point.x, point.y
        
        # Коло навколо точки
        draw.ellipse([
            x - radius, y - radius,
            x + radius, y + radius
        ], fill=color)
        
        # Центральна точка
        draw.ellipse([
            x - 2, y - 2,
            x + 2, y + 2
        ], fill=(255, 255, 255))
    
    def _draw_line_to_edge(self, draw: ImageDraw.Draw, point: AnalysisPoint,
                          edge_point: Tuple[int, int], color: Tuple[int, int, int], width: int):
        """Малювання лінії від точки до краю зображення"""
        draw.line([
            (point.x, point.y),
            edge_point
        ], fill=color, width=width)
    
    def _calculate_edge_point(self, point: AnalysisPoint) -> Tuple[int, int]:
        """Розрахунок точки на краю зображення в напрямку від центру"""
        if not self.working_image:
            return (point.x, point.y)
        
        # Вектор від центру до точки
        dx = point.x - self.grid_settings.center_x
        dy = point.y - self.grid_settings.center_y
        
        # Нормалізація вектора
        if dx == 0 and dy == 0:
            return (self.working_image.width - 1, point.y)
        
        # Знаходимо перетин з краями зображення
        width, height = self.working_image.width, self.working_image.height
        
        # Параметричне рівняння лінії: (x, y) = (center_x, center_y) + t * (dx, dy)
        t_values = []
        
        # Перетин з лівим краєм (x = 0)
        if dx < 0:
            t = -self.grid_settings.center_x / dx
            y = self.grid_settings.center_y + t * dy
            if 0 <= y <= height:
                t_values.append((t, (0, int(y))))
        
        # Перетин з правим краєм (x = width)
        if dx > 0:
            t = (width - self.grid_settings.center_x) / dx
            y = self.grid_settings.center_y + t * dy
            if 0 <= y <= height:
                t_values.append((t, (width - 1, int(y))))
        
        # Перетин з верхнім краєм (y = 0)
        if dy < 0:
            t = -self.grid_settings.center_y / dy
            x = self.grid_settings.center_x + t * dx
            if 0 <= x <= width:
                t_values.append((t, (int(x), 0)))
        
        # Перетин з нижнім краєм (y = height)
        if dy > 0:
            t = (height - self.grid_settings.center_y) / dy
            x = self.grid_settings.center_x + t * dx
            if 0 <= x <= width:
                t_values.append((t, (int(x), height - 1)))
        
        # Вибираємо найближчий край (найменше t > 0)
        valid_intersections = [(t, point) for t, point in t_values if t > 0]
        
        if valid_intersections:
            return min(valid_intersections, key=lambda x: x[0])[1]
        else:
            # Якщо не знайшли перетин, повертаємо праву сторону
            return (width - 1, point.y)
    
    # ===============================
    # ДОПОМІЖНІ МЕТОДИ
    # ===============================
    
    def _validate_coordinates(self, x: int, y: int) -> bool:
        """Перевірка чи координати знаходяться в межах зображення"""
        if not self.working_image:
            return False
        
        return (0 <= x < self.working_image.width and 
                0 <= y < self.working_image.height)
    
    def _calculate_pixel_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """Розрахунок відстані між двома точками в пікселях"""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def _get_current_timestamp(self) -> str:
        """Отримання поточної мітки часу"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_center_preview(self, size: int = 200) -> Image.Image:
        """
        Створення превью області навколо центру сітки
        
        Args:
            size: Розмір превью в пікселях
            
        Returns:
            PIL Image з областю навколо центру
        """
        if not self.working_image:
            return None
        
        half_size = size // 2
        
        # Координати області
        left = max(0, self.grid_settings.center_x - half_size)
        top = max(0, self.grid_settings.center_y - half_size)
        right = min(self.working_image.width, self.grid_settings.center_x + half_size)
        bottom = min(self.working_image.height, self.grid_settings.center_y + half_size)
        
        # Вирізаємо область
        preview = self.working_image.crop((left, top, right, bottom))
        
        # Малюємо хрестик в центрі
        draw = ImageDraw.Draw(preview)
        center_x = self.grid_settings.center_x - left
        center_y = self.grid_settings.center_y - top
        
        # Перевіряємо чи центр в межах превью
        if 0 <= center_x < preview.width and 0 <= center_y < preview.height:
            cross_size = 10
            draw.line([
                (center_x - cross_size, center_y),
                (center_x + cross_size, center_y)
            ], fill=(255, 0, 0), width=2)
            draw.line([
                (center_x, center_y - cross_size),
                (center_x, center_y + cross_size)
            ], fill=(255, 0, 0), width=2)
        
        return preview
    
    # ===============================
    # ЗБЕРЕЖЕННЯ ТА ЗАВАНТАЖЕННЯ НАЛАШТУВАНЬ
    # ===============================
    
    def save_grid_settings(self) -> Dict[str, Any]:
        """
        Збереження поточних налаштувань сітки
        
        Returns:
            Словник з налаштуваннями
        """
        settings = {
            'center_x': self.grid_settings.center_x,
            'center_y': self.grid_settings.center_y,
            'scale': self.grid_settings.scale,
            'rotation_angle': self.grid_settings.rotation_angle,
            'offset_x': self.grid_settings.offset_x,
            'offset_y': self.grid_settings.offset_y,
            'custom_scale_distance': self.grid_settings.custom_scale_distance,
            'scale_edge_point': self.grid_settings.scale_edge_point
        }
        
        print("Налаштування сітки збережено")
        return settings
    
    def load_grid_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Завантаження налаштувань сітки
        
        Args:
            settings: Словник з налаштуваннями
            
        Returns:
            True якщо завантаження успішне
        """
        try:
            self.grid_settings.center_x = settings.get('center_x', self.grid_settings.center_x)
            self.grid_settings.center_y = settings.get('center_y', self.grid_settings.center_y)
            self.grid_settings.scale = settings.get('scale', self.grid_settings.scale)
            self.grid_settings.rotation_angle = settings.get('rotation_angle', 0.0)
            self.grid_settings.offset_x = settings.get('offset_x', 0)
            self.grid_settings.offset_y = settings.get('offset_y', 0)
            self.grid_settings.custom_scale_distance = settings.get('custom_scale_distance')
            self.grid_settings.scale_edge_point = settings.get('scale_edge_point')
            
            # Застосовуємо поворот якщо потрібно
            if self.grid_settings.rotation_angle != 0:
                self._apply_rotation()
            
            self.is_modified = True
            print("Налаштування сітки завантажено")
            
            self.settings_changed.emit(self.grid_settings)
            return True
            
        except Exception as e:
            print(f"Помилка завантаження налаштувань: {e}")
            return False
    
    def _apply_rotation(self):
        """Застосування збереженого кута повороту"""
        if self.original_image and self.grid_settings.rotation_angle != 0:
            self.working_image = self.original_image.rotate(
                -self.grid_settings.rotation_angle,
                expand=True,
                fillcolor='white'
            )
            self._recalculate_center_after_rotation()
            self.image_processed.emit(self.working_image)
    
    def apply_settings_to_new_image(self, settings: Dict[str, Any]):
        """
        Застосування збережених налаштувань до нового зображення
        
        Args:
            settings: Збережені налаштування від попереднього зображення
        """
        if not self.working_image:
            return
        
        # Отримуємо центр нового зображення
        image_center_x = self.working_image.width // 2
        image_center_y = self.working_image.height // 2
        
        # Застосовуємо зміщення центру відносно центру зображення
        center_offset_x = settings.get('center_offset_x', 0)
        center_offset_y = settings.get('center_offset_y', 0)
        
        self.grid_settings.center_x = image_center_x + center_offset_x
        self.grid_settings.center_y = image_center_y + center_offset_y
        
        # Застосовуємо інші налаштування
        self.grid_settings.scale = settings.get('scale', 300)
        self.grid_settings.rotation_angle = settings.get('rotation_angle', 0.0)
        
        # Відновлюємо scale edge point відносно центру зображення
        if settings.get('scale_edge_relative') and settings.get('custom_scale_distance'):
            edge_relative = settings['scale_edge_relative']
            new_edge_x = image_center_x + edge_relative[0]
            new_edge_y = image_center_y + edge_relative[1]
            
            self.set_scale_edge_point(new_edge_x, new_edge_y)
        
        # Застосовуємо поворот
        if self.grid_settings.rotation_angle != 0:
            self._apply_rotation()
        
        print("Налаштування сітки застосовано до нового зображення")
        self.settings_changed.emit(self.grid_settings)
    
    # ===============================
    # СТАТИСТИКА ТА ІНФОРМАЦІЯ
    # ===============================
    
    def get_image_info(self) -> Dict[str, Any]:
        """
        Отримання інформації про поточне зображення
        
        Returns:
            Словник з інформацією про зображення
        """
        if not self.working_image:
            return {}
        
        return {
            'filename': os.path.basename(self.image_path) if self.image_path else "Невідомо",
            'width': self.working_image.width,
            'height': self.working_image.height,
            'mode': self.working_image.mode,
            'format': self.working_image.format,
            'has_analysis': self.current_analysis is not None,
            'is_modified': self.is_modified,
            'grid_center': (self.grid_settings.center_x, self.grid_settings.center_y),
            'scale': self.grid_settings.scale,
            'rotation': self.grid_settings.rotation_angle,
            'max_range': self._get_max_distance_to_edge() * (self.grid_settings.scale / self._get_max_distance_to_edge()) if self.working_image else 0
        }
    
    def get_analysis_summary(self) -> str:
        """
        Отримання текстового резюме аналізу
        
        Returns:
            Рядок з інформацією про поточний аналіз
        """
        if not self.current_analysis:
            return "Аналіз не виконано"
        
        info = self.get_image_info()
        
        summary = [
            f"📁 Файл: {info.get('filename', 'Невідомо')}",
            f"📐 Розмір: {info.get('width', 0)}×{info.get('height', 0)}",
            f"🎯 Центр сітки: ({self.grid_settings.center_x}, {self.grid_settings.center_y})",
            f"📏 Масштаб: 1:{self.grid_settings.scale}",
            f"📍 Точка аналізу: ({self.current_analysis.x}, {self.current_analysis.y})",
            f"🧭 Азимут: {self.current_analysis.azimuth:.1f}°",
            f"📊 Дальність: {self.current_analysis.range_value:.1f} од.",
            f"⏰ Час: {self.current_analysis.timestamp}"
        ]
        
        if self.grid_settings.rotation_angle != 0:
            summary.insert(-1, f"🔄 Поворот: {self.grid_settings.rotation_angle:.1f}°")
        
        return "\n".join(summary)
    
    # ===============================
    # МЕТОДИ ДЛЯ ЗОВНІШНЬОГО ВИКОРИСТАННЯ
    # ===============================
    
    def is_ready(self) -> bool:
        """Перевірка чи процесор готовий до роботи"""
        return self.working_image is not None
    
    def has_analysis(self) -> bool:
        """Перевірка чи є поточний аналіз"""
        return self.current_analysis is not None
    
    def clear_analysis(self):
        """Очищення поточного аналізу"""
        self.current_analysis = None
        print("Аналіз очищено")
    
    def get_current_image(self) -> Optional[Image.Image]:
        """Отримання поточного робочого зображення"""
        return self.working_image
    
    def get_processed_image(self) -> Optional[Image.Image]:
        """Отримання обробленого зображення з візуалізацією"""
        return self.create_processed_image()
    
    def export_analysis_data(self) -> Optional[Dict[str, Any]]:
        """
        Експорт даних аналізу для збереження
        
        Returns:
            Словник з повними даними аналізу
        """
        if not self.current_analysis:
            return None
        
        return {
            'image_info': self.get_image_info(),
            'grid_settings': self.save_grid_settings(),
            'analysis_point': {
                'x': self.current_analysis.x,
                'y': self.current_analysis.y,
                'azimuth': self.current_analysis.azimuth,
                'range_value': self.current_analysis.range_value,
                'timestamp': self.current_analysis.timestamp
            },
            'summary': self.get_analysis_summary()
        }


# ===============================
# ДОПОМІЖНІ ФУНКЦІЇ
# ===============================

def create_test_processor(width: int = 800, height: int = 600) -> ImageProcessor:
    """
    Створення тестового процесора з штучним зображенням
    
    Args:
        width, height: Розміри тестового зображення
        
    Returns:
        Налаштований ImageProcessor
    """
    # Створення тестового зображення
    test_image = Image.new('RGB', (width, height), (240, 240, 240))
    draw = ImageDraw.Draw(test_image)
    
    # Малюємо сітку
    for i in range(0, width, 50):
        draw.line([(i, 0), (i, height)], fill=(200, 200, 200))
    for i in range(0, height, 50):
        draw.line([(0, i), (width, i)], fill=(200, 200, 200))
    
    # Малюємо центральний хрест
    center_x, center_y = width // 2, height // 2
    draw.line([(center_x - 20, center_y), (center_x + 20, center_y)], fill=(255, 0, 0), width=3)
    draw.line([(center_x, center_y - 20), (center_x, center_y + 20)], fill=(255, 0, 0), width=3)
    
    # Створення процесора
    processor = ImageProcessor()
    processor.working_image = test_image
    processor.original_image = test_image.copy()
    processor._initialize_grid_center()
    
    return processor


if __name__ == "__main__":
    # Тестування модуля
    print("=== Тестування ImageProcessor ===")
    
    # Створення тестового процесора
    processor = create_test_processor()
    print(f"Тестовий процесор створено: {processor.working_image.width}×{processor.working_image.height}")
    
    # Тест розрахунків
    test_points = [
        (400, 300),  # Центр
        (450, 300),  # Схід
        (400, 250),  # Північ
        (350, 350),  # Південний захід
    ]
    
    for x, y in test_points:
        analysis = processor.process_click(x, y)
        print(f"Точка ({x}, {y}): Азимут={analysis.azimuth:.1f}°, Дальність={analysis.range_value:.1f}")
    
    print("=== Тестування завершено ===")