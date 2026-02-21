import csv
from datetime import datetime
from pathlib import Path
from django.conf import settings

def save_to_csv(name, email, message, source=''):
    """Сохраняет данные в CSV-файл (RK_masage_sate/messages.csv)"""
    csv_dir = Path(settings.BASE_DIR) / 'RK_masage_sate'
    csv_dir.mkdir(exist_ok=True)
    csv_file = csv_dir / 'messages.csv'

    file_exists = csv_file.exists()

    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Дата', 'Имя', 'Email', 'Сообщение', 'Источник'])
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            name,
            email,
            message,
            source
        ])