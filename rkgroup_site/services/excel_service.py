import os
import csv
import logging
from datetime import datetime
from django.conf import settings
from .excel_base import BaseExcelWriter
from telegram_notifier import send_new_lead_notification, send_status_change_notification

logger = logging.getLogger(__name__)


class ExcelService:
    def __init__(self):
        self.headers = ['№', 'Имя', 'Почта', 'Телефон', 'Описание', 'Источник', 'Статус заявки', 'Дата', 'Дата обновления']
        self.leads_dir = settings.LEADS_DIR
        self.backups_dir = settings.BACKUPS_DIR
        os.makedirs(self.leads_dir, exist_ok=True)

        self.excel_writer = BaseExcelWriter(
            base_dir=self.leads_dir,
            prefix='leads',
            headers=self.headers,
            backup_dir=self.backups_dir
        )
        # Создаём первый файл, если его нет
        self.excel_writer.create_file('Заявки')
        logger.info("ExcelService инициализирован (файлы по 100 записей)")

    def _get_csv_file_path(self, sheet_name, file_num):
        """CSV также сохраняем с номером файла для соответствия"""
        month_dir = os.path.join(self.leads_dir, 'csv')
        os.makedirs(month_dir, exist_ok=True)
        return os.path.join(month_dir, f"{sheet_name}_{file_num}.csv")

    def _add_to_csv(self, sheet_name, row_data, file_num):
        file_path = self._get_csv_file_path(sheet_name, file_num)
        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerow(self.headers)

        try:
            with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerow(row_data)
            return True
        except Exception as e:
            logger.error(f"Ошибка CSV: {e}")
            return False

    def add_record(self, sheet_name, data, source=''):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        row_data = [
            data.get('name', ''),
            data.get('email', ''),
            data.get('phone', ''),
            data.get('description', ''),
            source[:200],
            'Не обработано',
            timestamp,
            timestamp
        ]

        xlsx_ok = self.excel_writer.add_row('Заявки', row_data)
        
        # Для CSV используем текущий номер файла
        csv_ok = self._add_to_csv(sheet_name, [0] + row_data, self.excel_writer.current_file_num)

        if xlsx_ok or csv_ok:
            name = data.get('name', 'Не указано')
            phone = data.get('phone', 'Не указан')
            bot_name = data.get('bot_name', '')
            send_new_lead_notification(name, phone, source, bot_name)
            logger.info(f"Запись в '{sheet_name}': {name}")
        
        return xlsx_ok or csv_ok

    def get_all_leads(self, sheet_name='Заявки'):
        """Возвращает все лиды из ВСЕХ файлов"""
        rows = self.excel_writer.read_all_rows_with_styles(sheet_name)
        formatted_leads = []
        for row in rows:
            formatted_leads.append({
                'row_num': row['row_num'],
                'data': row['data'],
                'status': row['status'],
                'file_num': row.get('file_num', 1)
            })
        return formatted_leads

    def update_lead_status(self, row_num, new_status):
        old_status = self._get_cell_value(row_num, 'Статус заявки')
        phone = self._get_cell_value(row_num, 'Телефон')
        
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if new_status == "Обработано" or new_status == "✅ Отвечено":
            fill_color = "CCFFCC"
        elif new_status == "⏰ Просрочено":
            fill_color = "FEF3C7"
        else:
            fill_color = "FFCCCC"
        
        # Обновление происходит во всех файлах (метод найдёт нужный по row_num)
        status_success = self.excel_writer.update_cell_style(
            sheet_name='Заявки',
            row_num=row_num,
            col_num=7,
            value=new_status,
            fill_color=fill_color
        )
        
        # Обновление даты обновления (пока без отдельного метода, но можно добавить)
        if status_success and phone and old_status != new_status:
            send_status_change_notification(phone, old_status, new_status)
        
        return status_success

    def _get_cell_value(self, row_num, column_name):
        return self.excel_writer.get_cell_value('Заявки', row_num, column_name)

    # Остальные методы без изменений...
    def add_callback(self, name, phone, source=''):
        return self.add_record('Обратный звонок', {
            'name': name, 'phone': phone, 'description': 'Заявка на обратный звонок'
        }, source)

    def add_consultation(self, name, email, phone, message, bot_name='', source=''):
        desc = f"Консультация по боту: {bot_name}\nСообщение: {message}" if bot_name else f"Консультация\nСообщение: {message}"
        return self.add_record('Консультации', {
            'name': name, 'email': email, 'phone': phone, 'description': desc, 'bot_name': bot_name
        }, source)

    def add_contact(self, name, email, phone, message, source=''):
        return self.add_record('Контакты', {
            'name': name, 'email': email, 'phone': phone or '', 'description': message
        }, source)

    def add_partner(self, name, email, company, source=''):
        desc = f"Компания: {company}\nЗаявка на партнерство"
        return self.add_record('Партнеры', {
            'name': name, 'email': email, 'description': desc
        }, source)


excel_service = ExcelService()
