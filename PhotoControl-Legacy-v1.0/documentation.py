# ЗАМІНА WEBBROWSER НА БЕЗПЕЧНИЙ ЛОКАЛЬНИЙ ПЕРЕГЛЯД

# ПРОБЛЕМА: webbrowser намагається з'єднатися з інтернетом
# РІШЕННЯ: Створюємо власний локальний перегляд документації

# 1. ЗАМІНІТЬ documentation.py НА ЦЮ ВЕРСІЮ:

import os
import tempfile
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont

class DocumentationManager:
    """Менеджер документації програми Фотоконтроль БЕЗ веб-браузера"""
    
    def __init__(self):
        self.docs_dir = os.path.join(os.path.expanduser("~"), "PhotoControl_Docs")
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)
        
        # Шляхи до файлів документації
        self.html_file = os.path.join(self.docs_dir, "PhotoControl_Documentation.html")
        self.txt_file = os.path.join(self.docs_dir, "PhotoControl_Documentation.txt")
        self.version = "1.0"
    
    def create_documentation_files(self):
        """Створення всіх файлів документації"""
        success = True
        
        # Створюємо HTML документацію (для QTextBrowser)
        try:
            self._create_simple_html_documentation()
        except Exception as e:
            print(f"Error creating HTML documentation: {e}")
            success = False
        
        # Створюємо текстову документацію
        try:
            self._create_text_documentation()
        except Exception as e:
            print(f"Error creating text documentation: {e}")
            success = False
        
        # Створюємо README файл
        try:
            self._create_readme_file()
        except Exception as e:
            print(f"Error creating README: {e}")
            success = False
        
        return success
    
    def show_documentation(self):
        """Відкриття документації у власному вікні (БЕЗ веб-браузера)"""
        try:
            # Перевіряємо чи існують файли документації
            if not os.path.exists(self.html_file):
                self.create_documentation_files()
            
            # Створюємо власне вікно документації
            doc_dialog = DocumentationDialog(self.html_file, self.txt_file)
            doc_dialog.exec_()
            return True
            
        except Exception as e:
            print(f"Error opening documentation: {e}")
            # Fallback - відкриваємо README у Блокноті
            try:
                os.startfile(self.docs_dir)  # Відкриє папку в провіднику
                return True
            except:
                QMessageBox.warning(None, "Помилка", 
                                  f"Не вдалося відкрити документацію.\n"
                                  f"Файли знаходяться в: {self.docs_dir}")
                return False
    
    def _create_simple_html_documentation(self):
        """Створення спрощеної HTML документації для QTextBrowser"""
        html_content = self._get_simple_html_content()
        
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Simple HTML documentation created: {self.html_file}")
    
    def _create_text_documentation(self):
        """Створення текстової версії документації"""
        text_content = self._get_text_content()
        
        with open(self.txt_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        print(f"✓ Text documentation created: {self.txt_file}")
    
    def _create_readme_file(self):
        """Створення README файлу"""
        readme_path = os.path.join(self.docs_dir, "README.txt")
        readme_content = self._get_readme_content()
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✓ README created: {readme_path}")
    
    def _get_simple_html_content(self):
        """Спрощений HTML контент БЕЗ зовнішніх ресурсів"""
        return """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Фотоконтроль - Документація</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
            background-color: #f8f9fa;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        h2 {
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }
        h3 {
            color: #2980b9;
            margin-top: 20px;
        }
        .feature {
            background: #ecf0f1;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .step {
            background: #e8f5e8;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .warning {
            background: #fff3cd;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
        }
        code {
            background: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: #34495e;
            color: white;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📸 Фотоконтроль</h1>
        <p style="text-align: center; font-size: 18px; color: #7f8c8d;">
            Автоматизація створення фотоальбомів
        </p>

        <h2>📋 Огляд програми</h2>
        <p><strong>Фотоконтроль</strong> - це програма для пакетної обробки зображень та створення фотоальбомів у форматі Microsoft Word.</p>

        <div class="feature">
            <h3>🔧 Основні можливості</h3>
            <ul>
                <li>Автоматичний розрахунок азимуту та дальності</li>
                <li>Пакетна обробка зображень</li>
                <li>Створення фотоальбомів у форматі Word</li>
                <li>Система шаблонів документів</li>
                <li>Українська та англійська локалізація</li>
            </ul>
        </div>

        <h2>🚀 Початок роботи</h2>
        <div class="step">
            <h3>Створення фотоальбому</h3>
            <ol>
                <li>Запустіть програму</li>
                <li>Оберіть мову інтерфейсу: <strong>Налаштування → Мова</strong></li>
                <li>Відкрийте папку із зображеннями</li>
                <li>Встановіть центр азимутальної сітки кнопкою "Встановити центр"</li>
                <li>Встановіть край масштабу кнопкою "Встановити край"</li>
                <li>Оберіть масштаб із випадного списку</li>
                <li>Клікніть на зображенні для позначення цілі</li>
                <li>Заповніть дані про ціль у правій панелі</li>
                <li>Натисніть "Додати до альбому"</li>
                <li>Повторіть для всіх зображень</li>
                <li>Оберіть або створіть шаблон титульної сторінки</li>
                <li>Натисніть "Створити альбом"</li>
            </ol>
        </div>

        <h2>⚙️ Робота з зображеннями</h2>
        <div class="feature">
            <h3>Встановлення параметрів сітки</h3>
            <p>1. <strong>Центр сітки:</strong> Натисніть "Встановити центр" та клікніть на центр азимутальної сітки</p>
            <p>2. <strong>Масштаб:</strong> Натисніть "Встановити край" та клікніть на точку відомої відстані (25-350 км)</p>
            <p>3. <strong>Вибір масштабу:</strong> Оберіть відповідну відстань з випадного списку</p>
        </div>

        <div class="warning">
            <strong>💡 Важливо:</strong> Зображення повинні мати пропорції 13:15 для правильної обробки
        </div>

        <h2>📊 Заповнення даних</h2>
        <div class="step">
            <h3>Дані про ціль</h3>
            <ul>
                <li><strong>Номер цілі:</strong> Вводиться вручну</li>
                <li><strong>Азимут і дальність:</strong> Розраховуються автоматично</li>
                <li><strong>Висота:</strong> Вводиться вручну (якщо 0 - не відображається)</li>
                <li><strong>Перешкоди:</strong> Вибір з випадного списку</li>
                <li><strong>Статус:</strong> Виявлення/Супроводження/Втрата</li>
            </ul>
        </div>

        <h2>🎯 Гарячі клавіші</h2>
        <div class="feature">
            <p><code>Ctrl+B</code> - Перемикання браузера зображень</p>
            <p><code>←→↑↓</code> - Переміщення центру/краю в режимі налаштування</p>
            <p><code>Shift + стрілки</code> - Швидке переміщення</p>
            <p><code>Ctrl + стрілки</code> - Точне переміщення</p>
            <p><code>Esc</code> - Вихід з режиму налаштування</p>
        </div>

        <h2>📝 Система шаблонів</h2>
        <div class="step">
            <h3>Робота з шаблонами</h3>
            <p>1. <strong>Створення:</strong> Кнопка "Створити новий шаблон"</p>
            <p>2. <strong>Редагування:</strong> Кнопка "Редагувати шаблон"</p>
            <p>3. <strong>Застосування:</strong> Вибір з випадного списку</p>
            <p>Шаблони зберігаються в папці PhotoControl_Templates у домашній директорії</p>
        </div>

        <div class="footer">
            <h3>Підтримка</h3>
            <p><strong>Фотоконтроль v1.10.9</strong> | © 2025 | by Y.Bondarenko</p>
            <p>За технічною підтримкою звертайтеся до розробників програми</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_text_content(self):
        """Текстова версія документації"""
        return """
ФОТОКОНТРОЛЬ v1.10.9 - ДОКУМЕНТАЦІЯ
=====================================

ОГЛЯД ПРОГРАМИ
--------------
Фотоконтроль - це програма для пакетної обробки зображень та створення 
фотоальбомів у форматі Microsoft Word.

ОСНОВНІ МОЖЛИВОСТІ:
• Автоматичний розрахунок азимуту та дальності
• Пакетна обробка зображень
• Створення фотоальбомів у форматі Word
• Система шаблонів документів
• Українська та англійська локалізація

ПОЧАТОК РОБОТИ
--------------
1. Запустіть програму
2. Оберіть мову: Налаштування → Мова
3. Відкрийте папку із зображеннями
4. Встановіть центр сітки: кнопка "Встановити центр"
5. Встановіть край масштабу: кнопка "Встановити край"
6. Оберіть масштаб із списку
7. Клікніть на зображенні для позначення цілі
8. Заповніть дані про ціль
9. Натисніть "Додати до альбому"
10. Повторіть для всіх зображень
11. Створіть альбом

РОБОТА З ЗОБРАЖЕННЯМИ
--------------------
ВСТАНОВЛЕННЯ СІТКИ:
• Центр: Натисніть "Встановити центр" → клік на центр сітки
• Масштаб: Натисніть "Встановити край" → клік на відому відстань
• Вибір масштабу: Оберіть відстань з списку (25-350 км)

ВАЖЛИВО: Зображення повинні мати пропорції 13:15

ДАНІ ПРО ЦІЛЬ
-------------
• Номер цілі: Вводиться вручну
• Азимут і дальність: Розраховуються автоматично
• Висота: Вводиться вручну (0 = не відображається)
• Перешкоди: Вибір з списку
• Статус: Виявлення/Супроводження/Втрата

ГАРЯЧІ КЛАВІШІ
--------------
Ctrl+B - Перемикання браузера зображень
←→↑↓ - Переміщення центру/краю
Shift + стрілки - Швидке переміщення
Ctrl + стрілки - Точне переміщення
Esc - Вихід з режиму

СИСТЕМА ШАБЛОНІВ
----------------
• Створення: "Створити новий шаблон"
• Редагування: "Редагувати шаблон"
• Застосування: Вибір з списку
• Збереження: папка PhotoControl_Templates

ПІДТРИМУВАНІ ФОРМАТИ
--------------------
• Зображення: JPG, PNG, BMP, GIF, TIFF
• Вихідний документ: DOCX (Microsoft Word)

ТЕХНІЧНА ПІДТРИМКА
------------------
За додатковими питаннями звертайтеся до розробників програми.

© 2025 Фотоконтроль v1.10.9 by Y.Bondarenko
        """
    
    def _get_readme_content(self):
        """README файл (як і раніше)"""
        return """
ФОТОКОНТРОЛЬ v1.10.9 - ДОКУМЕНТАЦІЯ
=====================================

ШВИДКИЙ СТАРТ:
1. Запустіть програму
2. Оберіть мову в меню Налаштування → Мова
3. Відкрийте зображення або папку
4. Встановіть центр та масштаб сітки
5. Клікніть на точку для аналізу
6. Введіть дані про ціль
7. Створіть альбом

ОСНОВНІ ФУНКЦІЇ:
• Обробка зображень з азимутальними сітками
• Автоматичний розрахунок азимуту та дальності  
• Пакетна обробка зображень
• Створення альбомів у форматі Word
• Система шаблонів титульних сторінок
• Підтримка українського та англійського інтерфейсу

ГАРЯЧІ КЛАВІШІ:
• ←→↑↓ - переміщення центру/краю масштабу
• Shift + стрілки - швидке переміщення
• Ctrl + стрілки - точне переміщення  
• Esc - вихід з режиму

ПІДТРИМУВАНІ ФОРМАТИ:
• Зображення: JPG, PNG, BMP, GIF, TIFF
• Вихідний документ: DOCX (Microsoft Word)

ДЛЯ ДЕТАЛЬНОЇ ІНФОРМАЦІЇ:
Відкрийте повну документацію через меню програми:
Налаштування → Документація

© 2025 Фотоконтроль
"""

# 2. СТВОРІТЬ НОВИЙ ФАЙЛ documentation_dialog.py АБО ДОДАЙТЕ ДО ІСНУЮЧОГО:

class DocumentationDialog(QDialog):
    """Власне вікно документації БЕЗ веб-браузера"""
    
    def __init__(self, html_file, txt_file, parent=None):
        super().__init__(parent)
        self.html_file = html_file
        self.txt_file = txt_file
        
        self.setWindowTitle("Документація Фотоконтроль")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        self.setModal(True)
        
        self.setup_ui()
        self.load_documentation()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Браузер для HTML (БЕЗ інтернет-доступу)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)  # ВАЖЛИВО: блокуємо зовнішні лінки
        layout.addWidget(self.browser)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.html_btn = QPushButton("HTML версія")
        self.html_btn.clicked.connect(self.show_html_version)
        button_layout.addWidget(self.html_btn)
        
        self.text_btn = QPushButton("Текстова версія")
        self.text_btn.clicked.connect(self.show_text_version)
        button_layout.addWidget(self.text_btn)
        
        self.folder_btn = QPushButton("Відкрити папку")
        self.folder_btn.clicked.connect(self.open_docs_folder)
        button_layout.addWidget(self.folder_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Закрити")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Стилі
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QTextBrowser {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border: 1px solid #adb5bd;
            }
        """)
    
    def load_documentation(self):
        """Завантаження HTML документації"""
        self.show_html_version()
    
    def show_html_version(self):
        """Показати HTML версію"""
        try:
            if os.path.exists(self.html_file):
                with open(self.html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                self.browser.setHtml(html_content)
                self.html_btn.setStyleSheet("background-color: #007bff; color: white;")
                self.text_btn.setStyleSheet("")
            else:
                self.browser.setPlainText("HTML файл документації не знайдено")
        except Exception as e:
            self.browser.setPlainText(f"Помилка завантаження HTML: {e}")
    
    def show_text_version(self):
        """Показати текстову версію"""
        try:
            if os.path.exists(self.txt_file):
                with open(self.txt_file, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                self.browser.setPlainText(text_content)
                self.text_btn.setStyleSheet("background-color: #007bff; color: white;")
                self.html_btn.setStyleSheet("")
            else:
                self.browser.setPlainText("Текстовий файл документації не знайдено")
        except Exception as e:
            self.browser.setPlainText(f"Помилка завантаження тексту: {e}")
    
    def open_docs_folder(self):
        """Відкрити папку з документацією в провіднику"""
        try:
            docs_dir = os.path.dirname(self.html_file)
            if os.path.exists(docs_dir):
                os.startfile(docs_dir)  # Windows
            else:
                QMessageBox.warning(self, "Помилка", "Папка документації не знайдена")
        except Exception as e:
            QMessageBox.warning(self, "Помилка", f"Не вдалося відкрити папку: {e}")
