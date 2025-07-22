#!/usr/bin/env python3
"""
Головне вікно програми PhotoControl v2.0
Координує взаємодію між панелями та основною логікою
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QSplitter, 
                             QMessageBox, QFileDialog, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

# Імпорти наших модулів
from core.constants import UI, FILES, IMAGE
from core.image_processor import ImageProcessor, AnalysisPoint
from utils.file_utils import get_resource_path, get_images_in_directory
from ui.styles.qss_styles import get_main_window_styles

# Імпорти панелей
from ui.panels.control_panel import ControlPanel
from ui.panels.browser_panel import BrowserPanel
from ui.panels.image_panel import ImagePanel
from ui.panels.data_panel import DataPanel


class MainWindow(QMainWindow):
    """
    Головне вікно програми PhotoControl
    
    Структура:
    - Ліва панель: управління файлами, пакетна обробка
    - Браузер: мініатюри зображень (приховується/показується)
    - Центр: перегляд та обробка зображень  
    - Права панель: дані цілі, налаштування сітки
    """
    
    # Сигнали для комунікації між компонентами
    image_loaded = pyqtSignal(str)  # Нове зображення завантажено
    analysis_point_changed = pyqtSignal(object)  # Змінилась точка аналізу
    grid_settings_changed = pyqtSignal(dict)  # Змінились налаштування сітки
    
    def __init__(self):
        super().__init__()
        
        # Основні компоненти
        self.image_processor: Optional[ImageProcessor] = None
        self.current_image_path: Optional[str] = None
        self.current_folder: Optional[str] = None
        
        # Панелі UI
        self.control_panel = None
        self.browser_panel = None
        self.image_panel = None
        self.data_panel = None
        
        # Стан програми
        self.processed_images: List[Dict[str, Any]] = []
        self.grid_settings_cache: Dict[str, Any] = {}
        self.is_browser_visible = False
        
        # Ініціалізація UI
        self.init_ui()
        self.setup_connections()
        self.setup_menu_bar()
        
    def init_ui(self):
        """Ініціалізація користувацького інтерфейсу"""
        self.setWindowTitle("PhotoControl v2.0")
        self.setMinimumSize(UI.MIN_WINDOW_WIDTH, UI.MIN_WINDOW_HEIGHT)
        
        # Встановлення іконки
        try:
            icon_path = get_resource_path("icons/photocontrol.ico")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except:
            pass
        
        # Створення центрального віджету та основного layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Створення основного сплітера
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Створення панелей
        self.create_panels()
        
        # Початкові розміри сплітера
        self.set_initial_splitter_sizes()
        
        # Застосування стилів
        try:
            self.setStyleSheet(get_main_window_styles())
        except:
            # Базові стилі якщо не вдалося завантажити
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f8f9fa;
                    font-family: "Segoe UI", Arial, sans-serif;
                }
            """)
        
    def create_panels(self):
        """Створення всіх панелей інтерфейсу"""
        # Ліва панель управління
        self.control_panel = ControlPanel(self)
        self.main_splitter.addWidget(self.control_panel)
        
        # Браузер зображень (спочатку прихований)
        self.browser_panel = BrowserPanel(self)
        self.main_splitter.addWidget(self.browser_panel)
        self.browser_panel.hide()
        
        # Центральна панель зображень
        self.image_panel = ImagePanel(self)
        self.main_splitter.addWidget(self.image_panel)
        
        # Права панель даних
        self.data_panel = DataPanel(self)
        self.main_splitter.addWidget(self.data_panel)
        
        # Початково права панель прихована
        self.data_panel.hide()
        
    def set_initial_splitter_sizes(self):
        """Встановлення початкових розмірів панелей"""
        total_width = self.width()
        
        if self.is_browser_visible:
            # З браузером: 220 + 280 + залишок + 220
            image_width = max(450, total_width - UI.LEFT_PANEL_WIDTH - 
                            UI.BROWSER_PANEL_WIDTH - UI.RIGHT_PANEL_WIDTH)
            sizes = [UI.LEFT_PANEL_WIDTH, UI.BROWSER_PANEL_WIDTH, 
                    image_width, UI.RIGHT_PANEL_WIDTH]
        else:
            # Без браузера: 220 + 0 + залишок + 220
            image_width = max(450, total_width - UI.LEFT_PANEL_WIDTH - UI.RIGHT_PANEL_WIDTH)
            sizes = [UI.LEFT_PANEL_WIDTH, 0, image_width, UI.RIGHT_PANEL_WIDTH]
        
        self.main_splitter.setSizes(sizes)
    
    def setup_connections(self):
        """Налаштування зв'язків між компонентами"""
        # Зв'язки з панеллю управління
        self.control_panel.open_image_requested.connect(self.open_image)
        self.control_panel.open_folder_requested.connect(self.open_folder)
        self.control_panel.save_image_requested.connect(self.save_current_image)
        self.control_panel.create_album_requested.connect(self.create_album)
        
        # Зв'язки з браузером зображень
        self.browser_panel.image_selected.connect(self.load_image)
        
        # Зв'язки з панеллю зображень
        self.image_panel.point_clicked.connect(self.on_image_point_clicked)
        self.image_panel.center_move_requested.connect(self.on_center_move_requested)
        self.image_panel.scale_edge_requested.connect(self.on_scale_edge_requested)
        
        # Зв'язки з панеллю даних
        self.data_panel.scale_changed.connect(self.on_scale_changed)
        self.data_panel.center_mode_toggled.connect(self.on_center_mode_toggled)
        self.data_panel.scale_edge_mode_toggled.connect(self.on_scale_edge_mode_toggled)
        
        # Внутрішні сигнали вікна
        self.image_loaded.connect(self.on_image_loaded)
        self.analysis_point_changed.connect(self.on_analysis_point_changed)
        self.grid_settings_changed.connect(self.on_grid_settings_changed)
    
    def setup_menu_bar(self):
        """Створення меню програми"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        open_image_action = file_menu.addAction("Відкрити зображення")
        open_image_action.setShortcut("Ctrl+O")
        open_image_action.triggered.connect(self.open_image)
        
        open_folder_action = file_menu.addAction("Відкрити папку")
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(self.open_folder)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Вихід")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Меню "Допомога"
        help_menu = menubar.addMenu("Допомога")
        
        about_action = help_menu.addAction("Про програму")
        about_action.triggered.connect(self.show_about)
    
    # ===== ОСНОВНІ ОПЕРАЦІЇ З ФАЙЛАМИ =====
    
    def open_image(self):
        """Відкриття окремого зображення"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Виберіть зображення",
                "",
                f"Файли зображень ({' '.join('*' + ext for ext in IMAGE.SUPPORTED_FORMATS)});;Всі файли (*.*)"
            )
            
            if file_path:
                self.load_image(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка відкриття файлу: {e}")
    
    def open_folder(self):
        """Відкриття папки з зображеннями"""
        try:
            folder_path = QFileDialog.getExistingDirectory(self, "Виберіть папку з зображеннями")
            
            if folder_path:
                self.current_folder = folder_path
                self.load_folder_images()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка відкриття папки: {e}")
    
    def load_folder_images(self):
        """Завантаження зображень з папки в браузер"""
        if not self.current_folder:
            return
        
        try:
            # Отримання списку зображень
            image_files = get_images_in_directory(self.current_folder)
            
            if not image_files:
                QMessageBox.information(self, "Інформація", 
                                      "В обраній папці не знайдено зображень")
                return
            
            # Показ браузера та завантаження мініатюр
            self.show_browser_panel()
            self.browser_panel.load_images(image_files)
            
            # Показ правої панелі
            self.data_panel.show()
            self.set_initial_splitter_sizes()
            
            print(f"✓ Завантажено {len(image_files)} зображень з папки")
            
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка завантаження папки: {e}")
    
    def load_image(self, image_path: str):
        """Завантаження окремого зображення"""
        try:
            # Використовуємо оригінальну логіку з AzimuthImageProcessor  
            current_scale = 300
            if hasattr(self.data_panel, 'current_scale'):
                current_scale = self.data_panel.current_scale
            
            # Створення нового процесора зображень (сумісного з оригіналом)
            self.image_processor = ImageProcessor(image_path)
            
            if not self.image_processor.is_loaded:
                QMessageBox.critical(self, "Помилка", 
                                   f"Не вдалося завантажити зображення:\n{image_path}")
                return
            
            self.current_image_path = image_path
            
            # Застосування збережених налаштувань сітки  
            self.apply_cached_grid_settings()
            
            # Оновлення UI
            self.image_panel.set_image_processor(self.image_processor)
            
            # Показ правої панелі
            self.data_panel.show()
            self.set_initial_splitter_sizes()
            
            # Оновлення панелей
            self.control_panel.update_current_image_info(image_path)
            
            # Сигнал про завантаження
            self.image_loaded.emit(image_path)
            
            print(f"✓ Зображення завантажено: {os.path.basename(image_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка завантаження зображення:\n{str(e)}")
    
    def apply_cached_grid_settings(self):
        """Застосування збережених налаштувань сітки"""
        if self.grid_settings_cache and self.image_processor:
            self.image_processor.apply_grid_settings(self.grid_settings_cache)
    
    def save_current_image(self):
        """Збереження поточного зображення"""
        if not self.image_processor or not self.image_processor.is_loaded:
            QMessageBox.warning(self, "Попередження", "Немає завантаженого зображення")
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Зберегти зображення",
                "",
                "JPEG files (*.jpg);;PNG files (*.png);;All files (*.*)"
            )
            
            if file_path:
                success = self.image_processor.save_processed_image(file_path, include_grid=True)
                if success:
                    QMessageBox.information(self, "Успіх", f"Зображення збережено:\n{file_path}")
                else:
                    QMessageBox.critical(self, "Помилка", "Не вдалося зберегти зображення")
                    
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка збереження:\n{str(e)}")
    
    def create_album(self):
        """Створення альбому (заглушка)"""
        QMessageBox.information(self, "Інформація", 
                               "Функція створення альбому буде реалізована пізніше")
    
    def show_browser_panel(self):
        """Показ панелі браузера"""
        if not self.is_browser_visible:
            self.browser_panel.show()
            self.is_browser_visible = True
            self.set_initial_splitter_sizes()
    
    def hide_browser_panel(self):
        """Приховання панелі браузера"""
        if self.is_browser_visible:
            self.browser_panel.hide()
            self.is_browser_visible = False
            self.set_initial_splitter_sizes()
    
    # ===== ОБРОБНИКИ ПОДІЙ ЗОБРАЖЕННЯ =====
    
    def on_image_point_clicked(self, x: int, y: int):
        """Обробка кліка по зображенню"""
        if not self.image_processor:
            return
        
        # Перевірка спеціальних режимів
        if self.data_panel.center_setting_mode:
            self.on_center_move_requested(x, y)
            return
        
        if self.data_panel.scale_edge_mode:
            self.on_scale_edge_requested(x, y)
            return
        
        # Встановлення точки аналізу
        analysis_point = self.image_processor.set_analysis_point(x, y)
        
        if analysis_point:
            # Оновлення відображення
            self.image_panel.update_display()
            
            # Оновлення панелі даних
            self.data_panel.update_analysis_data(analysis_point)
            
            # Оновлення панелі управління
            self.control_panel.update_analysis_results(analysis_point)
            
            # Сигнал про зміну точки аналізу
            self.analysis_point_changed.emit(analysis_point)
    
    def on_center_move_requested(self, x: int, y: int):
        """Обробка запиту переміщення центру (клік або клавіатура)"""
        if not self.image_processor:
            return
        
        # Розрахунок зміщення від поточного центру
        current_center_x = self.image_processor.grid_settings.center_x
        current_center_y = self.image_processor.grid_settings.center_y
        
        dx = x - current_center_x
        dy = y - current_center_y
        
        # Використовуємо move_center для збереження налаштувань
        success = self.image_processor.move_center(dx, dy)
        if success:
            self.image_panel.update_display()
            
            # Перерахунок поточної точки аналізу якщо є
            if self.image_processor.current_analysis_point:
                self.data_panel.update_analysis_data(self.image_processor.current_analysis_point)
            
            self.control_panel.add_result(f"Центр переміщено: ({x}, {y})")
    
    def on_scale_edge_requested(self, x: int, y: int):
        """Обробка запиту встановлення краю масштабу"""
        if not self.image_processor:
            return
        
        success = self.image_processor.set_scale_edge(x, y)
        if success:
            self.image_panel.update_display()
            
            # Перерахунок поточної точки аналізу якщо є
            if self.image_processor.current_analysis_point:
                self.data_panel.update_analysis_data(self.image_processor.current_analysis_point)
    
    def on_scale_changed(self, scale_value: int):
        """Обробка зміни масштабу"""
        if not self.image_processor:
            return
        
        success = self.image_processor.set_scale_value(scale_value)
        if success:
            self.image_panel.update_display()
            
            # Перерахунок поточної точки аналізу якщо є
            if self.image_processor.current_analysis_point:
                self.data_panel.update_analysis_data(self.image_processor.current_analysis_point)
    
    def on_center_mode_toggled(self, enabled: bool):
        """Обробка перемикання режиму центру"""
        self.image_panel.set_center_setting_mode(enabled)
        
        if enabled:
            self.control_panel.add_result("Режим встановлення центру активовано")
            self.control_panel.add_result("Клікніть на зображенні або використовуйте стрілки")
        else:
            self.control_panel.add_result("Режим встановлення центру деактивовано")
    
    def on_scale_edge_mode_toggled(self, enabled: bool):
        """Обробка перемикання режиму краю масштабу"""
        self.image_panel.set_scale_edge_mode(enabled)
        
        if enabled:
            self.control_panel.add_result("Режим встановлення краю масштабу активовано")
            self.control_panel.add_result("Клікніть на зображенні або використовуйте стрілки")
        else:
            self.control_panel.add_result("Режим встановлення краю масштабу деактивовано")
    
    # ===== ОБРОБНИКИ СИГНАЛІВ =====
    
    def on_image_loaded(self, image_path: str):
        """Обробник завантаження нового зображення"""
        # Оновлення заголовку вікна
        filename = os.path.basename(image_path)
        self.setWindowTitle(f"PhotoControl v2.0 - {filename}")
    
    def on_analysis_point_changed(self, analysis_point: AnalysisPoint):
        """Обробник зміни точки аналізу"""
        # Збереження налаштувань для поточного зображення
        if self.image_processor:
            self.grid_settings_cache = self.image_processor.get_grid_settings()
    
    def on_grid_settings_changed(self, settings: Dict[str, Any]):
        """Обробник зміни налаштувань сітки"""
        self.grid_settings_cache = settings
    
    def show_about(self):
        """Показ діалогу "Про програму" """
        QMessageBox.about(self, "Про програму", 
                         "PhotoControl v2.0\n\n"
                         "Програма для обробки азимутальних зображень\n"
                         "та створення фотоальбомів\n\n"
                         "© 2025 PhotoControl Team")
    
    def resizeEvent(self, event):
        """Обробник зміни розміру вікна"""
        super().resizeEvent(event)
        
        # Оновлення розмірів панелей з затримкою
        QTimer.singleShot(50, self.set_initial_splitter_sizes)
    
    def cleanup(self):
        """Очищення ресурсів при закритті"""
        # Очищення процесора зображень
        if self.image_processor:
            self.image_processor = None
        
        # Очищення браузера
        if self.browser_panel:
            self.browser_panel.clear()
        
        print("✓ Ресурси очищено")
    
    def closeEvent(self, event):
        """Обробник закриття вікна"""
        self.cleanup()
        event.accept()


