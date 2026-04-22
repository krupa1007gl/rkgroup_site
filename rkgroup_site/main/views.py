# main/views.py

from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.http import JsonResponse
from bots.models import Bot
from cases.models import Case
from news.models import News
from .models import Partner
from .forms import CallbackForm, ContactForm
from services.excel_service import excel_service

class HomePageView(TemplateView):
    template_name = 'main/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cases'] = Case.objects.filter(is_active=True)[:4]
        context['news'] = News.objects.filter(is_active=True)[:3]
        context['bots'] = Bot.objects.filter(is_active=True)[:3]
        context['partners'] = Partner.objects.filter(is_active=True)[:6]
        context['callback_form'] = CallbackForm()
        return context

class AboutPageView(TemplateView):
    template_name = 'main/about.html'

class PartnersPageView(TemplateView):
    template_name = 'main/partners.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partners'] = Partner.objects.filter(is_active=True)
        return context
    
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        company = request.POST.get('company')
        
        success = excel_service.add_partner(name, email, company)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if success:
                return JsonResponse({'status': 'ok', 'message': 'Спасибо! Мы свяжемся с вами.'})
            return JsonResponse({'status': 'error', 'message': 'Ошибка'}, status=500)
        
        context = self.get_context_data(**kwargs)
        if success:
            context['message'] = 'Спасибо! Мы свяжемся с вами.'
        return self.render_to_response(context)

class ContactPageView(FormView):
    template_name = 'main/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('main:contact')
    
    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']
        
        # Сохраняем в Excel (телефон не обязателен)
        success = excel_service.add_contact(name, email, '', message)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if success:
                return JsonResponse({'status': 'ok', 'message': 'Спасибо! Мы свяжемся с вами.'})
            return JsonResponse({'status': 'error', 'message': 'Ошибка'}, status=500)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0] if error_list else 'Ошибка'
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
        return super().form_invalid(form)

class CallbackCreateView(FormView):
    form_class = CallbackForm
    success_url = reverse_lazy('main:home')
    
    def form_valid(self, form):
        name = form.cleaned_data['name']
        phone = form.cleaned_data['phone']
        
        success = excel_service.add_callback(name, phone)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if success:
                return JsonResponse({'status': 'ok', 'message': 'Спасибо! Мы перезвоним.'})
            return JsonResponse({'status': 'error', 'message': 'Ошибка'}, status=500)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return super().form_invalid(form)