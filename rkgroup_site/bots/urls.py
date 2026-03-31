from django.urls import path
from . import views

app_name = 'bots'

urlpatterns = [
    path('', views.BotListView.as_view(), name='bot_list'),
    path('<int:pk>/', views.BotDetailView.as_view(), name='bot_detail'),
    path('consultation/', views.ConsultationCreateView.as_view(), name='consultation'),
]