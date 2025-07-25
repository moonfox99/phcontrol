#!/usr/bin/env python3
"""
PhotoControl v2.0 - Права панель даних
Управління параметрами цілі та азимутальної сітки
"""

import os
from typing import Optional, Dict, Any, Tuple
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QComboBox, QGroupBox, QFrame, QSpinBox, QCheckBox,
                             QFormLayout, QScrollArea, QPushButton, QButtonGroup)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator

from core.constants import UI, GRID, ALBUM
from translations.translator import get_translator, TranslationKeys, Language


class DataPanel(QWidget):
    """
    Права панель даних PhotoControl v2.0
    
    Функціональність:
    - Параметри азимутальної сітки (центр, масштаб, кольори)
    - Управління переміщенням центру (клавіатурні команди)
    - Дані про ціль (номер, азимут, дальність, висота)
    - Параметри перешкод та статусу виявлення
    - Налаштування опису РЛС
    - Валідація даних в реальному часі
    """
    
    # Сигнали для взаємодії з головним вікном
    target_data_changed = pyqtSignal(dict)  # Дані про ціль змінились
    grid_center_move_requested = pyqtSignal(str, bool, bool)  # direction, shift, ctrl
    grid_scale_changed = pyqtSignal(int)  # Новий масштаб
    grid_settings_changed = pyqtSignal(dict)  # Налаштування сітки
    radar_description_changed = pyqtSignal(dict)  # Опис РЛС
    set_center_mode_requested = pyqtSignal()  # Режим встановлення центру
    set_scale_mode_requested = pyqtSignal()  # Режим встановлення масштабу
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Система перекладів
        self.translator = get_translator()
        
        # Налаштування панелі
        self.setFixedWidth(UI.DATA_PANEL_WIDTH)
        self.setStyleSheet(self._get_panel_styles())
        
        # Внутрішній стан
        self._updating_fields = False  # Флаг для запобігання рекурсивним викликам
        
        # Створення UI
        self._create_ui()
        
        # Підключення перекладів
        self.translator.language_changed.connect(self._update_translations)
        
        print("DataPanel створено")
    
    def _create_ui(self):
        """Створення інтерфейсу панелі"""
        # Основний контейнер з прокруткою
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarNever)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Віджет з контентом
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Заголовок панелі
        self._create_title(layout)
        
        # Азимутальна сітка
        self._create_azimuth_grid_section(layout)
        
        # Розділювач
        layout.addWidget(self._create_separator())
        
        # Переміщення центру
        self._create_move_center_section(layout)
        
        # Розділювач
        layout.addWidget(self._create_separator())
        
        # Дані про ціль
        self._create_target_data_section(layout)
        
        # Розділювач
        layout.addWidget(self._create_separator())
        
        # Опис РЛС
        self._create_radar_description_section(layout)
        
        # Розтягування знизу
        layout.addStretch()
        
        # Налаштування scroll area
        scroll_area.setWidget(content_widget)
        
        # Головний layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
    
    def _create_title(self, layout: QVBoxLayout):
        """Створення заголовка панелі"""
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            margin-bottom: 10px;
            color: #2c3e50;
        """)
        layout.addWidget(self.title_label)
    
    def _create_azimuth_grid_section(self, layout: QVBoxLayout):
        """Створення секції азимутальної сітки"""
        grid_group = QGroupBox()
        grid_layout = QVBoxLayout(grid_group)
        
        # Масштаб
        scale_layout = QHBoxLayout()
        self.scale_label = QLabel()
        scale_layout.addWidget(self.scale_label)
        
        self.scale_combo = QComboBox()
        # Стандартні масштаби (як в legacy версії)
        for scale in GRID.AVAILABLE_SCALES:
            self.scale_combo.addItem(f"1:{scale}", scale)
        self.scale_combo.currentIndexChanged.connect(self._on_scale_changed)
        scale_layout.addWidget(self.scale_combo)
        
        grid_layout.addLayout(scale_layout)
        
        # Кнопки управління сіткою
        buttons_layout = QHBoxLayout()
        
        self.set_center_btn = QPushButton()
        self.set_center_btn.clicked.connect(self.set_center_mode_requested.emit)
        buttons_layout.addWidget(self.set_center_btn)
        
        self.set_scale_btn = QPushButton()
        self.set_scale_btn.clicked.connect(self.set_scale_mode_requested.emit)
        buttons_layout.addWidget(self.set_scale_btn)
        
        grid_layout.addLayout(buttons_layout)
        
        # Координати центру (тільки для відображення)
        center_layout = QHBoxLayout()
        self.center_label = QLabel()
        center_layout.addWidget(self.center_label)
        
        self.center_display = QLabel("(—, —)")
        self.center_display.setStyleSheet("""
            background-color: #f8f9fa; 
            border: 1px solid #dee2e6; 
            padding: 4px 8px; 
            border-radius: 3px;
            font-family: monospace;
            font-size: 10px;
        """)
        center_layout.addWidget(self.center_display)
        
        grid_layout.addLayout(center_layout)
        
        layout.addWidget(grid_group)
        self.azimuth_grid_group = grid_group
    
    def _create_move_center_section(self, layout: QVBoxLayout):
        """Створення секції переміщення центру"""
        move_group = QGroupBox()
        move_layout = QVBoxLayout(move_group)
        
        # Інструкція
        self.move_instruction = QLabel()
        self.move_instruction.setWordWrap(True)
        self.move_instruction.setStyleSheet("""
            color: #6c757d; 
            font-size: 10px; 
            margin-bottom: 8px;
            padding: 8px;
            background-color: #f8f9fa;
            border-radius: 4px;
        """)
        move_layout.addWidget(self.move_instruction)
        
        # Поточний режим
        self.current_mode_label = QLabel()
        self.current_mode_label.setAlignment(Qt.AlignCenter)
        self.current_mode_label.setStyleSheet("""
            font-weight: bold;
            padding: 6px;
            border-radius: 4px;
            background-color: #e9ecef;
            color: #495057;
        """)
        move_layout.addWidget(self.current_mode_label)
        
        layout.addWidget(move_group)
        self.move_center_group = move_group
    
    def _create_target_data_section(self, layout: QVBoxLayout):
        """Створення секції даних про ціль"""
        target_group = QGroupBox()
        target_layout = QFormLayout(target_group)
        
        # Номер цілі
        self.target_number_label = QLabel()
        self.target_number_edit = QLineEdit()
        self.target_number_edit.setPlaceholderText("Ціль-01")
        self.target_number_edit.textChanged.connect(self._on_target_data_changed)
        target_layout.addRow(self.target_number_label, self.target_number_edit)
        
        # Азимут (тільки для відображення, обчислюється автоматично)
        self.azimuth_label = QLabel()
        self.azimuth_display = QLabel("—°")
        self.azimuth_display.setStyleSheet("""
            background-color: #f8f9fa; 
            border: 1px solid #dee2e6; 
            padding: 4px 8px; 
            border-radius: 3px;
            font-family: monospace;
            font-weight: bold;
            color: #0d6efd;
        """)
        target_layout.addRow(self.azimuth_label, self.azimuth_display)
        
        # Дальність (тільки для відображення, обчислюється автоматично)
        self.range_label = QLabel()
        self.range_display = QLabel("—")
        self.range_display.setStyleSheet("""
            background-color: #f8f9fa; 
            border: 1px solid #dee2e6; 
            padding: 4px 8px; 
            border-radius: 3px;
            font-family: monospace;
            font-weight: bold;
            color: #198754;
        """)
        target_layout.addRow(self.range_label, self.range_display)
        
        # Висота (вводиться користувачем)
        self.height_label = QLabel()
        self.height_edit = QLineEdit()
        self.height_edit.setPlaceholderText("150м")
        self.height_edit.textChanged.connect(self._on_target_data_changed)
        target_layout.addRow(self.height_label, self.height_edit)
        
        # Перешкоди
        self.obstacles_label = QLabel()
        self.obstacles_combo = QComboBox()
        self.obstacles_combo.addItem("без перешкод", "no_obstacles")
        self.obstacles_combo.addItem("з перешкодами", "with_obstacles")
        self.obstacles_combo.currentIndexChanged.connect(self._on_target_data_changed)
        target_layout.addRow(self.obstacles_label, self.obstacles_combo)
        
        # Статус виявлення
        self.detection_label = QLabel()
        self.detection_combo = QComboBox()
        self.detection_combo.addItem("Виявлення", "detection")
        self.detection_combo.addItem("Супроводження", "tracking")
        self.detection_combo.addItem("Втрата", "loss")
        self.detection_combo.currentIndexChanged.connect(self._on_target_data_changed)
        target_layout.addRow(self.detection_label, self.detection_combo)
        
        layout.addWidget(target_group)
        self.target_data_group = target_group
    
    def _create_radar_description_section(self, layout: QVBoxLayout):
        """Створення секції опису РЛС"""
        radar_group = QGroupBox()
        radar_layout = QVBoxLayout(radar_group)
        
        # Прапорець включення опису РЛС
        self.radar_enabled_checkbox = QCheckBox()
        self.radar_enabled_checkbox.setChecked(False)
        self.radar_enabled_checkbox.toggled.connect(self._on_radar_description_changed)
        radar_layout.addWidget(self.radar_enabled_checkbox)
        
        # Контейнер для полів опису (може бути відключений)
        self.radar_fields_widget = QWidget()
        radar_fields_layout = QFormLayout(self.radar_fields_widget)
        
        # Підрозділ
        self.unit_label = QLabel()
        self.unit_edit = QLineEdit()
        self.unit_edit.setPlaceholderText("1-й батальйон, 2-га рота")
        self.unit_edit.textChanged.connect(self._on_radar_description_changed)
        radar_fields_layout.addRow(self.unit_label, self.unit_edit)
        
        # Командир
        self.commander_label = QLabel()
        commander_layout = QHBoxLayout()
        
        self.commander_rank_edit = QLineEdit()
        self.commander_rank_edit.setPlaceholderText("капітан")
        self.commander_rank_edit.textChanged.connect(self._on_radar_description_changed)
        commander_layout.addWidget(self.commander_rank_edit)
        
        self.commander_name_edit = QLineEdit()
        self.commander_name_edit.setPlaceholderText("Іванов І.І.")
        self.commander_name_edit.textChanged.connect(self._on_radar_description_changed)
        commander_layout.addWidget(self.commander_name_edit)
        
        commander_widget = QWidget()
        commander_widget.setLayout(commander_layout)
        radar_fields_layout.addRow(self.commander_label, commander_widget)
        
        # Начальник штабу
        self.chief_label = QLabel()
        chief_layout = QHBoxLayout()
        
        self.chief_rank_edit = QLineEdit()
        self.chief_rank_edit.setPlaceholderText("старший лейтенант")
        self.chief_rank_edit.textChanged.connect(self._on_radar_description_changed)
        chief_layout.addWidget(self.chief_rank_edit)
        
        self.chief_name_edit = QLineEdit()
        self.chief_name_edit.setPlaceholderText("Петров П.П.")
        self.chief_name_edit.textChanged.connect(self._on_radar_description_changed)
        chief_layout.addWidget(self.chief_name_edit)
        
        chief_widget = QWidget()
        chief_widget.setLayout(chief_layout)
        radar_fields_layout.addRow(self.chief_label, chief_widget)
        
        # Додаємо поля до групи
        radar_layout.addWidget(self.radar_fields_widget)
        
        # За замовчуванням поля відключені
        self.radar_fields_widget.setEnabled(False)
        
        layout.addWidget(radar_group)
        self.radar_description_group = radar_group
    
    def _create_separator(self) -> QFrame:
        """Створення горизонтального розділювача"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #ccc; margin: 5px 0px;")
        return separator
    
    def _get_panel_styles(self) -> str:
        """Отримання стилів для панелі"""
        return """
            QWidget {
                background-color: #f5f5f5; 
                border-left: 1px solid #ccc;
                color: #333;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px 0 5px;
                color: #495057;
                font-size: 11px;
            }
            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px 8px;
                background-color: white;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #80bdff;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px 8px;
                background-color: white;
                font-size: 11px;
                min-height: 16px;
            }
            QComboBox:focus {
                border-color: #80bdff;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: 1px solid #007bff;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
                min-height: 16px;
            }
            QPushButton:hover {
                background-color: #0056b3;
                border-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
                border-color: #004085;
            }
            QCheckBox {
                font-size: 11px;
                font-weight: bold;
            }
            QLabel {
                background: none;
                border: none;
                color: #333;
                font-size: 11px;
            }
        """
    
    # ===============================
    # ОБРОБНИКИ ПОДІЙ
    # ===============================
    
    def _on_scale_changed(self):
        """Обробка зміни масштабу"""
        if not self._updating_fields:
            scale = self.scale_combo.currentData()
            if scale:
                self.grid_scale_changed.emit(scale)
    
    def _on_target_data_changed(self):
        """Обробка зміни даних про ціль"""
        if not self._updating_fields:
            target_data = self.get_target_data()
            self.target_data_changed.emit(target_data)
    
    def _on_radar_description_changed(self):
        """Обробка зміни опису РЛС"""
        if not self._updating_fields:
            # Включення/відключення полів
            enabled = self.radar_enabled_checkbox.isChecked()
            self.radar_fields_widget.setEnabled(enabled)
            
            # Передача даних
            radar_data = self.get_radar_description_data()
            self.radar_description_changed.emit(radar_data)
    
    # ===============================
    # ПУБЛІЧНІ МЕТОДИ
    # ===============================
    
    def update_grid_center(self, x: int, y: int):
        """Оновити відображення координат центру сітки"""
        self.center_display.setText(f"({x}, {y})")
    
    def update_analysis_point(self, azimuth: float, range_km: float):
        """Оновити відображення результатів аналізу"""
        self._updating_fields = True
        
        self.azimuth_display.setText(f"{azimuth:.1f}°")
        self.range_display.setText(f"{range_km:.2f} км")
        
        self._updating_fields = False
    
    def clear_analysis_point(self):
        """Очистити відображення результатів аналізу"""
        self._updating_fields = True
        
        self.azimuth_display.setText("—°")
        self.range_display.setText("—")
        
        self._updating_fields = False
    
    def set_current_mode(self, mode: str):
        """Встановити поточний режим роботи"""
        mode_texts = {
            "normal": "🖱️ Звичайний режим",
            "center_setting": "🎯 Встановлення центру", 
            "scale_setting": "📏 Встановлення масштабу",
            "analysis": "🔍 Аналіз точки"
        }
        
        mode_text = mode_texts.get(mode, f"⚙️ {mode}")
        self.current_mode_label.setText(mode_text)
        
        # Зміна кольору залежно від режиму
        if mode == "center_setting":
            bg_color = "#fff3cd"
            text_color = "#856404"
        elif mode == "scale_setting":
            bg_color = "#d4edda"
            text_color = "#155724"
        elif mode == "analysis":
            bg_color = "#cce5ff"
            text_color = "#004085"
        else:
            bg_color = "#e9ecef"
            text_color = "#495057"
        
        self.current_mode_label.setStyleSheet(f"""
            font-weight: bold;
            padding: 6px;
            border-radius: 4px;
            background-color: {bg_color};
            color: {text_color};
        """)
    
    def get_target_data(self) -> Dict[str, Any]:
        """Отримати дані про ціль"""
        return {
            "target_number": self.target_number_edit.text().strip(),
            "height": self.height_edit.text().strip(),
            "obstacles": self.obstacles_combo.currentData(),
            "detection": self.detection_combo.currentData()
        }
    
    def set_target_data(self, data: Dict[str, Any]):
        """Встановити дані про ціль"""
        self._updating_fields = True
        
        self.target_number_edit.setText(data.get("target_number", ""))
        self.height_edit.setText(data.get("height", ""))
        
        # Встановлення комбобоксів
        obstacles = data.get("obstacles", "no_obstacles")
        for i in range(self.obstacles_combo.count()):
            if self.obstacles_combo.itemData(i) == obstacles:
                self.obstacles_combo.setCurrentIndex(i)
                break
        
        detection = data.get("detection", "detection")
        for i in range(self.detection_combo.count()):
            if self.detection_combo.itemData(i) == detection:
                self.detection_combo.setCurrentIndex(i)
                break
        
        self._updating_fields = False
    
    def get_radar_description_data(self) -> Dict[str, Any]:
        """Отримати дані опису РЛС"""
        return {
            "enabled": self.radar_enabled_checkbox.isChecked(),
            "unit_info": self.unit_edit.text().strip(),
            "commander_rank": self.commander_rank_edit.text().strip(),
            "commander_name": self.commander_name_edit.text().strip(),
            "chief_rank": self.chief_rank_edit.text().strip(),
            "chief_name": self.chief_name_edit.text().strip()
        }
    
    def set_radar_description_data(self, data: Dict[str, Any]):
        """Встановити дані опису РЛС"""
        self._updating_fields = True
        
        enabled = data.get("enabled", False)
        self.radar_enabled_checkbox.setChecked(enabled)
        self.radar_fields_widget.setEnabled(enabled)
        
        self.unit_edit.setText(data.get("unit_info", ""))
        self.commander_rank_edit.setText(data.get("commander_rank", ""))
        self.commander_name_edit.setText(data.get("commander_name", ""))
        self.chief_rank_edit.setText(data.get("chief_rank", ""))
        self.chief_name_edit.setText(data.get("chief_name", ""))
        
        self._updating_fields = False
    
    def get_current_scale(self) -> int:
        """Отримати поточний масштаб"""
        return self.scale_combo.currentData() or GRID.DEFAULT_SCALE
    
    def set_current_scale(self, scale: int):
        """Встановити поточний масштаб"""
        self._updating_fields = True
        
        for i in range(self.scale_combo.count()):
            if self.scale_combo.itemData(i) == scale:
                self.scale_combo.setCurrentIndex(i)
                break
        
        self._updating_fields = False
    
    def clear_all_data(self):
        """Очистити всі поля панелі"""
        self._updating_fields = True
        
        # Очищення даних про ціль
        self.target_number_edit.clear()
        self.height_edit.clear()
        self.obstacles_combo.setCurrentIndex(0)
        self.detection_combo.setCurrentIndex(0)
        
        # Очищення результатів аналізу
        self.clear_analysis_point()
        
        # Очищення координат центру
        self.center_display.setText("(—, —)")
        
        # Очищення опису РЛС
        self.radar_enabled_checkbox.setChecked(False)
        self.radar_fields_widget.setEnabled(False)
        self.unit_edit.clear()
        self.commander_rank_edit.clear()
        self.commander_name_edit.clear()
        self.chief_rank_edit.clear()
        self.chief_name_edit.clear()
        
        self._updating_fields = False
    
    def validate_data(self) -> Tuple[bool, List[str]]:
        """Валідація даних панелі"""
        errors = []
        
        # Перевірка номера цілі
        if not self.target_number_edit.text().strip():
            errors.append("Номер цілі не може бути порожнім")
        
        # Перевірка висоти (якщо введена)
        height_text = self.height_edit.text().strip()
        if height_text and not any(c.isdigit() for c in height_text):
            errors.append("Висота має містити числове значення")
        
        # Перевірка опису РЛС (якщо включений)
        if self.radar_enabled_checkbox.isChecked():
            if not self.unit_edit.text().strip():
                errors.append("Підрозділ не може бути порожнім")
            if not self.commander_rank_edit.text().strip() or not self.commander_name_edit.text().strip():
                errors.append("Дані командира неповні")
        
        return len(errors) == 0, errors
    
    # ===============================
    # ПРИВАТНІ МЕТОДИ
    # ===============================
    
    def _update_translations(self):
        """Оновлення перекладів інтерфейсу"""
        tr = self.translator.tr
        
        # Заголовок
        self.title_label.setText(tr(TranslationKeys.REPORT_DATA))
        
        # Групи
        self.azimuth_grid_group.setTitle(tr(TranslationKeys.AZIMUTH_GRID))
        self.move_center_group.setTitle(tr(TranslationKeys.MOVE_CENTER))
        self.target_data_group.setTitle("Дані про ціль")
        self.radar_description_group.setTitle("Опис РЛС")
        
        # Азимутальна сітка
        self.scale_label.setText(tr(TranslationKeys.SCALE_SETTING) + ":")
        self.center_label.setText("Центр:")
        self.set_center_btn.setText(tr(TranslationKeys.SET_CENTER))
        self.set_scale_btn.setText(tr(TranslationKeys.SET_SCALE_EDGE))
        
        # Інструкція переміщення
        self.move_instruction.setText(
            "Використовуйте стрілки ←→↑↓ для переміщення\n"
            "Shift + стрілки = швидке переміщення\n"
            "Ctrl + стрілки = точне переміщення\n"
            "Esc = вихід з режиму"
        )
        
        # Дані про ціль
        self.target_number_label.setText(tr(TranslationKeys.TARGET_NUMBER) + ":")
        self.azimuth_label.setText(tr(TranslationKeys.AZIMUTH) + ":")
        self.range_label.setText(tr(TranslationKeys.RANGE) + ":")
        self.height_label.setText(tr(TranslationKeys.HEIGHT) + ":")
        self.obstacles_label.setText(tr(TranslationKeys.OBSTACLES) + ":")
        self.detection_label.setText("Статус:")
        
        # Опис РЛС
        self.radar_enabled_checkbox.setText("Додати опис РЛС")
        self.unit_label.setText("Підрозділ:")
        self.commander_label.setText("Командир:")
        self.chief_label.setText("Начальник штабу:")
        
        # Оновлення комбобоксів
        self._update_combo_translations()
    
    def _update_combo_translations(self):
        """Оновлення перекладів в комбобоксах"""
        tr = self.translator.tr
        
        # Зберігаємо поточні значення
        obstacles_current = self.obstacles_combo.currentData()
        detection_current = self.detection_combo.currentData()
        
        # Оновлюємо перешкоди
        self.obstacles_combo.clear()
        self.obstacles_combo.addItem(tr(TranslationKeys.NO_OBSTACLES), "no_obstacles")
        self.obstacles_combo.addItem(tr(TranslationKeys.WITH_OBSTACLES), "with_obstacles")
        
        # Відновлюємо значення
        for i in range(self.obstacles_combo.count()):
            if self.obstacles_combo.itemData(i) == obstacles_current:
                self.obstacles_combo.setCurrentIndex(i)
                break
        
        # Оновлюємо статус
        self.detection_combo.clear()
        self.detection_combo.addItem(tr(TranslationKeys.DETECTION), "detection")
        self.detection_combo.addItem(tr(TranslationKeys.TRACKING), "tracking")
        self.detection_combo.addItem(tr(TranslationKeys.LOSS), "loss")
        
        # Відновлюємо значення
        for i in range(self.detection_combo.count()):
            if self.detection_combo.itemData(i) == detection_current:
                self.detection_combo.setCurrentIndex(i)
                break
    
    # ===============================
    # СТАТИЧНІ МЕТОДИ ДЛЯ ТЕСТУВАННЯ
    # ===============================
    
    @staticmethod
    def create_test_panel() -> "DataPanel":
        """Створення тестової панелі з демо-даними"""
        panel = DataPanel()
        
        # Тестові дані
        panel.set_target_data({
            "target_number": "Ціль-01",
            "height": "150м",
            "obstacles": "no_obstacles",
            "detection": "detection"
        })
        
        panel.update_grid_center(320, 240)
        panel.update_analysis_point(45.5, 2.75)
        panel.set_current_mode("analysis")
        
        return panel


