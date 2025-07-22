#!/usr/bin/env python3
"""
QSS стилі для PhotoControl v2.0
Централізовані стилі для всіх UI компонентів
"""

from core.constants import STYLES


def get_main_window_styles() -> str:
    """Основні стилі для головного вікна"""
    return f"""
        QMainWindow {{
            background-color: {STYLES.BACKGROUND_LIGHT};
            font-family: {STYLES.DEFAULT_FONT_FAMILY};
            font-size: {STYLES.NORMAL_FONT_SIZE};
        }}
        
        QSplitter::handle {{
            background-color: {STYLES.BORDER_COLOR};
            border: 1px solid {STYLES.BORDER_COLOR};
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        QMenuBar {{
            background-color: {STYLES.BACKGROUND_WHITE};
            border-bottom: 1px solid {STYLES.BORDER_COLOR};
            padding: 4px;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 12px;
            border-radius: 4px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {STYLES.BACKGROUND_LIGHT};
        }}
        
        QMenu {{
            background-color: {STYLES.BACKGROUND_WHITE};
            border: 1px solid {STYLES.BORDER_COLOR};
            border-radius: {STYLES.BORDER_RADIUS};
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 16px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {STYLES.PRIMARY_COLOR};
            color: white;
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {STYLES.BORDER_COLOR};
            margin: 4px 0;
        }}
    """


def get_panel_styles() -> str:
    """Стилі для панелей"""
    return f"""
        .PanelWidget {{
            background-color: {STYLES.BACKGROUND_LIGHT};
            border: 1px solid {STYLES.BORDER_COLOR};
            border-radius: {STYLES.BORDER_RADIUS};
        }}
        
        .PanelTitle {{
            font-size: {STYLES.TITLE_FONT_SIZE};
            font-weight: bold;
            color: {STYLES.PRIMARY_COLOR};
            padding: 12px;
            background-color: {STYLES.BACKGROUND_WHITE};
            border-bottom: 1px solid {STYLES.BORDER_COLOR};
            border-top-left-radius: {STYLES.BORDER_RADIUS};
            border-top-right-radius: {STYLES.BORDER_RADIUS};
        }}
        
        .SectionLabel {{
            font-size: {STYLES.NORMAL_FONT_SIZE};
            font-weight: bold;
            color: {STYLES.SECONDARY_COLOR};
            padding: 8px 0;
            margin-top: 12px;
        }}
    """


def get_button_styles() -> str:
    """Стилі для кнопок"""
    return f"""
        QPushButton {{
            background-color: {STYLES.BACKGROUND_WHITE};
            border: 2px solid {STYLES.BORDER_COLOR};
            border-radius: {STYLES.BORDER_RADIUS};
            padding: {STYLES.BUTTON_PADDING};
            font-family: {STYLES.DEFAULT_FONT_FAMILY};
            font-size: {STYLES.NORMAL_FONT_SIZE};
            font-weight: 500;
            color: {STYLES.PRIMARY_COLOR};
            min-height: 16px;
        }}
        
        QPushButton:hover {{
            background-color: {STYLES.BACKGROUND_LIGHT};
            border: 2px solid {STYLES.SECONDARY_COLOR};
            color: {STYLES.PRIMARY_COLOR};
        }}
        
        QPushButton:pressed {{
            background-color: {STYLES.BORDER_COLOR};
            border: 2px solid {STYLES.PRIMARY_COLOR};
            border-style: inset;
        }}
        
        QPushButton:checked {{
            background-color: {STYLES.PRIMARY_COLOR};
            color: white;
            border: 2px solid {STYLES.PRIMARY_COLOR};
        }}
        
        QPushButton:checked:hover {{
            background-color: #343a40;
            border: 2px solid #212529;
        }}
        
        QPushButton:disabled {{
            background-color: #f5f5f5;
            color: {STYLES.SECONDARY_COLOR};
            border: 2px solid #e9ecef;
        }}
        
        QPushButton[buttonType="primary"] {{
            background-color: {STYLES.PRIMARY_COLOR};
            color: white;
            font-weight: 600;
            border: 2px solid {STYLES.PRIMARY_COLOR};
        }}
        
        QPushButton[buttonType="primary"]:hover {{
            background-color: #343a40;
            border: 2px solid #343a40;
        }}
        
        QPushButton[buttonType="success"] {{
            background-color: {STYLES.SUCCESS_COLOR};
            color: white;
            border: 2px solid {STYLES.SUCCESS_COLOR};
        }}
        
        QPushButton[buttonType="success"]:hover {{
            background-color: #218838;
            border: 2px solid #218838;
        }}
        
        QPushButton[buttonType="warning"] {{
            background-color: {STYLES.WARNING_COLOR};
            color: white;
            border: 2px solid {STYLES.WARNING_COLOR};
        }}
        
        QPushButton[buttonType="warning"]:hover {{
            background-color: #e76a00;
            border: 2px solid #e76a00;
        }}
        
        QPushButton[buttonType="danger"] {{
            background-color: {STYLES.DANGER_COLOR};
            color: white;
            border: 2px solid {STYLES.DANGER_COLOR};
        }}
        
        QPushButton[buttonType="danger"]:hover {{
            background-color: #c82333;
            border: 2px solid #c82333;
        }}
    """


