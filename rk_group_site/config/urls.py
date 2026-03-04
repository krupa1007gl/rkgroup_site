from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

def yandex_verify(request):
    return HttpResponse("Verification: 399b62af104e347c")

urlpatterns = [
    path('yandex_399b62af104e347c.html', yandex_verify),
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)