from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['id', 'lead_type', 'name', 'phone', 'email', 'status', 'phone_verified', 'created_at']
    list_filter = ['lead_type', 'status', 'phone_verified']
    search_fields = ['name', 'phone', 'email', 'company']
    readonly_fields = ['created_at', 'updated_at']
