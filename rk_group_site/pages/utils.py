import csv
import os
from datetime import datetime
from pathlib import Path
import requests
from django.conf import settings

# Настройки Telegram (лучше хранить в settings или .env)
TELEGRAM_BOT_TOKEN = 'ВАШ_ТОКЕН'
TELEGRAM_CHAT_ID = 'ВАШ_CHAT_ID'

def send_telegram_message(text):
    """Отправляет сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

def save_to_csv(name, email, message):
    """Сохраняет данные в CSV файл"""
    
    csv_file = Path(settings.BASE_DIR) / 'media' / 'messages.csv'
    csv_file.parent.mkdir(exist_ok=True)
    

    file_exists = csv_file.exists()
    
    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Дата', 'Имя', 'Email', 'Сообщение'])
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), name, email, message])