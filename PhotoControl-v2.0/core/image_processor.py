#!/usr/bin/env python3
"""
Основна логіка обробки зображень з азимутальними сітками
Клас для розрахунку азимуту, дальності та управління параметрами сітки
"""

import math
import os
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageOps

from core.constants import IMAGE, GRID, VALIDATION


@dataclass
class AnalysisPoint:
    """Точка аналізу на зображенні"""
    x: int
    y: int
    azimuth: float
    range_km: float


@dataclass
class GridSettings:
    """Налаштування азимутальної сітки"""
    center_x: int
    center_y: int
    scale_value: int
    custom_scale_distance: Optional[float] = None
    scale_edge_x: Optional[int] = None
    scale_edge_y: Optional[int] = None


class ImageProcessor:
    """
    Головний клас для обробки зображень з азимутальними сітками
    
    Функціональність:
    - Завантаження та попередня обробка зображень
    - Управління центром азимутальної сітки
    - Розрахунок азимуту та дальності
    - Калібрування масштабу
    - Збереження налаштувань між зображеннями
    """
    
    def __init__(self, image_path: str, scale_value: int = None):
        """
        Ініціалізація процесора зображень
        
        Args:
            image_path: Шлях до зображення
            scale_value: Значення масштабу (за замовчуванням з констант)
        """
        self.image_path = image_path
        self.original_image: Optional[Image.Image] = None
        self.working_image: Optional[Image.Image] = None
        
        # Налаштування сітки
        self.grid_settings = GridSettings(
            center_x=0,
            center_y=0,
            scale_value=scale_value or int(GRID.DEFAULT_SCALE)
        )
        
        # Поточна точка аналізу
        self.current_analysis_point: Optional[AnalysisPoint] = None
        
        # Флаги стану
        self.is_loaded = False
        self.has_custom_scale = False
        
        # Завантажуємо зображення
        self._load_image()
    
    def _load_image(self) -> bool:
        """
        Завантаження та попередня обробка зображення
        
        Returns:
            True якщо завантаження успішне
        """
        try:
            if not os.path.exists(self.image_path):
                raise FileNotFoundError(f"Файл не знайдено: {self.image_path}")
            
            # Завантажуємо оригінальне зображення
            self.original_image = Image.open(self.image_path)
            
            # Автокорекція EXIF орієнтації
            self.original_image = ImageOps.exif_transpose(self.original_image)
            
            # Перетворення в RGB для JPG сумісності
            if self.original_image.mode != 'RGB':
                if self.original_image.mode == 'RGBA':
                    # Створюємо білий фон для RGBA
                    rgb_image = Image.new('RGB', self.original_image.size, (255, 255, 255))
                    rgb_image.paste(self.original_image, mask=self.original_image.split()[-1])
                    self.original_image = rgb_image
                else:
                    self.original_image = self.original_image.convert('RGB')
            
            # Створюємо робочу копію
            self.working_image = self.original_image.copy()
            
            # Встановлюємо центр за замовчуванням (центр зображення)
            self.grid_settings.center_x = self.original_image.width // 2
            self.grid_settings.center_y = self.original_image.height // 2
            
            # Валідація розмірів
            self._validate_image_dimensions()
            
            self.is_loaded = True
            print(f"✓ Зображення завантажено: {os.path.basename(self.image_path)}")
            print(f"  Розмір: {self.original_image.width}x{self.original_image.height}")
            print(f"  Центр сітки: ({self.grid_settings.center_x}, {self.grid_settings.center_y})")
            
            return True
            
        except Exception as e:
            print(f"✗ Помилка завантаження зображення: {e}")
            self.is_loaded = False
            return False
    
    def _validate_image_dimensions(self) -> None:
        """Валідація розмірів зображення згідно з вимогами"""
        if not self.original_image:
            return
        
        width, height = self.original_image.size
        
        # Перевірка мінімальних розмірів
        if width < VALIDATION.MIN_IMAGE_WIDTH or height < VALIDATION.MIN_IMAGE_HEIGHT:
            print(f"⚠️ Попередження: Зображення менше рекомендованого розміру "
                  f"({VALIDATION.MIN_IMAGE_WIDTH}x{VALIDATION.MIN_IMAGE_HEIGHT})")
        
        # Перевірка пропорцій (15:13)
        actual_ratio = width / height
        expected_ratio = IMAGE.REQUIRED_ASPECT_RATIO
        tolerance = 0.1
        
        if abs(actual_ratio - expected_ratio) > tolerance:
            print(f"⚠️ Попередження: Невідповідність пропорцій. "
                  f"Очікується {expected_ratio:.2f}, фактично {actual_ratio:.2f}")
    
    def move_center(self, dx: int, dy: int) -> bool:
        """
        Переміщення центру азимутальної сітки
        
        Args:
            dx: Зміщення по X (право = додатнє)
            dy: Зміщення по Y (вниз = додатнє)
            
        Returns:
            True якщо переміщення успішне
        """
        if not self.is_loaded:
            return False
        
        # Розрахунок нових координат
        new_x = self.grid_settings.center_x + dx
        new_y = self.grid_settings.center_y + dy
        
        # Обмеження межами зображення
        new_x = max(0, min(new_x, self.original_image.width - 1))
        new_y = max(0, min(new_y, self.original_image.height - 1))
        
        # Оновлення координат
        old_x, old_y = self.grid_settings.center_x, self.grid_settings.center_y
        self.grid_settings.center_x = new_x
        self.grid_settings.center_y = new_y
        
        # Перерахунок поточної точки аналізу якщо є
        if self.current_analysis_point:
            self._recalculate_analysis_point()
        
        print(f"Центр переміщено: ({old_x}, {old_y}) → ({new_x}, {new_y})")
        return True
    
    def set_center(self, x: int, y: int) -> bool:
        """
        Встановлення центру сітки в абсолютних координатах
        
        Args:
            x: Координата X
            y: Координата Y
            
        Returns:
            True якщо встановлення успішне
        """
        if not self.is_loaded:
            return False
        
        # Обмеження межами зображення
        x = max(0, min(x, self.original_image.width - 1))
        y = max(0, min(y, self.original_image.height - 1))
        
        old_x, old_y = self.grid_settings.center_x, self.grid_settings.center_y
        self.grid_settings.center_x = x
        self.grid_settings.center_y = y
        
        # Перерахунок поточної точки аналізу
        if self.current_analysis_point:
            self._recalculate_analysis_point()
        
        print(f"Центр встановлено: ({old_x}, {old_y}) → ({x}, {y})")
        return True
    
    def set_scale_edge(self, x: int, y: int) -> bool:
        """
        Встановлення краю масштабу для калібрування
        
        Args:
            x: Координата X краю масштабу
            y: Координата Y краю масштабу
            
        Returns:
            True якщо встановлення успішне
        """
        if not self.is_loaded:
            return False
        
        # Обмеження межами зображення
        x = max(0, min(x, self.original_image.width - 1))
        y = max(0, min(y, self.original_image.height - 1))
        
        # Розрахунок відстані від центру до краю
        dx = x - self.grid_settings.center_x
        dy = y - self.grid_settings.center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Збереження налаштувань
        self.grid_settings.scale_edge_x = x
        self.grid_settings.scale_edge_y = y
        self.grid_settings.custom_scale_distance = distance
        self.has_custom_scale = True
        
        # Перерахунок поточної точки аналізу
        if self.current_analysis_point:
            self._recalculate_analysis_point()
        
        print(f"Край масштабу встановлено: ({x}, {y}), відстань: {distance:.1f}px")
        return True
    
    def set_scale_value(self, scale_value: int) -> bool:
        """
        Встановлення значення масштабу
        
        Args:
            scale_value: Значення масштабу (25-350)
            
        Returns:
            True якщо встановлення успішне
        """
        if scale_value not in [int(s) for s in GRID.AVAILABLE_SCALES]:
            print(f"✗ Невалідне значення масштабу: {scale_value}")
            return False
        
        old_scale = self.grid_settings.scale_value
        self.grid_settings.scale_value = scale_value
        
        # Перерахунок поточної точки аналізу
        if self.current_analysis_point:
            self._recalculate_analysis_point()
        
        print(f"Масштаб змінено: {old_scale} → {scale_value}")
        return True
    
    def set_analysis_point(self, x: int, y: int) -> Optional[AnalysisPoint]:
        """
        Встановлення точки аналізу та розрахунок азимуту/дальності
        
        Args:
            x: Координата X точки
            y: Координата Y точки
            
        Returns:
            Об'єкт AnalysisPoint з розрахованими значеннями або None
        """
        if not self.is_loaded:
            return None
        
        # Обмеження межами зображення
        x = max(0, min(x, self.original_image.width - 1))
        y = max(0, min(y, self.original_image.height - 1))
        
        # Розрахунок азимуту та дальності
        azimuth, range_km = self._calculate_azimuth_range(x, y)
        
        # Створення об'єкту точки аналізу
        self.current_analysis_point = AnalysisPoint(
            x=x,
            y=y,
            azimuth=azimuth,
            range_km=range_km
        )
        
        print(f"Точка аналізу: ({x}, {y}) → Азимут: {azimuth:.0f}°, Дальність: {range_km:.0f} км")
        return self.current_analysis_point
    
    def _calculate_azimuth_range(self, x: int, y: int) -> Tuple[float, float]:
        """
        Розрахунок азимуту та дальності для точки
        
        Args:
            x: Координата X точки
            y: Координата Y точки
            
        Returns:
            Кортеж (азимут_в_градусах, дальність_в_км)
        """
        # Відносні координати від центру
        dx = x - self.grid_settings.center_x
        dy = self.grid_settings.center_y - y  # Інвертуємо Y (математичні координати)
        
        # Розрахунок дальності в пікселях
        range_pixels = math.sqrt(dx * dx + dy * dy)
        
        # Розрахунок дальності в реальних одиницях
        if self.has_custom_scale and self.grid_settings.custom_scale_distance:
            # Використовуємо користувацький масштаб
            range_actual = (range_pixels / self.grid_settings.custom_scale_distance) * self.grid_settings.scale_value
        else:
            # Використовуємо стандартний масштаб (до нижнього краю)
            bottom_edge_distance = self.original_image.height - self.grid_settings.center_y
            if bottom_edge_distance > 0:
                range_actual = (range_pixels / bottom_edge_distance) * self.grid_settings.scale_value
            else:
                range_actual = 0.0
        
        # Розрахунок азимуту
        azimuth_radians = math.atan2(dx, dy)  # atan2(x, y) для стандартного азимуту
        azimuth_degrees = math.degrees(azimuth_radians)
        
        # Нормалізація азимуту до діапазону 0-360°
        if azimuth_degrees < 0:
            azimuth_degrees += 360
        
        return azimuth_degrees, range_actual
    
    def _recalculate_analysis_point(self) -> None:
        """Перерахунок поточної точки аналізу після зміни параметрів сітки"""
        if self.current_analysis_point:
            azimuth, range_km = self._calculate_azimuth_range(
                self.current_analysis_point.x,
                self.current_analysis_point.y
            )
            self.current_analysis_point.azimuth = azimuth
            self.current_analysis_point.range_km = range_km
    
    def create_preview_image(self, show_grid: bool = True, show_analysis: bool = True) -> Optional[Image.Image]:
        """
        Створення зображення з накладеними елементами сітки та аналізу
        
        Args:
            show_grid: Показувати елементи сітки (центр, край масштабу)
            show_analysis: Показувати точку аналізу та лінію
            
        Returns:
            Зображення з накладеними елементами або None
        """
        if not self.is_loaded:
            return None
        
        # Створюємо копію для малювання
        preview_image = self.working_image.copy()
        draw = ImageDraw.Draw(preview_image)
        
        if show_grid:
            self._draw_grid_elements(draw)
        
        if show_analysis and self.current_analysis_point:
            self._draw_analysis_elements(draw)
        
        return preview_image
    
    def _draw_grid_elements(self, draw: ImageDraw.Draw) -> None:
        """Малювання елементів сітки (центр, край масштабу)"""
        # Малювання центру сітки
        center_x, center_y = self.grid_settings.center_x, self.grid_settings.center_y
        cross_size = IMAGE.CROSS_SIZE
        
        # Червоний хрестик в центрі
        draw.line([center_x - cross_size, center_y, center_x + cross_size, center_y], 
                 fill=IMAGE.CENTER_COLOR, width=IMAGE.LINE_WIDTH)
        draw.line([center_x, center_y - cross_size, center_x, center_y + cross_size], 
                 fill=IMAGE.CENTER_COLOR, width=IMAGE.LINE_WIDTH)
        draw.ellipse([center_x - 3, center_y - 3, center_x + 3, center_y + 3], 
                    fill=IMAGE.CENTER_COLOR, outline='white')
        
        # Малювання краю масштабу якщо встановлено
        if (self.has_custom_scale and 
            self.grid_settings.scale_edge_x is not None and 
            self.grid_settings.scale_edge_y is not None):
            
            edge_x = self.grid_settings.scale_edge_x
            edge_y = self.grid_settings.scale_edge_y
            
            # Зелена точка краю масштабу
            draw.ellipse([edge_x - 5, edge_y - 5, edge_x + 5, edge_y + 5], 
                        fill=IMAGE.SCALE_EDGE_COLOR, outline='white', width=2)
            
            # Лінія від центру до краю
            draw.line([center_x, center_y, edge_x, edge_y], 
                     fill=IMAGE.SCALE_EDGE_COLOR, width=2)
            
            # Перпендикулярна лінія на кінці
            dx = edge_x - center_x
            dy = edge_y - center_y
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                nx, ny = -dy/length, dx/length
                perp_size = 8
                draw.line([
                    edge_x + nx*perp_size, edge_y + ny*perp_size,
                    edge_x - nx*perp_size, edge_y - ny*perp_size
                ], fill=IMAGE.SCALE_EDGE_COLOR, width=2)
    
    def _draw_analysis_elements(self, draw: ImageDraw.Draw) -> None:
        """Малювання елементів аналізу (точка, лінія)"""
        point = self.current_analysis_point
        if not point:
            return
        
        # Синя точка аналізу
        draw.ellipse([point.x - IMAGE.POINT_RADIUS, point.y - IMAGE.POINT_RADIUS, 
                     point.x + IMAGE.POINT_RADIUS, point.y + IMAGE.POINT_RADIUS], 
                    fill=IMAGE.ANALYSIS_POINT_COLOR, outline='white', width=1)
        
        # Лінія до правого краю (як в специфікації)
        image_width = self.original_image.width
        image_height = self.original_image.height
        
        # Кінцева точка лінії: правий край на рівні 12% висоти зображення
        end_x = image_width - 1
        end_y = int(image_height * 0.12)
        
        draw.line([point.x, point.y, end_x, end_y], 
                 fill=IMAGE.LINE_COLOR, width=IMAGE.LINE_WIDTH)
    
    def get_grid_settings(self) -> Dict[str, Any]:
        """
        Отримання поточних налаштувань сітки для збереження
        
        Returns:
            Словник з налаштуваннями сітки
        """
        return {
            'center_x': self.grid_settings.center_x,
            'center_y': self.grid_settings.center_y,
            'scale_value': self.grid_settings.scale_value,
            'custom_scale_distance': self.grid_settings.custom_scale_distance,
            'scale_edge_x': self.grid_settings.scale_edge_x,
            'scale_edge_y': self.grid_settings.scale_edge_y,
            'has_custom_scale': self.has_custom_scale
        }
    
    def apply_grid_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Застосування збережених налаштувань сітки
        
        Args:
            settings: Словник з налаштуваннями
            
        Returns:
            True якщо застосування успішне
        """
        try:
            if 'center_x' in settings and 'center_y' in settings:
                self.grid_settings.center_x = settings['center_x']
                self.grid_settings.center_y = settings['center_y']
            
            if 'scale_value' in settings:
                self.grid_settings.scale_value = settings['scale_value']
            
            if 'custom_scale_distance' in settings:
                self.grid_settings.custom_scale_distance = settings['custom_scale_distance']
            
            if 'scale_edge_x' in settings and 'scale_edge_y' in settings:
                self.grid_settings.scale_edge_x = settings['scale_edge_x']
                self.grid_settings.scale_edge_y = settings['scale_edge_y']
            
            if 'has_custom_scale' in settings:
                self.has_custom_scale = settings['has_custom_scale']
            
            # Перерахунок точки аналізу
            if self.current_analysis_point:
                self._recalculate_analysis_point()
            
            print("✓ Налаштування сітки застосовано")
            return True
            
        except Exception as e:
            print(f"✗ Помилка застосування налаштувань: {e}")
            return False
    
    def get_image_info(self) -> Dict[str, Any]:
        """
        Отримання інформації про зображення
        
        Returns:
            Словник з інформацією про зображення
        """
        if not self.is_loaded:
            return {}
        
        return {
            'path': self.image_path,
            'filename': os.path.basename(self.image_path),
            'width': self.original_image.width,
            'height': self.original_image.height,
            'mode': self.original_image.mode,
            'format': self.original_image.format,
            'aspect_ratio': self.original_image.width / self.original_image.height,
            'is_loaded': self.is_loaded
        }
    
    def save_processed_image(self, file_path: str, include_grid: bool = False) -> bool:
        """
        Збереження обробленого зображення
        
        Args:
            file_path: Шлях для збереження
            include_grid: Включати елементи сітки
            
        Returns:
            True якщо збереження успішне
        """
        try:
            if include_grid:
                image_to_save = self.create_preview_image(show_grid=True, show_analysis=True)
            else:
                image_to_save = self.create_preview_image(show_grid=False, show_analysis=True)
            
            if not image_to_save:
                return False
            
            # Визначення формату за розширенням
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                image_to_save.save(file_path, 'JPEG', quality=IMAGE.JPEG_QUALITY)
            elif file_path.lower().endswith('.png'):
                image_to_save.save(file_path, 'PNG')
            else:
                image_to_save.save(file_path)
            
            print(f"✓ Зображення збережено: {file_path}")
            return True
            
        except Exception as e:
            print(f"✗ Помилка збереження: {e}")
            return False


# Утилітні функції для тестування
def test_image_processor():
    """Тестування функціональності ImageProcessor"""
    print("=== Тестування ImageProcessor ===")
    
    # Створюємо тестове зображення якщо немає реального
    test_image_path = "test_image.jpg"
    if not os.path.exists(test_image_path):
        print("Створення тестового зображення...")
        test_img = Image.new('RGB', (450, 390), color='lightblue')
        draw = ImageDraw.Draw(test_img)
        
        # Малюємо тестову сітку
        center_x, center_y = 225, 195
        for i in range(5):
            radius = 50 * (i + 1)
            draw.ellipse([center_x - radius, center_y - radius, 
                         center_x + radius, center_y + radius], 
                        outline='black', width=1)
        
        test_img.save(test_image_path)
        print(f"✓ Тестове зображення створено: {test_image_path}")
    
    # Тестування процесора
    processor = ImageProcessor(test_image_path)
    
    if processor.is_loaded:
        print("✓ Зображення завантажено успішно")
        
        # Тест переміщення центру
        processor.move_center(10, -5)
        
        # Тест встановлення масштабу
        processor.set_scale_value(200)
        
        # Тест точки аналізу
        analysis_point = processor.set_analysis_point(300, 150)
        if analysis_point:
            print(f"✓ Точка аналізу: {analysis_point}")
        
        # Тест збереження налаштувань
        settings = processor.get_grid_settings()
        print(f"✓ Налаштування отримано: {settings}")
        
        # Тест створення превью
        preview = processor.create_preview_image()
        if preview:
            preview.save("test_preview.jpg")
            print("✓ Превью створено: test_preview.jpg")
        
        print("=== Тест завершено успішно ===")
    else:
        print("✗ Помилка завантаження зображення")


if __name__ == "__main__":
    test_image_processor()