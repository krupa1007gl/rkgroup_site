from django.urls import path

from . import views

app_name = 'ailab'

urlpatterns = [
    path('', views.AILabPageView.as_view(), name='page'),
    path('scenario/', views.scenario_view, name='scenario'),
    path('demo/crm/', views.demo_crm_view, name='demo_crm'),
    path('demo/excel/', views.demo_excel_view, name='demo_excel'),
    path('verify/start/', views.PhoneVerifyStartView.as_view(), name='verify_start'),
    path('verify/confirm/', views.PhoneVerifyConfirmView.as_view(), name='verify_confirm'),
    path('bot/status/', views.LiveBotStatusView.as_view(), name='bot_status'),
    path('bot/notify-me/', views.LiveBotNotifyMeView.as_view(), name='bot_notify_me'),
]
