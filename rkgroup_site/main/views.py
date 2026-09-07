from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from leads.models import Lead
from leads.services import create_lead
from common.mixins import AjaxFormMixin, RateLimitMixin, HoneypotMixin
from .models import Partner
from .forms import CallbackForm, ContactForm, PartnerForm


class HomePageView(TemplateView):
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partner_badges'] = Partner.objects.filter(is_active=True, partner_type=Partner.PartnerType.BADGE)
        context['callback_form'] = CallbackForm()
        return context


class AboutPageView(TemplateView):
    """Страница «О ботах» — простое объяснение AI-агентов (см. main/about.html)."""
    template_name = 'main/about.html'


class FAQPageView(TemplateView):
    template_name = 'main/faq.html'


class PartnersPageView(RateLimitMixin, HoneypotMixin, AjaxFormMixin, FormView):
    """
    Страница для CRM-интеграторов/агентств (white-label партнёрство) —
    логотипы клиентов и партнёрские бейджи сюда не относятся, они на Главной.
    """
    template_name = 'main/partners.html'
    form_class = PartnerForm
    success_url = reverse_lazy('main:partners')
    rate_limit_key = 'partners'
    rate_limit_per_hour = 10

    def get_success_message(self, cleaned_data):
        return 'Спасибо! Мы свяжемся с вами.'

    def form_valid(self, form):
        source = getattr(self.request, 'referer', '')
        create_lead(
            lead_type=Lead.LeadType.PARTNER,
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            company=form.cleaned_data['company'],
            description='Заявка на партнёрство',
            source=source,
        )
        return super().form_valid(form)


class ContactPageView(RateLimitMixin, HoneypotMixin, AjaxFormMixin, FormView):
    template_name = 'main/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('main:contact')
    rate_limit_key = 'contact'
    rate_limit_per_hour = 10

    def get_success_message(self, cleaned_data):
        return 'Спасибо! Мы свяжемся с вами.'

    def form_valid(self, form):
        source = getattr(self.request, 'referer', '')
        create_lead(
            lead_type=Lead.LeadType.CONTACT,
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            description=form.cleaned_data['message'],
            source=source,
        )
        return super().form_valid(form)


class CallbackCreateView(RateLimitMixin, HoneypotMixin, AjaxFormMixin, FormView):
    form_class = CallbackForm
    success_url = reverse_lazy('main:home')
    rate_limit_key = 'callback'
    rate_limit_per_hour = 10

    def get_success_message(self, cleaned_data):
        return 'Спасибо! Мы перезвоним.'

    def form_valid(self, form):
        source = getattr(self.request, 'referer', '')
        create_lead(
            lead_type=Lead.LeadType.CALLBACK,
            name=form.cleaned_data['name'],
            phone=form.cleaned_data['phone'],
            description='Заявка на обратный звонок',
            source=source,
        )
        return super().form_valid(form)
