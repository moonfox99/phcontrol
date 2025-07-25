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
    Оновлене головне вікно PhotoControl v2.0
    
    Функціональність:
    - Повна інтеграція всіх панелей (управління, зображення, даних, мініатюр)
    - Меню з файловими операціями та налаштуваннями
    - Пакетна обробка зображень
    - Створення Word альбомів
    - Система перекладів з автоматичним оновленням
    - Збереження налаштувань між сесіями
    - Клавіатурні скорочення
    - Повна підтримка legacy функціоналу
    """
    
    def __init__(self):
        super().__init__()
        
        # Основні компоненти
        self.image_processor: Optional[ImageProcessor] = None
        self.album_creator: Optional[AlbumCreator] = None
        self.processing_thread: Optional[ProcessingThread] = None
        
        # UI компоненти
        self.control_panel: Optional[ControlPanel] = None
        self.data_panel: Optional[DataPanel] = None
        self.image_panel: Optional[ImagePanel] = None
        self.thumbnail_browser: Optional[ThumbnailBrowser] = None
        
        # Система перекладів
        self.translator = get_translator()
        
        # Дані для обробки
        self.processed_images: List[ImageData] = []
        self.current_image_path: Optional[str] = None
        
        # Налаштування
        self.settings = QSettings("PhotoControl", "v2.0")
        
        # Ініціалізація UI
        self._init_ui()
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._setup_connections()
        self._load_settings()
        
        # Оновлення перекладів
        self.translator.language_changed.connect(self._update_translations)
        self._update_translations()
        
        print("MainWindow v2.0 створено з повною інтеграцією панелей")
    
    def _init_ui(self):
        """Ініціалізація інтерфейсу"""
        # Основні параметри вікна
        self.setWindowTitle("PhotoControl v2.0")
        self.setGeometry(100, 100, UI.DEFAULT_WINDOW_WIDTH, UI.DEFAULT_WINDOW_HEIGHT)
        self.setMinimumSize(UI.MIN_WINDOW_WIDTH, UI.MIN_WINDOW_HEIGHT)
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основний splitter (горизонтальний)
        main_splitter = QSplitter(Qt.Horizontal)
        
        # === ЛІВА ПАНЕЛЬ УПРАВЛІННЯ ===
        self.control_panel = ControlPanel()
        main_splitter.addWidget(self.control_panel)
        
        # === ЦЕНТРАЛЬНА ОБЛАСТЬ ===
        center_splitter = QSplitter(Qt.Horizontal)
        
        # Браузер мініатюр (вертикальний, ліворуч від зображення)
        self.thumbnail_browser = ThumbnailBrowser(width=UI.THUMBNAIL_PANEL_WIDTH)
        center_splitter.addWidget(self.thumbnail_browser)
        
        # Панель зображення (центр)
        self.image_panel = ImagePanel()
        center_splitter.addWidget(self.image_panel)
        
        # Налаштування пропорцій центральної області
        center_splitter.setSizes([UI.THUMBNAIL_PANEL_WIDTH, 600])
        center_splitter.setCollapsible(0, True)  # Мініатюри можна згорнути
        center_splitter.setCollapsible(1, False)  # Панель зображення завжди видима
        
        main_splitter.addWidget(center_splitter)
        
        # === ПРАВА ПАНЕЛЬ ДАНИХ ===
        self.data_panel = DataPanel()
        main_splitter.addWidget(self.data_panel)
        
        # Налаштування основних пропорцій
        main_splitter.setSizes([
            UI.CONTROL_PANEL_WIDTH,
            UI.DEFAULT_WINDOW_WIDTH - UI.CONTROL_PANEL_WIDTH - UI.DATA_PANEL_WIDTH,
            UI.DATA_PANEL_WIDTH
        ])
        main_splitter.setCollapsible(0, False)  # Ліва панель завжди видима
        main_splitter.setCollapsible(1, False)  # Центр завжди видимий
        main_splitter.setCollapsible(2, True)   # Праву панель можна згорнути
        
        # Layout
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)
        
        self.main_splitter = main_splitter
        self.center_splitter = center_splitter
    
    def _create_menu_bar(self):
        """Створення меню"""
        menubar = self.menuBar()
        
        # === МЕНЮ ФАЙЛ ===
        file_menu = menubar.addMenu("&Файл")
        
        # Відкрити зображення
        self.open_image_action = QAction("&Відкрити зображення", self)
        self.open_image_action.setShortcut(QKeySequence.Open)
        self.open_image_action.triggered.connect(self.open_image)
        file_menu.addAction(self.open_image_action)
        
        # Відкрити папку
        self.open_folder_action = QAction("Відкрити &папку", self)
        self.open_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        self.open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(self.open_folder_action)
        
        file_menu.addSeparator()
        
        # Зберегти зображення
        self.save_image_action = QAction("&Зберегти зображення", self)
        self.save_image_action.setShortcut(QKeySequence.Save)
        self.save_image_action.setEnabled(False)
        self.save_image_action.triggered.connect(self.save_current_image)
        file_menu.addAction(self.save_image_action)
        
        # Створити альбом
        self.create_album_action = QAction("Створити &альбом", self)
        self.create_album_action.setShortcut(QKeySequence("Ctrl+E"))
        self.create_album_action.setEnabled(False)
        self.create_album_action.triggered.connect(self.create_album)
        file_menu.addAction(self.create_album_action)
        
        file_menu.addSeparator()
        
        # Вихід
        exit_action = QAction("&Вихід", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # === МЕНЮ ВИГЛЯД ===
        view_menu = menubar.addMenu("&Вигляд")
        
        # Показати/приховати мініатюри
        self.toggle_thumbnails_action = QAction("Показати &мініатюри", self)
        self.toggle_thumbnails_action.setCheckable(True)
        self.toggle_thumbnails_action.setChecked(True)
        self.toggle_thumbnails_action.triggered.connect(self.toggle_thumbnails)
        view_menu.addAction(self.toggle_thumbnails_action)
        
        # Показати/приховати праву панель
        self.toggle_data_panel_action = QAction("Показати панель &даних", self)
        self.toggle_data_panel_action.setCheckable(True)
        self.toggle_data_panel_action.setChecked(True)
        self.toggle_data_panel_action.triggered.connect(self.toggle_data_panel)
        view_menu.addAction(self.toggle_data_panel_action)
        
        view_menu.addSeparator()
        
        # Зум
        self.show_zoom_action = QAction("Показати &зум", self)
        self.show_zoom_action.triggered.connect(self.show_zoom)
        view_menu.addAction(self.show_zoom_action)
        
        self.hide_zoom_action = QAction("Приховати з&ум", self)
        self.hide_zoom_action.triggered.connect(self.hide_zoom)
        view_menu.addAction(self.hide_zoom_action)
        
        # === МЕНЮ РЕЖИМИ ===
        modes_menu = menubar.addMenu("&Режими")
        
        # Група режимів (radio buttons)
        self.mode_group = QActionGroup(self)
        
        self.normal_mode_action = QAction("&Звичайний режим", self)
        self.normal_mode_action.setCheckable(True)
        self.normal_mode_action.setChecked(True)
        self.normal_mode_action.triggered.connect(lambda: self.set_grid_mode("normal"))
        self.mode_group.addAction(self.normal_mode_action)
        modes_menu.addAction(self.normal_mode_action)
        
        self.center_mode_action = QAction("Режим встановлення &центру", self)
        self.center_mode_action.setCheckable(True)
        self.center_mode_action.setShortcut(QKeySequence("C"))
        self.center_mode_action.triggered.connect(lambda: self.set_grid_mode("center_setting"))
        self.mode_group.addAction(self.center_mode_action)
        modes_menu.addAction(self.center_mode_action)
        
        self.scale_mode_action = QAction("Режим встановлення &масштабу", self)
        self.scale_mode_action.setCheckable(True)
        self.scale_mode_action.setShortcut(QKeySequence("S"))
        self.scale_mode_action.triggered.connect(lambda: self.set_grid_mode("scale_setting"))
        self.mode_group.addAction(self.scale_mode_action)
        modes_menu.addAction(self.scale_mode_action)
        
        # === МЕНЮ НАЛАШТУВАННЯ ===
        settings_menu = menubar.addMenu("&Налаштування")
        
        # Мова
        language_menu = settings_menu.addMenu("&Мова")
        self.language_group = QActionGroup(self)
        
        for language in Language:
            action = QAction(self.translator.get_language_name(language), self)
            action.setCheckable(True)
            action.setData(language)
            action.triggered.connect(lambda checked, lang=language: self.set_language(lang))
            self.language_group.addAction(action)
            language_menu.addAction(action)
            
            # Встановити поточну мову
            if language == self.translator.get_current_language():
                action.setChecked(True)
        
        settings_menu.addSeparator()
        
        # Документація
        self.documentation_action = QAction("&Документація", self)
        self.documentation_action.setShortcut(QKeySequence.HelpContents)
        self.documentation_action.triggered.connect(self.show_documentation)
        settings_menu.addAction(self.documentation_action)
        
        # Про програму
        self.about_action = QAction("&Про програму", self)
        self.about_action.triggered.connect(self.show_about)
        settings_menu.addAction(self.about_action)
    
    def _create_tool_bar(self):
        """Створення панелі інструментів"""
        toolbar = self.addToolBar("Головна панель")
        toolbar.setMovable(False)
        
        # Кнопки файлових операцій
        toolbar.addAction(self.open_image_action)
        toolbar.addAction(self.open_folder_action)
        toolbar.addSeparator()
        
        # Кнопки режимів
        self.center_toolbar_btn = toolbar.addAction("🎯 Центр")
        self.center_toolbar_btn.triggered.connect(lambda: self.set_grid_mode("center_setting"))
        
        self.scale_toolbar_btn = toolbar.addAction("📏 Масштаб")
        self.scale_toolbar_btn.triggered.connect(lambda: self.set_grid_mode("scale_setting"))
        
        toolbar.addSeparator()
        
        # Кнопки збереження та створення
        toolbar.addAction(self.save_image_action)
        toolbar.addAction(self.create_album_action)
    
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
        
        # Поточний режим
        self.mode_status = QLabel("Звичайний режим")
        status_bar.addPermanentWidget(self.mode_status)
    
    def _setup_connections(self):
        """Налаштування з'єднань сигналів"""
        # === ЛІВА ПАНЕЛЬ УПРАВЛІННЯ ===
        if self.control_panel:
            self.control_panel.open_image_requested.connect(self.open_image)
            self.control_panel.open_folder_requested.connect(self.open_folder)
            self.control_panel.save_image_requested.connect(self.save_current_image)
            self.control_panel.create_album_requested.connect(self.create_album)
            self.control_panel.save_current_data_requested.connect(self.save_current_image_data)
            self.control_panel.language_changed.connect(self.set_language)
        
        # === ПРАВА ПАНЕЛЬ ДАНИХ ===
        if self.data_panel:
            self.data_panel.target_data_changed.connect(self.on_target_data_changed)
            self.data_panel.grid_scale_changed.connect(self.on_grid_scale_changed)
            self.data_panel.set_center_mode_requested.connect(lambda: self.set_grid_mode("center_setting"))
            self.data_panel.set_scale_mode_requested.connect(lambda: self.set_grid_mode("scale_setting"))
        
        # === ПАНЕЛЬ ЗОБРАЖЕННЯ ===
        if self.image_panel:
            self.image_panel.image_clicked.connect(self.on_image_clicked)
            self.image_panel.analysis_point_changed.connect(self.on_analysis_point_changed)
            self.image_panel.grid_center_changed.connect(self.on_grid_center_changed)
            self.image_panel.scale_edge_set.connect(self.on_scale_edge_set)
            self.image_panel.mode_changed.connect(self.on_mode_changed)
        
        # === БРАУЗЕР МІНІАТЮР ===
        if self.thumbnail_browser:
            self.thumbnail_browser.image_selected.connect(self.on_thumbnail_selected)
            self.thumbnail_browser.processing_status_changed.connect(self.on_processing_status_changed)
    
    def _load_settings(self):
        """Завантаження налаштувань"""
        # Розміри вікна
        geometry = self.settings.value('geometry')
        if geometry:
            self.restoreGeometry(geometry)
        
        # Стан splitter'ів
        if hasattr(self, 'main_splitter'):
            splitter_state = self.settings.value('main_splitter')
            if splitter_state:
                self.main_splitter.restoreState(splitter_state)
        
        if hasattr(self, 'center_splitter'):
            center_state = self.settings.value('center_splitter')
            if center_state:
                self.center_splitter.restoreState(center_state)
        
        # Видимість панелей
        thumbnails_visible = self.settings.value('thumbnails_visible', True, type=bool)
        self.thumbnail_browser.setVisible(thumbnails_visible)
        self.toggle_thumbnails_action.setChecked(thumbnails_visible)
        
        data_panel_visible = self.settings.value('data_panel_visible', True, type=bool)
        self.data_panel.setVisible(data_panel_visible)
        self.toggle_data_panel_action.setChecked(data_panel_visible)
        
        print("Налаштування завантажено")
    
    def _save_settings(self):
        """Збереження налаштувань"""
        # Розміри та позиція вікна
        self.settings.setValue('geometry', self.saveGeometry())
        
        # Стан splitter'ів
        if hasattr(self, 'main_splitter'):
            self.settings.setValue('main_splitter', self.main_splitter.saveState())
        
        if hasattr(self, 'center_splitter'):
            self.settings.setValue('center_splitter', self.center_splitter.saveState())
        
        # Видимість панелей
        self.settings.setValue('thumbnails_visible', self.thumbnail_browser.isVisible())
        self.settings.setValue('data_panel_visible', self.data_panel.isVisible())
        
        print("Налаштування збережено")
    
    # ===============================
    # ФАЙЛОВІ ОПЕРАЦІЇ
    # ===============================
    
    def open_image(self):
        """Відкриття одного зображення"""
        tr = self.translator.tr
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr(TranslationKeys.SELECT_IMAGE),
            "",
            f"{tr(TranslationKeys.IMAGE_FILES)} (*.jpg *.jpeg *.png *.bmp *.gif *.tiff);;{tr(TranslationKeys.ALL_FILES)} (*.*)"
        )
        
        if file_path:
            self.load_single_image(file_path)
    
    def open_folder(self):
        """Відкриття папки з зображеннями"""
        tr = self.translator.tr
        
        folder_path = QFileDialog.getExistingDirectory(
            self,
            tr(TranslationKeys.SELECT_FOLDER)
        )
        
        if folder_path:
            self.load_folder_images(folder_path)
    
    def save_current_image(self):
        """Збереження поточного обробленого зображення"""
        if not self.image_processor or not self.image_processor.has_analysis():
            QMessageBox.warning(
                self,
                self.translator.tr(TranslationKeys.WARNING),
                self.translator.tr(TranslationKeys.NO_ANALYSIS_POINT)
            )
            return
        
        tr = self.translator.tr
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr(TranslationKeys.SAVE_PROCESSED_IMAGE),
            "",
            f"{tr(TranslationKeys.JPEG_FILES)} (*.jpg);;{tr(TranslationKeys.PNG_FILES)} (*.png)"
        )
        
        if file_path:
            try:
                processed_image = self.image_processor.get_processed_image()
                if processed_image:
                    processed_image.save(file_path)
                    self.status_message.setText(tr(TranslationKeys.IMAGE_SAVED_SUCCESSFULLY))
                    self.control_panel.add_result(f"Зображення збережено: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    tr(TranslationKeys.ERROR),
                    tr(TranslationKeys.COULD_NOT_SAVE, error=str(e))
                )
    
    def create_album(self):
        """Створення Word альбому"""
        if not self.processed_images:
            QMessageBox.warning(
                self,
                self.translator.tr(TranslationKeys.WARNING),
                "Немає оброблених зображень для створення альбому"
            )
            return
        
        # Отримання даних титульної сторінки
        title_data = TitlePageData(
            document_date=self.control_panel.get_document_date(),
            unit_info="",  # Можна додати поле в control_panel
            commander_rank="",
            commander_name="",
            chief_of_staff_rank="",
            chief_of_staff_name=""
        )
        
        # Діалог збереження
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Створити альбом",
            "",
            "Word документи (*.docx)"
        )
        
        if file_path:
            self._create_album_async(self.processed_images, title_data, file_path)
    
    def save_current_image_data(self):
        """Збереження даних поточного зображення для альбому"""
        if not self.image_processor or not self.image_processor.has_analysis():
            QMessageBox.warning(
                self,
                self.translator.tr(TranslationKeys.WARNING),
                self.translator.tr(TranslationKeys.NO_ANALYSIS_POINT)
            )
            return
        
        if not self.current_image_path:
            QMessageBox.warning(
                self,
                self.translator.tr(TranslationKeys.WARNING),
                self.translator.tr(TranslationKeys.NO_IMAGE_FIRST)
            )
            return
        
        # Отримання даних з панелей
        target_data = self.data_panel.get_target_data()
        analysis_point = self.image_processor.get_analysis_point()
        
        if not analysis_point:
            return
        
        # Створення ImageData
        image_data = ImageData(
            filename=os.path.basename(self.current_image_path),
            image_path=self.current_image_path,
            processed_image_path=self.current_image_path,  # Буде оновлено при збереженні
            target_number=target_data.get("target_number", ""),
            azimuth=analysis_point.azimuth,
            range_km=analysis_point.range_km,
            height=target_data.get("height", ""),
            obstacles=target_data.get("obstacles", "no_obstacles"),
            detection=target_data.get("detection", "detection"),
            timestamp=None  # Буде встановлено автоматично
        )
        
        # Перевірка чи вже існує запис для цього зображення
        existing_index = -1
        for i, existing_data in enumerate(self.processed_images):
            if existing_data.image_path == self.current_image_path:
                existing_index = i
                break
        
        if existing_index >= 0:
            # Оновлення існуючого запису
            self.processed_images[existing_index] = image_data
            self.control_panel.add_result(f"Оновлено дані: {image_data.filename}")
        else:
            # Додавання нового запису
            self.processed_images.append(image_data)
            self.control_panel.add_result(f"Додано до альбому: {image_data.filename}")
        
        # Оновлення статусу обробки в браузері мініатюр
        if self.thumbnail_browser:
            self.thumbnail_browser.mark_image_as_processed(self.current_image_path)
        
        # Оновлення лічильника
        self.processed_counter.setText(f"Оброблено: {len(self.processed_images)}")
        
        # Оновлення стану UI
        self._update_ui_state()
    
    # ===============================
    # ЗАВАНТАЖЕННЯ ЗОБРАЖЕНЬ
    # ===============================
    
    def load_single_image(self, image_path: str):
        """Завантаження одного зображення"""
        try:
            # Створення процесора зображення
            self.image_processor = ImageProcessor()
            self.image_processor.load_image(image_path)
            
            # Встановлення зображення в панель
            if self.image_panel:
                self.image_panel.set_image_processor(self.image_processor)
            
            # Оновлення поточного шляху
            self.current_image_path = image_path
            
            # Очищення попередніх даних
            if self.data_panel:
                self.data_panel.clear_all_data()
            
            # Оновлення статусу
            filename = os.path.basename(image_path)
            self.status_message.setText(f"Відкрито: {filename}")
            self.control_panel.add_result(f"Завантажено зображення: {filename}")
            
            # Оновлення стану UI
            self._update_ui_state()
            
            print(f"Зображення завантажено: {filename}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.translator.tr(TranslationKeys.ERROR),
                self.translator.tr(TranslationKeys.COULD_NOT_LOAD, error=str(e))
            )
    
    def load_folder_images(self, folder_path: str):
        """Завантаження папки з зображеннями"""
        try:
            # Пошук зображень в папці
            image_paths = get_images_in_directory(folder_path)
            
            if not image_paths:
                QMessageBox.information(
                    self,
                    self.translator.tr(TranslationKeys.WARNING),
                    self.translator.tr(TranslationKeys.NO_IMAGES_FOUND)
                )
                return
            
            # Завантаження в браузер мініатюр
            if self.thumbnail_browser:
                self.thumbnail_browser.load_images(image_paths)
                
                # Показати браузер мініатюр якщо був прихований
                if not self.thumbnail_browser.isVisible():
                    self.thumbnail_browser.setVisible(True)
                    self.toggle_thumbnails_action.setChecked(True)
                
                # Автоматично вибрати перше зображення
                if image_paths:
                    self.load_single_image(image_paths[0])
            
            # Оновлення статусу
            folder_name = os.path.basename(folder_path)
            self.status_message.setText(
                self.translator.tr(TranslationKeys.FOUND_IMAGES, count=len(image_paths))
            )
            self.control_panel.add_result(f"Завантажено папку: {folder_name} ({len(image_paths)} зображень)")
            
            print(f"Папка завантажена: {folder_name}, знайдено {len(image_paths)} зображень")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.translator.tr(TranslationKeys.ERROR),
                f"Помилка завантаження папки: {str(e)}"
            )
    
    # ===============================
    # ОБРОБНИКИ ПОДІЙ ПАНЕЛЕЙ
    # ===============================
    
    def on_thumbnail_selected(self, image_path: str):
        """Обробка вибору мініатюри"""
        self.load_single_image(image_path)
    
    def on_processing_status_changed(self, image_path: str, is_processed: bool):
        """Обробка зміни статусу обробки зображення"""
        status = "оброблено" if is_processed else "скасовано"
        filename = os.path.basename(image_path)
        self.control_panel.add_result(f"Статус обробки - {filename}: {status}")
        
        # Оновлення лічильника
        if self.thumbnail_browser:
            processed_count = len(self.thumbnail_browser.get_processed_images())
            self.processed_counter.setText(f"Оброблено: {processed_count}")
    
    def on_image_clicked(self, x: int, y: int):
        """Обробка кліку по зображенню"""
        if self.image_processor:
            self.image_processor.set_analysis_point(x, y)
            
            # Оновлення відображення в панелі даних
            analysis_point = self.image_processor.get_analysis_point()
            if analysis_point and self.data_panel:
                self.data_panel.update_analysis_point(analysis_point.azimuth, analysis_point.range_km)
            
            self.control_panel.add_result(f"Точка аналізу встановлена: ({x}, {y})")
    
    def on_analysis_point_changed(self, analysis_point: AnalysisPoint):
        """Обробка зміни точки аналізу"""
        if self.data_panel:
            self.data_panel.update_analysis_point(analysis_point.azimuth, analysis_point.range_km)
        
        self.control_panel.add_result(
            f"Аналіз: азимут {analysis_point.azimuth:.1f}°, дальність {analysis_point.range_km:.2f} км"
        )
    
    def on_grid_center_changed(self, x: int, y: int):
        """Обробка зміни центру сітки"""
        if self.data_panel:
            self.data_panel.update_grid_center(x, y)
        
        self.control_panel.add_result(f"Центр сітки: ({x}, {y})")
    
    def on_scale_edge_set(self, distance: float):
        """Обробка встановлення краю масштабу"""
        self.control_panel.add_result(f"Край масштабу встановлено: {distance}")
    
    def on_mode_changed(self, mode: str):
        """Обробка зміни режиму"""
        if self.data_panel:
            self.data_panel.set_current_mode(mode)
        
        # Оновлення статус-бару
        mode_names = {
            "normal": "Звичайний режим",
            "center_setting": "Встановлення центру",
            "scale_setting": "Встановлення масштабу",
            "analysis": "Аналіз точки"
        }
        self.mode_status.setText(mode_names.get(mode, mode))
        
        # Оновлення меню
        if mode == "center_setting":
            self.center_mode_action.setChecked(True)
        elif mode == "scale_setting":
            self.scale_mode_action.setChecked(True)
        else:
            self.normal_mode_action.setChecked(True)
    
    def on_target_data_changed(self, data: Dict[str, Any]):
        """Обробка зміни даних про ціль"""
        self.control_panel.add_result(f"Дані цілі оновлено: {data.get('target_number', 'Без назви')}")
    
    def on_grid_scale_changed(self, scale: int):
        """Обробка зміни масштабу сітки"""
        if self.image_processor:
            self.image_processor.set_scale(scale)
        
        self.control_panel.add_result(f"Масштаб змінено: 1:{scale}")
    
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
    # УПРАВЛІННЯ ВИДИМІСТЮ ПАНЕЛЕЙ
    # ===============================
    
    def toggle_thumbnails(self):
        """Перемикання видимості мініатюр"""
        if self.thumbnail_browser:
            visible = self.thumbnail_browser.isVisible()
            self.thumbnail_browser.setVisible(not visible)
            
            # Оновлення тексту дії
            text = "Приховати мініатюри" if not visible else "Показати мініатюри"
            self.toggle_thumbnails_action.setText(text)
    
    def toggle_data_panel(self):
        """Перемикання видимості правої панелі даних"""
        if self.data_panel:
            visible = self.data_panel.isVisible()
            self.data_panel.setVisible(not visible)
            
            # Оновлення тексту дії
            text = "Приховати панель даних" if not visible else "Показати панель даних"
            self.toggle_data_panel_action.setText(text)
    
    def show_zoom(self):
        """Показати зум"""
        if self.image_panel:
            self.image_panel.show_zoom()
    
    def hide_zoom(self):
        """Приховати зум"""
        if self.image_panel:
            self.image_panel.hide_zoom()
    
    # ===============================
    # СИСТЕМА ПЕРЕКЛАДІВ
    # ===============================
    
    def set_language(self, language: Language):
        """Встановлення мови інтерфейсу"""
        self.translator.set_language(language)
        
        # Оновлення позначки в меню
        for action in self.language_group.actions():
            action.setChecked(action.data() == language)
    
    def _update_translations(self):
        """Оновлення перекладів інтерфейсу"""
        tr = self.translator.tr
        
        # Заголовок вікна
        self.setWindowTitle(tr(TranslationKeys.WINDOW_TITLE))
        
        # Меню
        self._update_menu_translations()
        
        # Статус-бар
        if hasattr(self, 'processed_counter'):
            processed_count = len(self.processed_images)
            self.processed_counter.setText(f"Оброблено: {processed_count}")
    
    def _update_menu_translations(self):
        """Оновлення перекладів меню"""
        tr = self.translator.tr
        
        # Оновлення дій меню
        if hasattr(self, 'open_image_action'):
            self.open_image_action.setText(tr(TranslationKeys.OPEN_IMAGE))
        if hasattr(self, 'open_folder_action'):
            self.open_folder_action.setText(tr(TranslationKeys.OPEN_FOLDER))
        if hasattr(self, 'save_image_action'):
            self.save_image_action.setText(tr(TranslationKeys.SAVE_CURRENT_IMAGE))
        if hasattr(self, 'create_album_action'):
            self.create_album_action.setText(tr(TranslationKeys.CREATE_NEW_ALBUM))
        
        # Режими
        if hasattr(self, 'normal_mode_action'):
            self.normal_mode_action.setText(tr(TranslationKeys.NORMAL_MODE))
        if hasattr(self, 'center_mode_action'):
            self.center_mode_action.setText(tr(TranslationKeys.CENTER_MODE))
        if hasattr(self, 'scale_mode_action'):
            self.scale_mode_action.setText(tr(TranslationKeys.SCALE_MODE))
    
    # ===============================
    # АСИНХРОННА ОБРОБКА
    # ===============================
    
    def _create_album_async(self, images_data: List[ImageData], title_data: TitlePageData, output_path: str):
        """Асинхронне створення альбому"""
        # Створення album_creator якщо не існує
        if not self.album_creator:
            self.album_creator = AlbumCreator()
        
        # Показ прогрес-бару
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Невизначений прогрес
        
        # Створення та запуск потоку
        self.processing_thread = ProcessingThread(
            self.album_creator, images_data, title_data, output_path
        )
        self.processing_thread.progress.connect(self._on_processing_progress)
        self.processing_thread.finished.connect(self._on_processing_finished)
        self.processing_thread.start()
        
        self.control_panel.add_result("Розпочато створення альбому...")
    
    def _on_processing_progress(self, value: int, message: str):
        """Обробка прогресу створення альбому"""
        self.progress_bar.setValue(value)
        self.status_message.setText(message)
    
    def _on_processing_finished(self, success: bool, result: str):
        """Обробка завершення створення альбому"""
        # Приховування прогрес-бару
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(
                self,
                self.translator.tr(TranslationKeys.SUCCESS),
                f"Альбом створено успішно:\n{result}"
            )
            self.control_panel.add_result(f"Альбом створено: {os.path.basename(result)}")
            self.status_message.setText("Альбом створено успішно")
        else:
            QMessageBox.critical(
                self,
                self.translator.tr(TranslationKeys.ERROR),
                f"Помилка створення альбому:\n{result}"
            )
            self.control_panel.add_result(f"Помилка створення альбому: {result}")
            self.status_message.setText("Помилка створення альбому")
        
        # Очищення потоку
        self.processing_thread = None
    
    # ===============================
    # ОНОВЛЕННЯ СТАНУ UI
    # ===============================
    
    def _update_ui_state(self):
        """Оновлення стану елементів UI"""
        has_image = self.image_processor is not None
        has_analysis = has_image and self.image_processor.has_analysis()
        has_processed = len(self.processed_images) > 0
        
        # Кнопки меню та панелі інструментів
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
        
        # Панель інструментів
        if hasattr(self, 'center_toolbar_btn'):
            self.center_toolbar_btn.setEnabled(grid_modes_enabled)
        if hasattr(self, 'scale_toolbar_btn'):
            self.scale_toolbar_btn.setEnabled(grid_modes_enabled)
        
        # Панель управління
        if self.control_panel:
            self.control_panel.set_buttons_enabled(
                save_image=has_analysis,
                create_album=has_processed,
                save_current=has_analysis
            )
        
        # Статус зображення
        if has_image:
            info = self.image_processor.get_image_info()
            self.image_status.setText(f"{info.get('width', 0)}×{info.get('height', 0)}")
        else:
            self.image_status.setText("—")
    
    # ===============================
    # ДОДАТКОВІ ФУНКЦІЇ
    # ===============================
    
    def show_documentation(self):
        """Показ документації"""
        try:
            # Тут можна додати відкриття HTML документації
            QMessageBox.information(
                self,
                "Документація",
                "Документація PhotoControl v2.0\n\nВ розробці..."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.translator.tr(TranslationKeys.ERROR),
                f"Помилка відкриття документації: {str(e)}"
            )
    
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
    
    # ===============================
    # КЛАВІАТУРНІ СКОРОЧЕННЯ
    # ===============================
    
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
        elif event.key() == Qt.Key_Space:
            # Збереження поточних даних
            if event.modifiers() == Qt.ControlModifier:
                self.save_current_image_data()
        else:
            # Передача до панелі зображення для управління сіткою
            if self.image_panel:
                self.image_panel.keyPressEvent(event)
            else:
                super().keyPressEvent(event)
    
    # ===============================
    # ЗАКРИТТЯ ПРОГРАМИ
    # ===============================
    
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
        
        print("MainWindow закрито з повним збереженням налаштувань")
        event.accept()


