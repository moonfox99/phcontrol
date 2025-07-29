#!/usr/bin/env python3
"""
Модуль накладання опису РЛС на зображення
З точними пропорціями 28.60% × 19.54% та правильним позиціонуванням
"""

from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import os


class RadarDescriptionOverlay:
    """
    Клас для накладання опису РЛС на зображення
    
    Точні пропорції відповідно до legacy версії:
    - Ширина: 28.60% від ширини зображення
    - Висота: 19.54% від висоти зображення
    - Позиція: лівий нижній кут
    - Внутрішні відступи: 5.83% × 5.12%
    """
    
    # ⚠️ КРИТИЧНО ВАЖЛИВІ КОНСТАНТИ з legacy версії
    RADAR_BOX_WIDTH_PERCENT = 28.60   # 4.29см / 15см * 100% = 28.60%
    RADAR_BOX_HEIGHT_PERCENT = 19.54  # 2.54см / 13см * 100% = 19.54%
    
    # Внутрішні відступи (пропорційні)
    PADDING_HORIZONTAL_PERCENT = 5.83  # 0,25см / 4,29см * 100% = 5.83%
    PADDING_VERTICAL_PERCENT = 5.12    # 0,13см / 2,54см * 100% = 5.12%
    
    # Розмір шрифту (16.7% від висоти прямокутника = 12pt proportion)
    FONT_SIZE_PERCENT = 16.7
    
    # Відступ від краю зображення
    MARGIN_FROM_EDGE_PERCENT = 1.0  # 1% від ширини зображення
    
    def __init__(self):
        self.font_cache = {}
        self._load_fonts()
    
    def _load_fonts(self):
        """Завантаження шрифтів для різних розмірів"""
        try:
            # Спроба завантажити Arial Italic
            self.font_family = "arial.ttf"
            
            # Перевірка наявності шрифту в системі
            if os.name == 'nt':  # Windows
                font_paths = [
                    "C:/Windows/Fonts/ariali.ttf",  # Arial Italic
                    "C:/Windows/Fonts/arial.ttf",   # Arial Regular
                ]
            else:  # Linux/macOS
                font_paths = [
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
                    "/System/Library/Fonts/Arial.ttf",
                    "/usr/share/fonts/TTF/arial.ttf",
                ]
            
            self.available_font_path = None
            for path in font_paths:
                if os.path.exists(path):
                    self.available_font_path = path
                    break
                    
            print(f"Шрифт для опису РЛС: {self.available_font_path or 'системний за замовчуванням'}")
            
        except Exception as e:
            print(f"Помилка завантаження шрифтів: {e}")
            self.available_font_path = None
    
    def _get_font(self, size: int) -> ImageFont:
        """
        Отримання шрифту потрібного розміру з кешуванням
        
        Args:
            size: Розмір шрифту в пікселях
            
        Returns:
            Об'єкт шрифту PIL
        """
        if size not in self.font_cache:
            try:
                if self.available_font_path:
                    font = ImageFont.truetype(self.available_font_path, size)
                else:
                    font = ImageFont.load_default()
                self.font_cache[size] = font
            except Exception as e:
                print(f"Помилка створення шрифту розміру {size}: {e}")
                self.font_cache[size] = ImageFont.load_default()
        
        return self.font_cache[size]
    
    def add_radar_description(self, image: Image.Image, radar_data: Dict[str, Any]) -> Image.Image:
        """
        Додавання опису РЛС на зображення
        
        Args:
            image: Вихідне зображення PIL
            radar_data: Словник з даними опису РЛС
                       Очікувані ключі: 'date', 'time', 'operator', 'station', 'mode' тощо
            
        Returns:
            Зображення з накладеним описом РЛС
        """
        if not radar_data or not radar_data.get('enabled', False):
            return image
        
        # Створюємо копію зображення для модифікації
        result_image = image.copy()
        draw = ImageDraw.Draw(result_image)
        
        image_width, image_height = result_image.size
        
        # Розрахунок розмірів таблички відповідно до критичних пропорцій
        rect_width = int((image_width * self.RADAR_BOX_WIDTH_PERCENT) / 100)
        rect_height = int((image_height * self.RADAR_BOX_HEIGHT_PERCENT) / 100)
        
        # Розрахунок внутрішніх відступів
        padding_horizontal = int((rect_width * self.PADDING_HORIZONTAL_PERCENT) / 100)
        padding_vertical = int((rect_height * self.PADDING_VERTICAL_PERCENT) / 100)
        
        # Позиція таблички - лівий нижній кут з відступом від краю
        margin_from_edge = int(image_width * self.MARGIN_FROM_EDGE_PERCENT / 100)
        rect_x = margin_from_edge
        rect_y = image_height - rect_height - margin_from_edge
        
        # Розрахунок розміру шрифту пропорційно до висоти прямокутника
        font_size = max(8, int((rect_height * self.FONT_SIZE_PERCENT) / 100))
        font = self._get_font(font_size)
        
        print(f"📏 Накладання опису РЛС:")
        print(f"   Зображення: {image_width}×{image_height}px")
        print(f"   Табличка: {rect_width}×{rect_height}px ({self.RADAR_BOX_WIDTH_PERCENT:.1f}% × {self.RADAR_BOX_HEIGHT_PERCENT:.1f}%)")
        print(f"   Позиція: ({rect_x}, {rect_y})")
        print(f"   Відступи: {padding_horizontal}×{padding_vertical}px")
        print(f"   Шрифт: {font_size}px")
        
        # Малювання прямокутника з прозорим фоном
        border_width = max(2, int(rect_width * 0.008))  # Пропорційна товщина рамки
        
        draw.rectangle(
            [rect_x, rect_y, rect_x + rect_width, rect_y + rect_height],
            fill=None,  # Прозорий фон
            outline='black',
            width=border_width
        )
        
        # Додавання тексту опису
        self._add_radar_text(
            draw, radar_data, font,
            rect_x + padding_horizontal,
            rect_y + padding_vertical,
            rect_width - 2 * padding_horizontal,
            rect_height - 2 * padding_vertical
        )
        
        return result_image
    
    def _add_radar_text(self, draw: ImageDraw.Draw, radar_data: Dict[str, Any], 
                       font: ImageFont, text_x: int, text_y: int, 
                       text_width: int, text_height: int):
        """
        Додавання тексту опису РЛС всередину прямокутника
        
        Args:
            draw: Об'єкт ImageDraw для малювання
            radar_data: Дані опису РЛС
            font: Шрифт для тексту
            text_x, text_y: Координати початку тексту
            text_width, text_height: Розміри області для тексту
        """
        try:
            # Формування рядків тексту відповідно до legacy версії
            lines = self._format_radar_lines(radar_data)
            
            if not lines:
                return
            
            # Розрахунок висоти рядка (одинарний інтервал як в Word)
            line_height = int(font.size * 1.2)  # 120% від розміру шрифту
            
            # Перевірка чи поміщається весь текст
            total_text_height = len(lines) * line_height
            if total_text_height > text_height:
                # Якщо не поміщається, зменшуємо розмір шрифту
                scale_factor = text_height / total_text_height
                new_font_size = max(6, int(font.size * scale_factor * 0.9))
                font = self._get_font(new_font_size)
                line_height = int(font.size * 1.2)
            
            # Малювання кожного рядка
            current_y = text_y
            for line in lines:
                if current_y + line_height <= text_y + text_height:
                    draw.text(
                        (text_x, current_y),
                        line,
                        fill='black',
                        font=font
                    )
                    current_y += line_height
                else:
                    # Якщо рядок не поміщається, припиняємо
                    break
            
            print(f"   Додано {len(lines)} рядків тексту, висота рядка: {line_height}px")
            
        except Exception as e:
            print(f"Помилка додавання тексту опису РЛС: {e}")
    
    def _format_radar_lines(self, radar_data: Dict[str, Any]) -> list:
        """
        Форматування рядків тексту опису РЛС відповідно до стандарту
        
        Args:
            radar_data: Дані опису РЛС
            
        Returns:
            Список рядків для відображення
        """
        lines = []
        
        try:
            # Дата (обов'язкове поле)
            if 'date' in radar_data and radar_data['date']:
                lines.append(f"Дата: {radar_data['date']}")
            
            # Час
            if 'time' in radar_data and radar_data['time']:
                lines.append(f"Час: {radar_data['time']}")
            
            # Оператор
            if 'operator' in radar_data and radar_data['operator']:
                lines.append(f"Оператор: {radar_data['operator']}")
            
            # Станція/Пост
            if 'station' in radar_data and radar_data['station']:
                lines.append(f"Станція: {radar_data['station']}")
            
            # Режим роботи
            if 'mode' in radar_data and radar_data['mode']:
                lines.append(f"Режим: {radar_data['mode']}")
            
            # Додаткові поля залежно від потреб
            if 'frequency' in radar_data and radar_data['frequency']:
                lines.append(f"Частота: {radar_data['frequency']}")
            
            if 'weather' in radar_data and radar_data['weather']:
                lines.append(f"Погода: {radar_data['weather']}")
            
            # Обмеження кількості рядків для поміщення в табличку
            if len(lines) > 8:  # Максимум 8 рядків
                lines = lines[:8]
                lines[-1] = lines[-1][:50] + "..." if len(lines[-1]) > 50 else lines[-1]
            
        except Exception as e:
            print(f"Помилка форматування рядків опису РЛС: {e}")
            lines = ["Помилка форматування"]
        
        return lines
    
    def calculate_proportions(self, image_width: int, image_height: int) -> Dict[str, int]:
        """
        Розрахунок точних розмірів і позицій для опису РЛС
        
        Args:
            image_width: Ширина зображення в пікселях
            image_height: Висота зображення в пікселях
            
        Returns:
            Словник з розрахованими розмірами
        """
        rect_width = int((image_width * self.RADAR_BOX_WIDTH_PERCENT) / 100)
        rect_height = int((image_height * self.RADAR_BOX_HEIGHT_PERCENT) / 100)
        
        padding_horizontal = int((rect_width * self.PADDING_HORIZONTAL_PERCENT) / 100)
        padding_vertical = int((rect_height * self.PADDING_VERTICAL_PERCENT) / 100)
        
        margin_from_edge = int(image_width * self.MARGIN_FROM_EDGE_PERCENT / 100)
        rect_x = margin_from_edge
        rect_y = image_height - rect_height - margin_from_edge
        
        font_size = max(8, int((rect_height * self.FONT_SIZE_PERCENT) / 100))
        
        return {
            'rect_width': rect_width,
            'rect_height': rect_height,
            'rect_x': rect_x,
            'rect_y': rect_y,
            'padding_horizontal': padding_horizontal,
            'padding_vertical': padding_vertical,
            'font_size': font_size,
            'text_area_width': rect_width - 2 * padding_horizontal,
            'text_area_height': rect_height - 2 * padding_vertical
        }


