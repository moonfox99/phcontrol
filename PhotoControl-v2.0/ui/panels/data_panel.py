#!/usr/bin/env python3
"""
Права панель даних цілі та налаштувань азимутальної сітки
"""

from typing import Optional, Any
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QComboBox, QCheckBox, QDateEdit,
                             QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont

from core.constants import UI, GRID
from core.image_processor import AnalysisPoint


class DataPanel(QWidget):
    """
    Права панель для введення даних цілі та налаштувань сітки
    
    Функціональність:
    - Введення даних про ціль (номер, висота, перешкоди, статус)
    - Відображення розрахованих значень (азимут, дальність, масштаб)
    - Налаштування азимутальної сітки (масштаб, центр, край)
    - Опис РЛС з можливістю включення/виключення
    """
    
    # Сигнали для зв'язку з головним вікном
    target_data_changed = pyqtSignal(str, object)  # field_name, value
    scale_changed = pyqtSignal(int)
    center_mode_toggled = pyqtSignal(bool)
    scale_edge_mode_toggled = pyqtSignal(bool)
    radar_description_toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Стан даних
        self.current_target_number = "0001"
        self.current_height = "0.0"
        self.current_obstacles = "без перешкод"
        self.current_detection = "Виявлення"
        self.current_scale = 300
        
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
        # Контейнер для даних цілі
        target_group = QFrame()
        target_group.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        target_layout = QVBoxLayout()
        target_layout.setSpacing(10)
        target_group.setLayout(target_layout)
        
        # Номер цілі
        self.target_number_input = QLineEdit()
        self.target_number_input.setPlaceholderText("Номер цілі")
        self.target_number_input.setText(self.current_target_number)
        self.target_number_input.setStyleSheet(self.get_input_style())
        target_layout.addWidget(self.target_number_input)
        
        # Автоматичні поля (азимут, дальність)
        self.auto_azimuth_label = QLabel("β - --°")
        self.auto_azimuth_label.setStyleSheet("font-weight: 500; color: #495057; background: none; border: none;")
        target_layout.addWidget(self.auto_azimuth_label)
        
        self.auto_distance_label = QLabel("D - -- км")
        self.auto_distance_label.setStyleSheet("font-weight: 500; color: #495057; background: none; border: none;")
        target_layout.addWidget(self.auto_distance_label)
        
        # Висота (в одному рядку)
        height_container = QWidget()
        height_layout = QHBoxLayout()
        height_layout.setContentsMargins(0, 0, 0, 0)
        height_layout.setSpacing(6)
        height_container.setLayout(height_layout)
        
        height_label = QLabel("H –")
        height_label.setStyleSheet("color: #495057; font-weight: 500; background: none; border: none;")
        height_layout.addWidget(height_label)
        
        self.height_input = QLineEdit(self.current_height)
        self.height_input.setMaximumWidth(80)
        self.height_input.setStyleSheet(self.get_input_style())
        height_layout.addWidget(self.height_input)
        
        units_label = QLabel("м")
        units_label.setStyleSheet("color: #6c757d; background: none; border: none;")
        height_layout.addWidget(units_label)
        
        height_layout.addStretch()
        target_layout.addWidget(height_container)
        
        # Комбобокси
        self.obstacles_combo = QComboBox()
        self.obstacles_combo.addItems(["без перешкод", "з перешкодами"])
        self.obstacles_combo.setCurrentText(self.current_obstacles)
        self.obstacles_combo.setStyleSheet(self.get_combo_style())
        target_layout.addWidget(self.obstacles_combo)
        
        self.detection_combo = QComboBox()
        self.detection_combo.addItems(["Виявлення", "Супроводження", "Втрата"])
        self.detection_combo.setCurrentText(self.current_detection)
        self.detection_combo.setStyleSheet(self.get_combo_style())
        target_layout.addWidget(self.detection_combo)
        
        # Масштаб (автоматичний)
        self.auto_scale_label = QLabel(f"M = {self.current_scale}")
        self.auto_scale_label.setStyleSheet("font-weight: 500; color: #495057; background: none; border: none;")
        target_layout.addWidget(self.auto_scale_label)
        
        layout.addWidget(target_group)
    
    def create_grid_section(self, layout: QVBoxLayout):
        """Створення секції азимутальної сітки"""
        # Заголовок секції
        grid_label = QLabel("Азимутальна сітка")
        grid_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        grid_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-weight: bold;
                margin-bottom: 8px;
                background: none;
                border: none;
            }
        """)
        layout.addWidget(grid_label)
        
        # Масштаб (в одному рядку)
        scale_container = QWidget()
        scale_layout = QHBoxLayout()
        scale_layout.setContentsMargins(0, 0, 0, 0)
        scale_layout.setSpacing(8)
        scale_container.setLayout(scale_layout)
        
        scale_label = QLabel("Масштаб:")
        scale_label.setStyleSheet("color: #495057; font-weight: 500; background: none; border: none;")
        scale_layout.addWidget(scale_label)
        
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(GRID.AVAILABLE_SCALES)
        self.scale_combo.setCurrentText(str(self.current_scale))
        self.scale_combo.setStyleSheet(self.get_combo_style())
        scale_layout.addWidget(self.scale_combo)
        
        scale_layout.addStretch()
        layout.addWidget(scale_container)
        
        # Кнопки управління сіткою
        self.scale_edge_btn = QPushButton("Встановити край масштабу")
        self.scale_edge_btn.setCheckable(True)
        self.scale_edge_btn.setStyleSheet(self.get_toggle_button_style())
        layout.addWidget(self.scale_edge_btn)
        
        self.set_center_btn = QPushButton("Встановити центр")
        self.set_center_btn.setCheckable(True)
        self.set_center_btn.setStyleSheet(self.get_toggle_button_style())
        layout.addWidget(self.set_center_btn)
    
    def create_radar_section(self, layout: QVBoxLayout):
        """Створення секції опису РЛС"""
        # Checkbox для активації опису РЛС
        self.radar_description_checkbox = QCheckBox("Додати опис РЛС")
        self.radar_description_checkbox.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.radar_description_checkbox.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                color: #495057;
                padding: 6px;
                background: none;
                border: none;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #dee2e6;
                background-color: white;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #495057;
                background-color: #495057;
                border-radius: 3px;
            }
            QCheckBox::indicator:unchecked:hover {
                border: 2px solid #adb5bd;
                background-color: #f8f9fa;
            }
        """)
        layout.addWidget(self.radar_description_checkbox)
        
        # Група полів для опису РЛС
        radar_group = QFrame()
        radar_group.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        radar_layout = QVBoxLayout()
        radar_layout.setSpacing(10)
        radar_group.setLayout(radar_layout)
        
        # Дата РЛС
        self.radar_date_edit = QDateEdit()
        self.radar_date_edit.setDate(self.radar_date)
        self.radar_date_edit.setCalendarPopup(True)
        self.radar_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.radar_date_edit.setFixedHeight(32)
        self.radar_date_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.radar_date_edit.setEnabled(False)
        self.radar_date_edit.setStyleSheet(self.get_date_style())
        radar_layout.addWidget(self.radar_date_edit)
        
        # Позивний РЛС
        self.radar_callsign_input = QLineEdit()
        self.radar_callsign_input.setPlaceholderText("Позивний")
        self.radar_callsign_input.setFixedHeight(32)
        self.radar_callsign_input.setEnabled(False)
        self.radar_callsign_input.setStyleSheet(self.get_input_style())
        radar_layout.addWidget(self.radar_callsign_input)
        
        # Назва РЛС
        self.radar_name_input = QLineEdit()
        self.radar_name_input.setPlaceholderText("Назва РЛС")
        self.radar_name_input.setFixedHeight(32)
        self.radar_name_input.setEnabled(False)
        self.radar_name_input.setStyleSheet(self.get_input_style())
        radar_layout.addWidget(self.radar_name_input)
        
        # Номер РЛС
        self.radar_number_input = QLineEdit()
        self.radar_number_input.setPlaceholderText("Номер РЛС")
        self.radar_number_input.setFixedHeight(32)
        self.radar_number_input.setEnabled(False)
        self.radar_number_input.setStyleSheet(self.get_input_style())
        radar_layout.addWidget(self.radar_number_input)
        
        layout.addWidget(radar_group)
    
    def get_input_style(self) -> str:
        """Стиль для полів введення"""
        return """
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: white;
                font: 12pt "Segoe UI", Arial, sans-serif;
                color: #495057;
                min-height: 20px;
            }
            QLineEdit:hover {
                border: 1px solid #adb5bd;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 1px solid #6c757d;
                background-color: white;
            }
            QLineEdit:disabled {
                background-color: #f5f5f5;
                color: #6c757d;
                border: 1px solid #e9ecef;
            }
        """
    
    def get_combo_style(self) -> str:
        """Стиль для випадних списків"""
        return """
            QComboBox {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: white;
                font: 12pt "Segoe UI", Arial, sans-serif;
                color: #495057;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 1px solid #adb5bd;
                background-color: #f8f9fa;
            }
            QComboBox:focus {
                border: 1px solid #6c757d;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                border-left: 1px solid #dee2e6;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #f8f9fa;
            }
            QComboBox::drop-down:hover {
                background-color: #e9ecef;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6c757d;
            }
        """
    
    def get_date_style(self) -> str:
        """Стиль для поля дати"""
        return """
            QDateEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: white;
                font: 12pt "Segoe UI", Arial, sans-serif;
                color: #495057;
                min-height: 22px;
            }
            QDateEdit:hover {
                border: 1px solid #adb5bd;
                background-color: #f8f9fa;
            }
            QDateEdit:focus {
                border: 1px solid #6c757d;
            }
            QDateEdit:disabled {
                background-color: #f5f5f5;
                color: #6c757d;
                border: 1px solid #e9ecef;
            }
            QDateEdit::drop-down {
                border: none;
                background-color: transparent;
                width: 18px;
                margin-right: 4px;
            }
            QDateEdit::drop-down:hover {
                background-color: #f8f9fa;
                border-radius: 3px;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #6c757d;
                margin-top: 1px;
            }
        """
    
    def get_toggle_button_style(self) -> str:
        """Стиль для кнопок-перемикачів"""
        return """
            QPushButton {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 10px 14px;
                font: 500 12pt "Segoe UI", Arial, sans-serif;
                color: #495057;
                min-height: 16px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border: 2px solid #adb5bd;
                color: #343a40;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
                border: 2px solid #6c757d;
                border-style: inset;
            }
            QPushButton:checked {
                background-color: #495057;
                color: white;
                border: 2px solid #343a40;
            }
            QPushButton:checked:hover {
                background-color: #343a40;
                border: 2px solid #212529;
            }
        """
    
    def add_separator(self, layout: QVBoxLayout):
        """Додавання розділювача"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #dee2e6; margin: 8px 0px;")
        layout.addWidget(separator)
    
    def setup_connections(self):
        """Налаштування зв'язків сигналів"""
        # Дані цілі
        self.target_number_input.textChanged.connect(
            lambda text: self.handle_target_data_change("target_number", text))
        self.height_input.textChanged.connect(
            lambda text: self.handle_target_data_change("height", text))
        self.obstacles_combo.currentTextChanged.connect(
            lambda text: self.handle_target_data_change("obstacles", text))
        self.detection_combo.currentTextChanged.connect(
            lambda text: self.handle_target_data_change("detection", text))
        
        # Азимутальна сітка
        self.scale_combo.currentTextChanged.connect(self.on_scale_changed)
        self.scale_edge_btn.toggled.connect(self.on_scale_edge_toggled)
        self.set_center_btn.toggled.connect(self.on_center_mode_toggled)
        
        # Опис РЛС
        self.radar_description_checkbox.toggled.connect(self.on_radar_description_toggled)
        self.radar_date_edit.dateChanged.connect(self.on_radar_date_changed)
        self.radar_callsign_input.textChanged.connect(self.on_radar_callsign_changed)
        self.radar_name_input.textChanged.connect(self.on_radar_name_changed)
        self.radar_number_input.textChanged.connect(self.on_radar_number_changed)
    
    def handle_target_data_change(self, field: str, value: Any):
        """Обробка зміни даних цілі"""
        # Оновлення внутрішнього стану
        if field == "target_number":
            self.current_target_number = value
        elif field == "height":
            self.current_height = value
        elif field == "obstacles":
            self.current_obstacles = value
        elif field == "detection":
            self.current_detection = value
        
        # Сигнал для зовнішньої обробки
        self.target_data_changed.emit(field, value)
    
    def on_scale_changed(self, scale_text: str):
        """Обробка зміни масштабу"""
        try:
            scale_value = int(scale_text)
            self.current_scale = scale_value
            self.auto_scale_label.setText(f"M = {scale_value}")
            self.scale_changed.emit(scale_value)
        except ValueError:
            pass
    
    def on_scale_edge_toggled(self, checked: bool):
        """Обробка перемикання режиму краю масштабу"""
        self.scale_edge_mode = checked
        
        # Взаємно виключні режими
        if checked and self.center_setting_mode:
            self.set_center_btn.setChecked(False)
            self.center_setting_mode = False
        
        self.scale_edge_mode_toggled.emit(checked)
    
    def on_center_mode_toggled(self, checked: bool):
        """Обробка перемикання режиму центру"""
        self.center_setting_mode = checked
        
        # Взаємно виключні режими
        if checked and self.scale_edge_mode:
            self.scale_edge_btn.setChecked(False)
            self.scale_edge_mode = False
        
        self.center_mode_toggled.emit(checked)
    
    def on_radar_description_toggled(self, checked: bool):
        """Обробка перемикання опису РЛС"""
        self.radar_description_enabled = checked
        
        # Активація/деактивація полів РЛС
        self.radar_date_edit.setEnabled(checked)
        self.radar_callsign_input.setEnabled(checked)
        self.radar_name_input.setEnabled(checked)
        self.radar_number_input.setEnabled(checked)
        
        self.radar_description_toggled.emit(checked)
    
    def on_radar_date_changed(self, date: QDate):
        """Обробка зміни дати РЛС"""
        self.radar_date = date
    
    def on_radar_callsign_changed(self, text: str):
        """Обробка зміни позивного РЛС"""
        self.radar_callsign = text
    
    def on_radar_name_changed(self, text: str):
        """Обробка зміни назви РЛС"""
        self.radar_name = text
    
    def on_radar_number_changed(self, text: str):
        """Обробка зміни номера РЛС"""
        self.radar_number = text
    
    def update_analysis_data(self, analysis_point: AnalysisPoint):
        """Оновлення відображуваних даних аналізу"""
        # Оновлення автоматичних полів
        self.auto_azimuth_label.setText(f"β - {analysis_point.azimuth:.0f}°")
        self.auto_distance_label.setText(f"D - {analysis_point.range_km:.0f} км")
    
    def get_target_data(self) -> dict:
        """Отримання всіх даних цілі"""
        return {
            'target_number': self.current_target_number,
            'height': self.current_height,
            'obstacles': self.current_obstacles,
            'detection': self.current_detection,
            'scale': self.current_scale
        }
    
    def get_radar_data(self) -> dict:
        """Отримання даних РЛС"""
        if not self.radar_description_enabled:
            return {'enabled': False}
        
        return {
            'enabled': True,
            'date': self.radar_date,
            'callsign': self.radar_callsign,
            'name': self.radar_name,
            'number': self.radar_number
        }
    
    def reset_target_data(self):
        """Скидання даних цілі до базових значень"""
        self.current_target_number = "0001"
        self.current_height = "0.0"
        self.current_obstacles = "без перешкод"
        self.current_detection = "Виявлення"
        
        # Оновлення UI
        self.target_number_input.setText(self.current_target_number)
        self.height_input.setText(self.current_height)
        self.obstacles_combo.setCurrentText(self.current_obstacles)
        self.detection_combo.setCurrentText(self.current_detection)
        
        # Очищення автоматичних полів
        self.auto_azimuth_label.setText("β - --°")
        self.auto_distance_label.setText("D - -- км")