def get_input_styles() -> str:
    """Стилі для полів введення"""
    return f"""
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            border: 1px solid {STYLES.BORDER_COLOR};
            border-radius: 4px;
            padding: {STYLES.INPUT_PADDING};
            background-color: {STYLES.BACKGROUND_WHITE};
            font-family: {STYLES.DEFAULT_FONT_FAMILY};
            font-size: {STYLES.NORMAL_FONT_SIZE};
            color: {STYLES.PRIMARY_COLOR};
            min-height: 20px;
        }}
        
        QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
            border: 1px solid {STYLES.SECONDARY_COLOR};
            background-color: {STYLES.BACKGROUND_LIGHT};
        }}
        
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {STYLES.PRIMARY_COLOR};
            background-color: {STYLES.BACKGROUND_WHITE};
        }}
        
        QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
            background-color: #f5f5f5;
            color: {STYLES.SECONDARY_COLOR};
            border: 1px solid #e9ecef;
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
            border-left: 1px solid {STYLES.BORDER_COLOR};
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
            background-color: {STYLES.BACKGROUND_LIGHT};
        }}
        
        QComboBox::drop-down:hover {{
            background-color: {STYLES.BORDER_COLOR};
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {STYLES.SECONDARY_COLOR};
        }}
        
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            border: none;
            background-color: {STYLES.BACKGROUND_LIGHT};
            width: 16px;
        }}
        
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {STYLES.BORDER_COLOR};
        }}
    """


def get_label_styles() -> str:
    """Стилі для міток"""
    return f"""
        QLabel {{
            color: {STYLES.PRIMARY_COLOR};
            font-family: {STYLES.DEFAULT_FONT_FAMILY};
            font-size: {STYLES.NORMAL_FONT_SIZE};
            background: none;
            border: none;
        }}
        
        QLabel[labelType="title"] {{
            font-size: {STYLES.TITLE_FONT_SIZE};
            font-weight: bold;
            color: {STYLES.PRIMARY_COLOR};
        }}
        
        QLabel[labelType="section"] {{
            font-weight: bold;
            color: {STYLES.SECONDARY_COLOR};
            margin-top: 8px;
            margin-bottom: 4px;
        }}
        
        QLabel[labelType="data"] {{
            font-weight: 500;
            color: {STYLES.PRIMARY_COLOR};
        }}
        
        QLabel[labelType="small"] {{
            font-size: {STYLES.SMALL_FONT_SIZE};
            color: {STYLES.SECONDARY_COLOR};
        }}
    """


def get_checkbox_styles() -> str:
    """Стилі для чекбоксів"""
    return f"""
        QCheckBox {{
            color: {STYLES.PRIMARY_COLOR};
            font-family: {STYLES.DEFAULT_FONT_FAMILY};
            font-size: {STYLES.NORMAL_FONT_SIZE};
            font-weight: 500;
            padding: 6px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
        
        QCheckBox::indicator:unchecked {{
            border: 2px solid {STYLES.BORDER_COLOR};
            background-color: {STYLES.BACKGROUND_WHITE};
            border-radius: 3px;
        }}
        
        QCheckBox::indicator:checked {{
            border: 2px solid {STYLES.PRIMARY_COLOR};
            background-color: {STYLES.PRIMARY_COLOR};
            border-radius: 3px;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }}
        
        QCheckBox::indicator:unchecked:hover {{
            border: 2px solid {STYLES.SECONDARY_COLOR};
            background-color: {STYLES.BACKGROUND_LIGHT};
        }}
        
        QCheckBox::indicator:checked:hover {{
            background-color: #343a40;
            border: 2px solid #343a40;
        }}
    """


