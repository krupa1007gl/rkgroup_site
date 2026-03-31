# bots/views.py

from django.views.generic import ListView, DetailView, FormView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Bot
from .forms import ConsultationForm
from services.excel_service import excel_service  # <-- меняем импорт

class BotListView(ListView):
    model = Bot
    template_name = 'bots/bot_list.html'
    context_object_name = 'bots'
    
    def get_queryset(self):
        return Bot.objects.filter(is_active=True)

class BotDetailView(DetailView):
    model = Bot
    template_name = 'bots/bot_detail.html'
    context_object_name = 'bot'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['consultation_form'] = ConsultationForm(initial={'bot_name': self.object.name})
        
        # Получаем всех активных ботов для навигации
        bots = list(Bot.objects.filter(is_active=True).order_by('id'))
        current_index = bots.index(self.object)
        
        if current_index > 0:
            context['prev_bot'] = bots[current_index - 1]
        if current_index < len(bots) - 1:
            context['next_bot'] = bots[current_index + 1]
        
        context['current_index'] = current_index + 1
        context['total_count'] = len(bots)
        
        return context

class ConsultationCreateView(FormView):
    form_class = ConsultationForm
    success_url = reverse_lazy('bots:bot_list')
    
    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        message = form.cleaned_data.get('message', '')
        bot_name = form.cleaned_data.get('bot_name', '')
        
        # Сохраняем в Excel
        success = excel_service.add_consultation(name, email, phone, message, bot_name)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if success:
                return JsonResponse({'status': 'ok', 'message': 'Спасибо! Специалист свяжется с вами.'})
            return JsonResponse({'status': 'error', 'message': 'Ошибка'}, status=500)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return super().form_invalid(form)