# Додаткові константи для UI в файлі constants.py

# Додати в кінець файлу constants.py:

# Константи для браузера зображень (додати в UIConstants)
THUMBNAIL_SIZE: int = 80  # Розмір мініатюри в пікселях
THUMBNAIL_WIDTH: int = 90  # Ширина контейнера мініатюри  
THUMBNAIL_HEIGHT: int = 120  # Висота контейнера мініатюри

# Константи для опису РЛС (додати в RadarDescription)
DESCRIPTION_WIDTH_RATIO: float = 0.286  # 28.60% ширини зображення
DESCRIPTION_HEIGHT_RATIO: float = 0.195  # 19.54% висоти зображення

import math
import os
from typing import Tuple, Optional, Dict, Any, List
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont, ImageOps

from core.constants import IMAGE, GRID, VALIDATION, RADAR


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


@dataclass
class RadarDescription:
    """Опис РЛС для додавання на зображення"""
    date: str
    callsign: str
    name: str
    number: str
    enabled: bool = False


class ImageProcessor:
    """
    Головний клас для обробки зображень з азимутальними сітками
    
    Функціональність:
    - Завантаження та попередня обробка зображень
    - Управління центром азимутальної сітки
    - Розрахунок азимуту та дальності
    - Калібрування масштабу
    - Збереження налаштувань між зображеннями
    - Створення опису РЛС
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
            scale_value=scale_value or GRID.DEFAULT_SCALE
        )
        
        # Поточна точка аналізу
        self.current_analysis_point: Optional[AnalysisPoint] = None
        
        # Опис РЛС
        self.radar_description: Optional[RadarDescription] = None
        
        # Прапорці стану
        self.is_loaded = False
        self.has_custom_scale = False
        
        # Завантаження зображення
        self._load_image()
        self._initialize_grid_center()
    
    def _load_image(self) -> bool:
        """Завантаження та попередня обробка зображення"""
        try:
            if not os.path.exists(self.image_path):
                print(f"❌ Файл не існує: {self.image_path}")
                return False
            
            # Завантаження зображення
            self.original_image = Image.open(self.image_path)
            
            # Конвертація в RGB якщо потрібно
            if self.original_image.mode == 'RGBA':
                # Створюємо білий фон для RGBA
                rgb_image = Image.new('RGB', self.original_image.size, (255, 255, 255))
                rgb_image.paste(self.original_image, mask=self.original_image.split()[-1])
                self.original_image = rgb_image
            elif self.original_image.mode != 'RGB':
                self.original_image = self.original_image.convert('RGB')
            
            # Створення робочої копії
            self.working_image = self.original_image.copy()
            
            self.is_loaded = True
            print(f"✅ Зображення завантажено: {os.path.basename(self.image_path)}")
            print(f"   Розмір: {self.original_image.width}x{self.original_image.height}")
            
            # Валідація пропорцій
            self._validate_aspect_ratio()
            
            return True
            
        except Exception as e:
            print(f"❌ Помилка завантаження зображення: {e}")
            self.is_loaded = False
            return False
    
    def _validate_aspect_ratio(self) -> None:
        """Перевірка пропорцій зображення (15:13)"""
        if not self.original_image:
            return
        
        width, height = self.original_image.size
        actual_ratio = width / height
        expected_ratio = IMAGE.REQUIRED_ASPECT_RATIO
        tolerance = 0.1
        
        if abs(actual_ratio - expected_ratio) > tolerance:
            print(f"⚠️  Увага: Пропорції зображення {actual_ratio:.2f} відрізняються від рекомендованих {expected_ratio:.2f}")
    
    def _initialize_grid_center(self) -> None:
        """Ініціалізація центру сітки в центрі зображення"""
        if not self.original_image:
            return
        
        self.grid_settings.center_x = self.original_image.width // 2
        self.grid_settings.center_y = self.original_image.height // 2
        
        print(f"📍 Центр сітки встановлено: ({self.grid_settings.center_x}, {self.grid_settings.center_y})")
    
    # ===== УПРАВЛІННЯ ЦЕНТРОМ СІТКИ =====
    
    def move_center(self, dx: int, dy: int) -> bool:
        """
        Переміщення центру сітки
        
        Args:
            dx: Зміщення по X
            dy: Зміщення по Y
            
        Returns:
            True якщо переміщення успішне
        """
        if not self.original_image:
            return False
        
        new_x = self.grid_settings.center_x + dx
        new_y = self.grid_settings.center_y + dy
        
        # Перевірка меж
        if (0 <= new_x < self.original_image.width and 
            0 <= new_y < self.original_image.height):
            
            self.grid_settings.center_x = new_x
            self.grid_settings.center_y = new_y
            
            # Перерахунок точки аналізу якщо існує
            self._recalculate_analysis_point()
            
            print(f"📍 Центр переміщено на: ({new_x}, {new_y})")
            return True
        
        return False
    
    def set_center(self, x: int, y: int) -> bool:
        """
        Встановлення центру сітки в конкретну точку
        
        Args:
            x: Координата X
            y: Координата Y
            
        Returns:
            True якщо встановлення успішне
        """
        if not self.original_image:
            return False
        
        if (0 <= x < self.original_image.width and 
            0 <= y < self.original_image.height):
            
            self.grid_settings.center_x = x
            self.grid_settings.center_y = y
            
            # Перерахунок точки аналізу якщо існує
            self._recalculate_analysis_point()
            
            print(f"📍 Центр встановлено: ({x}, {y})")
            return True
        
        return False
    
    # ===== УПРАВЛІННЯ МАСШТАБОМ =====
    
    def set_scale_edge(self, x: int, y: int) -> bool:
        """
        Встановлення краю масштабу для калібрування
        
        Args:
            x: Координата X краю
            y: Координата Y краю
            
        Returns:
            True якщо встановлення успішне
        """
        if not self.original_image:
            return False
        
        # Розрахунок відстані від центру до краю в пікселях
        dx = x - self.grid_settings.center_x
        dy = y - self.grid_settings.center_y
        distance_pixels = math.sqrt(dx * dx + dy * dy)
        
        if distance_pixels > 0:
            self.grid_settings.scale_edge_x = x
            self.grid_settings.scale_edge_y = y
            self.grid_settings.custom_scale_distance = distance_pixels
            self.has_custom_scale = True
            
            # Перерахунок точки аналізу якщо існує
            self._recalculate_analysis_point()
            
            print(f"📏 Край масштабу встановлено: ({x}, {y}), відстань: {distance_pixels:.1f} пікс")
            return True
        
        return False
    
    def set_scale_value(self, scale_value: int) -> bool:
        """
        Встановлення значення масштабу
        
        Args:
            scale_value: Значення масштабу в км
            
        Returns:
            True якщо встановлення успішне
        """
        if scale_value in GRID.AVAILABLE_SCALES:
            self.grid_settings.scale_value = scale_value
            
            # Перерахунок точки аналізу якщо існує
            self._recalculate_analysis_point()
            
            print(f"📏 Масштаб встановлено: {scale_value} км")
            return True
        
        return False
    
    # ===== АНАЛІЗ ТОЧОК =====
    
    def set_analysis_point(self, x: int, y: int) -> Optional[AnalysisPoint]:
        """
        Встановлення точки аналізу з розрахунком азимуту та дальності
        
        Args:
            x: Координата X точки
            y: Координата Y точки
            
        Returns:
            AnalysisPoint з розрахованими значеннями або None
        """
        if not self.original_image:
            return None
        
        # Розрахунок азимуту та дальності
        azimuth, range_km = self._calculate_azimuth_range(x, y)
        
        # Створення точки аналізу
        self.current_analysis_point = AnalysisPoint(
            x=x,
            y=y,
            azimuth=azimuth,
            range_km=range_km
        )
        
        print(f"🎯 Точка аналізу: ({x}, {y}) → Азимут: {azimuth:.0f}°, Дальність: {range_km:.0f} км")
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
    
    # ===== ВІЗУАЛІЗАЦІЯ =====
    
    def create_preview_image(self, show_grid: bool = True, show_analysis: bool = True, 
                           show_radar_desc: bool = False) -> Optional[Image.Image]:
        """
        Створення зображення для попереднього перегляду з накладеними елементами
        
        Args:
            show_grid: Показувати азимутальну сітку
            show_analysis: Показувати точку аналізу
            show_radar_desc: Показувати опис РЛС
            
        Returns:
            Зображення для перегляду або None
        """
        if not self.working_image:
            return None
        
        # Створюємо копію для роботи
        preview = self.working_image.copy()
        draw = ImageDraw.Draw(preview)
        
        # Малювання азимутальної сітки
        if show_grid:
            self._draw_azimuth_grid(draw, preview.size)
        
        # Малювання точки аналізу
        if show_analysis and self.current_analysis_point:
            self._draw_analysis_point(draw)
        
        # Додавання опису РЛС
        if show_radar_desc and self.radar_description and self.radar_description.enabled:
            preview = self._add_radar_description(preview)
        
        return preview
    
    def _draw_azimuth_grid(self, draw: ImageDraw.Draw, image_size: Tuple[int, int]) -> None:
        """Малювання азимутальної сітки"""
        center_x = self.grid_settings.center_x
        center_y = self.grid_settings.center_y
        
        # Колір та товщина ліній
        line_color = (0, 255, 0, 128)  # Зелений з прозорістю
        line_width = 1
        
        # Малювання азимутальних ліній (через кожні 30°)
        max_radius = max(image_size[0], image_size[1])
        
        for angle in range(0, 360, 30):
            angle_rad = math.radians(angle)
            end_x = center_x + max_radius * math.sin(angle_rad)
            end_y = center_y - max_radius * math.cos(angle_rad)
            
            draw.line([center_x, center_y, end_x, end_y], 
                     fill=line_color, width=line_width)
        
        # Малювання концентричних кіл
        if self.has_custom_scale and self.grid_settings.custom_scale_distance:
            scale_distance = self.grid_settings.custom_scale_distance
            scale_value = self.grid_settings.scale_value
            
            # Кола через кожні 25 км до максимальної дальності
            for range_km in range(25, scale_value + 25, 25):
                radius = (range_km / scale_value) * scale_distance
                if radius < max_radius:
                    bbox = [center_x - radius, center_y - radius,
                           center_x + radius, center_y + radius]
                    draw.ellipse(bbox, outline=line_color, width=line_width)
        
        # Малювання центру
        center_size = 3
        draw.ellipse([center_x - center_size, center_y - center_size,
                     center_x + center_size, center_y + center_size],
                    fill=(255, 0, 0), outline=(255, 255, 255), width=1)
        
        # Малювання краю масштабу якщо встановлено
        if (self.has_custom_scale and 
            self.grid_settings.scale_edge_x is not None and 
            self.grid_settings.scale_edge_y is not None):
            
            edge_x = self.grid_settings.scale_edge_x
            edge_y = self.grid_settings.scale_edge_y
            
            # Лінія до краю масштабу
            draw.line([center_x, center_y, edge_x, edge_y], 
                     fill=(255, 255, 0), width=2)
            
            # Точка краю масштабу
            edge_size = 4
            draw.ellipse([edge_x - edge_size, edge_y - edge_size,
                         edge_x + edge_size, edge_y + edge_size],
                        fill=(255, 255, 0), outline=(0, 0, 0), width=1)
    
    def _draw_analysis_point(self, draw: ImageDraw.Draw) -> None:
        """Малювання точки аналізу"""
        if not self.current_analysis_point:
            return
        
        x = self.current_analysis_point.x
        y = self.current_analysis_point.y
        
        # Точка аналізу
        point_size = 5
        draw.ellipse([x - point_size, y - point_size,
                     x + point_size, y + point_size],
                    fill=(0, 0, 255), outline=(255, 255, 255), width=2)
        
        # Лінія від центру до точки
        draw.line([self.grid_settings.center_x, self.grid_settings.center_y, x, y], 
                 fill=(0, 0, 255), width=2)
    
    def _add_radar_description(self, image: Image.Image) -> Image.Image:
        """Додавання опису РЛС в лівий нижній кут"""
        if not self.radar_description:
            return image
        
        # Створюємо копію для роботи
        result = image.copy()
        draw = ImageDraw.Draw(result)
        
        # Розміри таблички
        table_width = int(image.width * RADAR.DESCRIPTION_WIDTH_RATIO)
        table_height = int(image.height * RADAR.DESCRIPTION_HEIGHT_RATIO)
        
        # Позиція в лівому нижньому кутку
        margin = 10
        table_x = margin
        table_y = image.height - table_height - margin
        
        # Фон таблички
        draw.rectangle([table_x, table_y, table_x + table_width, table_y + table_height],
                      fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        
        # Текст опису (спрощена версія)
        try:
            font_size = max(8, table_height // 8)
            font = ImageFont.load_default()
        except:
            font = None
        
        # Додавання тексту
        text_y = table_y + 5
        line_height = table_height // 6
        
        lines = [
            f"Дата: {self.radar_description.date}",
            f"Позивний: {self.radar_description.callsign}",
            f"Назва: {self.radar_description.name}",
            f"Номер: {self.radar_description.number}"
        ]
        
        for line in lines:
            if text_y + line_height < table_y + table_height:
                draw.text((table_x + 5, text_y), line, fill=(0, 0, 0), font=font)
                text_y += line_height
        
        return result
    
    # ===== ОПИС РЛС =====
    
    def set_radar_description(self, date: str, callsign: str, name: str, number: str, enabled: bool = True) -> None:
        """Встановлення опису РЛС"""
        self.radar_description = RadarDescription(
            date=date,
            callsign=callsign,
            name=name,
            number=number,
            enabled=enabled
        )
        
        print(f"📡 Опис РЛС встановлено: {callsign} - {name}")
    
    def toggle_radar_description(self, enabled: bool) -> None:
        """Включення/виключення опису РЛС"""
        if self.radar_description:
            self.radar_description.enabled = enabled
            print(f"📡 Опис РЛС {'увімкнено' if enabled else 'вимкнено'}")
    
    # ===== ЗБЕРЕЖЕННЯ =====
    
    def save_processed_image(self, output_path: str, include_grid: bool = True, 
                           include_analysis: bool = True, include_radar_desc: bool = None) -> bool:
        """
        Збереження обробленого зображення
        
        Args:
            output_path: Шлях для збереження
            include_grid: Включати азимутальну сітку
            include_analysis: Включати точку аналізу
            include_radar_desc: Включати опис РЛС (за замовчуванням авто)
            
        Returns:
            True якщо збереження успішне
        """
        try:
            # Автоматичне визначення включення опису РЛС
            if include_radar_desc is None:
                include_radar_desc = (self.radar_description and 
                                    self.radar_description.enabled)
            
            # Створення фінального зображення
            final_image = self.create_preview_image(
                show_grid=include_grid,
                show_analysis=include_analysis,
                show_radar_desc=include_radar_desc
            )
            
            if final_image:
                # Збереження з оптимальною якістю
                final_image.save(output_path, format='JPEG', quality=95, optimize=True)
                print(f"💾 Зображення збережено: {output_path}")
                return True
            
        except Exception as e:
            print(f"❌ Помилка збереження: {e}")
        
        return False
    
    # ===== ЕКСПОРТ ДАНИХ =====
    
    def get_export_data(self) -> Dict[str, Any]:
        """
        Отримання даних для експорту в альбом
        
        Returns:
            Словник з даними зображення
        """
        data = {
            'image_path': self.image_path,
            'image_filename': os.path.basename(self.image_path),
            'image_size': (self.original_image.width, self.original_image.height) if self.original_image else (0, 0),
            'grid_settings': {
                'center_x': self.grid_settings.center_x,
                'center_y': self.grid_settings.center_y,
                'scale_value': self.grid_settings.scale_value,
                'has_custom_scale': self.has_custom_scale,
                'custom_scale_distance': self.grid_settings.custom_scale_distance,
                'scale_edge_x': self.grid_settings.scale_edge_x,
                'scale_edge_y': self.grid_settings.scale_edge_y
            }
        }
        
        # Додавання даних точки аналізу
        if self.current_analysis_point:
            data['analysis_point'] = {
                'x': self.current_analysis_point.x,
                'y': self.current_analysis_point.y,
                'azimuth': self.current_analysis_point.azimuth,
                'range_km': self.current_analysis_point.range_km
            }
        
        # Додавання опису РЛС
        if self.radar_description:
            data['radar_description'] = {
                'date': self.radar_description.date,
                'callsign': self.radar_description.callsign,
                'name': self.radar_description.name,
                'number': self.radar_description.number,
                'enabled': self.radar_description.enabled
            }
        
        return data
    
    # ===== УТИЛІТАРНІ МЕТОДИ =====
    
    def get_image_info(self) -> Dict[str, Any]:
        """Отримання інформації про зображення"""
        if not self.original_image:
            return {}
        
        return {
            'path': self.image_path,
            'filename': os.path.basename(self.image_path),
            'size': (self.original_image.width, self.original_image.height),
            'mode': self.original_image.mode,
            'format': self.original_image.format,
            'file_size': os.path.getsize(self.image_path) if os.path.exists(self.image_path) else 0
        }
    
    def reset_analysis(self) -> None:
        """Скидання точки аналізу"""
        self.current_analysis_point = None
        print("🔄 Точка аналізу очищена")
    
    def reset_grid_settings(self) -> None:
        """Скидання налаштувань сітки до початкових"""
        self._initialize_grid_center()
        self.grid_settings.scale_value = GRID.DEFAULT_SCALE
        self.grid_settings.custom_scale_distance = None
        self.grid_settings.scale_edge_x = None
        self.grid_settings.scale_edge_y = None
        self.has_custom_scale = False
        
        # Перерахунок точки аналізу
        self._recalculate_analysis_point()
        
        print("🔄 Налаштування сітки скинуто")


# ===== ТЕСТУВАННЯ МОДУЛЯ =====

if __name__ == "__main__":
    print("=== Тестування ImageProcessor ===")
    
    # Тест базового функціоналу
    # processor = ImageProcessor("test_image.jpg")
    # print(f"Завантажено: {processor.is_loaded}")
    # print(f"Інфо: {processor.get_image_info()}")
    
    print("Модуль ImageProcessor готовий до використання")