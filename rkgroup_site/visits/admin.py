from django.contrib import admin

from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ['id', 'path', 'ip', 'status_code', 'created_at']
    list_filter = ['status_code']
    search_fields = ['path', 'ip', 'referer']
    readonly_fields = ['ip', 'path', 'referer', 'user_agent', 'status_code', 'created_at']

    def has_add_permission(self, request):
        return False
