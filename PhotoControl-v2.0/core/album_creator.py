#!/usr/bin/env python3
"""
Система створення Word альбомів з точними розмірами
Генерує професійні альбоми з титульною сторінкою, описом та сторінками зображень
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from core.constants import ALBUM, WORD_STYLES, TEMPLATE_DEFAULTS, mm_to_cm


@dataclass
class ImageData:
    """Дані про оброблене зображення"""
    filename: str
    image_path: str
    processed_image_path: str
    target_number: str
    azimuth: float
    range_km: float
    height: float
    obstacles: str
    detection: str
    timestamp: datetime


@dataclass
class TitleData:
    """Дані для титульної сторінки"""
    date: str
    unit_info: str
    commander_rank: str
    commander_name: str
    chief_of_staff_rank: str
    chief_of_staff_name: str


class AlbumCreator:
    """
    Клас для створення професійних Word альбомів
    
    Функціональність:
    - Титульна сторінка з правильним форматуванням
    - Сторінка опису документів
    - Сторінки з зображеннями (по 2 на сторінку)
    - Точні розміри таблиць (205мм × 130мм)
    - Правильні поля сторінок (2.5мм ліворуч)
    """
    
    def __init__(self):
        self.document = None
        self.processed_images: List[ImageData] = []
        self.title_data: Optional[TitleData] = None
    
    def create_album(self, images_data: List[ImageData], title_data: TitleData, output_path: str) -> bool:
        """
        Створення повного альбому
        
        Args:
            images_data: Список даних про оброблені зображення
            title_data: Дані для титульної сторінки
            output_path: Шлях для збереження альбому
            
        Returns:
            True якщо альбом створено успішно
        """
        try:
            self.processed_images = images_data
            self.title_data = title_data
            
            # Створення нового документу
            self.document = Document()
            
            print("=== Створення Word альбому ===")
            print(f"Зображень для обробки: {len(images_data)}")
            
            # 1. Титульна сторінка
            print("1. Створення титульної сторінки...")
            self._create_title_page()
            
            # 2. Сторінка опису документів
            print("2. Створення сторінки опису...")
            self._create_description_page()
            
            # 3. Сторінки з зображеннями
            print("3. Створення сторінок із зображеннями...")
            self._create_image_pages()
            
            # 4. Збереження документу
            print(f"4. Збереження у файл: {output_path}")
            self.document.save(output_path)
            
            print("✅ Альбом створено успішно!")
            return True
            
        except Exception as e:
            print(f"❌ Помилка створення альбому: {e}")
            return False
    
    def _create_title_page(self):
        """Створення титульної сторінки з правильним форматуванням"""
        # Встановлення стандартних полів для титульної сторінки
        section = self.document.sections[0]
        self._set_standard_margins(section)
        
        # Верхній відступ (3 см)
        title_spacer = self.document.add_paragraph()
        title_spacer_format = title_spacer.paragraph_format
        title_spacer_format.space_before = Pt(WORD_STYLES.TITLE_TOP_SPACER_SIZE)
        title_spacer_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Основний заголовок
        title_paragraph = self.document.add_paragraph()
        title_run = title_paragraph.add_run("ФОТОАЛЬБОМ\n")
        title_run.font.size = Pt(WORD_STYLES.TITLE_MAIN_SIZE)
        title_run.font.name = 'Times New Roman'
        title_run.bold = True
        
        # Підзаголовок з датою
        subtitle_run = title_paragraph.add_run(f'за "{self.title_data.date}"')
        subtitle_run.font.size = Pt(WORD_STYLES.TITLE_MAIN_SIZE)
        subtitle_run.font.name = 'Times New Roman'
        subtitle_run.bold = True
        
        title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Відступ перед підписами
        signature_spacer = self.document.add_paragraph()
        signature_spacer_format = signature_spacer.paragraph_format
        signature_spacer_format.space_before = Pt(WORD_STYLES.TITLE_SIGNATURE_SPACER_SIZE * 10)
        
        # Підписи
        self._add_signature_section()
        
        # Розрив сторінки після титульної
        self.document.add_page_break()
    
    def _add_signature_section(self):
        """Додавання секції підписів на титульну сторінку"""
        # Командир частини
        commander_p = self.document.add_paragraph()
        commander_run = commander_p.add_run(f"{self.title_data.commander_rank} {self.title_data.unit_info}")
        commander_run.font.size = Pt(WORD_STYLES.TITLE_SIGNATURE_SIZE)
        commander_run.font.name = 'Times New Roman'
        
        # Відступ зліва для підписів
        commander_p.paragraph_format.left_indent = Cm(3.75)
        
        # Лінія для підпису командира
        commander_line_p = self.document.add_paragraph()
        commander_line_run = commander_line_p.add_run("__________________________ " + self.title_data.commander_name)
        commander_line_run.font.size = Pt(WORD_STYLES.TITLE_SIGNATURE_SIZE)
        commander_line_run.font.name = 'Times New Roman'
        commander_line_p.paragraph_format.left_indent = Cm(3.75)
        commander_line_p.paragraph_format.space_before = Pt(WORD_STYLES.TITLE_SIGNATURE_SPACER_SIZE)
        
        # Начальник штабу
        chief_p = self.document.add_paragraph()
        chief_run = chief_p.add_run(f"{self.title_data.chief_of_staff_rank}")
        chief_run.font.size = Pt(WORD_STYLES.TITLE_SIGNATURE_SIZE)
        chief_run.font.name = 'Times New Roman'
        chief_p.paragraph_format.left_indent = Cm(3.75)
        chief_p.paragraph_format.space_before = Pt(WORD_STYLES.TITLE_SIGNATURE_SPACER_SIZE * 2)
        
        # Лінія для підпису начальника штабу
        chief_line_p = self.document.add_paragraph()
        chief_line_run = chief_line_p.add_run("__________________________ " + self.title_data.chief_of_staff_name)
        chief_line_run.font.size = Pt(WORD_STYLES.TITLE_SIGNATURE_SIZE)
        chief_line_run.font.name = 'Times New Roman'
        chief_line_p.paragraph_format.left_indent = Cm(3.75)
        chief_line_p.paragraph_format.space_before = Pt(WORD_STYLES.TITLE_SIGNATURE_SPACER_SIZE)
    
    def _create_description_page(self):
        """Створення сторінки опису документів"""
        # Заголовок сторінки
        desc_title = self.document.add_paragraph()
        desc_title_run = desc_title.add_run("ОПИС\nфотодокументів")
        desc_title_run.font.size = Pt(WORD_STYLES.DESCRIPTION_HEADING_SIZE)
        desc_title_run.font.name = 'Times New Roman'
        desc_title_run.bold = True
        desc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Відступ перед таблицею
        spacer = self.document.add_paragraph()
        spacer.paragraph_format.space_before = Pt(WORD_STYLES.DESCRIPTION_SPACER_SIZE)
        
        # Створення таблиці опису
        self._create_description_table()
        
        # Підпис відповідального
        signature_spacer = self.document.add_paragraph()
        signature_spacer.paragraph_format.space_before = Pt(WORD_STYLES.DESCRIPTION_SPACER_SIZE)
        
        resp_signature = self.document.add_paragraph()
        resp_run = resp_signature.add_run(f"Відповідальний: _______________ {TEMPLATE_DEFAULTS.SIGNATURE_INFO['name']}")
        resp_run.font.size = Pt(WORD_STYLES.DESCRIPTION_SIGNATURE_SIZE)
        resp_run.font.name = 'Times New Roman'
        
        # Розрив сторінки
        self.document.add_page_break()
    
    def _create_description_table(self):
        """Створення таблиці опису документів"""
        # Заголовки таблиці
        headers = [
            "№ пп",
            "Назва документа", 
            "Обліковий номер",
            "Кількість аркушів (знімків)",
            "Гриф секретності",
            "Примітка"
        ]
        
        # Ширини колонок (в см)
        col_widths = [0.84, 3.43, 2.69, 2.54, 2.77, 2.27]
        
        # Створення таблиці
        table = self.document.add_table(rows=1 + len(self.processed_images), cols=len(headers))
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Налаштування заголовків
        header_row = table.rows[0]
        header_row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        header_row.height = Cm(WORD_STYLES.TABLE_HEADER_HEIGHT_CM)
        
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            cell = header_row.cells[i]
            cell.width = Cm(width)
            
            # Текст заголовка
            paragraph = cell.paragraphs[0]
            run = paragraph.add_run(header)
            run.font.size = Pt(WORD_STYLES.TABLE_HEADER_SIZE)
            run.font.name = 'Times New Roman'
            run.bold = True
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Заповнення даних
        for idx, image_data in enumerate(self.processed_images):
            data_row = table.rows[idx + 1]
            data_row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            data_row.height = Cm(WORD_STYLES.TABLE_DATA_HEIGHT_CM)
            
            # Дані для рядка
            row_data = [
                str(idx + 1),  # № пп
                f"Фотознімок №{image_data.target_number}",  # Назва документа
                image_data.filename,  # Обліковий номер
                "1",  # Кількість аркушів
                "Для службового користування",  # Гриф секретності
                f"β-{image_data.azimuth:.0f}°, D-{image_data.range_km:.0f}км"  # Примітка
            ]
            
            for i, (data, width) in enumerate(zip(row_data, col_widths)):
                cell = data_row.cells[i]
                cell.width = Cm(width)
                
                paragraph = cell.paragraphs[0]
                run = paragraph.add_run(data)
                run.font.size = Pt(WORD_STYLES.TABLE_DATA_SIZE)
                run.font.name = 'Times New Roman'
                
                if i == 0:  # Номер по центру
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    def _create_image_pages(self):
        """Створення сторінок із зображеннями (по 2 на сторінку)"""
        # Встановлення спеціальних полів для сторінок з таблицями
        section = self.document.sections[-1]  # Остання секція
        self._set_table_margins(section)
        
        # Обробка зображень парами
        for i in range(0, len(self.processed_images), 2):
            first_image = self.processed_images[i]
            second_image = self.processed_images[i + 1] if i + 1 < len(self.processed_images) else None
            
            print(f"\n=== Створення сторінки для зображень {i+1}-{i+2 if second_image else i+1} ===")
            
            # Створення єдиної таблиці з правильною структурою
            self._create_unified_page_table(first_image, second_image)
            
            # Розрив сторінки (крім останньої сторінки)
            if i + 2 < len(self.processed_images):
                self.document.add_page_break()
    
    def _create_unified_page_table(self, first_image: ImageData, second_image: Optional[ImageData]):
        """Створення єдиної таблиці на сторінку з правильною структурою"""
        try:
            # Розрахунок розмірів
            table_width_mm = 205  # Загальна ширина таблиці
            table_height_mm = 130 # Висота кожної таблиці зображення
            spacer_height_mm = 5  # Висота параграфа-розділювача
            
            # Ширини колонок (мм)
            left_width_mm = 25   # "Індикатор ЗРЛ"
            middle_width_mm = 150 # Зображення
            right_width_mm = 30   # Дані
            
            # Створення основної структури
            # 1. Параграф-розділювач 5мм
            self._create_spacer_paragraph(spacer_height_mm)
            
            # 2. Перша таблиця 130мм
            self._create_single_image_table(first_image, table_width_mm, table_height_mm,
                                          left_width_mm, middle_width_mm, right_width_mm)
            
            # 3. Параграф-розділювач 5мм
            self._create_spacer_paragraph(spacer_height_mm)
            
            # 4. Друга таблиця 130мм (якщо є друге зображення)
            if second_image:
                self._create_single_image_table(second_image, table_width_mm, table_height_mm,
                                              left_width_mm, middle_width_mm, right_width_mm)
            else:
                # Порожня таблиця для збереження структури
                self._create_empty_image_table(table_width_mm, table_height_mm,
                                             left_width_mm, middle_width_mm, right_width_mm)
            
            print("✅ Єдина структура сторінки створена")
            
        except Exception as e:
            print(f"❌ Помилка створення структури сторінки: {e}")
    
    def _create_spacer_paragraph(self, height_mm: float):
        """Створення параграфа-розділювача точної висоти"""
        spacer = self.document.add_paragraph()
        spacer.paragraph_format.space_before = Pt(0)
        spacer.paragraph_format.space_after = Pt(height_mm * 2.83)  # Конвертація мм в пункти
        spacer.paragraph_format.line_spacing = 1
    
    def _create_single_image_table(self, image_data: ImageData, total_width: float, 
                                  total_height: float, left_width: float, 
                                  middle_width: float, right_width: float):
        """Створення таблиці для одного зображення з точними розмірами"""
        # Створення таблиці 1x3
        table = self.document.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.LEFT  # Притиснути до лівого краю
        
        # Налаштування висоти рядка
        row = table.rows[0]
        row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        row.height = Cm(mm_to_cm(total_height))
        
        # Налаштування комірок
        left_cell = row.cells[0]
        middle_cell = row.cells[1]  
        right_cell = row.cells[2]
        
        # Встановлення ширин комірок
        left_cell.width = Cm(mm_to_cm(left_width))
        middle_cell.width = Cm(mm_to_cm(middle_width))
        right_cell.width = Cm(mm_to_cm(right_width))
        
        # Заповнення комірок
        self._setup_left_cell(left_cell)
        self._setup_middle_cell(middle_cell, image_data, middle_width, total_height)
        self._setup_right_cell(right_cell, image_data)
        
        # Налаштування рамок (без лівої рамки у лівої та правої комірки)
        self._set_cell_borders(left_cell, top=True, bottom=True, left=False, right=True)
        self._set_cell_borders(middle_cell, top=True, bottom=True, left=True, right=True)
        self._set_cell_borders(right_cell, top=True, bottom=True, left=False, right=True)
    
    def _create_empty_image_table(self, total_width: float, total_height: float,
                                 left_width: float, middle_width: float, right_width: float):
        """Створення порожньої таблиці для збереження структури"""
        table = self.document.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        
        row = table.rows[0]
        row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        row.height = Cm(mm_to_cm(total_height))
        
        # Налаштування комірок
        for i, width in enumerate([left_width, middle_width, right_width]):
            cell = row.cells[i]
            cell.width = Cm(mm_to_cm(width))
            
            # Порожній текст
            paragraph = cell.paragraphs[0]
            paragraph.text = ""
        
        # Налаштування рамок
        self._set_cell_borders(row.cells[0], top=True, bottom=True, left=False, right=True)
        self._set_cell_borders(row.cells[1], top=True, bottom=True, left=True, right=True)
        self._set_cell_borders(row.cells[2], top=True, bottom=True, left=False, right=True)
    
    def _setup_left_cell(self, cell):
        """Налаштування лівої комірки ('Індикатор ЗРЛ')"""
        paragraph = cell.paragraphs[0]
        run = paragraph.add_run("Індикатор ЗРЛ")
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
        run.bold = True
        
        # Вертикальне центрування та поворот тексту
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Поворот тексту на 90 градусів (вертикально)
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        textDirection = OxmlElement('w:textDirection')
        textDirection.set(qn('w:val'), 'btLr')  # Bottom to Left, Right
        tcPr.append(textDirection)
    
    def _setup_middle_cell(self, cell, image_data: ImageData, width_mm: float, height_mm: float):
        """Налаштування середньої комірки (зображення)"""
        paragraph = cell.paragraphs[0]
        
        # Додавання зображення якщо файл існує
        if os.path.exists(image_data.processed_image_path):
            try:
                # Розрахунок розмірів зображення в см (з відступом для рамок)
                image_width_cm = mm_to_cm(width_mm - 2)  # Мінус 1мм з кожного боку
                image_height_cm = mm_to_cm(height_mm - 2)
                
                # Додавання зображення
                run = paragraph.add_run()
                run.add_picture(image_data.processed_image_path, 
                              width=Cm(image_width_cm), height=Cm(image_height_cm))
                
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
            except Exception as e:
                print(f"⚠️ Помилка додавання зображення {image_data.filename}: {e}")
                # Додаємо текст-заглушку
                run = paragraph.add_run(f"Зображення недоступне\n{image_data.filename}")
                run.font.size = Pt(10)
                run.font.name = 'Times New Roman'
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            # Текст-заглушка якщо файл не існує
            run = paragraph.add_run(f"Файл не знайдено\n{image_data.filename}")
            run.font.size = Pt(10)
            run.font.name = 'Times New Roman'
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    def _setup_right_cell(self, cell, image_data: ImageData):
        """Налаштування правої комірки (дані цілі)"""
        paragraph = cell.paragraphs[0]
        
        # Формування тексту з даними
        data_lines = [
            f"№{image_data.target_number}",
            "",  # Порожній рядок
            f"β-{image_data.azimuth:.0f}°",
            "",  # Порожній рядок  
            f"D-{image_data.range_km:.0f} км"
        ]
        
        # Додавання висоти якщо вона не 0
        if image_data.height > 0:
            data_lines.extend(["", f"H-{image_data.height:.1f} км"])
        
        # Додавання перешкод та статусу
        data_lines.extend([
            "",  # Порожній рядок
            image_data.obstacles,
            "",  # Порожній рядок
            image_data.detection
        ])
        
        # Створення тексту
        text_content = "\n".join(data_lines)
        run = paragraph.add_run(text_content)
        run.font.size = Pt(10)
        run.font.name = 'Times New Roman'
        
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Додавання відступу зверху
        paragraph.paragraph_format.space_before = Pt(15)
    
    def _set_cell_borders(self, cell, top=True, bottom=True, left=True, right=True):
        """Налаштування рамок комірки"""
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        tcBorders = tcPr.first_child_found_in('w:tcBorders')
        
        if tcBorders is None:
            tcBorders = OxmlElement('w:tcBorders')
            tcPr.append(tcBorders)
        
        # Стиль рамки
        border_style = 'single'
        border_size = '4'  # 0.5pt
        border_color = '000000'  # Чорний
        
        # Налаштування окремих рамок
        borders = {
            'top': top,
            'bottom': bottom, 
            'left': left,
            'right': right
        }
        
        for border_name, show_border in borders.items():
            border_element = tcBorders.find(qn(f'w:{border_name}'))
            
            if show_border:
                if border_element is None:
                    border_element = OxmlElement(f'w:{border_name}')
                    tcBorders.append(border_element)
                
                border_element.set(qn('w:val'), border_style)
                border_element.set(qn('w:sz'), border_size)
                border_element.set(qn('w:color'), border_color)
            else:
                if border_element is not None:
                    tcBorders.remove(border_element)
    
    def _set_standard_margins(self, section):
        """Встановлення стандартних полів (2.5см з усіх боків)"""
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        
        print("✅ Встановлено стандартні поля: 2.5см з усіх боків")
    
    def _set_table_margins(self, section):
        """Встановлення спеціальних полів для сторінок з таблицями"""
        # Критично важливі поля для таблиць!
        section.left_margin = Cm(mm_to_cm(ALBUM.TABLE_PAGES_LEFT_MARGIN))    # 2.5мм зліва!
        section.right_margin = Cm(mm_to_cm(ALBUM.TABLE_PAGES_RIGHT_MARGIN))  # 5мм справа
        section.top_margin = Cm(mm_to_cm(ALBUM.TABLE_PAGES_TOP_MARGIN))      # 20мм зверху
        section.bottom_margin = Cm(mm_to_cm(ALBUM.TABLE_PAGES_BOTTOM_MARGIN)) # 5мм знизу
        
        print(f"✅ Встановлено поля для таблиць: ліво={ALBUM.TABLE_PAGES_LEFT_MARGIN}мм, "
              f"право={ALBUM.TABLE_PAGES_RIGHT_MARGIN}мм, "
              f"верх={ALBUM.TABLE_PAGES_TOP_MARGIN}мм, "
              f"низ={ALBUM.TABLE_PAGES_BOTTOM_MARGIN}мм")


# ===== УТИЛІТАРНІ ФУНКЦІЇ =====

def format_ukrainian_date(date_str: str) -> str:
    """Форматування дати по-українськи"""
    try:
        if isinstance(date_str, str) and '.' in date_str:
            day, month, year = date_str.split('.')
            
            months = {
                '01': 'січня', '02': 'лютого', '03': 'березня', '04': 'квітня',
                '05': 'травня', '06': 'червня', '07': 'липня', '08': 'серпня',
                '09': 'вересня', '10': 'жовтня', '11': 'листопада', '12': 'грудня'
            }
            
            month_name = months.get(month.zfill(2), month)
            return f'"{int(day)}" {month_name} {year} року'
        
        return date_str
        
    except Exception:
        return date_str


def create_sample_album_data() -> tuple:
    """Створення тестових даних для альбому"""
    # Тестові дані зображень
    images_data = [
        ImageData(
            filename="IMG_001.jpg",
            image_path="/path/to/original/IMG_001.jpg",
            processed_image_path="/path/to/processed/IMG_001.jpg", 
            target_number="0001",
            azimuth=45.0,
            range_km=250.0,
            height=0.0,
            obstacles="без перешкод",
            detection="Виявлення",
            timestamp=datetime.now()
        ),
        ImageData(
            filename="IMG_002.jpg",
            image_path="/path/to/original/IMG_002.jpg",
            processed_image_path="/path/to/processed/IMG_002.jpg",
            target_number="