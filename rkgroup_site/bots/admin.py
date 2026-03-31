from django.contrib import admin
from .models import Bot

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ['name', 'bot_type', 'price_from', 'is_active']
    list_filter = ['bot_type', 'is_active']
    search_fields = ['name']
    fieldsets = (
        ('Основное', {
            'fields': ('bot_type', 'name', 'short_description', 'full_description', 'price_from', 'icon', 'is_active')
        }),
        ('Метрики', {
            'fields': ('cost_reduction', 'conversion_increase', 'time_saving')
        }),
        ('Преимущества', {
            'fields': ('advantages',),
            'description': 'Каждое преимущество пишите с новой строки'
        }),
        ('Результаты внедрения', {
            'fields': ('results',),
            'description': 'Каждый результат пишите с новой строки'
        }),
        ('Теги', {
            'fields': ('tags',),
            'description': 'Каждый тег пишите с новой строки'
        }),
        ('Интеграции', {
            'fields': ('integrations',),
            'description': 'Каждую интеграцию пишите с новой строки'
        }),
    )