#!/usr/bin/env python
"""
Скрипт для миграции с SQLite на PostgreSQL
Запуск: python migrate_to_postgres.py
"""

import os
import sys
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rkgroup.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def migrate_to_postgres():
    print("🔄 НАЧАЛО МИГРАЦИИ SQLite → PostgreSQL")
    
    print("📦 Создание дампа из SQLite...")
    call_command('dumpdata', 
                 '--natural-foreign', 
                 '--natural-primary',
                 '--output=db_dump.json')
    
    print("⚠️ ВНИМАНИЕ: Измените DATABASE_URL в .env на PostgreSQL!")
    print("   Пример: DATABASE_URL=postgres://user:pass@localhost:5432/dbname")
    
    input("Нажмите Enter после изменения .env...")
    
    print("🔄 Применение миграций к PostgreSQL...")
    call_command('migrate', '--noinput')
    
    print("📥 Загрузка данных в PostgreSQL...")
    call_command('loaddata', 'db_dump.json')
    
    print("🗑️ Очистка кэша...")
    from django.core.cache import cache
    cache.clear()
    
    print("✅ МИГРАЦИЯ ЗАВЕРШЕНА!")
    print("   Проверьте данные и удалите db_dump.json и старый db.sqlite3")

if __name__ == '__main__':
    migrate_to_postgres()
