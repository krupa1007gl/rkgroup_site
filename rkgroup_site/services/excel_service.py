# services/excel_service.py

import os
from datetime import datetime
from openpyxl import Workbook, load_workbook
from django.conf import settings

class ExcelService:
    def __init__(self):
        self.excel_file = os.path.join(settings.BASE_DIR, 'leads.xlsx')
        self._init_workbook()
    
    def _init_workbook(self):
        """Инициализировать Excel файл с листами, если его нет"""
        if not os.path.exists(self.excel_file):
            wb = Workbook()
            
            # Удаляем дефолтный лист
            wb.remove(wb.active)
            
            # Создаем листы
            sheets = ['Обратный звонок', 'Консультации', 'Контакты', 'Партнеры']
            
            for sheet_name in sheets:
                ws = wb.create_sheet(sheet_name)
                # Добавляем заголовки
                headers = ['№', 'Имя клиента', 'Почта', 'Номер телефона', 'Описание', 'Дата']
                ws.append(headers)
                
                # Настраиваем ширину колонок
                ws.column_dimensions['A'].width = 6
                ws.column_dimensions['B'].width = 25
                ws.column_dimensions['C'].width = 30
                ws.column_dimensions['D'].width = 20
                ws.column_dimensions['E'].width = 50
                ws.column_dimensions['F'].width = 20
            
            wb.save(self.excel_file)
    
    def _get_worksheet(self, sheet_name):
        """Получить рабочий лист"""
        try:
            wb = load_workbook(self.excel_file)
            if sheet_name not in wb.sheetnames:
                ws = wb.create_sheet(sheet_name)
                ws.append(['№', 'Имя клиента', 'Почта', 'Номер телефона', 'Описание', 'Дата'])
                wb.save(self.excel_file)
            else:
                ws = wb[sheet_name]
            return wb, ws
        except Exception as e:
            print(f"Ошибка открытия Excel файла: {e}")
            return None, None
    
    def _get_next_row_number(self, ws):
        """Получить следующий номер строки"""
        return ws.max_row + 1
    
    def add_callback(self, name, phone):
        """Добавить заявку на обратный звонок"""
        try:
            wb, ws = self._get_worksheet('Обратный звонок')
            if not ws:
                return False
            
            row_num = self._get_next_row_number(ws)
            data = [
                row_num,
                name,
                '',  # почта пустая для обратного звонка
                phone,
                'Заявка на обратный звонок',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            ws.append(data)
            wb.save(self.excel_file)
            print(f"Заявка на обратный звонок добавлена: {name}, {phone}")
            return True
        except Exception as e:
            print(f"Ошибка добавления обратного звонка: {e}")
            return False
    
    def add_consultation(self, name, email, phone, message, bot_name=''):
        """Добавить заявку на консультацию"""
        try:
            wb, ws = self._get_worksheet('Консультации')
            if not ws:
                return False
            
            row_num = self._get_next_row_number(ws)
            
            # Формируем описание
            description = f"Консультация по боту: {bot_name}\nСообщение: {message}" if bot_name else f"Консультация\nСообщение: {message}"
            
            data = [
                row_num,
                name,
                email,
                phone,
                description,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            ws.append(data)
            wb.save(self.excel_file)
            print(f"Заявка на консультацию добавлена: {name}, {email}, {phone}")
            return True
        except Exception as e:
            print(f"Ошибка добавления консультации: {e}")
            return False
    
    def add_contact(self, name, email, phone, message):
        """Добавить сообщение из формы контактов"""
        try:
            wb, ws = self._get_worksheet('Контакты')
            if not ws:
                return False
            
            row_num = self._get_next_row_number(ws)
            data = [
                row_num,
                name,
                email,
                phone,
                message,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            ws.append(data)
            wb.save(self.excel_file)
            print(f"Сообщение из контактов добавлено: {name}, {email}")
            return True
        except Exception as e:
            print(f"Ошибка добавления контакта: {e}")
            return False
    
    def add_partner(self, name, email, company):
        """Добавить заявку на партнерство"""
        try:
            wb, ws = self._get_worksheet('Партнеры')
            if not ws:
                return False
            
            row_num = self._get_next_row_number(ws)
            description = f"Компания: {company}\nЗаявка на партнерство"
            data = [
                row_num,
                name,
                email,
                '',  # телефон не обязателен для партнеров
                description,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            ws.append(data)
            wb.save(self.excel_file)
            print(f"Заявка на партнерство добавлена: {name}, {company}")
            return True
        except Exception as e:
            print(f"Ошибка добавления партнера: {e}")
            return False

# Создаем глобальный экземпляр
excel_service = ExcelService()