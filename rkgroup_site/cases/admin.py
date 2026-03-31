from django.contrib import admin
from .models import Case

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'is_active', 'created_at']
    list_filter = ['is_active', 'category']
    search_fields = ['title', 'company']