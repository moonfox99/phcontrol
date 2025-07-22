from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextBrowser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

class AboutDialog(QDialog):
    """Діалог 'Про програму'"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Про програму Фотоконтроль")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Заголовок
        title = QLabel("📸 Фотоконтроль")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        layout.addWidget(title)
        
        # Версія
        version = QLabel("Версія 1.10.9")
        version.setFont(QFont("Arial", 12))
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        layout.addWidget(version)
        
        # Опис
        description = QTextBrowser()
        description.setHtml(self.get_about_text())
        description.setMaximumHeight(250)
        layout.addWidget(description)
        
        # Кнопка закриття
        close_btn = QPushButton("Закрити")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def get_about_text(self):
        return """
        <div style="text-align: center; font-family: Arial;">
            <h3 style="color: #2c3e50;">Програма для створення фотоальбомів</h3>
            
            <p><b>Основні можливості:</b></p>
            <ul style="text-align: left;">
                <li>Автоматичний розрахунок азимуту та дальності</li>
                <li>Пакетна обробка зображень</li>
                <li>Створення  фотоальбомів у форматі Word</li>
                <li>Система шаблонів документів</li>
                <li>Українська та англійська локалізація</li>
            </ul>
            
            <hr>
            <p style="color: #7f8c8d; font-size: 12px;">
                © 2025 | Розроблено для автоматизації рутинних задач | by Y.Bondarenko
            </p>
        </div>
        """
