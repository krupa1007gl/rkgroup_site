from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('projects/', views.projects, name='projects'),
    path('partners/', views.partners, name='partners'),
    path('contact/', views.contact, name='contact'),
]