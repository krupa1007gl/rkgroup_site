from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Раздел «Кейсы» скрыт: ссылок в навигации нет, и прямой заход по /cases/
# тоже не открывает страницу — маршруты приложения не подключены, любой
# путь под /cases/ отдаёт 404. Само приложение (модель, данные, шаблоны)
# остаётся в проекте, чтобы вернуть раздел одной строкой, когда появится
# первый настоящий кейс.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('ailab/', include('ailab.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