# ===============================
# ТЕСТУВАННЯ ПАНЕЛІ
# ===============================

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QLabel
    
    class TestMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Тестування DataPanel")
            self.setGeometry(100, 100, 900, 700)
            
            # Центральний віджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QHBoxLayout(central_widget)
            
            # Центральна область (заглушка)
            center_label = QLabel("Центральна область\n\n(тут буде панель зображення)")
            center_label.setAlignment(Qt.AlignCenter)
            center_label.setStyleSheet("""
                background-color: white; 
                border: 1px solid #ddd;
                color: #666;
                font-size: 14px;
            """)
            layout.addWidget(center_label)
            
            # Права панель даних
            self.data_panel = DataPanel.create_test_panel()
            layout.addWidget(self.data_panel)
            
            # Підключення сигналів для тестування
            self.data_panel.target_data_changed.connect(
                lambda data: print(f"Дані про ціль змінено: {data}")
            )
            self.data_panel.grid_scale_changed.connect(
                lambda scale: print(f"Масштаб змінено: 1:{scale}")
            )
            self.data_panel.radar_description_changed.connect(
                lambda data: print(f"Опис РЛС змінено: {data}")
            )
            self.data_panel.set_center_mode_requested.connect(
                lambda: print("Запит на встановлення центру")
            )
            self.data_panel.set_scale_mode_requested.connect(
                lambda: print("Запит на встановлення масштабу")
            )
            
            print("Тестове вікно DataPanel створено")
    
    # Запуск тесту
    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    
    print("=== Тестування DataPanel ===")
    print("Функції для тестування:")
    print("1. Налаштування азимутальної сітки")
    print("2. Введення даних про ціль")
    print("3. Автоматичне відображення азимуту/дальності")
    print("4. Налаштування опису РЛС")
    print("5. Валідація введених даних")
    
    sys.exit(app.exec_())