def get_date_edit_styles() -> str:
    """Стилі для полів дати"""
    return f"""
        QDateEdit {{
            border: 1px solid {STYLES.BORDER_COLOR};
            border-radius: 4px;
            padding: {STYLES.INPUT_PADDING};
            background-color: {STYLES.BACKGROUND_WHITE};
            font-family: {STYLES.DEFAULT_FONT_FAMILY};
            font-size: {STYLES.NORMAL_FONT_SIZE};
            color: {STYLES.PRIMARY_COLOR};
            min-height: 22px;
        }}
        
        QDateEdit:hover {{
            border: 1px solid {STYLES.SECONDARY_COLOR};
            background-color: {STYLES.BACKGROUND_LIGHT};
        }}
        
        QDateEdit:focus {{
            border: 2px solid {STYLES.PRIMARY_COLOR};
            background-color: {STYLES.BACKGROUND_WHITE};
        }}
        
        QDateEdit:disabled {{
            background-color: #f5f5f5;
            color: {STYLES.SECONDARY_COLOR};
            border: 1px solid #e9ecef;
        }}
        
        QDateEdit::drop-down {{
            border: none;
            background-color: transparent;
            width: 18px;
            margin-right: 4px;
        }}
        
        QDateEdit::drop-down:hover {{
            background-color: {STYLES.BACKGROUND_LIGHT};
            border-radius: 3px;
        }}
        
        QDateEdit::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {STYLES.SECONDARY_COLOR};
            margin-top: 1px;
        }}
        
        QDateEdit::down-arrow:hover {{
            border-top-color: {STYLES.PRIMARY_COLOR};
        }}
        
        QCalendarWidget {{
            background-color: {STYLES.BACKGROUND_WHITE};
            color: {STYLES.PRIMARY_COLOR};
            border: 1px solid {STYLES.BORDER_COLOR};
            border-radius: {STYLES.BORDER_RADIUS};
            font-family: {STYLES.DEFAULT_FONT_FAMILY};
        }}
        
        QCalendarWidget QWidget#qt_calendar_navigationbar {{
            background-color: {STYLES.BACKGROUND_LIGHT};
            border-bottom: 1px solid {STYLES.BORDER_COLOR};
            border-top-left-radius: {STYLES.BORDER_RADIUS};
            border-top-right-radius: {STYLES.BORDER_RADIUS};
            padding: 4px;
        }}
        
        QCalendarWidget QToolButton {{
            color: {STYLES.SECONDARY_COLOR};
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            margin: 1px;
            padding: 4px 8px;
            font-weight: normal;
            min-width: 24px;
            min-height: 24px;
        }}
        
        QCalendarWidget QToolButton:hover {{
            background-color: {STYLES.BORDER_COLOR};
            color: {STYLES.PRIMARY_COLOR};
            border: 1px solid {STYLES.SECONDARY_COLOR};
        }}
    """


def get_text_edit_styles() -> str:
    """Стилі для текстових областей"""
    return f"""
        QTextEdit {{
            background-color: {STYLES.BACKGROUND_WHITE};
            border: 1px solid {STYLES.BORDER_COLOR};
            font-family: {STYLES.MONOSPACE_FONT_FAMILY};
            font-size: 11pt;
            color: {STYLES.PRIMARY_COLOR};
            border-radius: 4px;
            padding: 8px;
        }}
        
        QTextEdit:focus {{
            border: 2px solid {STYLES.PRIMARY_COLOR};
        }}
        
        QScrollBar:vertical {{
            border: none;
            background-color: {STYLES.BACKGROUND_LIGHT};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {STYLES.BORDER_COLOR};
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {STYLES.SECONDARY_COLOR};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0px;
        }}
    """


def get_tooltip_styles() -> str:
    """Стилі для підказок"""
    return f"""
        QToolTip {{
            background-color: {STYLES.PRIMARY_COLOR};
            color: white;
            border: 1px solid {STYLES.PRIMARY_COLOR};
            border-radius: 4px;
            padding: 8px;
            font-size: 11pt;
            font-family: {STYLES.DEFAULT_FONT_FAMILY};
        }}
    """


def get_combined_styles() -> str:
    """Об'єднання всіх стилів"""
    return (
        get_main_window_styles() +
        get_panel_styles() +
        get_button_styles() +
        get_input_styles() +
        get_label_styles() +
        get_checkbox_styles() +
        get_date_edit_styles() +
        get_text_edit_styles() +
        get_tooltip_styles()
    )


if __name__ == "__main__":
    # Тестування генерації стилів
    print("=== Тестування QSS стилів ===")
    styles = get_combined_styles()
    print(f"Згенеровано {len(styles)} символів стилів")
    
    # Збереження у файл для перевірки
    with open("generated_styles.qss", "w", encoding="utf-8") as f:
        f.write(styles)
    print("✓ Стилі збережено у generated_styles.qss")