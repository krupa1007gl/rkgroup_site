from django.urls import path
from . import views
from .admin import export_statistics

app_name = 'main'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('about/', views.AboutPageView.as_view(), name='about'),
    path('partners/', views.PartnersPageView.as_view(), name='partners'),
    path('contact/', views.ContactPageView.as_view(), name='contact'),
    path('callback/', views.CallbackCreateView.as_view(), name='callback'),
    path('export-statistics/', export_statistics, name='export_statistics'),
    path('leads/', views.LeadListView.as_view(), name='leads_list'),
    path('leads/update-status/', views.update_lead_status, name='update_lead_status'),
]
