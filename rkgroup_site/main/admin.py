from django.contrib import admin
from django.urls import path

from leads.views import leads_list_view, update_lead_status_view
from visits.admin import export_statistics

from .models import Partner


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


original_get_urls = admin.site.get_urls


def get_urls():
    custom_urls = [
        path('leads/', admin.site.admin_view(leads_list_view), name='leads_list'),
        path('leads/update-status/', admin.site.admin_view(update_lead_status_view), name='leads_update_status'),
        path('export-statistics/', admin.site.admin_view(export_statistics), name='export-statistics'),
    ]
    return custom_urls + original_get_urls()


admin.site.get_urls = get_urls
admin.site.site_header = 'RK Group Администрирование'
admin.site.site_title = 'RK Group'
admin.site.index_title = 'Управление сайтом'
