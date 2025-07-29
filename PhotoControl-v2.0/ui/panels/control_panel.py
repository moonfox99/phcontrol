#!/usr/bin/env python3
"""
PhotoControl v2.0 - Ліва панель управління (ВИПРАВЛЕНА ВЕРСІЯ)
Повна реалізація файлових операцій, пакетної обробки та результатів
"""

import os
from datetime import datetime
from typing import Optional, List, Callable
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFrame, QFileDialog, QMessageBox, QTextEdit,
                             QScrollArea, QComboBox, QDateEdit, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont

# Безпечні імпорти
try:
    from core.constants import UI, FILES
    print("✅ Constants завантажено в ControlPanel")
except ImportError:
    print("⚠️ Constants недоступний, використовуємо fallback")
    class UI:
        CONTROL_PANEL_WIDTH = 250
    class FILES:
        SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']

try:
    from translations.translator import get_translator, TranslationKeys, Language
    print("✅ Translator завантажено в ControlPanel")
except ImportError:
    print("⚠️ Translator недоступний")
    get_translator = None
    TranslationKeys = None
    Language = None


class ControlPanel(QWidget):
    """
    ВИПРАВЛЕНА ліва панель управління PhotoControl v2.0
    
    Функціональність:
    - Файлові операції (відкриття зображень/папок, збереження)
    - Пакетна обробка зображень
    - Управління шаблонами документів
    - Налаштування дати документу
    - Область результатів з прокруткою та логуванням
    - Система перекладів (якщо доступна)
    """
    
    # Сигнали для взаємодії з головним вікном
    open_image_requested = pyqtSignal()
    open_folder_requested = pyqtSignal()
    save_image_requested = pyqtSignal()
    create_album_requested = pyqtSignal()
    save_current_data_requested = pyqtSignal()
    template_created_requested = pyqtSignal()
    template_edited_requested = pyqtSignal()
    language_changed = pyqtSignal(str) # Використовуємо str замість Language enum
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        print("📋 Створення ControlPanel...")
        
        # Система перекладів
        self.translator = get_translator() if get_translator else None
        
        # Налаштування панелі
        self.setFixedWidth(UI.CONTROL_PANEL_WIDTH)
        self.setStyleSheet(self._get_panel_styles())
        
        # Створення UI
        self._create_ui()
        
        # Підключення перекладів
        if self.translator:
            self.translator.language_changed.connect(self._update_translations)
        
        print("✅ ControlPanel створено успішно!")
    
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
        if Language:
            layout.addWidget(self._create_separator())
            self._create_language_section(layout)
        
        # Розтягування знизу
        layout.addStretch()
        
        # Додавання початкових повідомлень
        self.add_result("PhotoControl v2.0 запущено")
        self.add_result("Панель управління готова")
    
    def _create_title(self, layout: QVBoxLayout):
        """Створення заголовка панелі"""
        self.title_label = QLabel("Управління")
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
        self.file_ops_label = QLabel("Файлові операції")
        self.file_ops_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.file_ops_label.setStyleSheet("color: #666; margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(self.file_ops_label)
        
        # Кнопки файлових операцій
        self.open_image_btn = QPushButton("Відкрити зображення")
        self.open_image_btn.setToolTip("Відкрити одне зображення для обробки (Ctrl+O)")
        self.open_image_btn.clicked.connect(self._on_open_image_clicked)
        layout.addWidget(self.open_image_btn)
        
        self.open_folder_btn = QPushButton("Відкрити папку")
        self.open_folder_btn.setToolTip("Відкрити папку з зображеннями (Ctrl+Shift+O)")
        self.open_folder_btn.clicked.connect(self._on_open_folder_clicked)
        layout.addWidget(self.open_folder_btn)
        
        self.save_image_btn = QPushButton("Зберегти зображення")
        self.save_image_btn.setToolTip("Зберегти оброблене зображення (Ctrl+S)")
        self.save_image_btn.clicked.connect(self._on_save_image_clicked)
        self.save_image_btn.setEnabled(False)  # За замовчуванням неактивна
        layout.addWidget(self.save_image_btn)
    
    def _create_batch_processing_section(self, layout: QVBoxLayout):
        """ЗАВЕРШЕНИЙ метод створення секції пакетної обробки"""
        # Заголовок секції
        self.batch_label = QLabel("Пакетна обробка")
        self.batch_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.batch_label.setStyleSheet("color: #666; margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(self.batch_label)
        
        # Кнопка збереження поточних даних
        self.save_current_btn = QPushButton("Зберегти дані поточного зображення")
        self.save_current_btn.setToolTip("Зберегти дані поточного зображення для альбому (Ctrl+D)")
        self.save_current_btn.clicked.connect(self._on_save_current_data_clicked)
        self.save_current_btn.setEnabled(False)  # За замовчуванням неактивна
        layout.addWidget(self.save_current_btn)
        
        # Кнопка створення альбому
        self.create_album_btn = QPushButton("Створити альбом")
        self.create_album_btn.setToolTip("Створити Word документ з оброблених зображень (Ctrl+A)")
        self.create_album_btn.clicked.connect(self._on_create_album_clicked)
        self.create_album_btn.setEnabled(False)  # За замовчуванням неактивна
        layout.addWidget(self.create_album_btn)
        
        # Лічильник оброблених зображень
        self.processed_count_label = QLabel("Оброблено зображень: 0")
        self.processed_count_label.setStyleSheet("color: #666; font-size: 11px; margin-top: 5px;")
        layout.addWidget(self.processed_count_label)
    
    def _create_title_page_section(self, layout: QVBoxLayout):
        """Створення секції титульної сторінки"""
        # Заголовок секції
        self.title_page_label = QLabel("Титульна сторінка")
        self.title_page_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.title_page_label.setStyleSheet("color: #666; margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(self.title_page_label)
        
        # Дата документу
        date_layout = QHBoxLayout()
        self.date_label = QLabel("Дата документу:")
        self.date_label.setStyleSheet("font-size: 11px;")
        date_layout.addWidget(self.date_label)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.setToolTip("Дата для титульної сторінки альбому")
        self.date_edit.setStyleSheet("""
            QDateEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
            }
        """)
        date_layout.addWidget(self.date_edit)
        
        layout.addLayout(date_layout)
        
        # Кнопки управління шаблонами
        self.create_template_btn = QPushButton("Створити новий шаблон")
        self.create_template_btn.setToolTip("Створити новий шаблон титульної сторінки")
        self.create_template_btn.clicked.connect(self._on_create_template_clicked)
        layout.addWidget(self.create_template_btn)
        
        self.edit_template_btn = QPushButton("Редагувати шаблон")
        self.edit_template_btn.setToolTip("Редагувати існуючий шаблон")
        self.edit_template_btn.clicked.connect(self._on_edit_template_clicked)
        layout.addWidget(self.edit_template_btn)
    
    def _create_results_section(self, layout: QVBoxLayout):
        """Створення секції результатів"""
        # Заголовок секції
        self.results_label = QLabel("Результати")
        self.results_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.results_label.setStyleSheet("color: #666; margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(self.results_label)
        
        # Текстова область з прокруткою
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.results_text)
        
        # Кнопка очищення результатів
        clear_results_layout = QHBoxLayout()
        self.clear_results_btn = QPushButton("Очистити")
        self.clear_results_btn.setMaximumWidth(80)
        self.clear_results_btn.setToolTip("Очистити область результатів")
        self.clear_results_btn.clicked.connect(self._on_clear_results_clicked)
        clear_results_layout.addStretch()
        clear_results_layout.addWidget(self.clear_results_btn)
        
        layout.addLayout(clear_results_layout)
    
    def _create_language_section(self, layout: QVBoxLayout):
        """Створення секції вибору мови"""
        # Заголовок секції
        language_label = QLabel("Мова інтерфейсу")
        language_label.setFont(QFont("Arial", 10, QFont.Bold))
        language_label.setStyleSheet("color: #666; margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(language_label)
        
        # Комбобокс вибору мови
        self.language_combo = QComboBox()
        self.language_combo.addItem("Українська", "ukrainian")
        self.language_combo.addItem("English", "english")
        self.language_combo.setToolTip("Вибір мови інтерфейсу програми")
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        self.language_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.language_combo)
    
    def _create_separator(self) -> QFrame:
        """Створення горизонтального розділювача"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #dee2e6;")
        return separator
    
    def _get_panel_styles(self) -> str:
        """Стилі для панелі"""
        return """
            ControlPanel {
                background-color: #f8f9fa;
                border-right: 1px solid #dee2e6;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                min-height: 20px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                color: #6c757d;
                border-color: #dee2e6;
            }
        """
    
    # ===============================
    # ОБРОБНИКИ ПОДІЙ КНОПОК
    # ===============================
    
    def _on_open_image_clicked(self):
        """Обробка кнопки відкриття зображення"""
        self.add_result("🖼️ Запит на відкриття зображення")
        self.open_image_requested.emit()
    
    def _on_open_folder_clicked(self):
        """Обробка кнопки відкриття папки"""
        self.add_result("📁 Запит на відкриття папки")
        self.open_folder_requested.emit()
    
    def _on_save_image_clicked(self):
        """Обробка кнопки збереження зображення"""
        self.add_result("💾 Запит на збереження зображення")
        self.save_image_requested.emit()
    
    def _on_save_current_data_clicked(self):
        """Обробка кнопки збереження поточних даних"""
        self.add_result("📋 Запит на збереження даних поточного зображення")
        self.save_current_data_requested.emit()
    
    def _on_create_album_clicked(self):
        """Обробка кнопки створення альбому"""
        self.add_result("📄 Запит на створення альбому")
        self.create_album_requested.emit()
    
    def _on_create_template_clicked(self):
        """Обробка кнопки створення шаблону"""
        self.add_result("📝 Запит на створення нового шаблону")
        self.template_created_requested.emit()
    
    def _on_edit_template_clicked(self):
        """Обробка кнопки редагування шаблону"""
        self.add_result("✏️ Запит на редагування шаблону")
        self.template_edited_requested.emit()
    
    def _on_clear_results_clicked(self):
        """Очищення області результатів"""
        self.results_text.clear()
        self.add_result("🗑️ Результати очищено")
    
    def _on_language_changed(self, index: int):
        """Обробка зміни мови"""
        language_code = self.language_combo.itemData(index)
        if language_code:
            self.add_result(f"🌐 Мова змінена на: {language_code}")
            self.language_changed.emit(language_code)
    
    # ===============================
    # ПУБЛІЧНІ МЕТОДИ
    # ===============================
    
    def add_result(self, message: str):
        """
        Додавання повідомлення до області результатів з часовою міткою
        
        Args:
            message: Повідомлення для додавання
        """
        if hasattr(self, 'results_text'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            
            self.results_text.append(formatted_message)
            
            # Автоматичне прокручування вниз
            scrollbar = self.results_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
            print(f"📋 ControlPanel: {message}")
    
    def set_buttons_enabled(self, save_image=None, save_data=None, create_album=None):
        """
        Увімкнення/вимкнення кнопок залежно від стану програми
        
        Args:
            save_image: Стан кнопки збереження зображення
            save_data: Стан кнопки збереження даних
            create_album: Стан кнопки створення альбому
        """
        if save_image is not None:
            self.save_image_btn.setEnabled(save_image)
        
        if save_data is not None:
            self.save_current_btn.setEnabled(save_data)
        
        if create_album is not None:
            self.create_album_btn.setEnabled(create_album)
    
    def update_processed_count(self, count: int):
        """
        Оновлення лічильника оброблених зображень
        
        Args:
            count: Кількість оброблених зображень
        """
        if hasattr(self, 'processed_count_label'):
            self.processed_count_label.setText(f"Оброблено зображень: {count}")
        
        # Активація кнопки створення альбому якщо є оброблені зображення
        if hasattr(self, 'create_album_btn'):
            self.create_album_btn.setEnabled(count > 0)
    
    def get_document_date(self) -> str:
        """
        Отримання обраної дати документу
        
        Returns:
            Дата в форматі dd.MM.yyyy
        """
        if hasattr(self, 'date_edit'):
            return self.date_edit.date().toString("dd.MM.yyyy")
        return datetime.now().strftime("%d.%m.%Y")
    
    def set_document_date(self, date_str: str):
        """
        Встановлення дати документу
        
        Args:
            date_str: Дата в форматі dd.MM.yyyy
        """
        if hasattr(self, 'date_edit'):
            try:
                date = QDate.fromString(date_str, "dd.MM.yyyy")
                if date.isValid():
                    self.date_edit.setDate(date)
                    self.add_result(f"📅 Дата встановлена: {date_str}")
            except Exception as e:
                self.add_result(f"❌ Помилка встановлення дати: {e}")
    
    def get_current_language(self) -> str:
        """
        Отримання поточної мови
        
        Returns:
            Код поточної мови
        """
        if hasattr(self, 'language_combo'):
            return self.language_combo.currentData() or "ukrainian"
        return "ukrainian"
    
    def set_language(self, language_code: str):
        """
        Встановлення мови інтерфейсу
        
        Args:
            language_code: Код мови (ukrainian, english)
        """
        if hasattr(self, 'language_combo'):
            for i in range(self.language_combo.count()):
                if self.language_combo.itemData(i) == language_code:
                    self.language_combo.setCurrentIndex(i)
                    break
    
    # ===============================
    # СИСТЕМА ПЕРЕКЛАДІВ
    # ===============================
    
    def _update_translations(self):
        """Оновлення перекладів інтерфейсу"""
        if not self.translator:
            return
        
        # Використовуємо базові переклади якщо TranslationKeys недоступний
        tr = self.translator.tr if hasattr(self.translator, 'tr') else lambda x: x
        
        # Заголовки
        if hasattr(self, 'title_label'):
            self.title_label.setText("Управління")
        
        if hasattr(self, 'file_ops_label'):
            self.file_ops_label.setText("Файлові операції")
        
        if hasattr(self, 'batch_label'):
            self.batch_label.setText("Пакетна обробка")
        
        if hasattr(self, 'title_page_label'):
            self.title_page_label.setText("Титульна сторінка")
        
        if hasattr(self, 'results_label'):
            self.results_label.setText("Результати")
        
        # Кнопки
        if hasattr(self, 'open_image_btn'):
            self.open_image_btn.setText("Відкрити зображення")
        
        if hasattr(self, 'open_folder_btn'):
            self.open_folder_btn.setText("Відкрити папку")
        
        if hasattr(self, 'save_image_btn'):
            self.save_image_btn.setText("Зберегти зображення")
        
        if hasattr(self, 'save_current_btn'):
            self.save_current_btn.setText("Зберегти дані поточного зображення")
        
        if hasattr(self, 'create_album_btn'):
            self.create_album_btn.setText("Створити альбом")
        
        # Шаблони
        if hasattr(self, 'create_template_btn'):
            self.create_template_btn.setText("Створити новий шаблон")
        
        if hasattr(self, 'edit_template_btn'):
            self.edit_template_btn.setText("Редагувати шаблон")
        
        # Дата
        if hasattr(self, 'date_label'):
            self.date_label.setText("Дата документу:")
        
        self.add_result("🌐 Переклади оновлено")
    
    # ===============================
    # СТАТИЧНІ МЕТОДИ ДЛЯ ТЕСТУВАННЯ
    # ===============================
    
    @staticmethod
    def create_test_panel() -> "ControlPanel":
        """Створення тестової панелі з демо-даними"""
        panel = ControlPanel()
        
        # Додавання тестових результатів
        panel.add_result("🧪 Тестова панель створена")
        panel.add_result("📋 Всі компоненти готові")
        panel.add_result("✅ Готова до тестування")
        
        # Активація деяких кнопок для тестування
        panel.set_buttons_enabled(save_image=True, save_data=True)
        panel.update_processed_count(3)
        
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
            self.setWindowTitle("Тестування ControlPanel v2.0")
            self.setGeometry(100, 100, 900, 600)
            
            # Центральний віджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QHBoxLayout(central_widget)
            
            # Ліва панель управління
            self.control_panel = ControlPanel.create_test_panel()
            layout.addWidget(self.control_panel)
            
            # Центральна область (заглушка)
            center_label = QLabel("Центральна область\n\n(тут буде панель зображення)\n\nТестуйте кнопки в лівій панелі!")
            center_label.setAlignment(Qt.AlignCenter)
            center_label.setStyleSheet("""
                background-color: white; 
                border: 1px solid #ddd;
                color: #666;
                font-size: 14px;
                border-radius: 8px;
                margin: 10px;
            """)
            layout.addWidget(center_label)
            
            # Підключення сигналів для тестування
            self.control_panel.open_image_requested.connect(
                lambda: self.control_panel.add_result("✅ Сигнал: відкриття зображення")
            )
            self.control_panel.open_folder_requested.connect(
                lambda: self.control_panel.add_result("✅ Сигнал: відкриття папки")
            )
            self.control_panel.save_image_requested.connect(
                lambda: self.control_panel.add_result("✅ Сигнал: збереження зображення")
            )
            self.control_panel.create_album_requested.connect(
                lambda: self.control_panel.add_result("✅ Сигнал: створення альбому")
            )
            self.control_panel.save_current_data_requested.connect(
                lambda: self.control_panel.add_result("✅ Сигнал: збереження поточних даних")
            )
            self.control_panel.template_created_requested.connect(
                lambda: self.control_panel.add_result("✅ Сигнал: створення шаблону")
            )
            self.control_panel.template_edited_requested.connect(
                lambda: self.control_panel.add_result("✅ Сигнал: редагування шаблону")
            )
            self.control_panel.language_changed.connect(
                lambda lang: self.control_panel.add_result(f"✅ Сигнал: мова змінена на {lang}")
            )
            
            print("✅ Тестове вікно ControlPanel створено")
    
    # Запуск тесту
    app = QApplication(sys.argv)
    app.setApplicationName("ControlPanel Test")
    
    window = TestMainWindow()
    window.show()
    
    print("\n" + "=" * 60)
    print("🧪 ТЕСТУВАННЯ CONTROLPANEL")
    print("=" * 60)
    print("\n📋 Що тестувати:")
    print("1. 🖼️ Кнопки файлових операцій")
    print("2. 📋 Кнопки пакетної обробки")
    print("3. 📅 Вибір дати документу")
    print("4. 📝 Кнопки управління шаблонами")
    print("5. 🌐 Зміна мови інтерфейсу")
    print("6. 🗑️ Кнопка очищення результатів")
    print("7. 📊 Область результатів з логуванням")
    print("\n✅ Всі кнопки повинні генерувати повідомлення в області результатів")
    print("🔗 Перевірте що всі сигнали працюють коректно")
    print("\n" + "=" * 60)
    
    sys.exit(app.exec_())