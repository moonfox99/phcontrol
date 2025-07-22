#!/usr/bin/env python3
"""
Ліва панель управління PhotoControl v2.0
Файлові операції, пакетна обробка, результати
"""

import os
from typing import Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QFrame, QGroupBox, QDateEdit,
                             QComboBox, QLineEdit, QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont

from core.constants import UI, FILES, GRID
from core.image_processor import AnalysisPoint
from utils.file_utils import get_templates_directory, list_template_files


class ControlPanel(QWidget):
    """
    Ліва панель управління програмою
    
    Функціональність:
    - Файлові операції (відкриття зображень/папок)
    - Управління шаблонами документів
    - Пакетна обробка зображень
    - Відображення результатів операцій
    """
    
    # Сигнали для зв'язку з головним вікном
    open_image_requested = pyqtSignal()
    open_folder_requested = pyqtSignal()
    save_image_requested = pyqtSignal()
    create_album_requested = pyqtSignal()
    template_changed = pyqtSignal(str)
    document_date_changed = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Стан панелі
        self.current_image_info: Optional[str] = None
        self.current_template: Optional[str] = None
        self.document_date = QDate.currentDate()
        self.processed_count = 0
        
        # Налаштування панелі
        self.setFixedWidth(UI.LEFT_PANEL_WIDTH)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-right: 1px solid #dee2e6;
            }
        """)
        
        self.init_ui()
        self.setup_connections()
        self.load_templates()
    
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.setLayout(layout)
        
        # Заголовок панелі
        self.create_title_section(layout)
        
        # Файлові операції
        self.create_file_operations_section(layout)
        
        # Розділювач
        self.add_separator(layout)
        
        # Заповнення документу
        self.create_document_section(layout)
        
        # Розділювач
        self.add_separator(layout)
        
        # Пакетна обробка
        self.create_batch_processing_section(layout)
        
        # Результати
        self.create_results_section(layout)
        
        # Розтягування внизу
        layout.addStretch()
    
    def create_title_section(self, layout: QVBoxLayout):
        """Створення заголовку панелі"""
        title_label = QLabel("Керування")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                font-weight: bold;
                margin-bottom: 12px;
                color: #343a40;
                background: none;
                border: none;
            }
        """)
        layout.addWidget(title_label)
    
    def create_file_operations_section(self, layout: QVBoxLayout):
        """Створення секції файлових операцій"""
        # Заголовок секції
        section_label = QLabel("Операції з файлами")
        section_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        section_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                margin-top: 12px;
                margin-bottom: 8px;
                font-weight: bold;
                background: none;
                border: none;
            }
        """)
        layout.addWidget(section_label)
        
        # Кнопки файлових операцій
        self.open_image_btn = self.create_button("Відкрити зображення")
        layout.addWidget(self.open_image_btn)
        
        self.open_folder_btn = self.create_button("Відкрити папку")
        layout.addWidget(self.open_folder_btn)
        
        self.save_image_btn = self.create_button("Зберегти зображення")
        layout.addWidget(self.save_image_btn)
    
    def create_document_section(self, layout: QVBoxLayout):
        """Створення секції заповнення документу"""
        # Заголовок секції
        section_label = QLabel("Заповнення документу")
        section_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        section_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                margin-top: 8px;
                margin-bottom: 8px;
                font-weight: bold;
                background: none;
                border: none;
            }
        """)
        layout.addWidget(section_label)
        
        # Вибір шаблону
        template_container = QWidget()
        template_layout = QHBoxLayout()
        template_layout.setContentsMargins(0, 0, 0, 0)
        template_layout.setSpacing(8)
        template_container.setLayout(template_layout)
        
        template_label = QLabel("Шаблон:")
        template_label.setStyleSheet("color: #495057; background: none; border: none;")
        template_layout.addWidget(template_label)
        
        self.template_combo = QComboBox()
        self.template_combo.setStyleSheet(self.get_input_style())
        template_layout.addWidget(self.template_combo)
        
        layout.addWidget(template_container)
        
        # Дата документу
        date_container = QWidget()
        date_layout = QHBoxLayout()
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(8)
        date_container.setLayout(date_layout)
        
        self.document_date_edit = QDateEdit()
        self.document_date_edit.setDate(self.document_date)
        self.document_date_edit.setCalendarPopup(True)
        self.document_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.document_date_edit.setFixedHeight(32)
        self.document_date_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.document_date_edit.setStyleSheet(self.get_date_style())
        date_layout.addWidget(self.document_date_edit)
        
        self.today_btn = QPushButton("Сьогодні")
        self.today_btn.setFixedHeight(32)
        self.today_btn.setFixedWidth(85)
        self.today_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: 1px solid #495057;
                border-radius: 4px;
                padding: 6px 8px;
                font: 500 10pt "Segoe UI", Arial, sans-serif;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #495057;
                border: 1px solid #343a40;
            }
            QPushButton:pressed {
                background-color: #343a40;
            }
        """)
        date_layout.addWidget(self.today_btn)
        
        layout.addWidget(date_container)
        
        # Кнопки управління шаблонами
        self.create_template_btn = self.create_button("Створити новий шаблон")
        layout.addWidget(self.create_template_btn)
        
        self.edit_template_btn = self.create_button("Редагувати шаблон")
        layout.addWidget(self.edit_template_btn)
    
    def create_batch_processing_section(self, layout: QVBoxLayout):
        """Створення секції пакетної обробки"""
        # Заголовок секції
        section_label = QLabel("Пакетна обробка")
        section_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        section_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                margin-top: 8px;
                margin-bottom: 8px;
                font-weight: bold;
                background: none;
                border: none;
            }
        """)
        layout.addWidget(section_label)
        
        # Кнопки пакетної обробки
        self.save_current_btn = self.create_button("Додати до альбому")
        layout.addWidget(self.save_current_btn)
        
        self.cancel_current_btn = self.create_button("Скасувати зміни", button_type="warning")
        layout.addWidget(self.cancel_current_btn)
        
        self.clear_all_btn = self.create_button("Очистити все", button_type="danger")
        layout.addWidget(self.clear_all_btn)
        
        # Головна кнопка створення альбому
        self.create_album_btn = self.create_button("Створити альбом", button_type="primary")
        layout.addWidget(self.create_album_btn)
    
    def create_results_section(self, layout: QVBoxLayout):
        """Створення секції результатів"""
        # Заголовок секції
        results_label = QLabel("Інформація")
        results_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        results_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                margin-top: 12px;
                margin-bottom: 8px;
                font-weight: bold;
                background: none;
                border: none;
            }
        """)
        layout.addWidget(results_label)
        
        # Текстова область для результатів
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(120)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #dee2e6;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
                color: #495057;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.results_text)
    
    def create_button(self, text: str, button_type: str = "normal") -> QPushButton:
        """Створення стилізованої кнопки"""
        button = QPushButton(text)
        
        base_style = """
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
        """
        
        if button_type == "primary":
            base_style += """
                QPushButton {
                    background-color: #495057;
                    color: white;
                    font-weight: 600;
                    border: 2px solid #212529;
                }
                QPushButton:hover {
                    background-color: #343a40;
                    border: 2px solid #343a40;
                }
                QPushButton:pressed {
                    background-color: #212529;
                }
            """
        elif button_type == "warning":
            base_style += """
                QPushButton {
                    background-color: #fd7e14;
                    color: white;
                    border: 2px solid #e76a00;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #e76a00;
                    border: 2px solid #dc6502;
                }
            """
        elif button_type == "danger":
            base_style += """
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: 2px solid #c82333;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #c82333;
                    border: 2px solid #bd2130;
                }
            """
        
        button.setStyleSheet(base_style)
        return button
    
    def get_input_style(self) -> str:
        """Стиль для полів введення"""
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
            QDateEdit::down-arrow:hover {
                border-top-color: #495057;
            }
        """
    
    def add_separator(self, layout: QVBoxLayout):
        """Додавання розділювача"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #dee2e6; margin: 12px 0px;")
        layout.addWidget(separator)
    
    def setup_connections(self):
        """Налаштування зв'язків сигналів"""
        # Файлові операції
        self.open_image_btn.clicked.connect(self.open_image_requested.emit)
        self.open_folder_btn.clicked.connect(self.open_folder_requested.emit)
        self.save_image_btn.clicked.connect(self.save_image_requested.emit)
        
        # Управління документом
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        self.document_date_edit.dateChanged.connect(self.on_document_date_changed)
        self.today_btn.clicked.connect(self.set_date_today)
        
        # Управління шаблонами
        self.create_template_btn.clicked.connect(self.create_new_template)
        self.edit_template_btn.clicked.connect(self.edit_current_template)
        
        # Пакетна обробка
        self.save_current_btn.clicked.connect(self.save_current_image)
        self.cancel_current_btn.clicked.connect(self.cancel_current_changes)
        self.clear_all_btn.clicked.connect(self.clear_all_changes)
        self.create_album_btn.clicked.connect(self.create_album_requested.emit)
    
    def load_templates(self):
        """Завантаження списку шаблонів"""
        try:
            template_names = list_template_files()
            
            self.template_combo.clear()
            if template_names:
                self.template_combo.addItems(template_names)
                self.current_template = template_names[0] if template_names else None
            else:
                self.template_combo.addItem("Базовий шаблон")
                self.current_template = "Базовий шаблон"
                
            self.add_result(f"Завантажено {len(template_names)} шаблонів")
            
        except Exception as e:
            self.add_result(f"Помилка завантаження шаблонів: {e}")
    
    def on_template_changed(self, template_name: str):
        """Обробка зміни шаблону"""
        if template_name:
            self.current_template = template_name
            self.template_changed.emit(template_name)
            self.add_result(f"Обрано шаблон: {template_name}")
    
    def on_document_date_changed(self, date: QDate):
        """Обробка зміни дати документу"""
        self.document_date = date
        self.document_date_changed.emit(date)
        self.add_result(f"Дата документу: {date.toString('dd.MM.yyyy')}")
    
    def set_date_today(self):
        """Встановлення поточної дати"""
        today = QDate.currentDate()
        self.document_date_edit.setDate(today)
        self.add_result(f"Встановлено сьогоднішню дату: {today.toString('dd.MM.yyyy')}")
    
    def create_new_template(self):
        """Створення нового шаблону (заглушка)"""
        QMessageBox.information(self, "Інформація", 
                               "Функція створення шаблону буде реалізована пізніше")
    
    def edit_current_template(self):
        """Редагування поточного шаблону (заглушка)"""
        if not self.current_template:
            QMessageBox.warning(self, "Попередження", "Немає обраного шаблону")
            return
        
        QMessageBox.information(self, "Інформація", 
                               f"Функція редагування шаблону '{self.current_template}' буде реалізована пізніше")
    
    def save_current_image(self):
        """Збереження поточного зображення до альбому (заглушка)"""
        self.processed_count += 1
        self.add_result(f"Зображення додано до альбому (#{self.processed_count})")
    
    def cancel_current_changes(self):
        """Скасування змін поточного зображення (заглушка)"""
        self.add_result("Зміни поточного зображення скасовано")
    
    def clear_all_changes(self):
        """Очищення всіх змін (заглушка)"""
        if self.processed_count > 0:
            reply = QMessageBox.question(self, "Підтвердження",
                                       f"Очистити всі {self.processed_count} оброблених зображень?",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.processed_count = 0
                self.add_result("Всі зміни очищено")
        else:
            self.add_result("Немає змін для очищення")
    
    def update_current_image_info(self, image_path: str):
        """Оновлення інформації про поточне зображення"""
        self.current_image_info = image_path
        filename = os.path.basename(image_path)
        self.add_result(f"Завантажено: {filename}")
    
    def update_analysis_results(self, analysis_point: AnalysisPoint):
        """Оновлення результатів аналізу"""
        self.add_result(f"Точка аналізу: ({analysis_point.x}, {analysis_point.y})")
        self.add_result(f"Азимут: {analysis_point.azimuth:.0f}°, Дальність: {analysis_point.range_km:.0f} км")
    
    def add_result(self, text: str):
        """Додавання тексту до області результатів"""
        self.results_text.append(text)
        
        # Автоматичне прокручування вниз
        scrollbar = self.results_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_results(self):
        """Очищення області результатів"""
        self.results_text.clear()