from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    path(
        'yandex_399b62af104e347c.html', 
        TemplateView.as_view(template_name='yandex_399b62af104e347c.html')
    ),
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