# ===============================
# ТЕСТУВАННЯ ГОЛОВНОГО ВІКНА
# ===============================

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    # Налаштування для високої роздільної здатності
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("PhotoControl")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("PhotoControl Team")
    
    # Створення головного вікна
    window = MainWindow()
    window.show()
    
    print("=== PhotoControl v2.0 ===")
    print("Повна інтеграція всіх панелей:")
    print("✅ Ліва панель управління (файли, пакетна обробка, результати)")
    print("✅ Центральна панель зображення (з азимутальною сіткою)")
    print("✅ Браузер мініатюр (вертикальний)")
    print("✅ Права панель даних (параметри цілі, сітки)")
    print("✅ Система перекладів (українська/англійська)")
    print("✅ Повне меню та панель інструментів")
    print("✅ Клавіатурні скорочення")
    print("✅ Збереження налаштувань")
    print("✅ Асинхронна обробка альбомів")
    
    sys.exit(app.exec_())#!/usr/bin/env python3
"""
PhotoControl v2.0 - Оновлене головне вікно
Повна інтеграція всіх панелей: управління, зображення, даних, мініатюр
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

# Наші створені панелі
from ui.panels.control_panel import ControlPanel
from ui.panels.data_panel import DataPanel
from ui.panels.image_panel import ImagePanel
from ui.widgets.thumbnail_browser import ThumbnailBrowser

# Основні компоненти
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