from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from .models import Bot
from .forms import ConsultationForm
from leads.models import Lead
from leads.services import create_lead
from common.mixins import AjaxFormMixin, RateLimitMixin, HoneypotMixin


class BotListView(ListView):
    model = Bot
    template_name = 'bots/bot_list.html'
    context_object_name = 'bots'
    paginate_by = 9
    
    def get_queryset(self):
        return Bot.objects.get_active_bots()


class BotDetailView(DetailView):
    model = Bot
    template_name = 'bots/bot_detail.html'
    context_object_name = 'bot'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['consultation_form'] = ConsultationForm(initial={'bot_name': self.object.name})
        
        nav_data = Bot.objects.get_bot_with_navigation(self.object.pk)
        
        if nav_data:
            context['prev_bot'] = nav_data['prev']
            context['next_bot'] = nav_data['next']
            context['current_index'] = nav_data['index']
            context['total_count'] = nav_data['total']
        
        return context


class ConsultationCreateView(RateLimitMixin, HoneypotMixin, AjaxFormMixin, FormView):
    form_class = ConsultationForm
    success_url = reverse_lazy('bots:bot_list')
    rate_limit_key = 'consultation'
    rate_limit_per_hour = 10
    
    def get_success_message(self, cleaned_data):
        return f"Спасибо, {cleaned_data['name']}! Специалист свяжется с вами."
    
    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        message = form.cleaned_data.get('message', '')
        bot_name = form.cleaned_data.get('bot_name', '')

        description = f"Консультация по боту: {bot_name}\nСообщение: {message}" if bot_name else f"Консультация\nСообщение: {message}"
        create_lead(
            lead_type=Lead.LeadType.CONSULTATION,
            name=name,
            email=email,
            phone=phone,
            bot_name=bot_name,
            description=description,
        )

        return super().form_valid(form)
