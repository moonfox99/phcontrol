#!/usr/bin/env python3
"""
Центральна панель для відображення зображення з азимутальною сіткою
Інтегрує ClickableLabel, ZoomWidget та всі засоби взаємодії з зображенням
"""

import os
from typing import Optional, Tuple, Dict, Any
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QSizePolicy, QToolTip)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt5.QtGui import QFont, QCursor

from ui.widgets.clickable_label import ClickableLabel
from ui.widgets.zoom_widget import ZoomWidget
from core.image_processor import ImageProcessor, AnalysisPoint, GridSettings
from core.constants import UI, GRID
from translations.translator import get_translator, TranslationKeys
try:
    from PIL.ImageQt import ImageQt
    IMAGEQT_AVAILABLE = True
except ImportError:
    try:
        # Альтернативний імпорт для Python 3.13
        import PIL.ImageQt as ImageQt_module
        ImageQt = ImageQt_module.ImageQt
        IMAGEQT_AVAILABLE = True
    except ImportError:
        IMAGEQT_AVAILABLE = False
        ImageQt = None
        print("⚠️ PIL.ImageQt недоступний - панель зображень обмежена")

class ImagePanel(QWidget):
    """
    Центральна панель для відображення та взаємодії з зображенням
    
    Функціональність:
    - Відображення зображення з азимутальною сіткою
    - Інтеграція ClickableLabel для взаємодії
    - ZoomWidget для детального перегляду
    - Режими: звичайний, налаштування центру, налаштування масштабу
    - Клавіатурне управління центром сітки
    - Tooltips з координатами та азимутальними даними
    - Статус-бар з інформацією про поточний стан
    """
    
    # Сигнали для взаємодії з головним вікном
    image_clicked = pyqtSignal(int, int)              # Клік на зображенні
    analysis_point_changed = pyqtSignal(object)       # Зміна точки аналізу
    grid_center_changed = pyqtSignal(int, int)        # Зміна центру сітки
    scale_edge_set = pyqtSignal(int, int)             # Встановлення точки масштабу
    mode_changed = pyqtSignal(str)                    # Зміна режиму роботи
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Основні компоненти
        self.image_processor: Optional[ImageProcessor] = None
        self.clickable_label: Optional[ClickableLabel] = None
        self.zoom_widget: Optional[ZoomWidget] = None
        
        # Стан панелі
        self.current_mode = "normal"  # normal, center_setting, scale_setting
        self.mouse_tracking_enabled = True
        self.tooltip_enabled = True
        
        # Система перекладів
        self.translator = get_translator()
        
        # Налаштування панелі
        self.setMinimumSize(UI.MIN_IMAGE_PANEL_WIDTH, UI.MIN_IMAGE_PANEL_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Ініціалізація UI
        self._setup_ui()
        self._setup_connections()
        
        print("ImagePanel ініціалізовано")
    
    def _setup_ui(self):
        """Налаштування інтерфейсу панелі"""
        # Основний layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(4)
        self.setLayout(main_layout)
        
        # Заголовок панелі
        self._create_header(main_layout)
        
        # Основна область зображення
        self._create_image_area(main_layout)
        
        # Статус-бар
        self._create_status_bar(main_layout)
    
    def _create_header(self, parent_layout):
        """Створення заголовка панелі"""
        header_frame = QFrame()
        header_frame.setFixedHeight(30)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(8, 4, 8, 4)
        
        # Заголовок
        self.header_label = QLabel(self.translator.tr(TranslationKeys.OPEN_INSTRUCTION))
        self.header_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #495057;
                border: none;
                background: transparent;
            }
        """)
        header_layout.addWidget(self.header_label)
        
        header_layout.addStretch()
        
        # Індикатор режиму
        self.mode_indicator = QLabel("●")
        self.mode_indicator.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 16px;
                border: none;
                background: transparent;
            }
        """)
        self.mode_indicator.setToolTip("Звичайний режим")
        header_layout.addWidget(self.mode_indicator)
        
        parent_layout.addWidget(header_frame)
    
    def _create_image_area(self, parent_layout):
        """Створення основної області зображення"""
        # Контейнер для зображення
        image_container = QFrame()
        image_container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        
        container_layout = QVBoxLayout(image_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Створення ClickableLabel
        self.clickable_label = ClickableLabel()
        self.clickable_label.setMinimumSize(400, 300)
        container_layout.addWidget(self.clickable_label)
        
        # Створення ZoomWidget (прив'язаний до ClickableLabel)
        self.zoom_widget = ZoomWidget(self.clickable_label)
        
        parent_layout.addWidget(image_container)
    
    def _create_status_bar(self, parent_layout):
        """Створення статус-бару"""
        status_frame = QFrame()
        status_frame.setFixedHeight(25)
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(8, 2, 8, 2)
        
        # Координати курсора
        self.cursor_coords = QLabel("—")
        self.cursor_coords.setStyleSheet("""
            QLabel {
                font-family: 'Courier New', monospace;
                font-size: 10px;
                color: #6c757d;
                border: none;
                background: transparent;
            }
        """)
        status_layout.addWidget(self.cursor_coords)
        
        status_layout.addStretch()
        
        # Інформація про зображення
        self.image_info = QLabel("—")
        self.image_info.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #6c757d;
                border: none;
                background: transparent;
            }
        """)
        status_layout.addWidget(self.image_info)
        
        status_layout.addStretch()
        
        # Інформація про сітку
        self.grid_info = QLabel("—")
        self.grid_info.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #6c757d;
                border: none;
                background: transparent;
            }
        """)
        status_layout.addWidget(self.grid_info)
        
        parent_layout.addWidget(status_frame)
    
    def _setup_connections(self):
        """Налаштування з'єднань сигналів"""
        if not self.clickable_label:
            return
        
        # З'єднання з ClickableLabel
        self.clickable_label.clicked.connect(self._on_image_clicked)
        self.clickable_label.dragged.connect(self._on_image_dragged)
        self.clickable_label.mouse_moved.connect(self._on_mouse_moved)
        self.clickable_label.center_moved.connect(self._on_center_moved)
        self.clickable_label.scale_edge_set.connect(self._on_scale_edge_set)
        
        # Підключення до системи перекладів
        self.translator.language_changed.connect(self._update_translations)
    
    # ===============================
    # УПРАВЛІННЯ ЗОБРАЖЕННЯМ
    # ===============================
    
    def set_image_processor(self, processor: ImageProcessor):
        """
        Встановлення процесора зображення
        
        Args:
            processor: Екземпляр ImageProcessor
        """
        # Відключення старих з'єднань
        if self.image_processor:
            try:
                self.image_processor.image_processed.disconnect()
                self.image_processor.settings_changed.disconnect()
                self.image_processor.analysis_completed.disconnect()
            except TypeError:
                pass  # Сигнали не були підключені
        
        self.image_processor = processor
        
        if processor:
            # Підключення нових сигналів
            processor.image_processed.connect(self._on_image_processed)
            processor.settings_changed.connect(self._on_grid_settings_changed)
            processor.analysis_completed.connect(self._on_analysis_completed)
            
            # Ініціальне завантаження
            current_image = processor.get_current_image()
            if current_image:
                self._display_image(current_image)
                self._update_grid_display(processor.grid_settings)
            
            print(f"ImageProcessor встановлено: {processor.get_image_info()}")
        else:
            self._clear_display()
    
    def _display_image(self, pil_image):
        """
        Відображення PIL зображення
        
        Args:
            pil_image: PIL Image для відображення
        """
        if not pil_image or not self.clickable_label:
            return
        
        # Встановлення зображення в ClickableLabel
        grid_center = None
        if self.image_processor:
            grid_center = (
                self.image_processor.grid_settings.center_x,
                self.image_processor.grid_settings.center_y
            )
        
        self.clickable_label.set_image(pil_image, grid_center)
        
        # Встановлення зображення в ZoomWidget
        if self.zoom_widget:
            self.zoom_widget.set_image(pil_image)
        
        # Оновлення інформації про зображення
        self._update_image_info()
        
        # Оновлення заголовка
        if self.image_processor:
            filename = os.path.basename(self.image_processor.image_path) if self.image_processor.image_path else "Невідомий файл"
            self.header_label.setText(f"📁 {filename}")
        
        print(f"Зображення відображено: {pil_image.width}×{pil_image.height}")
    
    def _clear_display(self):
        """Очищення відображення"""
        if self.clickable_label:
            self.clickable_label.clear_image()
        
        if self.zoom_widget:
            self.zoom_widget.set_image(None)
            self.zoom_widget.hide_zoom()
        
        # Очищення інформації
        self.header_label.setText(self.translator.tr(TranslationKeys.OPEN_INSTRUCTION))
        self.cursor_coords.setText("—")
        self.image_info.setText("—")
        self.grid_info.setText("—")
        
        print("Відображення очищено")
    
    # ===============================
    # ОБРОБКА ПОДІЙ ЗОБРАЖЕННЯ
    # ===============================
    
    def _on_image_clicked(self, x: int, y: int):
        """Обробка кліку на зображенні"""
        if not self.image_processor:
            return
        
        print(f"🖱️ Клік на зображенні: ({x}, {y})")
        
        # Оновлення координат курсора
        self.cursor_coords.setText(f"({x}, {y})")
        
        # Передача сигналу для обробки
        self.image_clicked.emit(x, y)
        
        # Якщо в режимі встановлення центру
        if self.current_mode == "center_setting":
            self._on_center_moved(x, y)
            self.set_mode("normal")
        
        # Якщо в режимі встановлення масштабу
        elif self.current_mode == "scale_setting":
            self._on_scale_edge_set(x, y)
            self.set_mode("normal")
        
        # Звичайний режим - встановлення точки аналізу
        else:
            if self.image_processor:
                # Розрахунок азимута та дальності
                azimuth, range_km = self.image_processor.pixel_to_azimuth_range(x, y)
                
                # Створення точки аналізу
                analysis_point = AnalysisPoint(x, y, azimuth, range_km)
                
                # Оновлення в процесорі
                self.image_processor.set_analysis_point(analysis_point)
                
                # Передача сигналу
                self.analysis_point_changed.emit(analysis_point)
                
                print(f"📊 Точка аналізу: азимут {azimuth:.1f}°, дальність {range_km:.1f}км")

    def _on_image_dragged(self, x: int, y: int):
        """Обробка перетягування на зображенні"""
        if not self.image_processor:
            return
        
        # Оновлення координат курсора під час перетягування
        self.cursor_coords.setText(f"({x}, {y})")

    def _on_mouse_moved(self, x: int, y: int):
        """Обробка руху миші над зображенням"""
        if not self.image_processor:
            return
        
        # Оновлення координат курсора
        self.cursor_coords.setText(f"({x}, {y})")
        
        # Оновлення позиції зум віджету
        if self.zoom_widget and self.zoom_widget.isVisible():
            self.zoom_widget.update_position(x, y)

    def _on_center_moved(self, x: int, y: int):
        """Обробка переміщення центру сітки"""
        if not self.image_processor:
            return
        
        print(f"🎯 Новий центр сітки: ({x}, {y})")
        
        # Оновлення центру в процесорі
        self.image_processor.set_grid_center(x, y)
        
        # Передача сигналу
        self.grid_center_changed.emit(x, y)
        
        # Оновлення відображення
        self._update_grid_display(self.image_processor.grid_settings)

    def _on_scale_edge_set(self, x: int, y: int):
        """Обробка встановлення краю масштабу"""
        if not self.image_processor:
            return
        
        print(f"📏 Край масштабу встановлено: ({x}, {y})")
        
        # Розрахунок нового масштабу на основі відстані від центру
        center_x = self.image_processor.grid_settings.center_x
        center_y = self.image_processor.grid_settings.center_y
        
        # Відстань від центру до краю в пікселях
        distance_pixels = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
        
        # Розрахунок масштабу (припускаємо що край відповідає одному кілометру)
        if distance_pixels > 0:
            scale = int(1000 / distance_pixels * 1000)  # масштаб 1:scale
            
            # Обмеження масштабу до доступних значень
            from core.constants import GRID
            available_scales = GRID.AVAILABLE_SCALES
            scale = min(available_scales, key=lambda x: abs(x - scale))
            
            # Встановлення нового масштабу
            self.image_processor.set_grid_scale(scale)
            
            # Передача сигналу
            self.scale_edge_set.emit(x, y, scale)
            
            # Оновлення відображення
            self._update_grid_display(self.image_processor.grid_settings)
            
            print(f"📏 Новий масштаб: 1:{scale}")
    
    def _show_tooltip(self, text: str):
        """Показ tooltip з азимутальною інформацією"""
        if self.tooltip_enabled and self.clickable_label:
            cursor_pos = QCursor.pos()
            QToolTip.showText(cursor_pos, text, self.clickable_label)
    
    # ===============================
    # ОБРОБКА ПОДІЙ ПРОЦЕСОРА
    # ===============================
    
    def _on_image_processed(self, processed_image):
        """Обробка сигналу про оброблене зображення"""
        if processed_image:
            self._display_image(processed_image)
            print("🖼️ Зображення оброблено та оновлено")

    def _on_grid_settings_changed(self, grid_settings):
        """Обробка зміни налаштувань сітки"""
        self._update_grid_display(grid_settings)
        print("🕸️ Налаштування сітки оновлено")

    def _on_analysis_completed(self, analysis_point):
        """Обробка завершення аналізу"""
        if analysis_point:
            print(f"✅ Аналіз завершено: {analysis_point}")
            # Оновлення інформації про сітку
            self.grid_info.setText(f"Азимут: {analysis_point.azimuth:.1f}° | Дальність: {analysis_point.range_km:.1f}км")
    
    def _update_grid_display(self, grid_settings: GridSettings):
        """Оновлення відображення сітки"""
        if self.clickable_label:
            self.clickable_label.set_grid_center(
                grid_settings.center_x, grid_settings.center_y
            )
        
        # Оновлення інформації про сітку
        self.grid_info.setText(
            f"Центр: ({grid_settings.center_x}, {grid_settings.center_y}) | "
            f"Масштаб: 1:{grid_settings.scale}"
        )
    
    # ===============================
    # УПРАВЛІННЯ РЕЖИМАМИ
    # ===============================
    
    def set_mode(self, mode: str):
        """
        Встановлення режиму роботи панелі
        
        Args:
            mode: 'normal', 'center_setting' або 'scale_setting'
        """
        old_mode = self.current_mode
        self.current_mode = mode
        
        if not self.clickable_label:
            return
        
        # Налаштування ClickableLabel відповідно до режиму
        if mode == "center_setting":
            self.clickable_label.set_center_setting_mode(True)
            self.clickable_label.set_scale_edge_mode(False)
            
            # Показ зуму в режимі центру
            if self.zoom_widget:
                self.zoom_widget.set_mode('center')
                self.zoom_widget.show_zoom_at_center()
            
            self._update_mode_indicator("🎯", "#ffc107", "Режим налаштування центру")
            
        elif mode == "scale_setting":
            self.clickable_label.set_center_setting_mode(False)
            self.clickable_label.set_scale_edge_mode(True)
            
            # Показ зуму в режимі масштабу
            if self.zoom_widget:
                self.zoom_widget.set_mode('scale')
                self.zoom_widget.show_zoom()
            
            self._update_mode_indicator("📏", "#fd7e14", "Режим налаштування масштабу")
            
        else:  # normal
            self.clickable_label.set_center_setting_mode(False)
            self.clickable_label.set_scale_edge_mode(False)
            
            # Приховування зуму в звичайному режимі
            if self.zoom_widget:
                self.zoom_widget.set_mode('normal')
                self.zoom_widget.hide_zoom()
            
            self._update_mode_indicator("●", "#6c757d", "Звичайний режим")
        
        # Сигнал про зміну режиму
        if old_mode != mode:
            self.mode_changed.emit(mode)
            print(f"Режим змінено: {old_mode} → {mode}")
    
    def _update_mode_indicator(self, symbol: str, color: str, tooltip: str):
        """Оновлення індикатора режиму"""
        if self.mode_indicator:
            self.mode_indicator.setText(symbol)
            self.mode_indicator.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: 16px;
                    border: none;
                    background: transparent;
                }}
            """)
            self.mode_indicator.setToolTip(tooltip)
    
    def get_current_mode(self) -> str:
        """Отримання поточного режиму"""
        return self.current_mode
    
    # ===============================
    # КЕРУВАННЯ ЗУМОМ
    # ===============================
    
    def show_zoom(self):
        """Показати зум"""
        if self.zoom_widget:
            self.zoom_widget.show_zoom()
    
    def hide_zoom(self):
        """Приховати зум"""
        if self.zoom_widget:
            self.zoom_widget.hide_zoom()
    
    def toggle_zoom(self):
        """Перемикання видимості зуму"""
        if self.zoom_widget:
            self.zoom_widget.toggle_zoom()
    
    def set_zoom_factor(self, factor: int):
        """Встановлення коефіцієнта зуму"""
        if self.zoom_widget:
            self.zoom_widget.set_zoom_factor(factor)
    
    # ===============================
    # НАЛАШТУВАННЯ ПАНЕЛІ
    # ===============================
    
    def set_mouse_tracking_enabled(self, enabled: bool):
        """Увімкнення/вимкнення відстеження миші"""
        self.mouse_tracking_enabled = enabled
        print(f"Відстеження миші: {'увімкнено' if enabled else 'вимкнено'}")
    
    def set_tooltip_enabled(self, enabled: bool):
        """Увімкнення/вимкнення tooltips"""
        self.tooltip_enabled = enabled
        print(f"Tooltips: {'увімкнені' if enabled else 'вимкнені'}")
    
    def set_zoom_enabled(self, enabled: bool):
        """Увімкнення/вимкнення зуму"""
        if self.zoom_widget:
            if not enabled:
                self.zoom_widget.hide_zoom()
            print(f"Зум: {'увімкнений' if enabled else 'вимкнений'}")
    
    # ===============================
    # ОНОВЛЕННЯ ІНФОРМАЦІЇ
    # ===============================
    
    def _update_image_info(self):
        """Оновлення інформації про зображення"""
        if not self.image_processor:
            self.image_info.setText("—")
            return
        
        info = self.image_processor.get_image_info()
        
        size_text = f"{info.get('width', 0)}×{info.get('height', 0)}"
        scale_text = f"1:{info.get('scale', 0)}"
        
        self.image_info.setText(f"Розмір: {size_text} | Масштаб: {scale_text}")
    
    def _update_translations(self):
        """Оновлення перекладів при зміні мови"""
        if self.image_processor and self.image_processor.image_path:
            filename = os.path.basename(self.image_processor.image_path)
            self.header_label.setText(f"📁 {filename}")
        else:
            self.header_label.setText(self.translator.tr(TranslationKeys.OPEN_INSTRUCTION))
        
        # Оновлення tooltips індикатора режиму
        mode_tooltips = {
            "normal": "Звичайний режим",
            "center_setting": "Режим налаштування центру",
            "scale_setting": "Режим налаштування масштабу"
        }
        
        tooltip = mode_tooltips.get(self.current_mode, "Невідомий режим")
        if self.mode_indicator:
            self.mode_indicator.setToolTip(tooltip)
    
    # ===============================
    # ПУБЛІЧНІ МЕТОДИ
    # ===============================
    
    def get_panel_info(self) -> Dict[str, Any]:
        """
        Отримання інформації про панель
        
        Returns:
            Словник з інформацією про панель
        """
        info = {
            'current_mode': self.current_mode,
            'mouse_tracking_enabled': self.mouse_tracking_enabled,
            'tooltip_enabled': self.tooltip_enabled,
            'has_image_processor': self.image_processor is not None,
            'has_image': False,
            'zoom_info': None
        }
        
        if self.image_processor:
            info['has_image'] = self.image_processor.is_ready()
            info['image_info'] = self.image_processor.get_image_info()
        
        if self.zoom_widget:
            info['zoom_info'] = self.zoom_widget.get_zoom_info()
        
        return info
    
    def has_image(self) -> bool:
        """Перевірка чи завантажено зображення"""
        return (self.image_processor is not None and 
                self.image_processor.is_ready())
    
    def get_current_analysis_point(self) -> Optional[Tuple[int, int]]:
        """Отримання поточної точки аналізу"""
        if self.clickable_label:
            return self.clickable_label.get_current_analysis_point()
        return None
    
    def clear_analysis_point(self):
        """Очищення поточної точки аналізу"""
        if self.clickable_label:
            self.clickable_label.clear_analysis_point()
        
        if self.image_processor:
            self.image_processor.clear_analysis()
    
    def focus_image(self):
        """Встановлення фокусу на зображення"""
        if self.clickable_label:
            self.clickable_label.setFocus()
    
    # ===============================
    # ОБРОБКА ПОДІЙ ВІДЖЕТУ
    # ===============================
    
    def resizeEvent(self, event):
        """Обробка зміни розміру панелі"""
        super().resizeEvent(event)
        
        # Переміщення зуму при зміні розміру
        if self.zoom_widget and self.zoom_widget.is_visible:
            QTimer.singleShot(100, self.zoom_widget._position_widget)
    
    def showEvent(self, event):
        """Обробка показу панелі"""
        super().showEvent(event)
        
        # Встановлення фокусу на зображення
        if self.clickable_label:
            QTimer.singleShot(100, self.clickable_label.setFocus)
    
    def keyPressEvent(self, event):
        """Передача клавіатурних подій до ClickableLabel"""
        if self.clickable_label:
            self.clickable_label.keyPressEvent(event)
        else:
            super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Передача клавіатурних подій до ClickableLabel"""
        if self.clickable_label:
            self.clickable_label.keyReleaseEvent(event)
        else:
            super().keyReleaseEvent(event)


if __name__ == "__main__":
    # Тестування панелі зображення
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QGroupBox, QCheckBox
    from PIL import Image, ImageDraw
    import tempfile
    
    class ImagePanelTestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Тестування ImagePanel")
            self.setGeometry(100, 100, 1200, 800)
            
            # Центральний віджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QHBoxLayout(central_widget)
            
            # Панель управління
            control_panel = self.create_control_panel()
            layout.addWidget(control_panel)
            
            # Головна панель зображення
            self.image_panel = ImagePanel()
            layout.addWidget(self.image_panel)
            
            # Створення тестового процесора зображення
            self.setup_test_processor()
            
            # Підключення сигналів
            self.image_panel.image_clicked.connect(self.on_image_clicked)
            self.image_panel.analysis_point_changed.connect(self.on_analysis_point_changed)
            self.image_panel.grid_center_changed.connect(self.on_grid_center_changed)
            self.image_panel.scale_edge_set.connect(self.on_scale_edge_set)
            self.image_panel.mode_changed.connect(self.on_mode_changed)