if __name__ == "__main__":
    # Тестування головного вікна
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
        
        # Встановлення іконки
        try:
            icon_path = get_resource_path("icons/photocontrol.ico")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except:
            pass
        
        # Створення центрального віджету та основного layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Створення основного сплітера
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Створення панелей
        self.create_panels()
        
        # Початкові розміри сплітера
        self.set_initial_splitter_sizes()
        
        # Застосування стилів
        try:
            self.setStyleSheet(get_main_window_styles())
        except:
            # Базові стилі якщо не вдалося завантажити
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f8f9fa;
                    font-family: "Segoe UI", Arial, sans-serif;
                }
            """)
        
    def create_panels(self):
        """Створення всіх панелей інтерфейсу"""
        # Ліва панель управління
        self.control_panel = ControlPanel(self)
        self.main_splitter.addWidget(self.control_panel)
        
        # Браузер зображень (спочатку прихований)
        self.browser_panel = BrowserPanel(self)
        self.main_splitter.addWidget(self.browser_panel)
        self.browser_panel.hide()
        
        # Центральна панель зображень
        self.image_panel = ImagePanel(self)
        self.main_splitter.addWidget(self.image_panel)
        
        # Права панель даних
        self.data_panel = DataPanel(self)
        self.main_splitter.addWidget(self.data_panel)
        
        # Початково права панель прихована
        self.data_panel.hide()
        
    def set_initial_splitter_sizes(self):
        """Встановлення початкових розмірів панелей"""
        total_width = self.width()
        
        if self.is_browser_visible:
            # З браузером: 220 + 280 + залишок + 220
            image_width = max(450, total_width - UI.LEFT_PANEL_WIDTH - 
                            UI.BROWSER_PANEL_WIDTH - UI.RIGHT_PANEL_WIDTH)
            sizes = [UI.LEFT_PANEL_WIDTH, UI.BROWSER_PANEL_WIDTH, 
                    image_width, UI.RIGHT_PANEL_WIDTH]
        else:
            # Без браузера: 220 + 0 + залишок + 220
            image_width = max(450, total_width - UI.LEFT_PANEL_WIDTH - UI.RIGHT_PANEL_WIDTH)
            sizes = [UI.LEFT_PANEL_WIDTH, 0, image_width, UI.RIGHT_PANEL_WIDTH]
        
        self.main_splitter.setSizes(sizes)
    
    def setup_connections(self):
        """Налаштування зв'язків між компонентами"""
        # Зв'язки з панеллю управління
        self.control_panel.open_image_requested.connect(self.open_image)
        self.control_panel.open_folder_requested.connect(self.open_folder)
        self.control_panel.save_image_requested.connect(self.save_current_image)
        self.control_panel.create_album_requested.connect(self.create_album)
        
        # Зв'язки з браузером зображень
        self.browser_panel.image_selected.connect(self.load_image)
        
        # Зв'язки з панеллю зображень
        self.image_panel.point_clicked.connect(self.on_image_point_clicked)
        self.image_panel.center_move_requested.connect(self.on_center_move_requested)
        self.image_panel.scale_edge_requested.connect(self.on_scale_edge_requested)
        
        # Зв'язки з панеллю даних
        self.data_panel.scale_changed.connect(self.on_scale_changed)
        self.data_panel.center_mode_toggled.connect(self.on_center_mode_toggled)
        self.data_panel.scale_edge_mode_toggled.connect(self.on_scale_edge_mode_toggled)
        
        # Внутрішні сигнали вікна
        self.image_loaded.connect(self.on_image_loaded)
        self.analysis_point_changed.connect(self.on_analysis_point_changed)
        self.grid_settings_changed.connect(self.on_grid_settings_changed)
    
    def setup_menu_bar(self):
        """Створення меню програми"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        open_image_action = file_menu.addAction("Відкрити зображення")
        open_image_action.setShortcut("Ctrl+O")
        open_image_action.triggered.connect(self.open_image)
        
        open_folder_action = file_menu.addAction("Відкрити папку")
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(self.open_folder)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Вихід")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Меню "Допомога"
        help_menu = menubar.addMenu("Допомога")
        
        about_action = help_menu.addAction("Про програму")
        about_action.triggered.connect(self.show_about)
    
    # ===== ОСНОВНІ ОПЕРАЦІЇ З ФАЙЛАМИ =====
    
    def open_image(self):
        """Відкриття окремого зображення"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Виберіть зображення",
                "",
                f"Файли зображень ({' '.join('*' + ext for ext in IMAGE.SUPPORTED_FORMATS)});;Всі файли (*.*)"
            )
            
            if file_path:
                self.load_image(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка відкриття файлу: {e}")
    
    def open_folder(self):
        """Відкриття папки з зображеннями"""
        try:
            folder_path = QFileDialog.getExistingDirectory(self, "Виберіть папку з зображеннями")
            
            if folder_path:
                self.current_folder = folder_path
                self.load_folder_images()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка відкриття папки: {e}")
    
    def load_folder_images(self):
        """Завантаження зображень з папки в браузер"""
        if not self.current_folder:
            return
        
        try:
            # Отримання списку зображень
            image_files = get_images_in_directory(self.current_folder)
            
            if not image_files:
                QMessageBox.information(self, "Інформація", 
                                      "В обраній папці не знайдено зображень")
                return
            
            # Показ браузера та завантаження мініатюр
            self.show_browser_panel()
            self.browser_panel.load_images(image_files)
            
            # Показ правої панелі
            self.data_panel.show()
            self.set_initial_splitter_sizes()
            
            print(f"✓ Завантажено {len(image_files)} зображень з папки")
            
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка завантаження папки: {e}")
    
    def load_image(self, image_path: str):
        """Завантаження окремого зображення"""
        try:
            # Створення нового процесора зображень
            self.image_processor = ImageProcessor(image_path)
            
            if not self.image_processor.is_loaded:
                QMessageBox.critical(self, "Помилка", 
                                   f"Не вдалося завантажити зображення:\n{image_path}")
                return
            
            self.current_image_path = image_path
            
            # Застосування збережених налаштувань сітки
            self.apply_cached_grid_settings()
            
            # Оновлення UI
            self.image_panel.set_image_processor(self.image_processor)
            
            # Показ правої панелі
            self.data_panel.show()
            self.set_initial_splitter_sizes()
            
            # Оновлення панелей
            self.control_panel.update_current_image_info(image_path)
            
            # Сигнал про завантаження
            self.image_loaded.emit(image_path)
            
            print(f"✓ Зображення завантажено: {os.path.basename(image_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка завантаження зображення:\n{str(e)}")
    
    def apply_cached_grid_settings(self):
        """Застосування збережених налаштувань сітки"""
        if self.grid_settings_cache and self.image_processor:
            self.image_processor.apply_grid_settings(self.grid_settings_cache)
    
    def save_current_image(self):
        """Збереження поточного зображення"""
        if not self.image_processor or not self.image_processor.is_loaded:
            QMessageBox.warning(self, "Попередження", "Немає завантаженого зображення")
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Зберегти зображення",
                "",
                "JPEG files (*.jpg);;PNG files (*.png);;All files (*.*)"
            )
            
            if file_path:
                success = self.image_processor.save_processed_image(file_path, include_grid=True)
                if success:
                    QMessageBox.information(self, "Успіх", f"Зображення збережено:\n{file_path}")
                else:
                    QMessageBox.critical(self, "Помилка", "Не вдалося зберегти зображення")
                    
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка збереження:\n{str(e)}")
    
    def create_album(self):
        """Створення альбому (заглушка)"""
        QMessageBox.information(self, "Інформація", 
                               "Функція створення альбому буде реалізована пізніше")
    
    def show_browser_panel(self):
        """Показ панелі браузера"""
        if not self.is_browser_visible:
            self.browser_panel.show()
            self.is_browser_visible = True
            self.set_initial_splitter_sizes()
    
    def hide_browser_panel(self):
        """Приховання панелі браузера"""
        if self.is_browser_visible:
            self.browser_panel.hide()
            self.is_browser_visible = False
            self.set_initial_splitter_sizes()
    
    # ===== ОБРОБНИКИ ПОДІЙ ЗОБРАЖЕННЯ =====
    
    def on_image_point_clicked(self, x: int, y: int):
        """Обробка кліка по зображенню"""
        if not self.image_processor:
            return
        
        # Перевірка спеціальних режимів
        if self.data_panel.center_setting_mode:
            self.on_center_move_requested(x, y)
            return
        
        if self.data_panel.scale_edge_mode:
            self.on_scale_edge_requested(x, y)
            return
        
        # Встановлення точки аналізу
        analysis_point = self.image_processor.set_analysis_point(x, y)
        
        if analysis_point:
            # Оновлення відображення
            self.image_panel.update_display()
            
            # Оновлення панелі даних
            self.data_panel.update_analysis_data(analysis_point)
            
            # Оновлення панелі управління
            self.control_panel.update_analysis_results(analysis_point)
            
            # Сигнал про зміну точки аналізу
            self.analysis_point_changed.emit(analysis_point)
    
    def on_center_move_requested(self, x: int, y: int):
        """Обробка запиту переміщення центру (клік або клавіатура)"""
        if not self.image_processor:
            return
        
        # Розрахунок зміщення від поточного центру
        current_center_x = self.image_processor.grid_settings.center_x
        current_center_y = self.image_processor.grid_settings.center_y
        
        dx = x - current_center_x
        dy = y - current_center_y
        
        # Використовуємо move_center для збереження налаштувань
        success = self.image_processor.move_center(dx, dy)
        if success:
            self.image_panel.update_display()
            
            # Перерахунок поточної точки аналізу якщо є
            if self.image_processor.current_analysis_point:
                self.data_panel.update_analysis_data(self.image_processor.current_analysis_point)
            
            self.control_panel.add_result(f"Центр переміщено: ({x}, {y})")
    
    def on_scale_edge_requested(self, x: int, y: int):
        """Обробка запиту встановлення краю масштабу"""
        if not self.image_processor:
            return
        
        success = self.image_processor.set_scale_edge(x, y)
        if success:
            self.image_panel.update_display()
            
            # Перерахунок поточної точки аналізу якщо є
            if self.image_processor.current_analysis_point:
                self.data_panel.update_analysis_data(self.image_processor.current_analysis_point)
    
    def on_scale_changed(self, scale_value: int):
        """Обробка зміни масштабу"""
        if not self.image_processor:
            return
        
        success = self.image_processor.set_scale_value(scale_value)
        if success:
            self.image_panel.update_display()
            
            # Перерахунок поточної точки аналізу якщо є
            if self.image_processor.current_analysis_point:
                self.data_panel.update_analysis_data(self.image_processor.current_analysis_point)
    
    def on_center_mode_toggled(self, enabled: bool):
        """Обробка перемикання режиму центру"""
        self.image_panel.set_center_setting_mode(enabled)
        
        if enabled:
            self.control_panel.add_result("Режим встановлення центру активовано")
            self.control_panel.add_result("Клікніть на зображенні або використовуйте стрілки")
        else:
            self.control_panel.add_result("Режим встановлення центру деактивовано")
    
    def on_scale_edge_mode_toggled(self, enabled: bool):
        """Обробка перемикання режиму краю масштабу"""
        self.image_panel.set_scale_edge_mode(enabled)
        
        if enabled:
            self.control_panel.add_result("Режим встановлення краю масштабу активовано")
            self.control_panel.add_result("Клікніть на зображенні або використовуйте стрілки")
        else:
            self.control_panel.add_result("Режим встановлення краю масштабу деактивовано")
    
    # ===== ОБРОБНИКИ СИГНАЛІВ =====
    
    def on_image_loaded(self, image_path: str):
        """Обробник завантаження нового зображення"""
        # Оновлення заголовку вікна
        filename = os.path.basename(image_path)
        self.setWindowTitle(f"PhotoControl v2.0 - {filename}")
    
    def on_analysis_point_changed(self, analysis_point: AnalysisPoint):
        """Обробник зміни точки аналізу"""
        # Збереження налаштувань для поточного зображення
        if self.image_processor:
            self.grid_settings_cache = self.image_processor.get_grid_settings()
    
    def on_grid_settings_changed(self, settings: Dict[str, Any]):
        """Обробник зміни налаштувань сітки"""
        self.grid_settings_cache = settings
    
    def show_about(self):
        """Показ діалогу "Про програму" """
        QMessageBox.about(self, "Про програму", 
                         "PhotoControl v2.0\n\n"
                         "Програма для обробки азимутальних зображень\n"
                         "та створення фотоальбомів\n\n"
                         "© 2025 PhotoControl Team")
    
    def resizeEvent(self, event):
        """Обробник зміни розміру вікна"""
        super().resizeEvent(event)
        
        # Оновлення розмірів панелей з затримкою
        QTimer.singleShot(50, self.set_initial_splitter_sizes)
    
    def cleanup(self):
        """Очищення ресурсів при закритті"""
        # Очищення процесора зображень
        if self.image_processor:
            self.image_processor = None
        
        # Очищення браузера
        if self.browser_panel:
            self.browser_panel.clear()
        
        print("✓ Ресурси очищено")
    
    def closeEvent(self, event):
        """Обробник закриття вікна"""
        self.cleanup()
        event.accept()


if __name__ == "__main__":
    # Тестування головного вікна
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())