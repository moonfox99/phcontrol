#!/usr/bin/env python3
"""
Права панель даних цілі та налаштувань азимутальної сітки
Повна версія з інтеграцією в основну логіку програми
"""

from typing import Optional, Any, Dict
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QComboBox, QCheckBox, QDateEdit,
                             QFrame, QSizePolicy, QSpinBox, QDoubleSpinBox, 
                             QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QValidator, QDoubleValidator

from core.constants import UI, GRID, RADAR
from core.image_processor import AnalysisPoint


class TargetNumberValidator(QValidator):
    """Валідатор для номера цілі (4 цифри)"""
    def validate(self, text: str, pos: int):
        if len(text) == 0:
            return QValidator.Intermediate, text, pos
        if len(text) <= 4 and text.isdigit():
            return QValidator.Acceptable, text, pos
        return QValidator.Invalid, text, pos


class HeightValidator(QDoubleValidator):
    """Валідатор для висоти цілі"""
    def __init__(self):
        super().__init__(0.0, 99.9, 1)  # 0.0 - 99.9 км, 1 знак після коми


class DataPanel(QWidget):
    """
    Права панель для введення даних цілі та налаштувань сітки
    
    Функціональність:
    - Введення даних про ціль (номер, висота, перешкоди, статус)
    - Відображення розрахованих значень (азимут, дальність)
    - Налаштування азимутальної сітки (масштаб, центр, край)
    - Опис РЛС з можливістю включення/виключення
    - Інтеграція з основною логікою програми
    """
    
    # Сигнали для зв'язку з головним вікном
    target_data_changed = pyqtSignal(str, object)  # field_name, value
    scale_changed = pyqtSignal(int)
    center_mode_toggled = pyqtSignal(bool)
    scale_edge_mode_toggled = pyqtSignal(bool)
    radar_description_toggled = pyqtSignal(bool)
    add_to_album_requested = pyqtSignal()  # Запит додавання до альбому
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Стан даних цілі
        self.current_target_number = "0001"
        self.current_height = 0.0
        self.current_obstacles = "без перешкод"
        self.current_detection = "Виявлення"
        self.current_scale = 300
        
        # Поточні розраховані значення
        self.current_azimuth = 0.0
        self.current_range = 0.0
        
        # Стан режимів
        self.center_setting_mode = False
        self.scale_edge_mode = False
        self.radar_description_enabled = False
        
        # Дані РЛС
        self.radar_date = QDate.currentDate()
        self.radar_callsign = ""
        self.radar_name = ""
        self.radar_number = ""
        
        # Налаштування панелі
        self.setFixedWidth(UI.RIGHT_PANEL_WIDTH)
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                border-left: 1px solid #dee2e6;
            }
        """)
        
        self.init_ui()
        self.setup_connections()
        self.load_saved_values()
        
        print("✅ DataPanel ініціалізовано")
    
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.setLayout(layout)
        
        # Заголовок панелі
        self.create_title_section(layout)
        
        # Дані цілі
        self.create_target_data_section(layout)
        
        # Розділювач
        self.add_separator(layout)
        
        # Азимутальна сітка
        self.create_grid_section(layout)
        
        # Розділювач
        self.add_separator(layout)
        
        # Опис РЛС
        self.create_radar_section(layout)
        
        # Розділювач
        self.add_separator(layout)
        
        # Дії з даними
        self.create_actions_section(layout)
        
        # Розтягування внизу
        layout.addStretch()
    
    def create_title_section(self, layout: QVBoxLayout):
        """Створення заголовку панелі"""
        title_label = QLabel("Дані цілі")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                margin-bottom: 12px;
                color: #343a40;
                background: none;
                border: none;
            }
        """)
        layout.addWidget(title_label)
    
    def create_target_data_section(self, layout: QVBoxLayout):
        """Створення секції даних цілі"""
        # Група даних цілі
        target_group = QGroupBox("Параметри цілі")
        target_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #f9f9f9;
            }
        """)
        
        target_layout = QVBoxLayout()
        target_layout.setSpacing(10)
        target_group.setLayout(target_layout)
        
        # Номер цілі з валідацією
        target_number_container = QWidget()
        target_number_layout = QHBoxLayout()
        target_number_layout.setContentsMargins(0, 0, 0, 0)
        target_number_container.setLayout(target_number_layout)
        
        target_number_label = QLabel("№:")
        target_number_label.setFixedWidth(20)
        target_number_label.setStyleSheet("background: none; border: none; font-weight: 500;")
        target_number_layout.addWidget(target_number_label)
        
        self.target_number_input = QLineEdit()
        self.target_number_input.setText(self.current_target_number)
        self.target_number_input.setPlaceholderText("0001")
        self.target_number_input.setValidator(TargetNumberValidator())
        self.target_number_input.setMaxLength(4)
        self.target_number_input.setStyleSheet(self.get_input_style())
        target_number_layout.addWidget(self.target_number_input)
        
        target_layout.addWidget(target_number_container)
        
        # Автоматичні поля (азимут, дальність) - тільки для читання
        auto_fields_container = QFrame()
        auto_fields_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        auto_layout = QVBoxLayout()
        auto_layout.setContentsMargins(5, 5, 5, 5)
        auto_layout.setSpacing(5)
        auto_fields_container.setLayout(auto_layout)
        
        # Азимут
        self.auto_azimuth_label = QLabel("β = --°")
        self.auto_azimuth_label.setFont(QFont("Consolas", 11, QFont.Bold))
        self.auto_azimuth_label.setStyleSheet("color: #007bff; background: none; border: none;")
        auto_layout.addWidget(self.auto_azimuth_label)
        
        # Дальність
        self.auto_distance_label = QLabel("D = -- км")
        self.auto_distance_label.setFont(QFont("Consolas", 11, QFont.Bold))
        self.auto_distance_label.setStyleSheet("color: #007bff; background: none; border: none;")
        auto_layout.addWidget(self.auto_distance_label)
        
        target_layout.addWidget(auto_fields_container)
        
        # Висота (опціональна)
        height_container = QWidget()
        height_layout = QHBoxLayout()
        height_layout.setContentsMargins(0, 0, 0, 0)
        height_layout.setSpacing(6)
        height_container.setLayout(height_layout)
        
        height_label = QLabel("H =")
        height_label.setFixedWidth(25)
        height_label.setStyleSheet("background: none; border: none; font-weight: 500;")
        height_layout.addWidget(height_label)
        
        self.height_input = QLineEdit()
        self.height_input.setText(str(self.current_height))
        self.height_input.setPlaceholderText("0.0")
        self.height_input.setValidator(HeightValidator())
        self.height_input.setStyleSheet(self.get_input_style())
        height_layout.addWidget(self.height_input)
        
        height_unit_label = QLabel("км")
        height_unit_label.setStyleSheet("background: none; border: none; color: #6c757d;")
        height_layout.addWidget(height_unit_label)
        
        target_layout.addWidget(height_container)
        
        # Перешкоди
        obstacles_label = QLabel("Перешкоди:")
        obstacles_label.setStyleSheet("background: none; border: none; font-weight: 500; margin-top: 5px;")
        target_layout.addWidget(obstacles_label)
        
        self.obstacles_combo = QComboBox()
        self.obstacles_combo.addItems(["без перешкод", "з перешкодами"])
        self.obstacles_combo.setCurrentText(self.current_obstacles)
        self.obstacles_combo.setStyleSheet(self.get_combo_style())
        target_layout.addWidget(self.obstacles_combo)
        
        # Тип виявлення
        detection_label = QLabel("Статус:")
        detection_label.setStyleSheet("background: none; border: none; font-weight: 500; margin-top: 5px;")
        target_layout.addWidget(detection_label)
        
        self.detection_combo = QComboBox()
        self.detection_combo.addItems(["Виявлення", "Супров-ня", "Втрата"])
        self.detection_combo.setCurrentText(self.current_detection)
        self.detection_combo.setStyleSheet(self.get_combo_style())
        target_layout.addWidget(self.detection_combo)
        
        layout.addWidget(target_group)
    
    def create_grid_section(self, layout: QVBoxLayout):
        """Створення секції азимутальної сітки"""
        grid_group = QGroupBox("Азимутальна сітка")
        grid_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #f9f9f9;
            }
        """)
        
        grid_layout = QVBoxLayout()
        grid_layout.setSpacing(10)
        grid_group.setLayout(grid_layout)
        
        # Масштаб
        scale_container = QWidget()
        scale_layout = QHBoxLayout()
        scale_layout.setContentsMargins(0, 0, 0, 0)
        scale_layout.setSpacing(6)
        scale_container.setLayout(scale_layout)
        
        scale_label = QLabel("Масштаб:")
        scale_label.setStyleSheet("background: none; border: none; font-weight: 500;")
        scale_layout.addWidget(scale_label)
        
        self.scale_combo = QComboBox()
        scale_items = [str(scale) for scale in GRID.AVAILABLE_SCALES]
        self.scale_combo.addItems(scale_items)
        self.scale_combo.setCurrentText(str(self.current_scale))
        self.scale_combo.setStyleSheet(self.get_combo_style())
        scale_layout.addWidget(self.scale_combo)
        
        scale_unit_label = QLabel("км")
        scale_unit_label.setStyleSheet("background: none; border: none; color: #6c757d;")
        scale_layout.addWidget(scale_unit_label)
        
        grid_layout.addWidget(scale_container)
        
        # Кнопки управління сіткою
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        buttons_layout.setSpacing(8)
        buttons_container.setLayout(buttons_layout)
        
        # Кнопка встановлення центру
        self.center_btn = QPushButton("📍 Встановити центр")
        self.center_btn.setCheckable(True)
        self.center_btn.setStyleSheet(self.get_button_style())
        self.center_btn.setToolTip(
            "Встановлення центру азимутальної сітки\n" +
            "• Клацніть на зображенні для встановлення\n" +
            "• Стрілки: переміщення (±5 пікс)\n" +
            "• Shift+стрілки: швидке (±10 пікс)\n" +
            "• Ctrl+стрілки: точне (±1 пікс)\n" +
            "• Esc: вихід з режиму"
        )
        buttons_layout.addWidget(self.center_btn)
        
        # Кнопка встановлення краю
        self.edge_btn = QPushButton("📏 Встановити край")
        self.edge_btn.setCheckable(True)
        self.edge_btn.setStyleSheet(self.get_button_style())
        self.edge_btn.setToolTip(
            "Встановлення краю масштабу\n" +
            "• Оберіть точку на азимутальній сітці\n" +
            "• Вкажіть відстань у випадаючому списку\n" +
            "• Стрілки: переміщення краю\n" +
            "• Esc: вихід з режиму"
        )
        buttons_layout.addWidget(self.edge_btn)
        
        grid_layout.addWidget(buttons_container)
        
        # Інформація про поточні налаштування
        info_container = QFrame()
        info_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 8px;
                margin-top: 10px;
            }
        """)
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(5, 5, 5, 5)
        info_layout.setSpacing(4)
        info_container.setLayout(info_layout)
        
        self.center_info_label = QLabel("Центр: автоматично")
        self.center_info_label.setFont(QFont("", 9))
        self.center_info_label.setStyleSheet("background: none; border: none; color: #6c757d;")
        info_layout.addWidget(self.center_info_label)
        
        self.scale_info_label = QLabel("Калібрування: стандартне")
        self.scale_info_label.setFont(QFont("", 9))
        self.scale_info_label.setStyleSheet("background: none; border: none; color: #6c757d;")
        info_layout.addWidget(self.scale_info_label)
        
        grid_layout.addWidget(info_container)
        
        layout.addWidget(grid_group)
    
    def create_radar_section(self, layout: QVBoxLayout):
        """Створення секції опису РЛС"""
        radar_group = QGroupBox("Опис РЛС")
        radar_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #f9f9f9;
            }
        """)
        
        radar_layout = QVBoxLayout()
        radar_layout.setSpacing(10)
        radar_group.setLayout(radar_layout)
        
        # Перемикач включення опису
        self.radar_enabled_checkbox = QCheckBox("Додавати опис на зображення")
        self.radar_enabled_checkbox.setChecked(self.radar_description_enabled)
        self.radar_enabled_checkbox.setStyleSheet("""
            QCheckBox {
                font-weight: 500;
                color: #495057;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #ced4da;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #007bff;
                border-radius: 3px;
                background-color: #007bff;
                image: url(none);
            }
        """)
        self.radar_enabled_checkbox.setToolTip(
            "Опис додається в лівий нижній кут зображення\n" +
            f"Розмір: {RADAR.BOX_WIDTH_PERCENT:.1f}% × {RADAR.BOX_HEIGHT_PERCENT:.1f}%"
        )
        radar_layout.addWidget(self.radar_enabled_checkbox)
        
        # Поля опису РЛС
        self.radar_fields_container = QWidget()
        radar_fields_layout = QVBoxLayout()
        radar_fields_layout.setContentsMargins(0, 0, 0, 0)
        radar_fields_layout.setSpacing(8)
        self.radar_fields_container.setLayout(radar_fields_layout)
        
        # Дата
        date_label = QLabel("Дата:")
        date_label.setStyleSheet("background: none; border: none; font-weight: 500;")
        radar_fields_layout.addWidget(date_label)
        
        self.radar_date_edit = QDateEdit()
        self.radar_date_edit.setDate(self.radar_date)
        self.radar_date_edit.setCalendarPopup(True)
        self.radar_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.radar_date_edit.setStyleSheet(self.get_input_style())
        radar_fields_layout.addWidget(self.radar_date_edit)
        
        # Позивний
        callsign_label = QLabel("Позивний:")
        callsign_label.setStyleSheet("background: none; border: none; font-weight: 500;")
        radar_fields_layout.addWidget(callsign_label)
        
        self.radar_callsign_input = QLineEdit()
        self.radar_callsign_input.setText(self.radar_callsign)
        self.radar_callsign_input.setPlaceholderText("Введіть позивний")
        self.radar_callsign_input.setStyleSheet(self.get_input_style())
        radar_fields_layout.addWidget(self.radar_callsign_input)
        
        # Назва РЛС
        name_label = QLabel("Назва РЛС:")
        name_label.setStyleSheet("background: none; border: none; font-weight: 500;")
        radar_fields_layout.addWidget(name_label)
        
        self.radar_name_input = QLineEdit()
        self.radar_name_input.setText(self.radar_name)
        self.radar_name_input.setPlaceholderText("Введіть назву РЛС")
        self.radar_name_input.setStyleSheet(self.get_input_style())
        radar_fields_layout.addWidget(self.radar_name_input)
        
        # Номер
        number_label = QLabel("Номер:")
        number_label.setStyleSheet("background: none; border: none; font-weight: 500;")
        radar_fields_layout.addWidget(number_label)
        
        self.radar_number_input = QLineEdit()
        self.radar_number_input.setText(self.radar_number)
        self.radar_number_input.setPlaceholderText("Введіть номер")
        self.radar_number_input.setStyleSheet(self.get_input_style())
        radar_fields_layout.addWidget(self.radar_number_input)
        
        radar_layout.addWidget(self.radar_fields_container)
        
        # Початково поля відключені
        self.radar_fields_container.setEnabled(self.radar_description_enabled)
        
        layout.addWidget(radar_group)
    
    def create_actions_section(self, layout: QVBoxLayout):
        """Створення секції дій з даними"""
        actions_group = QGroupBox("Дії")
        actions_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #f9f9f9;
            }
        """)
        
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)
        actions_group.setLayout(actions_layout)
        
        # Кнопка скидання точки аналізу
        self.clear_analysis_btn = QPushButton("🗑️ Очистити точку аналізу")
        self.clear_analysis_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                border: 1px solid #5a6268;
                border-radius: 4px;
                padding: 6px 10px;
                font: 10pt "Segoe UI", Arial, sans-serif;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a6268;
                border: 1px solid #545b62;
            }
        """)
        self.clear_analysis_btn.setToolTip("Очистити поточну точку аналізу")
        self.clear_analysis_btn.setEnabled(False)  # Спочатку відключена
        actions_layout.addWidget(self.clear_analysis_btn)
        
        # Кнопка додавання до альбому
        self.add_to_album_btn = QPushButton("➕ Додати до альбому")
        self.add_to_album_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                border: 1px solid #0056b3;
                border-radius: 6px;
                padding: 10px 14px;
                font: 500 11pt "Segoe UI", Arial, sans-serif;
                color: white;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #0056b3;
                border: 1px solid #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                border: 1px solid #5a6268;
                color: #fff;
            }
        """)
        self.add_to_album_btn.setToolTip("Додати поточне оброблене зображення до альбому")
        self.add_to_album_btn.setEnabled(False)  # Спочатку відключена
        actions_layout.addWidget(self.add_to_album_btn)
        
        # Індикатор готовності
        self.readiness_indicator = QLabel("❌ Дані неповні")
        self.readiness_indicator.setAlignment(Qt.AlignCenter)
        self.readiness_indicator.setStyleSheet("""
            QLabel {
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                padding: 6px;
                color: #721c24;
                font-size: 10pt;
                font-weight: 500;
            }
        """)
        actions_layout.addWidget(self.readiness_indicator)
        
        layout.addWidget(actions_group)
    
    def add_separator(self, layout: QVBoxLayout):
        """Додавання розділювача"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("QFrame { color: #dee2e6; margin: 5px 0px; }")
        layout.addWidget(separator)
    
    def setup_connections(self):
        """Налаштування зв'язків між компонентами"""
        # Дані цілі
        self.target_number_input.textChanged.connect(
            lambda text: self.on_target_data_changed('target_number', text))
        self.height_input.textChanged.connect(
            lambda text: self.on_target_data_changed('height', text))
        self.obstacles_combo.currentTextChanged.connect(
            lambda text: self.on_target_data_changed('obstacles', text))
        self.detection_combo.currentTextChanged.connect(
            lambda text: self.on_target_data_changed('detection', text))
        
        # Азимутальна сітка
        self.scale_combo.currentTextChanged.connect(self.on_scale_changed)
        self.center_btn.toggled.connect(self.on_center_mode_toggled)
        self.edge_btn.toggled.connect(self.on_edge_mode_toggled)
        
        # Опис РЛС
        self.radar_enabled_checkbox.toggled.connect(self.on_radar_enabled_toggled)
        self.radar_date_edit.dateChanged.connect(
            lambda date: self.on_radar_data_changed('date', date.toString('dd.MM.yyyy')))
        self.radar_callsign_input.textChanged.connect(
            lambda text: self.on_radar_data_changed('callsign', text))
        self.radar_name_input.textChanged.connect(
            lambda text: self.on_radar_data_changed('name', text))
        self.radar_number_input.textChanged.connect(
            lambda text: self.on_radar_data_changed('number', text))
        
        # Дії
        self.clear_analysis_btn.clicked.connect(self.clear_analysis_point)
        self.add_to_album_btn.clicked.connect(self.add_to_album_requested.emit)
    
    def load_saved_values(self):
        """Завантаження збережених значень"""
        # TODO: Реалізувати завантаження з налаштувань
        self.update_readiness_indicator()
    
    # ===== ОБРОБНИКИ ПОДІЙ =====
    
    def on_target_data_changed(self, field: str, value: str):
        """Обробка зміни даних цілі"""
        # Збереження локально
        if field == 'target_number':
            # Автоматичне заповнення нулями
            if value.isdigit() and len(value) <= 4:
                padded_value = value.zfill(4)
                if padded_value != self.target_number_input.text():
                    self.target_number_input.setText(padded_value)
                self.current_target_number = padded_value
        elif field == 'height':
            try:
                self.current_height = float(value) if value else 0.0
            except ValueError:
                self.current_height = 0.0
        elif field == 'obstacles':
            self.current_obstacles = value
        elif field == 'detection':
            self.current_detection = value
        
        # Оновлення індикатора готовності
        self.update_readiness_indicator()
        
        # Сигнал наверх
        self.target_data_changed.emit(field, value)
        
        print(f"🎯 Дані цілі змінено: {field} = {value}")
    
    def on_scale_changed(self, scale_text: str):
        """Обробка зміни масштабу"""
        try:
            scale_value = int(scale_text)
            self.current_scale = scale_value
            self.scale_changed.emit(scale_value)
            self.update_scale_info()
            print(f"📏 Масштаб змінено: {scale_value} км")
        except ValueError:
            print(f"❌ Неправильне значення масштабу: {scale_text}")
    
    def on_center_mode_toggled(self, checked: bool):
        """Обробка перемикання режиму встановлення центру"""
        self.center_setting_mode = checked
        
        if checked:
            # Вимикаємо інший режим
            self.edge_btn.setChecked(False)
            self.center_btn.setText("🎯 Встановлення...")
            self.center_btn.setStyleSheet(self.get_active_button_style())
        else:
            self.center_btn.setText("📍 Встановити центр")
            self.center_btn.setStyleSheet(self.get_button_style())
        
        self.center_mode_toggled.emit(checked)
        print(f"🎯 Режим встановлення центру: {'увімкнено' if checked else 'вимкнено'}")
    
    def on_edge_mode_toggled(self, checked: bool):
        """Обробка перемикання режиму встановлення краю"""
        self.scale_edge_mode = checked
        
        if checked:
            # Вимикаємо інший режим
            self.center_btn.setChecked(False)
            self.edge_btn.setText("🎯 Встановлення...")
            self.edge_btn.setStyleSheet(self.get_active_button_style())
        else:
            self.edge_btn.setText("📏 Встановити край")
            self.edge_btn.setStyleSheet(self.get_button_style())
        
        self.scale_edge_mode_toggled.emit(checked)
        print(f"📏 Режим встановлення краю: {'увімкнено' if checked else 'вимкнено'}")
    
    def on_radar_enabled_toggled(self, checked: bool):
        """Обробка включення/виключення опису РЛС"""
        self.radar_description_enabled = checked
        self.radar_fields_container.setEnabled(checked)
        self.radar_description_toggled.emit(checked)
        self.update_readiness_indicator()
        print(f"📡 Опис РЛС: {'увімкнено' if checked else 'вимкнено'}")
    
    def on_radar_data_changed(self, field: str, value: str):
        """Обробка зміни даних РЛС"""
        # Збереження локально
        if field == 'date':
            pass  # Дата зберігається автоматично через QDateEdit
        elif field == 'callsign':
            self.radar_callsign = value
        elif field == 'name':
            self.radar_name = value
        elif field == 'number':
            self.radar_number = value
        
        print(f"📡 Дані РЛС змінено: {field} = {value}")
    
    def clear_analysis_point(self):
        """Очищення точки аналізу"""
        self.reset_analysis_data()
        self.clear_analysis_btn.setEnabled(False)
        self.update_readiness_indicator()
        print("🗑️ Точка аналізу очищена")
    
    # ===== ОНОВЛЕННЯ ВІДОБРАЖЕННЯ =====
    
    def update_analysis_data(self, analysis_point: AnalysisPoint):
        """Оновлення даних аналізу"""
        if analysis_point:
            self.current_azimuth = analysis_point.azimuth
            self.current_range = analysis_point.range_km
            
            azimuth_text = f"β = {analysis_point.azimuth:.0f}°"
            distance_text = f"D = {analysis_point.range_km:.0f} км"
            
            self.auto_azimuth_label.setText(azimuth_text)
            self.auto_distance_label.setText(distance_text)
            
            # Активація кнопки очищення
            self.clear_analysis_btn.setEnabled(True)
            
            print(f"📊 Дані аналізу оновлено: β={analysis_point.azimuth:.0f}°, D={analysis_point.range_km:.0f}км")
        else:
            self.reset_analysis_data()
        
        self.update_readiness_indicator()
    
    def update_grid_info(self, center_x: int, center_y: int, has_custom_scale: bool = False):
        """Оновлення інформації про сітку"""
        self.center_info_label.setText(f"Центр: ({center_x}, {center_y})")
        
        if has_custom_scale:
            self.scale_info_label.setText("Калібрування: користувацьке")
            self.scale_info_label.setStyleSheet("background: none; border: none; color: #28a745; font-weight: bold;")
        else:
            self.scale_info_label.setText("Калібрування: стандартне")
            self.scale_info_label.setStyleSheet("background: none; border: none; color: #6c757d;")
        
        print(f"ℹ️ Інформація про сітку оновлена: центр=({center_x},{center_y}), калібрування={'користувацьке' if has_custom_scale else 'стандартне'}")
    
    def update_scale_info(self):
        """Оновлення інформації про масштаб"""
        # Метод викликається автоматично при зміні масштабу
        pass
    
    def update_readiness_indicator(self):
        """Оновлення індикатора готовності даних"""
        # Перевірка готовності даних для додавання до альбому
        has_target_number = bool(self.current_target_number.strip())
        has_analysis_data = self.current_azimuth > 0 or self.current_range > 0
        
        # Перевірка даних РЛС якщо увімкнено
        radar_complete = True
        if self.radar_description_enabled:
            radar_complete = (bool(self.radar_callsign.strip()) and 
                            bool(self.radar_name.strip()) and 
                            bool(self.radar_number.strip()))
        
        is_ready = has_target_number and has_analysis_data and radar_complete
        
        if is_ready:
            self.readiness_indicator.setText("✅ Готово до додавання")
            self.readiness_indicator.setStyleSheet("""
                QLabel {
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 4px;
                    padding: 6px;
                    color: #155724;
                    font-size: 10pt;
                    font-weight: 500;
                }
            """)
            self.add_to_album_btn.setEnabled(True)
        else:
            missing_items = []
            if not has_target_number:
                missing_items.append("номер цілі")
            if not has_analysis_data:
                missing_items.append("точка аналізу")
            if self.radar_description_enabled and not radar_complete:
                missing_items.append("дані РЛС")
            
            self.readiness_indicator.setText(f"❌ Потрібно: {', '.join(missing_items)}")
            self.readiness_indicator.setStyleSheet("""
                QLabel {
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 4px;
                    padding: 6px;
                    color: #721c24;
                    font-size: 10pt;
                    font-weight: 500;
                }
            """)
            self.add_to_album_btn.setEnabled(False)
    
    def reset_analysis_data(self):
        """Скидання даних аналізу"""
        self.current_azimuth = 0.0
        self.current_range = 0.0
        self.auto_azimuth_label.setText("β = --°")
        self.auto_distance_label.setText("D = -- км")
    
    # ===== ПУБЛІЧНІ МЕТОДИ =====
    
    def set_center_mode(self, enabled: bool):
        """Програмне включення режиму центру"""
        self.center_btn.setChecked(enabled)
    
    def set_edge_mode(self, enabled: bool):
        """Програмне включення режиму краю"""
        self.edge_btn.setChecked(enabled)
    
    def exit_special_modes(self):
        """Вихід з всіх спеціальних режимів"""
        self.center_btn.setChecked(False)
        self.edge_btn.setChecked(False)
    
    def get_target_data(self) -> Dict[str, Any]:
        """Отримання поточних даних цілі"""
        return {
            'target_number': self.current_target_number,
            'height': self.current_height,
            'obstacles': self.current_obstacles,
            'detection': self.current_detection,
            'azimuth': self.current_azimuth,
            'range_km': self.current_range
        }
    
    def get_radar_data(self) -> Dict[str, Any]:
        """Отримання даних РЛС"""
        return {
            'enabled': self.radar_description_enabled,
            'date': self.radar_date_edit.date().toString('dd.MM.yyyy'),
            'callsign': self.radar_callsign,
            'name': self.radar_name,
            'number': self.radar_number
        }
    
    def set_target_data(self, data: Dict[str, Any]):
        """Встановлення даних цілі"""
        if 'target_number' in data:
            self.target_number_input.setText(data['target_number'])
        if 'height' in data:
            self.height_input.setText(str(data['height']))
        if 'obstacles' in data:
            self.obstacles_combo.setCurrentText(data['obstacles'])
        if 'detection' in data:
            self.detection_combo.setCurrentText(data['detection'])
    
    def get_complete_image_data(self) -> Optional[Dict[str, Any]]:
        """Отримання повних даних зображення для альбому"""
        if not self.add_to_album_btn.isEnabled():
            return None
        
        target_data = self.get_target_data()
        radar_data = self.get_radar_data()
        
        return {
            'target_data': target_data,
            'radar_data': radar_data,
            'timestamp': QDate.currentDate().toString('dd.MM.yyyy hh:mm:ss')
        }
    
    def set_placeholder_mode(self):
        """Режим-заглушка коли немає зображення"""
        self.reset_analysis_data()
        self.center_info_label.setText("Центр: не встановлено")
        self.scale_info_label.setText("Калібрування: не встановлено")
        
        # Відключення кнопок
        self.center_btn.setEnabled(False)
        self.edge_btn.setEnabled(False)
        self.clear_analysis_btn.setEnabled(False)
        self.add_to_album_btn.setEnabled(False)
        
        self.update_readiness_indicator()
    
    def set_active_mode(self):
        """Активний режим коли є зображення"""
        # Включення кнопок
        self.center_btn.setEnabled(True)
        self.edge_btn.setEnabled(True)
        
        self.update_readiness_indicator()
    
    def auto_increment_target_number(self):
        """Автоматичне збільшення номера цілі після додавання до альбому"""
        try:
            current_number = int(self.current_target_number)
            new_number = str(current_number + 1).zfill(4)
            self.target_number_input.setText(new_number)
            print(f"🔢 Номер цілі автоматично збільшено: {new_number}")
        except ValueError:
            print("⚠️ Не вдалося збільшити номер цілі")
    
    # ===== СТИЛІ =====
    
    def get_input_style(self) -> str:
        """Стиль для полів вводу"""
        return """
            QLineEdit, QDateEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
                font: 12pt "Segoe UI", Arial, sans-serif;
                color: #495057;
                min-height: 16px;
            }
            QLineEdit:hover, QDateEdit:hover {
                border: 1px solid #80bdff;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #007bff;
                background-color: #fff;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
            }
            QDateEdit::down-arrow {
                image: url(none);
                border: 1px solid #ced4da;
                background: #f8f9fa;
            }
        """
    
    def get_combo_style(self) -> str:
        """Стиль для випадаючих списків"""
        return """
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
                font: 12pt "Segoe UI", Arial, sans-serif;
                color: #495057;
                min-height: 16px;
            }
            QComboBox:hover {
                border: 1px solid #80bdff;
            }
            QComboBox:focus {
                border: 2px solid #007bff;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: url(none);
                border: 1px solid #ced4da;
                background: #f8f9fa;
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ced4da;
                background-color: white;
                selection-background-color: #007bff;
                selection-color: white;
            }
        """
    
    def get_button_style(self) -> str:
        """Стиль для звичайних кнопок"""
        return """
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 14px;
                font: 500 11pt "Segoe UI", Arial, sans-serif;
                color: #495057;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border: 1px solid #adb5bd;
                color: #343a40;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #007bff;
                border: 1px solid #0056b3;
                color: white;
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                color: #6c757d;
            }
        """
    
    def get_active_button_style(self) -> str:
        """Стиль для активних (натиснутих) кнопок"""
        return """
            QPushButton {
                background-color: #007bff;
                border: 1px solid #0056b3;
                border-radius: 6px;
                padding: 8px 14px;
                font: 500 11pt "Segoe UI", Arial, sans-serif;
                color: white;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #0056b3;
                border: 1px solid #004085;
            }
        """


# ===== ТЕСТУВАННЯ МОДУЛЯ =====

if __name__ == "__main__":
    print("=== Тестування DataPanel ===")
    print("Модуль DataPanel готовий до використання")