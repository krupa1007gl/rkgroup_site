from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('about/', views.AboutPageView.as_view(), name='about'),
    path('partners/', views.PartnersPageView.as_view(), name='partners'),
    path('contact/', views.ContactPageView.as_view(), name='contact'),
    path('callback/', views.CallbackCreateView.as_view(), name='callback'),
]