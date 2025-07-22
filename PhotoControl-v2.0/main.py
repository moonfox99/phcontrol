# Додати в main.py ці зміни:

# В імпортах додати:
from core.album_creator import AlbumCreator, ImageData, TitleData
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        # ... existing code ...
        
        # Додати систему альбомів
        self.album_creator = AlbumCreator()
        self.album_images_data: List[ImageData] = []  # Дані для альбому
        
    def setup_connections(self):
        # ... existing code ...
        
        # Додати зв'язок з правою панеллю для додавання до альбому
        self.data_panel.add_to_album_requested.connect(self.add_current_to_album)
        
    def add_current_to_album(self):
        """Додавання поточного зображення до альбому"""
        if not self.image_processor or not self.current_image_path:
            QMessageBox.warning(self, "Увага", "Немає зображення для додавання")
            return
        
        try:
            # Отримання даних з правої панелі
            target_data = self.data_panel.get_target_data()
            radar_data = self.data_panel.get_radar_data()
            
            # Перевірка готовності даних
            complete_data = self.data_panel.get_complete_image_data()
            if not complete_data:
                QMessageBox.warning(self, "Увага", "Дані неповні для додавання до альбому")
                return
            
            # Збереження обробленого зображення для альбому
            processed_filename = f"processed_{target_data['target_number']}_{os.path.basename(self.current_image_path)}"
            processed_path = os.path.join(
                os.path.dirname(self.current_image_path), 
                "processed", 
                processed_filename
            )
            
            # Створення папки якщо не існує
            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            
            # Збереження з усіма елементами
            success = self.image_processor.save_processed_image(
                processed_path,
                include_grid=True,
                include_analysis=True,
                include_radar_desc=radar_data['enabled']
            )
            
            if not success:
                QMessageBox.critical(self, "Помилка", "Не вдалося зберегти оброблене зображення")
                return
            
            # Створення об'єкта ImageData
            image_data = ImageData(
                filename=os.path.basename(self.current_image_path),
                image_path=self.current_image_path,
                processed_image_path=processed_path,
                target_number=target_data['target_number'],
                azimuth=target_data['azimuth'],
                range_km=target_data['range_km'],
                height=target_data['height'],
                obstacles=target_data['obstacles'],
                detection=target_data['detection'],
                timestamp=datetime.now()
            )
            
            # Додавання до списку альбому
            self.album_images_data.append(image_data)
            
            # Позначення в браузері як оброблене
            if self.is_browser_visible and self.current_image_path:
                self.browser_panel.mark_as_processed(self.current_image_path)
            
            # Оновлення лічильника в лівій панелі
            self.control_panel.processed_count = len(self.album_images_data)
            self.control_panel.update_processed_count_display()
            self.control_panel.create_album_btn.setEnabled(True)
            
            # Автоматичне збільшення номера цілі
            self.data_panel.auto_increment_target_number()
            
            # Очищення точки аналізу для наступного зображення
            self.data_panel.clear_analysis_point()
            
            # Повідомлення про успіх
            self.control_panel.add_result(f"✅ Додано до альбому: {target_data['target_number']} - {os.path.basename(self.current_image_path)}")
            
            QMessageBox.information(self, "Успіх", 
                                  f"Зображення додано до альбому!\n" +
                                  f"Ціль №{target_data['target_number']}\n" +
                                  f"Всього в альбомі: {len(self.album_images_data)}")
            
            print(f"✅ Зображення додано до альбому: {target_data['target_number']}")
            
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка додавання до альбому:\n{str(e)}")
            print(f"❌ Помилка додавання до альбому: {e}")
    
    def create_album(self):
        """Створення Word альбому з оброблених зображень"""
        try:
            # Перевірка наявності оброблених зображень
            if not self.album_images_data:
                QMessageBox.information(self, "Інформація", 
                                      "Немає оброблених зображень для створення альбому.\n"
                                      "Додайте зображення натиснувши 'Додати до альбому' в правій панелі")
                return
            
            # Отримання даних для титульної сторінки
            title_data = self.get_title_page_data()
            if not title_data:
                return  # Користувач скасував
            
            # Діалог вибору файлу для збереження
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Зберегти альбом",
                f"Фотоальбом_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                "Word документи (*.docx);;Всі файли (*.*)"
            )
            
            if file_path:
                # Показ індикатора прогресу
                from PyQt5.QtWidgets import QProgressDialog
                progress = QProgressDialog("Створення альбому...", "Скасувати", 0, 100, self)
                progress.setWindowModality(Qt.WindowModal)
                progress.show()
                progress.setValue(10)
                
                # Створення альбому
                success = self.album_creator.create_album(
                    self.album_images_data, 
                    title_data, 
                    file_path
                )
                
                progress.setValue(100)
                progress.close()
                
                if success:
                    QMessageBox.information(self, "Успіх", 
                                          f"Альбом створено успішно!\n" +
                                          f"Файл: {file_path}\n" +
                                          f"Зображень: {len(self.album_images_data)}")
                    
                    # Пропозиція очистити дані
                    reply = QMessageBox.question(self, "Очищення", 
                                               "Очистити дані альбому після створення?",
                                               QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        self.clear_album_data()
                else:
                    QMessageBox.critical(self, "Помилка", "Не вдалося створити альбом")
        
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка створення альбому:\n{str(e)}")
            print(f"❌ Помилка створення альбому: {e}")
    
    def get_title_page_data(self) -> Optional[TitleData]:
        """Отримання даних для титульної сторінки через діалог"""
        try:
            from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Дані титульної сторінки")
            dialog.setModal(True)
            dialog.resize(400, 300)
            
            layout = QVBoxLayout()
            form_layout = QFormLayout()
            
            # Поля для вводу
            date_edit = QDateEdit()
            date_edit.setDate(QDate.currentDate())
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat("dd.MM.yyyy")
            
            unit_input = QLineEdit("А0000")
            commander_rank_input = QLineEdit("полковник")
            commander_name_input = QLineEdit("П.П. ПЕТРЕНКО")
            chief_rank_input = QLineEdit("підполковник")
            chief_name_input = QLineEdit("С.С. СИДОРЕНКО")
            
            # Додавання полів
            form_layout.addRow("Дата:", date_edit)
            form_layout.addRow("Підрозділ:", unit_input)
            form_layout.addRow("Звання командира:", commander_rank_input)
            form_layout.addRow("ПІБ командира:", commander_name_input)
            form_layout.addRow("Звання нач. штабу:", chief_rank_input)
            form_layout.addRow("ПІБ нач. штабу:", chief_name_input)
            
            # Кнопки
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            
            layout.addLayout(form_layout)
            layout.addWidget(buttons)
            dialog.setLayout(layout)
            
            # Показ діалогу
            if dialog.exec_() == QDialog.Accepted:
                return TitleData(
                    date=date_edit.date().toString("dd.MM.yyyy"),
                    unit_info=unit_input.text().strip(),
                    commander_rank=commander_rank_input.text().strip(),