from django.conf import settings

def site_settings(request):
    """Глобальные переменные для всех шаблонов"""
    return {
        'SITE_NAME': 'RK Group',
        'SITE_PHONE': '+7 (915) 725-88-78',
        'SITE_EMAIL': 'info@rkgroup.tech',
        'SITE_TELEGRAM': '@rkgtech',
        'DEBUG': settings.DEBUG,
    }