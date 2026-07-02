from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
from django.utils.timezone import now, timedelta
from .models import Partner
from services.visit_tracker import visit_tracker
import os


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


def export_statistics(request):
    context = {'title': 'Экспорт статистики посещений'}

    if request.method == 'POST':
        period = request.POST.get('period', 'day')
        end_date = now()

        if period == 'day':
            start_date = end_date - timedelta(days=1)
        elif period == 'week':
            start_date = end_date - timedelta(days=7)
        else:
            start_date = end_date - timedelta(days=30)

        stats = visit_tracker.get_stats_for_period(start_date, end_date)
        excel_path = visit_tracker.export_stats_to_excel(start_date, end_date, stats)

        with open(excel_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="statistics_{period}_{now().strftime("%Y%m%d")}.xlsx"'

        os.unlink(excel_path)
        return response

    return render(request, 'admin/export_stats.html', context)


original_get_urls = admin.site.get_urls

def get_urls():
    urls = original_get_urls()
    custom_urls = [path('export-statistics/', export_statistics, name='export-statistics')]
    return custom_urls + urls

admin.site.get_urls = get_urls
admin.site.site_header = 'RK Group Администрирование'
admin.site.site_title = 'RK Group'
admin.site.index_title = 'Управление сайтом'
