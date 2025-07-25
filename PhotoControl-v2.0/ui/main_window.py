#!/usr/bin/env python3
"""
Головне вікно PhotoControl v2.0
Інтеграція всіх компонентів: панелі управління, зображення, мініатюр, меню
"""

import os
import sys
from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QMenuBar, QMenu, QAction, QStatusBar,
                             QFileDialog, QMessageBox, QProgressBar, QLabel,
                             QApplication, QActionGroup, QToolBar)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, QSettings
from PyQt5.QtGui import QIcon, QKeySequence, QFont

from ui.panels.image_panel import ImagePanel
from ui.widgets.thumbnail_browser import ThumbnailBrowser
from core.image_processor import ImageProcessor, AnalysisPoint
from core.album_creator import AlbumCreator, ImageData, TitlePageData
from core.constants import UI, FILES, ALBUM
from utils.file_utils import (get_images_in_directory, is_image_file, 
                              get_user_data_directory, save_json_file, load_json_file)
from translations.translator import get_translator, TranslationKeys, Language


class ProcessingThread(QThread):
    """Потік для обробки зображень без блокування UI"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, album_creator, images_data, title_data, output_path):
        super().__init__()
        self.album_creator = album_creator
        self.images_data = images_data
        self.title_data = title_data
        self.output_path = output_path
    
    def run(self):
        try:
            success = self.album_creator.create_album(
                self.images_data, self.title_data, self.output_path
            )
            self.finished.emit(success, self.output_path if success else "Помилка створення")
        except Exception as e:
            self.finished.emit(False, str(e))


class MainWindow(QMainWindow):
    """
    Головне вікно PhotoControl v2.0
    
    Функціональність:
    - Інтеграція всіх панелей (управління, зображення, мініатюри)
    - Повне меню з файловими операціями та налаштуваннями
    - Пакетна обробка зображень
    - Створення Word альбомів
    - Система перекладів
    - Збереження налаштувань між сесіями
    - Клавіатурні скорочення
    """
    
    def __init__(self):
        super().__init__()
        
        # Основні компоненти
        self.image_processor: Optional[ImageProcessor] = None
        self.album_creator: Optional[AlbumCreator] = None
        self.processing_thread: Optional[ProcessingThread] = None
        
        # Панелі UI
        self.image_panel: Optional[ImagePanel] = None
        self.thumbnail_browser: Optional[ThumbnailBrowser] = None
        
        # Стан програми
        self.current_folder_path: Optional[str] = None
        self.processed_images: List[Dict[str, Any]] = []
        self.settings = QSettings('PhotoControl', 'PhotoControl v2.0')
        
        # Система перекладів
        self.translator = get_translator()
        
        # Ініціалізація
        self._setup_window()
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_central_widget()
        self._create_status_bar()
        self._setup_connections()
        self._load_settings()
        self._update_ui_state()
        
        print("MainWindow ініціалізовано")
    
    # ===============================
    # ІНІЦІАЛІЗАЦІЯ UI
    # ===============================
    
    def _setup_window(self):
        """Налаштування основних властивостей вікна"""
        # Розміри та позиція
        self.setWindowTitle(self.translator.tr(TranslationKeys.WINDOW_TITLE))
        self.setMinimumSize(UI.MIN_WINDOW_WIDTH, UI.MIN_WINDOW_HEIGHT)
        self.resize(UI.DEFAULT_WINDOW_WIDTH, UI.DEFAULT_WINDOW_HEIGHT)
        
        # Іконка
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'netaz.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Стиль вікна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QSplitter::handle {
                background-color: #dee2e6;
                width: 4px;
                height: 4px;
            }
            QSplitter::handle:hover {
                background-color: #adb5bd;
            }
        """)
    
    def _create_menu_bar(self):
        """Створення головного меню"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu(self.translator.tr(TranslationKeys.FILE_OPERATIONS))
        
        # Відкрити зображення
        open_image_action = QAction(self.translator.tr(TranslationKeys.OPEN_IMAGE), self)
        open_image_action.setShortcut(QKeySequence.Open)
        open_image_action.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))
        open_image_action.triggered.connect(self.open_image)
        file_menu.addAction(open_image_action)
        
        # Відкрити папку
        open_folder_action = QAction(self.translator.tr(TranslationKeys.OPEN_FOLDER), self)
        open_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_folder_action.setIcon(self.style().standardIcon(self.style().SP_DirOpenIcon))
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        # Зберегти поточне зображення
        save_image_action = QAction(self.translator.tr(TranslationKeys.SAVE_CURRENT_IMAGE), self)
        save_image_action.setShortcut(QKeySequence.Save)
        save_image_action.setIcon(self.style().standardIcon(self.style().SP_DialogSaveButton))
        save_image_action.triggered.connect(self.save_current_image)
        file_menu.addAction(save_image_action)
        self.save_image_action = save_image_action  # Зберігаємо для оновлення стану
        
        file_menu.addSeparator()
        
        # Створити альбом
        create_album_action = QAction(self.translator.tr(TranslationKeys.CREATE_NEW_ALBUM), self)
        create_album_action.setShortcut(QKeySequence("Ctrl+N"))
        create_album_action.setIcon(self.style().standardIcon(self.style().SP_FileDialogNewFolder))
        create_album_action.triggered.connect(self.create_album)
        file_menu.addAction(create_album_action)
        self.create_album_action = create_album_action
        
        file_menu.addSeparator()
        
        # Вихід
        exit_action = QAction("Вихід", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Вид"
        view_menu = menubar.addMenu("Вид")
        
        # Показати/приховати мініатюри
        toggle_thumbnails_action = QAction("Показати мініатюри", self)
        toggle_thumbnails_action.setCheckable(True)
        toggle_thumbnails_action.setChecked(True)
        toggle_thumbnails_action.triggered.connect(self.toggle_thumbnails)
        view_menu.addAction(toggle_thumbnails_action)
        self.toggle_thumbnails_action = toggle_thumbnails_action
        
        # Зум
        zoom_menu = view_menu.addMenu("Зум")
        
        show_zoom_action = QAction("Показати зум", self)
        show_zoom_action.setShortcut(QKeySequence("Ctrl+Z"))
        show_zoom_action.triggered.connect(self.show_zoom)
        zoom_menu.addAction(show_zoom_action)
        
        hide_zoom_action = QAction("Приховати зум", self)
        hide_zoom_action.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        hide_zoom_action.triggered.connect(self.hide_zoom)
        zoom_menu.addAction(hide_zoom_action)
        
        # Меню "Сітка"
        grid_menu = menubar.addMenu(self.translator.tr(TranslationKeys.AZIMUTH_GRID))
        
        # Режим налаштування центру
        center_mode_action = QAction(self.translator.tr(TranslationKeys.SET_CENTER), self)
        center_mode_action.setShortcut(QKeySequence("Ctrl+C"))
        center_mode_action.setCheckable(True)
        center_mode_action.triggered.connect(lambda: self.set_grid_mode("center_setting"))
        grid_menu.addAction(center_mode_action)
        self.center_mode_action = center_mode_action
        
        # Режим налаштування масштабу
        scale_mode_action = QAction(self.translator.tr(TranslationKeys.SET_SCALE_EDGE), self)
        scale_mode_action.setShortcut(QKeySequence("Ctrl+S"))
        scale_mode_action.setCheckable(True)
        scale_mode_action.triggered.connect(lambda: self.set_grid_mode("scale_setting"))
        grid_menu.addAction(scale_mode_action)
        self.scale_mode_action = scale_mode_action
        
        # Звичайний режим
        normal_mode_action = QAction("Звичайний режим", self)
        normal_mode_action.setShortcut(QKeySequence("Escape"))
        normal_mode_action.setCheckable(True)
        normal_mode_action.setChecked(True)
        normal_mode_action.triggered.connect(lambda: self.set_grid_mode("normal"))
        grid_menu.addAction(normal_mode_action)
        self.normal_mode_action = normal_mode_action
        
        # Група дій для режимів (щоб тільки один був активний)
        self.grid_mode_group = QActionGroup(self)
        self.grid_mode_group.addAction(normal_mode_action)
        self.grid_mode_group.addAction(center_mode_action)
        self.grid_mode_group.addAction(scale_mode_action)
        
        # Меню "Мова"
        language_menu = menubar.addMenu(self.translator.tr(TranslationKeys.LANGUAGE))
        
        # Українська
        ukrainian_action = QAction("Українська", self)
        ukrainian_action.setCheckable(True)
        ukrainian_action.triggered.connect(lambda: self.change_language(Language.UKRAINIAN))
        language_menu.addAction(ukrainian_action)
        
        # Англійська
        english_action = QAction("English", self)
        english_action.setCheckable(True)
        english_action.triggered.connect(lambda: self.change_language(Language.ENGLISH))
        language_menu.addAction(english_action)
        
        # Група мов
        self.language_group = QActionGroup(self)
        self.language_group.addAction(ukrainian_action)
        self.language_group.addAction(english_action)
        
        # Встановлення поточної мови
        current_lang = self.translator.get_current_language()
        if current_lang == Language.UKRAINIAN:
            ukrainian_action.setChecked(True)
        else:
            english_action.setChecked(True)
        
        # Збереження посилань
        self.ukrainian_action = ukrainian_action
        self.english_action = english_action
        
        # Меню "Довідка"
        help_menu = menubar.addMenu("Довідка")
        
        about_action = QAction("Про програму", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _create_tool_bar(self):
        """Створення панелі інструментів"""
        toolbar = self.addToolBar("Основні інструменти")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        # Відкрити зображення
        open_image_btn = toolbar.addAction(
            self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            "Зображення",
            self.open_image
        )
        
        # Відкрити папку
        open_folder_btn = toolbar.addAction(
            self.style().standardIcon(self.style().SP_DirOpenIcon),
            "Папка",
            self.open_folder
        )
        
        toolbar.addSeparator()
        
        # Режими сітки
        center_btn = toolbar.addAction("🎯", self.toggle_center_mode)
        center_btn.setToolTip("Налаштування центру (Ctrl+C)")
        center_btn.setCheckable(True)
        self.center_toolbar_btn = center_btn
        
        scale_btn = toolbar.addAction("📏", self.toggle_scale_mode)
        scale_btn.setToolTip("Налаштування масштабу (Ctrl+S)")
        scale_btn.setCheckable(True)
        self.scale_toolbar_btn = scale_btn
        
        toolbar.addSeparator()
        
        # Створити альбом
        album_btn = toolbar.addAction(
            self.style().standardIcon(self.style().SP_FileDialogNewFolder),
            "Альбом",
            self.create_album
        )
        
        self.toolbar = toolbar
    
    def _create_central_widget(self):
        """Створення центрального віджету з панелями"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основний горизонтальний розділювач
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Ліва панель з мініатюрами
        self.thumbnail_browser = ThumbnailBrowser(width=UI.THUMBNAIL_PANEL_WIDTH)
        main_splitter.addWidget(self.thumbnail_browser)
        
        # Центральна панель зображення
        self.image_panel = ImagePanel()
        main_splitter.addWidget(self.image_panel)
        
        # Налаштування пропорцій
        main_splitter.setSizes([UI.THUMBNAIL_PANEL_WIDTH, UI.DEFAULT_WINDOW_WIDTH - UI.THUMBNAIL_PANEL_WIDTH])
        main_splitter.setCollapsible(0, True)  # Мініатюри можна згорнути
        main_splitter.setCollapsible(1, False)  # Панель зображення завжди видима
        
        # Layout
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)
        
        self.main_splitter = main_splitter
    
    def _create_status_bar(self):
        """Створення статус-бару"""
        status_bar = self.statusBar()
        
        # Повідомлення
        self.status_message = QLabel("Готовий")
        status_bar.addWidget(self.status_message)
        
        # Прогрес-бар (приховано за замовчуванням)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        status_bar.addPermanentWidget(self.progress_bar)
        
        # Інформація про зображення
        self.image_status = QLabel("—")
        status_bar.addPermanentWidget(self.image_status)
        
        # Лічильник оброблених зображень
        self.processed_counter = QLabel("Оброблено: 0")
        status_bar.addPermanentWidget(self.processed_counter)
    
    def _setup_connections(self):
        """Налаштування з'єднань сигналів"""
        # Панель зображення
        if self.image_panel:
            self.image_panel.image_clicked.connect(self.on_image_clicked)
            self.image_panel.analysis_point_changed.connect(self.on_analysis_point_changed)
            self.image_panel.grid_center_changed.connect(self.on_grid_center_changed)
            self.image_panel.scale_edge_set.connect(self.on_scale_edge_set)
            self.image_panel.mode_changed.connect(self.on_mode_changed)
        
        # Браузер мініатюр
        if self.thumbnail_browser:
            self.thumbnail_browser.image_selected.connect(self.on_thumbnail_selected)
            self.thumbnail_browser.processing_status_changed.connect(self.on_processing_status_changed)
        
        # Система перекладів
        self.translator.language_changed.connect(self.update_translations)
    
    # ===============================
    # ФАЙЛОВІ ОПЕРАЦІЇ
    # ===============================
    
    def open_image(self):
        """Відкриття одного зображення"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.translator.tr(TranslationKeys.SELECT_IMAGE),
            "",
            self.translator.tr_file_filter('images')
        )
        
        if file_path and is_image_file(file_path):
            self.load_single_image(file_path)
    
    def open_folder(self):
        """Відкриття папки з зображеннями"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            self.translator.tr(TranslationKeys.SELECT_FOLDER),
            ""
        )
        
        if folder_path:
            self.load_folder(folder_path)
    
    def load_single_image(self, image_path: str):
        """
        Завантаження одного зображення
        
        Args:
            image_path: Шлях до зображення
        """
        try:
            # Створення нового процесора
            self.image_processor = ImageProcessor(image_path)
            
            # Встановлення в панель зображення
            self.image_panel.set_image_processor(self.image_processor)
            
            # Оневлення статусу
            self.status_message.setText(f"Завантажено: {os.path.basename(image_path)}")
            self.image_status.setText(f"{self.image_processor.working_image.width}×{self.image_processor.working_image.height}")
            
            # Очищення мініатюр (для одного зображення)
            self.thumbnail_browser.clear_thumbnails()
            
            self._update_ui_state()
            
            print(f"Зображення завантажено: {image_path}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.translator.tr(TranslationKeys.ERROR),
                self.translator.tr(TranslationKeys.COULD_NOT_LOAD, error=str(e))
            )
    
    def load_folder(self, folder_path: str):
        """
        Завантаження папки з зображеннями
        
        Args:
            folder_path: Шлях до папки
        """
        try:
            # Пошук зображень в папці
            image_files = get_images_in_directory(folder_path)
            
            if not image_files:
                QMessageBox.information(
                    self,
                    self.translator.tr(TranslationKeys.WARNING),
                    self.translator.tr(TranslationKeys.NO_IMAGES_FOUND)
                )
                return
            
            self.current_folder_path = folder_path
            
            # Завантаження мініатюр
            self.thumbnail_browser.load_images(image_files)
            
            # Завантаження першого зображення
            if image_files:
                first_image = image_files[0]
                self.image_processor = ImageProcessor(first_image)
                self.image_panel.set_image_processor(self.image_processor)
            
            # Оновлення статусу
            folder_name = os.path.basename(folder_path)
            self.status_message.setText(
                self.translator.tr(TranslationKeys.FOUND_IMAGES, count=len(image_files)) + 
                f" в папці: {folder_name}"
            )
            
            self._update_ui_state()
            
            print(f"Папка завантажена: {folder_path}, зображень: {len(image_files)}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.translator.tr(TranslationKeys.ERROR),
                f"Помилка завантаження папки: {str(e)}"
            )
    
    def save_current_image(self):
        """Збереження поточного обробленого зображення"""
        if not self.image_processor or not self.image_processor.has_analysis():
            QMessageBox.warning(
                self,
                self.translator.tr(TranslationKeys.WARNING),
                self.translator.tr(TranslationKeys.NO_ANALYSIS_POINT)
            )
            return
        
        # Діалог збереження
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.translator.tr(TranslationKeys.SAVE_PROCESSED_IMAGE),
            "",
            self.translator.tr_file_filter('images')
        )
        
        if file_path:
            try:
                # Створення обробленого зображення
                processed_image = self.image_processor.create_processed_image()
                
                if processed_image:
                    processed_image.save(file_path)
                    self.status_message.setText(f"Збережено: {os.path.basename(file_path)}")
                    print(f"Зображення збережено: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.translator.tr(TranslationKeys.ERROR),
                    self.translator.tr(TranslationKeys.COULD_NOT_SAVE, error=str(e))
                )
    
    # ===============================
    # ОБРОБКА ПОДІЙ ПАНЕЛЕЙ
    # ===============================
    
    def on_image_clicked(self, x: int, y: int):
        """Обробка кліку на зображенні"""
        print(f"Клік на зображенні: ({x}, {y})")
        self._update_ui_state()
    
    def on_analysis_point_changed(self, analysis_point: AnalysisPoint):
        """Обробка зміни точки аналізу"""
        # Автоматичне збереження даних для пакетної обробки
        self.save_current_analysis()
        
        # Оновлення статусу
        azimuth_text = f"{analysis_point.azimuth:.1f}°"
        range_text = f"{analysis_point.range_value:.1f}"
        self.status_message.setText(f"Аналіз: Азимут {azimuth_text}, Дальність {range_text}")
        
        self._update_ui_state()
    
    def on_grid_center_changed(self, x: int, y: int):
        """Обробка зміни центру сітки"""
        self.status_message.setText(f"Центр сітки: ({x}, {y})")
    
    def on_scale_edge_set(self, x: int, y: int):
        """Обробка встановлення точки масштабу"""
        self.status_message.setText(f"Масштаб встановлено: ({x}, {y})")
        
        # Автоматичне повернення до звичайного режиму
        self.set_grid_mode("normal")
    
    def on_mode_changed(self, mode: str):
        """Обробка зміни режиму"""
        # Оновлення стану кнопок панелі інструментів
        if hasattr(self, 'center_toolbar_btn'):
            self.center_toolbar_btn.setChecked(mode == "center_setting")
        if hasattr(self, 'scale_toolbar_btn'):
            self.scale_toolbar_btn.setChecked(mode == "scale_setting")
        
        # Оновлення стану меню
        if hasattr(self, 'center_mode_action'):
            self.center_mode_action.setChecked(mode == "center_setting")
        if hasattr(self, 'scale_mode_action'):
            self.scale_mode_action.setChecked(mode == "scale_setting")
        if hasattr(self, 'normal_mode_action'):
            self.normal_mode_action.setChecked(mode == "normal")
    
    def on_thumbnail_selected(self, image_path: str):
        """Обробка вибору мініатюри"""
        try:
            # Збереження поточного аналізу перед переключенням
            if self.image_processor and self.image_processor.has_analysis():
                self.save_current_analysis()
            
            # Завантаження нового зображення
            self.image_processor = ImageProcessor(image_path)
            self.image_panel.set_image_processor(self.image_processor)
            
            # Оновлення статусу
            filename = os.path.basename(image_path)
            self.status_message.setText(f"Відкрито: {filename}")
            
            print(f"Мініатюра обрана: {filename}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.translator.tr(TranslationKeys.ERROR),
                f"Помилка завантаження зображення: {str(e)}"
            )
    
    def on_processing_status_changed(self, image_path: str, is_processed: bool):
        """Обробка зміни статусу обробки зображення"""
        status = "оброблено" if is_processed else "скасовано"
        filename = os.path.basename(image_path)
        print(f"Статус обробки змінено - {filename}: {status}")
        
        # Оновлення лічильника
        processed_count = len(self.thumbnail_browser.get_processed_images())
        self.processed_counter.setText(f"Оброблено: {processed_count}")
    
    # ===============================
    # УПРАВЛІННЯ РЕЖИМАМИ
    # ===============================
    
    def set_grid_mode(self, mode: str):
        """Встановлення режиму роботи з сіткою"""
        if self.image_panel:
            self.image_panel.set_mode(mode)
    
    def toggle_center_mode(self):
        """Перемикання режиму налаштування центру"""
        if self.image_panel:
            current_mode = self.image_panel.get_current_mode()
            new_mode = "center_setting" if current_mode != "center_setting" else "normal"
            self.image_panel.set_mode(new_mode)
    
    def toggle_scale_mode(self):
        """Перемикання режиму налаштування масштабу"""
        if self.image_panel:
            current_mode = self.image_panel.get_current_mode()
            new_mode = "scale_setting" if current_mode != "scale_setting" else "normal"
            self.image_panel.set_mode(new_mode)
    
    # ===============================
    # УПРАВЛІННЯ ЗУМОМ
    # ===============================
    
    def show_zoom(self):
        """Показати зум"""
        if self.image_panel:
            self.image_panel.show_zoom()
    
    def hide_zoom(self):
        """Приховати зум"""
        if self.image_panel:
            self.image_panel.hide_zoom()
    
    def toggle_thumbnails(self):
        """Перемикання видимості мініатюр"""
        if self.thumbnail_browser:
            visible = self.thumbnail_browser.isVisible()
            self.thumbnail_browser.setVisible(not visible)
            
            # Оновлення тексту дії
            if hasattr(self, 'toggle_thumbnails_action'):
                text = "Приховати мініатюри" if not visible else "Показати мініатюри"
                self.toggle_thumbnails_action.setText(text)
    
    # ===============================
    # ПАКЕТНА ОБРОБКА ТА АЛЬБОМИ
    # ===============================
    
    def save_current_analysis(self):
        """Збереження поточного аналізу для пакетної обробки"""
        if not self.image_processor or not self.image_processor.has_analysis():
            return
        
        analysis_data = self.image_processor.export_analysis_data()
        if not analysis_data:
            return
        
        # Позначення зображення як обробленого в браузері мініатюр
        if self.thumbnail_browser and self.image_processor.image_path:
            self.thumbnail_browser.mark_image_as_processed(self.image_processor.image_path)
        
        # Додавання до списку оброблених зображень
        existing_index = -1
        for i, img_data in enumerate(self.processed_images):
            if img_data.get('image_path') == self.image_processor.image_path:
                existing_index = i
                break
        
        if existing_index >= 0:
            # Оновлення існуючих даних
            self.processed_images[existing_index] = analysis_data
        else:
            # Додавання нових даних
            self.processed_images.append(analysis_data)
        
        # Оновлення лічильника
        self.processed_counter.setText(f"Оброблено: {len(self.processed_images)}")
        
        print(f"Аналіз збережено: {os.path.basename(self.image_processor.image_path)}")
    
    def create_album(self):
        """Створення Word альбому з оброблених зображень"""
        if not self.processed_images:
            QMessageBox.warning(
                self,
                self.translator.tr(TranslationKeys.WARNING),
                "Немає оброблених зображень для створення альбому"
            )
            return
        
        # Збереження поточного аналізу
        if self.image_processor and self.image_processor.has_analysis():
            self.save_current_analysis()
        
        # Діалог налаштування альбому
        title_data = self.get_album_title_data()
        if not title_data:
            return  # Користувач скасував
        
        # Діалог збереження
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Створити альбом",
            "",
            "Word Documents (*.docx);;All files (*.*)"
        )
        
        if not file_path:
            return
        
        # Конвертація даних для AlbumCreator
        images_data = self.convert_to_album_format()
        
        # Ініціалізація AlbumCreator
        if not self.album_creator:
            try:
                self.album_creator = AlbumCreator()
            except ImportError:
                QMessageBox.critical(
                    self,
                    self.translator.tr(TranslationKeys.ERROR),
                    self.translator.tr(TranslationKeys.DOCX_NOT_AVAILABLE)
                )
                return
        
        # Підключення сигналів прогресу
        self.album_creator.progress_updated.connect(self.update_album_progress)
        self.album_creator.error_occurred.connect(self.on_album_error)
        
        # Показ прогрес-бару
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Запуск створення в окремому потоці
        self.processing_thread = ProcessingThread(
            self.album_creator, images_data, title_data, file_path
        )
        self.processing_thread.progress.connect(self.update_album_progress)
        self.processing_thread.finished.connect(self.on_album_finished)
        self.processing_thread.start()
        
        # Блокування UI під час обробки
        self.setEnabled(False)
        self.status_message.setText("Створення альбому...")
        
        print(f"Розпочато створення альбому: {len(images_data)} зображень")
    
    def get_album_title_data(self) -> Optional[TitlePageData]:
        """Отримання даних для титульної сторінки альбому"""
        from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDateEdit, QComboBox, QDialogButtonBox
        from datetime import datetime
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Налаштування альбому")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QFormLayout(dialog)
        
        # Дата документу
        date_edit = QDateEdit()
        date_edit.setDate(datetime.now().date())
        date_edit.setCalendarPopup(True)
        layout.addRow("Дата документу:", date_edit)
        
        # Інформація про підрозділ
        unit_edit = QLineEdit()
        unit_edit.setPlaceholderText("Наприклад: 1-й батальйон, 2-га рота")
        layout.addRow("Підрозділ:", unit_edit)
        
        # Командир
        commander_rank_edit = QLineEdit()
        commander_rank_edit.setPlaceholderText("капітан")
        layout.addRow("Звання командира:", commander_rank_edit)
        
        commander_name_edit = QLineEdit()
        commander_name_edit.setPlaceholderText("Іванов І.І.")
        layout.addRow("Ім'я командира:", commander_name_edit)
        
        # Начальник штабу
        chief_rank_edit = QLineEdit()
        chief_rank_edit.setPlaceholderText("старший лейтенант")
        layout.addRow("Звання нач. штабу:", chief_rank_edit)
        
        chief_name_edit = QLineEdit()
        chief_name_edit.setPlaceholderText("Петров П.П.")
        layout.addRow("Ім'я нач. штабу:", chief_name_edit)
        
        # Шаблон
        template_combo = QComboBox()
        if self.album_creator:
            templates = self.album_creator.get_available_templates()
            for name, description in templates.items():
                template_combo.addItem(f"{description}", name)
        layout.addRow("Шаблон:", template_combo)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            return TitlePageData(
                document_date=date_edit.date().toString('dd.MM.yyyy'),
                unit_info=unit_edit.text() or "Не вказано",
                commander_rank=commander_rank_edit.text() or "",
                commander_name=commander_name_edit.text() or "",
                chief_of_staff_rank=chief_rank_edit.text() or "",
                chief_of_staff_name=chief_name_edit.text() or "",
                template_name=template_combo.currentData() or "default"
            )
        
        return None
    
    def convert_to_album_format(self) -> List[ImageData]:
        """Конвертація внутрішніх даних в формат для AlbumCreator"""
        album_images = []
        
        for i, img_data in enumerate(self.processed_images):
            try:
                image_info = img_data.get('image_info', {})
                grid_settings = img_data.get('grid_settings', {})
                analysis_point = img_data.get('analysis_point', {})
                
                # Створення обробленого зображення
                temp_processor = ImageProcessor(img_data['image_path'])
                temp_processor.load_grid_settings(grid_settings)
                temp_processor.process_click(analysis_point['x'], analysis_point['y'])
                
                processed_image = temp_processor.create_processed_image()
                
                # Збереження обробленого зображення
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                processed_image.save(temp_file.name, 'JPEG')
                temp_file.close()
                
                # Створення ImageData
                album_image = ImageData(
                    filename=image_info.get('filename', f'image_{i+1:02d}.jpg'),
                    image_path=img_data['image_path'],
                    processed_image_path=temp_file.name,
                    target_number=f"Ціль-{i+1:02d}",
                    azimuth=analysis_point.get('azimuth', 0.0),
                    range_km=analysis_point.get('range_value', 0.0),
                    height="150м",  # За замовчуванням
                    obstacles="без перешкод",
                    detection="Виявлення",
                    timestamp=datetime.now()
                )
                
                album_images.append(album_image)
                
            except Exception as e:
                print(f"Помилка конвертації зображення {i}: {e}")
                continue
        
        return album_images
    
    def update_album_progress(self, progress: int, message: str):
        """Оновлення прогресу створення альбому"""
        self.progress_bar.setValue(progress)
        self.status_message.setText(message)
    
    def on_album_error(self, error_message: str):
        """Обробка помилки створення альбому"""
        print(f"Помилка альбому: {error_message}")
    
    def on_album_finished(self, success: bool, result: str):
        """Завершення створення альбому"""
        # Відновлення UI
        self.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_message.setText(f"Альбом створено: {os.path.basename(result)}")
            
            # Пропозиція відкрити файл
            reply = QMessageBox.question(
                self,
                "Альбом створено",
                f"Альбом успішно створено:\n{result}\n\nВідкрити файл?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.open_file(result)
        else:
            self.status_message.setText("Помилка створення альбому")
            QMessageBox.critical(
                self,
                self.translator.tr(TranslationKeys.ERROR),
                f"Помилка створення альбому:\n{result}"
            )
        
        # Очищення потоку
        if self.processing_thread:
            self.processing_thread.deleteLater()
            self.processing_thread = None
    
    def open_file(self, file_path: str):
        """Відкриття файлу системним додатком"""
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            print(f"Не вдалося відкрити файл: {e}")
    
    # ===============================
    # СИСТЕМА ПЕРЕКЛАДІВ
    # ===============================
    
    def change_language(self, language: Language):
        """Зміна мови інтерфейсу"""
        self.translator.set_language(language)
        
        # Збереження в налаштуваннях
        self.settings.setValue('language', language.value)
        
        # Оновлення стану кнопок мови
        if hasattr(self, 'ukrainian_action'):
            self.ukrainian_action.setChecked(language == Language.UKRAINIAN)
        if hasattr(self, 'english_action'):
            self.english_action.setChecked(language == Language.ENGLISH)
    
    def update_translations(self):
        """Оновлення всіх перекладів інтерфейсу"""
        # Заголовок вікна
        self.setWindowTitle(self.translator.tr(TranslationKeys.WINDOW_TITLE))
        
        # Статус-бар
        if not self.image_processor:
            self.status_message.setText("Готовий")
        
        print(f"Переклади оновлено для мови: {self.translator.get_current_language().value}")
    
    # ===============================
    # НАЛАШТУВАННЯ
    # ===============================
    
    def _load_settings(self):
        """Завантаження налаштувань програми"""
        # Розміри та позиція вікна
        geometry = self.settings.value('geometry')
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value('windowState')
        if state:
            self.restoreState(state)
        
        # Мова
        language_code = self.settings.value('language', 'uk')
        for lang in Language:
            if lang.value == language_code:
                self.translator.set_language(lang)
                break
        
        # Стан панелей
        thumbnails_visible = self.settings.value('thumbnails_visible', True, type=bool)
        if hasattr(self, 'toggle_thumbnails_action'):
            self.toggle_thumbnails_action.setChecked(thumbnails_visible)
        
        if self.thumbnail_browser:
            self.thumbnail_browser.setVisible(thumbnails_visible)
        
        # Пропорції розділювача
        splitter_sizes = self.settings.value('splitter_sizes')
        if splitter_sizes and hasattr(self, 'main_splitter'):
            self.main_splitter.restoreState(splitter_sizes)
        
        print("Налаштування завантажено")
    
    def _save_settings(self):
        """Збереження налаштувань програми"""
        # Розміри та позиція вікна
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('windowState', self.saveState())
        
        # Мова
        self.settings.setValue('language', self.translator.get_current_language().value)
        
        # Стан панелей
        if self.thumbnail_browser:
            self.settings.setValue('thumbnails_visible', self.thumbnail_browser.isVisible())
        
        # Пропорції розділювача
        if hasattr(self, 'main_splitter'):
            self.settings.setValue('splitter_sizes', self.main_splitter.saveState())
        
        print("Налаштування збережено")
    
    # ===============================
    # ОНОВЛЕННЯ СТАНУ UI
    # ===============================
    
    def _update_ui_state(self):
        """Оновлення стану елементів UI"""
        has_image = self.image_processor is not None
        has_analysis = has_image and self.image_processor.has_analysis()
        has_processed = len(self.processed_images) > 0
        
        # Кнопки меню
        if hasattr(self, 'save_image_action'):
            self.save_image_action.setEnabled(has_analysis)
        
        if hasattr(self, 'create_album_action'):
            self.create_album_action.setEnabled(has_processed)
        
        # Режими сітки
        grid_modes_enabled = has_image
        if hasattr(self, 'center_mode_action'):
            self.center_mode_action.setEnabled(grid_modes_enabled)
        if hasattr(self, 'scale_mode_action'):
            self.scale_mode_action.setEnabled(grid_modes_enabled)
        if hasattr(self, 'normal_mode_action'):
            self.normal_mode_action.setEnabled(grid_modes_enabled)
        
        # Панель інструментів
        if hasattr(self, 'center_toolbar_btn'):
            self.center_toolbar_btn.setEnabled(grid_modes_enabled)
        if hasattr(self, 'scale_toolbar_btn'):
            self.scale_toolbar_btn.setEnabled(grid_modes_enabled)
        
        # Статус зображення
        if has_image:
            info = self.image_processor.get_image_info()
            self.image_status.setText(f"{info.get('width', 0)}×{info.get('height', 0)}")
        else:
            self.image_status.setText("—")
    
    # ===============================
    # ДОДАТКОВІ ФУНКЦІЇ
    # ===============================
    
    def show_about(self):
        """Показ діалогу 'Про програму'"""
        QMessageBox.about(
            self,
            "Про PhotoControl",
            """<h3>PhotoControl v2.0</h3>
            <p>Професійна програма для обробки зображень з азимутальною сіткою</p>
            <p><b>Функціональність:</b></p>
            <ul>
            <li>Аналіз азимуту та дальності цілей</li>
            <li>Пакетна обробка зображень</li>
            <li>Створення Word альбомів</li>
            <li>Підтримка української та англійської мов</li>
            </ul>
            <p><b>Версія:</b> 2.0.0</p>
            <p><b>Підтримка:</b> Україна 🇺🇦</p>
            """
        )
    
    def keyPressEvent(self, event):
        """Обробка клавіатурних скорочень"""
        # Навігація по зображеннях
        if event.key() == Qt.Key_Left:
            if self.thumbnail_browser:
                self.thumbnail_browser.select_previous_image()
        elif event.key() == Qt.Key_Right:
            if self.thumbnail_browser:
                self.thumbnail_browser.select_next_image()
        elif event.key() == Qt.Key_Escape:
            # Повернення до звичайного режиму
            self.set_grid_mode("normal")
        else:
            # Передача до батьківського класу
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Обробка закриття програми"""
        # Збереження налаштувань
        self._save_settings()
        
        # Зупинка потоків
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.quit()
            self.processing_thread.wait(3000)  # Максимум 3 секунди
        
        # Очищення тимчасових файлів
        if self.album_creator:
            self.album_creator.cleanup_temp_files()
        
        print("MainWindow закрито")
        event.accept()


if __name__ == "__main__":
    # Запуск програми
    app = QApplication(sys.argv)
    
    # Налаштування програми
    app.setApplicationName("PhotoControl")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("PhotoControl Team")
    
    # Створення головного вікна
    window = MainWindow()
    window.show()
    
    print("PhotoControl v2.0 запущено")
    sys.exit(app.exec_())