# ===============================
# ІНТЕГРАЦІЯ З IMAGE PROCESSOR
# ===============================

class ImageProcessorRadarExtension:
    """
    Розширення ImageProcessor для підтримки опису РЛС
    Ці методи потрібно додати до core/image_processor.py
    """
    
    def __init__(self):
        self.radar_overlay = RadarDescriptionOverlay()
    
    def create_processed_image_with_radar(self, radar_data: Optional[Dict[str, Any]] = None) -> Image.Image:
        """
        ДОПОВНЕНИЙ метод створення обробленого зображення з описом РЛС
        Додати до ImageProcessor
        
        Args:
            radar_data: Дані опису РЛС (опціонально)
            
        Returns:
            PIL Image з нанесеними елементами та описом РЛС
        """
        if not self.working_image:
            raise ValueError("Зображення не завантажено")
        
        # Створюємо базове оброблене зображення
        processed_image = self.create_processed_image()
        
        # Додаємо опис РЛС якщо потрібно
        if radar_data and radar_data.get('enabled', False):
            processed_image = self.radar_overlay.add_radar_description(processed_image, radar_data)
        
        return processed_image
    
    def preview_radar_overlay(self, radar_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Попередній перегляд накладання опису РЛС без створення зображення
        Додати до ImageProcessor
        
        Args:
            radar_data: Дані опису РЛС
            
        Returns:
            Словник з інформацією про накладання
        """
        if not self.working_image:
            return {}
        
        image_width, image_height = self.working_image.size
        proportions = self.radar_overlay.calculate_proportions(image_width, image_height)
        
        # Додаємо інформацію про текст
        lines = self.radar_overlay._format_radar_lines(radar_data)
        proportions['text_lines'] = lines
        proportions['lines_count'] = len(lines)
        
        return proportions


# ===============================
# ІНТЕГРАЦІЯ З DATA PANEL
# ===============================

class DataPanelRadarExtension:
    """
    Розширення DataPanel для управління описом РЛС
    Ці методи потрібно додати до ui/panels/data_panel.py
    """
    
    def _create_radar_description_section(self, layout):
        """
        ДОПОВНЕНИЙ метод створення секції опису РЛС
        Додати до DataPanel._create_ui()
        """
        radar_group = QGroupBox()
        radar_layout = QVBoxLayout(radar_group)
        
        # Заголовок та перемикач
        header_layout = QHBoxLayout()
        
        self.radar_title_label = QLabel("Опис РЛС")
        self.radar_title_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(self.radar_title_label)
        
        header_layout.addStretch()
        
        self.radar_enabled_checkbox = QCheckBox("Включити")
        self.radar_enabled_checkbox.stateChanged.connect(self._on_radar_enabled_changed)
        header_layout.addWidget(self.radar_enabled_checkbox)
        
        radar_layout.addLayout(header_layout)
        
        # Поля для введення даних
        self.radar_fields = {}
        
        # Дата
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Дата:"))
        self.radar_fields['date'] = QDateEdit()
        self.radar_fields['date'].setDate(QDate.currentDate())
        self.radar_fields['date'].setDisplayFormat("dd.MM.yyyy")
        date_layout.addWidget(self.radar_fields['date'])
        radar_layout.addLayout(date_layout)
        
        # Час
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Час:"))
        self.radar_fields['time'] = QLineEdit()
        self.radar_fields['time'].setPlaceholderText("14:30")
        time_layout.addWidget(self.radar_fields['time'])
        radar_layout.addLayout(time_layout)
        
        # Оператор
        operator_layout = QHBoxLayout()
        operator_layout.addWidget(QLabel("Оператор:"))
        self.radar_fields['operator'] = QLineEdit()
        self.radar_fields['operator'].setPlaceholderText("І. Петренко")
        operator_layout.addWidget(self.radar_fields['operator'])
        radar_layout.addLayout(operator_layout)
        
        # Станція
        station_layout = QHBoxLayout()
        station_layout.addWidget(QLabel("Станція:"))
        self.radar_fields['station'] = QLineEdit()
        self.radar_fields['station'].setPlaceholderText("Пост №1")
        station_layout.addWidget(self.radar_fields['station'])
        radar_layout.addLayout(station_layout)
        
        # Режим
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Режим:"))
        self.radar_fields['mode'] = QComboBox()
        self.radar_fields['mode'].addItems([
            "Огляд", "Супроводження", "Пошук", 
            "Калібрування", "Тестування"
        ])
        mode_layout.addWidget(self.radar_fields['mode'])
        radar_layout.addLayout(mode_layout)
        
        # Кнопка попереднього перегляду
        self.radar_preview_btn = QPushButton("Попередній перегляд")
        self.radar_preview_btn.clicked.connect(self._on_radar_preview)
        self.radar_preview_btn.setEnabled(False)
        radar_layout.addWidget(self.radar_preview_btn)
        
        # Спочатку всі поля неактивні
        self._set_radar_fields_enabled(False)
        
        layout.addWidget(radar_group)
    
    def _on_radar_enabled_changed(self, state):
        """Обробка зміни стану включення опису РЛС"""
        enabled = state == Qt.Checked
        self._set_radar_fields_enabled(enabled)
        self.radar_preview_btn.setEnabled(enabled)
        
        # Сигнал про зміну стану
        if hasattr(self, 'radar_enabled_changed'):
            self.radar_enabled_changed.emit(enabled)
    
    def _set_radar_fields_enabled(self, enabled: bool):
        """Увімкнення/вимкнення полів опису РЛС"""
        for field in self.radar_fields.values():
            field.setEnabled(enabled)
    
    def _on_radar_preview(self):
        """Попередній перегляд опису РЛС"""
        radar_data = self.get_radar_description()
        
        if hasattr(self, 'radar_preview_requested'):
            self.radar_preview_requested.emit(radar_data)
    
    def get_radar_description(self) -> Dict[str, Any]:
        """
        ДОПОВНЕНИЙ метод отримання опису РЛС
        """
        if not self.radar_enabled_checkbox.isChecked():
            return {'enabled': False}
        
        radar_data = {'enabled': True}
        
        # Дата
        if 'date' in self.radar_fields:
            radar_data['date'] = self.radar_fields['date'].date().toString('dd.MM.yyyy')
        
        # Інші поля
        for field_name, field_widget in self.radar_fields.items():
            if field_name == 'date':
                continue
            
            if hasattr(field_widget, 'text'):
                value = field_widget.text().strip()
                if value:
                    radar_data[field_name] = value
            elif hasattr(field_widget, 'currentText'):
                radar_data[field_name] = field_widget.currentText()
        
        return radar_data


# ===============================
# ТЕСТУВАННЯ
# ===============================

if __name__ == "__main__":
    # Тестування модуля накладання опису РЛС
    import sys
    from datetime import datetime
    
    def test_radar_overlay():
        """Тестування накладання опису РЛС"""
        print("=== ТЕСТУВАННЯ НАКЛАДАННЯ ОПИСУ РЛС ===")
        
        # Створення тестового зображення
        test_image = Image.new('RGB', (1200, 900), (240, 240, 240))
        draw = ImageDraw.Draw(test_image)
        
        # Малюємо сітку для наочності
        for i in range(0, 1200, 100):
            draw.line([(i, 0), (i, 900)], fill=(200, 200, 200))
        for i in range(0, 900, 100):
            draw.line([(0, i), (1200, i)], fill=(200, 200, 200))
        
        # Створення тестових даних опису РЛС
        radar_data = {
            'enabled': True,
            'date': datetime.now().strftime('%d.%m.%Y'),
            'time': datetime.now().strftime('%H:%M'),
            'operator': 'І. Петренко',
            'station': 'Пост №1',
            'mode': 'Огляд',
            'frequency': '9.5 ГГц',
            'weather': 'Ясно'
        }
        
        # Створення об'єкта накладання
        overlay = RadarDescriptionOverlay()
        
        # Розрахунок пропорцій
        proportions = overlay.calculate_proportions(1200, 900)
        print("\n📐 РОЗРАХОВАНІ ПРОПОРЦІЇ:")
        for key, value in proportions.items():
            print(f"   {key}: {value}")
        
        # Додавання опису РЛС на зображення
        result_image = overlay.add_radar_description(test_image, radar_data)
        
        # Збереження результату
        output_path = "test_radar_overlay.png"
        result_image.save(output_path)
        print(f"\n✅ Тестове зображення збережено: {output_path}")
        
        # Тестування з різними розмірами зображень
        print("\n📏 ТЕСТУВАННЯ РІЗНИХ РОЗМІРІВ:")
        test_sizes = [(800, 600), (1600, 1200), (2000, 1500)]
        
        for width, height in test_sizes:
            props = overlay.calculate_proportions(width, height)
            print(f"   {width}×{height}px → табличка: {props['rect_width']}×{props['rect_height']}px")
    
    # Запуск тестування
    test_radar_overlay()
    
    print("\n" + "="*60)
    print("📋 МОДУЛЬ НАКЛАДАННЯ ОПИСУ РЛС ГОТОВИЙ!")
    print("="*60)
    print("\n🎯 КЛЮЧОВІ ОСОБЛИВОСТІ:")
    print("1. ✅ Точні пропорції: 28.60% × 19.54%")
    print("2. ✅ Правильне позиціонування: лівий нижній кут")
    print("3. ✅ Пропорційні внутрішні відступи: 5.83% × 5.12%")
    print("4. ✅ Автоматичне масштабування шрифту")
    print("5. ✅ Підтримка Arial Italic або системного шрифту")
    print("6. ✅ Прозорий фон з чорною рамкою")
    print("7. ✅ Кешування шрифтів для продуктивності")
    print("8. ✅ Гнучке форматування тексту")
    
    print("\n🔗 ІНТЕГРАЦІЯ:")
    print("- Додати RadarDescriptionOverlay в ImageProcessor")
    print("- Розширити DataPanel секцією опису РЛС")
    print("- Підключити до створення оброблених зображень")
    
    print("\n⚙️ ВИКОРИСТАННЯ:")
    print("```python")
    print("overlay = RadarDescriptionOverlay()")
    print("radar_data = {'enabled': True, 'date': '25.07.2025', ...}")
    print("result_image = overlay.add_radar_description(image, radar_data)")
    print("```")