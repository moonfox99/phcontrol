import os
import webbrowser
import tempfile
from PyQt5.QtWidgets import QMessageBox

class DocumentationManager:
    """Менеджер документації програми Фотоконтроль"""
    
    def __init__(self):
        self.docs_dir = os.path.join(os.path.expanduser("~"), "PhotoControl_Docs")
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)
        
        # Шляхи до файлів документації
        self.html_file = os.path.join(self.docs_dir, "PhotoControl_Documentation.html")
        self.version = "1.0"
    
    def create_documentation_files(self):
        """Створення всіх файлів документації"""
        success = True
        
        # Створюємо HTML документацію
        try:
            self._create_html_documentation()
        except Exception as e:
            print(f"Error creating HTML documentation: {e}")
            success = False
        
        # Створюємо README файл
        try:
            self._create_readme_file()
        except Exception as e:
            print(f"Error creating README: {e}")
            success = False
        
        return success
    
    def show_documentation(self):
        """Відкриття документації в браузері"""
        # Перевіряємо чи існує файл документації
        if not os.path.exists(self.html_file):
            self.create_documentation_files()
        
        try:
            webbrowser.open(f'file://{self.html_file}')
            return True
        except Exception as e:
            print(f"Error opening documentation: {e}")
            return False
    
    def _create_html_documentation(self):
        """Створення HTML файлу документації"""
        html_content = self._get_html_content()
        
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ HTML documentation created: {self.html_file}")
    
    def _create_readme_file(self):
        """Створення README файлу"""
        readme_path = os.path.join(self.docs_dir, "README.txt")
        readme_content = self._get_readme_content()
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✓ README created: {readme_path}")
    
    def _get_html_content(self):
        """HTML контент документації (детальний)"""
        return """
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Фотоконтроль - Документація</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
                padding: 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                margin: -20px -20px 40px -20px;
            }
            h1 {
                font-size: 2.5em;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .subtitle {
                font-size: 1.2em;
                margin-top: 10px;
                opacity: 0.9;
            }
            h2 {
                color: #2c3e50;
                margin-top: 40px;
                border-left: 5px solid #3498db;
                padding-left: 20px;
                font-size: 1.8em;
            }
            h3 {
                color: #2980b9;
                margin-top: 30px;
                font-size: 1.4em;
            }
            .step,.image-processing, .data-processing, .description-processing {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-left: 5px solid #3498db;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .warning {
                background: linear-gradient(135deg, #fff9c4 0%, #f76b1c 100%);
                color: white;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .tip {
                background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .keyboard {
                background: #34495e;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                box-shadow: 0 2px 3px rgba(0,0,0,0.2);
            }
            .toc {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 25px;
                margin: 30px 0;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            }
            .toc h3 {
                margin-top: 0;
                color: #495057;
            }
            .toc a {
                color: #2980b9;
                text-decoration: none;
                transition: all 0.3s ease;
            }
            .toc a:hover {
                color: #3498db;
                text-decoration: underline;
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .feature-card h4 {
                margin-top: 0;
                font-size: 1.3em;
            }
            ul {
                margin: 15px 0;
            }
            li {
                margin: 10px 0;
            }
            code {
                background: #f8f9fa;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .footer {
                text-align: center;
                margin-top: 50px;
                padding: 30px;
                background: #2c3e50;
                color: white;
                border-radius: 10px;
                margin-left: -20px;
                margin-right: -20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📸 Фотоконтроль</h1>
                <div class="subtitle">Автоматизація створення фотоальбомів</div>
            </div>

            <div class="toc">
                <h3>📋 Зміст документації</h3>
                <div style="columns: 2; gap: 30px;">
                    <ul>
                        <li><a href="#overview">Огляд програми</a></li>
                        <li><a href="#interface">Інтерфейс</a></li>
                        <li><a href="#getting-started">Початок роботи</a></li>
                        <li><a href="#i_processing">Обробка зображень</a></li>
                        <li><a href="#d_processing">Робота з формуляром</a></li>
                        <li><a href="#des_processing">Робота з формуляром</a></li>
                        <li><a href="#templates">Шаблони</a></li>
                    </ul>
                </div>
            </div>

            <h2 id="overview">Огляд програми</h2>
            
            <p><strong>Фотоконтроль</strong> - це програма для пакетної обробки зображень та створення фотоальбомів у форматі Microsoft Word.</p>

            <div class="feature-grid">
                <div class="feature-card">
                    <h4>🔧 Обробка зображень</h4>
                    <p>Автоматичний розрахунок азимуту та дальності</p>
                </div>
                <div class="feature-card">
                    <h4>📦 Пакетна обробка</h4>
                    <p>Робота з групою зображень</p>
                </div>
                <div class="feature-card">
                    <h4>📖 Альбоми</h4>
                    <p>Автоматичне створення альбомів за визначеними вимогами</p>
                </div>
                <div class="feature-card">
                    <h4>📝 Шаблони</h4>
                    <p>Система шаблонів для зручного формування Word-документа</p>
                </div>
            </div>

                    <h2 id="interface">Інтерфейс програми</h2>

            <h3>Основні панелі</h3>
            <ul>
                <li><strong>Ліва панель управління</strong> - файлові операції, налаштування, результати</li>
                <li><strong>Браузер зображень</strong> - мініатюри з візуальним статусом обробки</li>
                <li><strong>Центральна область</strong> - перегляд зображень з інструментами</li>
                <li><strong>Права панель даних</strong> - параметри цілі та азимутальної сітки</li>
            </ul>

            <h2 id="getting-started">Інструкції з користування</h2>

            <div class="step">
                <h3>Створення фотоальбому</h3>
                <ol>
                    <li>Запустіть файл PhControl.exe</li>
                    <li>Оберіть мову інтерфейсу за потреби: <strong>Налаштування → Мова</strong></li>
                    <li>Відкрийте папку із зображеннями через відповідну кнопку в лівій панелі програми</li>
                    <li>Після вибору папки у програмі відкриється вертикальний браузер зображень, які розміщенні у вашій папці</li>
                    <li>Завершивши редагування зображення натисніть "Додати до альбому" у розділі "Пакетна обробка"</li>
                    <li>Оберіть наступне потрібне зображення та повторіть етапи редагування та збереження</li>
                    <li>Оберіть дату для титульної сторінки документу</li>
                    <li>Оберіть або створіть шаблон заповнення титульної сторінки фотоальбому у розділі "Титульна сторінка"</li>
                    <li>Натисніть кнопку "Створити альбом" для формування Word-документа</li>
                    <li>Збережіть створений альбом у потрібне місце на диску</li>
                </ol>
            </div>
            <div class="tip">
                <strong>💡 Підказка:</strong> При повторній обробці зображення після натискання кнопки "Додати до альбому" у альбом буде додане лише зображення із останніми змінами.
                <strong>💡 Підказка:</strong> Будь-яке зображення, яке завантажується для подальшої обробки повинно мати пропорції 13 на 15
            </div>
            <div class="image-processing">
                <h3 id="i_processing">Обробка зображень</h3>
                <ol>
                    <li>Після відкриття зображення натисніть кнопку "Встановити центр" та оберіть необхідну точку на зображенні, щоб встановити центр азимутальної сітки.</li>
                    <li>Натисність кнопку "Встановити край масштабу" та оберіть необхідну точку на зображенні (обирайте будь-яку точку на азимутальній сітці із дальністю 25км - 350км) </li>
                    <li>У випадному списку "Масштаб" оберіть ту відстань, яку ви обрали в попередньому пункті. Правильне задання центру сітки і границі гарантує нам точні підрахунки азимуту та дальності цілі </li>
                    <li>Впевніться, що кнопки "Встановити край масштабу" та "Встановити центр" неактивні, та натисність на зображенні на необхідну точку (розташування цілі)</li>
                </ol>
            </div>
            <div class="tip">
                <strong>💡 Підказка:</strong> При активному режимі вибору центру сітки або вибору краю сітки можна використовувати стрілки на клавіатурі для зсуву в потрібну сторону"
            </div>
            <div class="data-processing">
                <h3 id="d_processing">Робота з формуляром</h3>
                <ol>
                    <li>У правій панелі розташований формуляр, який візуально повторює праву комірку таблиці фотоальбому</li>
                    <li>Номер цілі вводиться вручну у відповідному полі, та зберігається автоматично при переході від зображення до зображення</li>
                    <li>Азимут та дальність цілі встановлюються автоматично при виборі точки на зображенні</li>
                    <li>Висота цілі задається вручну за потребою. Якщо висота дорівнює 0 - рядок висоти в таблицю не вноситься</li>
                    <li>Випадні списки дозволяють обрати опції "Без перешкод", "З перешкодами", а також статуси "Виявлення", "Супроводження", та "Втрата"</li>
                    <li>Масштаб обирається автоматично при виборі відповідного пункту з випадного списку у розділі "Азимутальна сітка"</li>
                </ol>
            </div>
            <div class="description-processing">
                <h3 id="des_processing">Табличка опису РЛС</h3>
                <ol>
                    <li>У правій панелі розташований формуляр опису РЛС, опис додається в лівий нижній кут зображення</li>
                    <li>Дата обирається вибором через функціонал програми, всі інші поля заповнюються вручну</li>
                    <li>Табличка з описом РЛС додається ЛИШЕ до зображень, які були додані до альбому при включеній опції "Опис РЛС"</li>
                </ol>
            </div>
            <div class="tip">
                <strong>💡 Підказка:</strong> Опис додається безпосередньо на саме зображення, а не як окремий елемент у Word"
            </div>
            <div class="footer">
                <h3>Підтримка</h3>
                <p>За технічною підтримкою та додатковими питаннями звертайтеся до розробників програми.</p>
                <p><strong>Фотоконтроль v1.10.9</strong> | © 2025 | by Y.Bondarenko</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    def _get_readme_content(self):
        """Простий README файл"""
        return """
ФОТОКОНТРОЛЬ v1.10.9 - ДОКУМЕНТАЦІЯ
=====================================

ШВИДКИЙ СТАРТ:
1. Запустіть azymuth6.py
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
Відкрийте повну HTML документацію через меню програми:
Налаштування → Документація

© 2025 Фотоконтроль
"""