from collections import Counter

from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import now, timedelta

from services.xlsx_export import build_workbook

from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ['id', 'path', 'ip', 'status_code', 'created_at']
    list_filter = ['status_code']
    search_fields = ['path', 'ip', 'referer']
    readonly_fields = ['ip', 'path', 'referer', 'user_agent', 'status_code', 'created_at']

    def has_add_permission(self, request):
        return False


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

        qs = Visit.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        total_visits = qs.count()
        unique_ips = qs.values('ip').distinct().count()
        top_pages = Counter(qs.values_list('path', flat=True)).most_common(10)
        top_referers = Counter(qs.exclude(referer='').values_list('referer', flat=True)).most_common(10)

        sheets = [
            ('Общая статистика', ['Показатель', 'Значение'], [
                ['Период', f"{start_date.strftime('%d.%m.%Y')} — {end_date.strftime('%d.%m.%Y')}"],
                ['Всего визитов', total_visits],
                ['Уникальных IP', unique_ips],
            ]),
            ('Топ-10 страниц', ['URL', 'Количество'], [[url, count] for url, count in top_pages]),
            ('Топ-10 источников', ['Referer', 'Количество'], [[ref, count] for ref, count in top_referers]),
        ]
        buffer = build_workbook(sheets)

        response = HttpResponse(
            buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="statistics_{period}_{now().strftime("%Y%m%d")}.xlsx"'
        return response

    return render(request, 'admin/export_stats.html', context)
