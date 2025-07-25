#!/usr/bin/env python3
"""
PhotoControl v2.0 - Ліва панель управління
Інтеграція файлових операцій, пакетної обробки та результатів
"""

import os
from typing import Optional, List, Callable
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFrame, QFileDialog, QMessageBox, QTextEdit,
                             QScrollArea, QComboBox, QDateEdit, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont

from core.constants import UI, FILES
from translations.translator import get_translator, TranslationKeys, Language


class ControlPanel(QWidget):
    """
    Ліва панель управління PhotoControl v2.0
    
    Функціональність:
    - Файлові операції (відкриття зображень/папок, збереження)
    - Пакетна обробка зображень
    - Управління шаблонами документів
    - Налаштування дати та опису РЛС
    - Область результатів з прокруткою
    - Система перекладів
    """
    
    # Сигнали для взаємодії з головним вікном
    open_image_requested = pyqtSignal()
    open_folder_requested = pyqtSignal()
    save_image_requested = pyqtSignal()
    create_album_requested = pyqtSignal()
    save_current_data_requested = pyqtSignal()
    template_created_requested = pyqtSignal()
    template_edited_requested = pyqtSignal()
    language_changed = pyqtSignal(Language)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Система перекладів
        self.translator = get_translator()
        
        # Налаштування панелі
        self.setFixedWidth(UI.CONTROL_PANEL_WIDTH)
        self.setStyleSheet(self._get_panel_styles())
        
        # Створення UI
        self._create_ui()
        
        # Підключення перекладів
        self.translator.language_changed.connect(self._update_translations)
        
        print("ControlPanel створено")
    
    def _create_ui(self):
        """Створення інтерфейсу панелі"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Заголовок панелі
        self._create_title(layout)
        
        # Файлові операції
        self._create_file_operations_section(layout)
        
        # Розділювач
        layout.addWidget(self._create_separator())
        
        # Пакетна обробка
        self._create_batch_processing_section(layout)
        
        # Розділювач
        layout.addWidget(self._create_separator())
        
        # Титульна сторінка та шаблони
        self._create_title_page_section(layout)
        
        # Розділювач
        layout.addWidget(self._create_separator())
        
        # Область результатів
        self._create_results_section(layout)
        
        # Налаштування мови (в нижній частині)
        layout.addWidget(self._create_separator())
        self._create_language_section(layout)
        
        # Розтягування знизу
        layout.addStretch()
    
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
    
    def _create_file_operations_section(self, layout: QVBoxLayout):
        """Створення секції файлових операцій"""
        # Заголовок секції
        self.file_ops_label = QLabel()
        self.file_ops_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.file_ops_label.setStyleSheet("color: #666; margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(self.file_ops_label)
        
        # Кнопки файлових операцій
        self.open_image_btn = QPushButton()
        self.open_image_btn.clicked.connect(self.open_image_requested.emit)
        layout.addWidget(self.open_image_btn)
        
        self.open_folder_btn = QPushButton()
        self.open_folder_btn.clicked.connect(self.open_folder_requested.emit)
        layout.addWidget(self.open_folder_btn)
        
        self.save_image_btn = QPushButton()
        self.save_image_btn.clicked.connect(self.save_image_requested.emit)
        layout.addWidget(self.save_image_btn)
    
    def _create_batch_processing_section(self, layout: QVBoxLayout):
        """Створення секції пакетної обробки"""
        # Заголовок секції
        self.batch_label = QLabel()
        self.batch_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.batch_label.setStyleSheet("color: #666; margin-top: 5px; margin-bottom: 5px;")
        layout.addWidget(self.batch_label)
        
        # Кнопка збереження поточних даних
        self.save_current_btn = QPushButton()
        self.save_current_btn.clicked.connect(self.save_current_data_requested.emit)
        layout.addWidget(self.save_current_btn)
        
        # Головна кнопка створення альбому
        self.create_album_btn = QPushButton()
        self.create_album_btn.clicked.connect(self.create_album_requested.emit)
        self.create_album_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold; 
                background-color: #4CAF50; 
                color: white;
                border: 1px solid #45a049;
                border-radius: 6px;
                padding: 10px 12px;
                min-height: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
            }
            QPushButton:hover {
                background-color: #45a049;
                box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
            }
            QPushButton:pressed {
                background-color: #3d8b40;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
            }
        """)
        layout.addWidget(self.create_album_btn)
    
    def _create_title_page_section(self, layout: QVBoxLayout):
        """Створення секції титульної сторінки"""
        # Заголовок секції
        self.title_page_label = QLabel()
        self.title_page_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.title_page_label.setStyleSheet("color: #666; margin-top: 5px; margin-bottom: 5px;")
        layout.addWidget(self.title_page_label)
        
        # Вибір дати документу
        date_layout = QHBoxLayout()
        self.date_label = QLabel()
        self.date_label.setStyleSheet("color: #555; font-size: 10px;")
        date_layout.addWidget(self.date_label)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("""
            QDateEdit {
                border: 1px solid #c1c1c1;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                font-size: 10px;
            }
        """)
        date_layout.addWidget(self.date_edit)
        
        date_widget = QWidget()
        date_widget.setLayout(date_layout)
        layout.addWidget(date_widget)
        
        # Кнопки управління шаблонами
        self.create_template_btn = QPushButton()
        self.create_template_btn.clicked.connect(self.template_created_requested.emit)
        layout.addWidget(self.create_template_btn)
        
        self.edit_template_btn = QPushButton()
        self.edit_template_btn.clicked.connect(self.template_edited_requested.emit)
        layout.addWidget(self.edit_template_btn)
    
    def _create_results_section(self, layout: QVBoxLayout):
        """Створення секції результатів з прокруткою"""
        # Заголовок секції
        self.results_label = QLabel()
        self.results_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.results_label.setStyleSheet("color: #666; margin-top: 5px; margin-bottom: 5px;")
        layout.addWidget(self.results_label)
        
        # Область результатів з прокруткою
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(150)
        self.results_text.setMinimumHeight(100)
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: #fafafa;
                font-family: Consolas, monospace;
                font-size: 9px;
                color: #333;
            }
        """)
        layout.addWidget(self.results_text)
    
    def _create_language_section(self, layout: QVBoxLayout):
        """Створення секції вибору мови"""
        # Заголовок
        lang_label = QLabel("Мова / Language:")
        lang_label.setFont(QFont("Arial", 9))
        lang_label.setStyleSheet("color: #666; margin-top: 5px; margin-bottom: 3px;")
        layout.addWidget(lang_label)
        
        # Комбобокс вибору мови
        self.language_combo = QComboBox()
        self.language_combo.addItem("🇺🇦 Українська", Language.UKRAINIAN)
        self.language_combo.addItem("🇺🇸 English", Language.ENGLISH)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        self.language_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #c1c1c1;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                font-size: 10px;
                min-height: 16px;
            }
        """)
        layout.addWidget(self.language_combo)
    
    def _create_separator(self) -> QFrame:
        """Створення горизонтального розділювача"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #ccc; margin: 10px 0px;")
        return separator
    
    def _get_panel_styles(self) -> str:
        """Отримання стилів для панелі"""
        return """
            QWidget {
                background-color: #f5f5f5; 
                border-right: 1px solid #ccc;
                color: #333;
            }
            QPushButton {
                background-color: #e1e1e1;
                border: 1px solid #c1c1c1;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
                min-height: 16px;
            }
            QPushButton:hover {
                background-color: #d1d1d1;
                border: 1px solid #b1b1b1;
            }
            QPushButton:pressed {
                background-color: #c1c1c1;
            }
            QComboBox {
                border: 1px solid #c1c1c1;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                font-size: 11px;
            }
            QLabel {
                background: none;
                border: none;
                color: #333;
            }
        """
    
    # ===============================
    # ПУБЛІЧНІ МЕТОДИ
    # ===============================
    
    def add_result(self, message: str):
        """Додати повідомлення до області результатів"""
        self.results_text.append(f"• {message}")
        # Прокрутка до кінця
        cursor = self.results_text.textCursor()
        cursor.movePosition(cursor.End)
        self.results_text.setTextCursor(cursor)
    
    def clear_results(self):
        """Очистити область результатів"""
        self.results_text.clear()
    
    def get_document_date(self) -> str:
        """Отримати вибрану дату документу"""
        return self.date_edit.date().toString("dd.MM.yyyy")
    
    def set_document_date(self, date_str: str):
        """Встановити дату документу"""
        try:
            date = QDate.fromString(date_str, "dd.MM.yyyy")
            self.date_edit.setDate(date)
        except:
            self.date_edit.setDate(QDate.currentDate())
    
    def set_buttons_enabled(self, save_image: bool = True, create_album: bool = True, 
                           save_current: bool = True):
        """Управління доступністю кнопок"""
        self.save_image_btn.setEnabled(save_image)
        self.create_album_btn.setEnabled(create_album)
        self.save_current_btn.setEnabled(save_current)
    
    def get_current_language(self) -> Language:
        """Отримати поточну мову"""
        return self.language_combo.currentData()
    
    def set_current_language(self, language: Language):
        """Встановити поточну мову"""
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == language:
                self.language_combo.setCurrentIndex(i)
                break
    
    # ===============================
    # ПРИВАТНІ МЕТОДИ
    # ===============================
    
    def _on_language_changed(self):
        """Обробка зміни мови"""
        current_language = self.language_combo.currentData()
        if current_language:
            self.language_changed.emit(current_language)
    
    def _update_translations(self):
        """Оновлення перекладів інтерфейсу"""
        tr = self.translator.tr
        
        # Заголовки секцій
        self.title_label.setText(tr(TranslationKeys.CONTROLS))
        self.file_ops_label.setText(tr(TranslationKeys.FILE_OPERATIONS))
        self.batch_label.setText(tr(TranslationKeys.BATCH_PROCESSING))
        self.title_page_label.setText(tr(TranslationKeys.TITLE_PAGE))
        self.results_label.setText(tr(TranslationKeys.RESULTS))
        
        # Кнопки
        self.open_image_btn.setText(tr(TranslationKeys.OPEN_IMAGE))
        self.open_folder_btn.setText(tr(TranslationKeys.OPEN_FOLDER))
        self.save_image_btn.setText(tr(TranslationKeys.SAVE_CURRENT_IMAGE))
        self.save_current_btn.setText(tr(TranslationKeys.SAVE_CURRENT_IMAGE_DATA))
        self.create_album_btn.setText(tr(TranslationKeys.CREATE_NEW_ALBUM))
        
        # Шаблони
        self.create_template_btn.setText("Створити новий шаблон")
        self.edit_template_btn.setText("Редагувати шаблон")
        
        # Дата
        self.date_label.setText(tr(TranslationKeys.DOCUMENT_DATE) + ":")
    
    # ===============================
    # СТАТИЧНІ МЕТОДИ ДЛЯ ТЕСТУВАННЯ
    # ===============================
    
    @staticmethod
    def create_test_panel() -> "ControlPanel":
        """Створення тестової панелі з демо-даними"""
        panel = ControlPanel()
        
        # Додавання тестових результатів
        panel.add_result("Програма запущена")
        panel.add_result("Готова до роботи")
        panel.add_result("Ліва панель створена успішно")
        
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
            self.setWindowTitle("Тестування ControlPanel")
            self.setGeometry(100, 100, 800, 600)
            
            # Центральний віджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QHBoxLayout(central_widget)
            
            # Ліва панель управління
            self.control_panel = ControlPanel.create_test_panel()
            layout.addWidget(self.control_panel)
            
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
            
            # Підключення сигналів для тестування
            self.control_panel.open_image_requested.connect(
                lambda: self.control_panel.add_result("Запит на відкриття зображення")
            )
            self.control_panel.open_folder_requested.connect(
                lambda: self.control_panel.add_result("Запит на відкриття папки")
            )
            self.control_panel.save_image_requested.connect(
                lambda: self.control_panel.add_result("Запит на збереження зображення")
            )
            self.control_panel.create_album_requested.connect(
                lambda: self.control_panel.add_result("Запит на створення альбому")
            )
            self.control_panel.save_current_data_requested.connect(
                lambda: self.control_panel.add_result("Запит на збереження поточних даних")
            )
            self.control_panel.language_changed.connect(
                lambda lang: self.control_panel.add_result(f"Мова змінена на: {lang.value}")
            )
            
            print("Тестове вікно ControlPanel створено")
    
    # Запуск тесту
    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    
    print("=== Тестування ControlPanel ===")
    print("Функції для тестування:")
    print("1. Кнопки файлових операцій")
    print("2. Кнопки пакетної обробки")
    print("3. Вибір дати документу")
    print("4. Область результатів з прокруткою")
    print("5. Зміна мови інтерфейсу")
    
    sys.exit(app.exec_())