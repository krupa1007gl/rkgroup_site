from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.edit import FormView
from django.core.cache import cache
from django.conf import settings

RATE_LIMIT_MESSAGE = 'Слишком много запросов. Попробуйте через час.'


def check_rate_limit_key(key, limit, period=3600):
    """
    Общая проверка rate limit по произвольному ключу кэша — используется
    и RateLimitMixin (лимит по IP на форме), и вьюхами AI Lab (лимит по
    номеру телефона отдельно от лимита по IP).
    Возвращает True, если запрос ещё разрешён (и увеличивает счётчик).
    """
    if not getattr(settings, 'RATELIMIT_ENABLED', False):
        return True

    count = cache.get(key, 0)
    if count >= limit:
        return False

    cache.set(key, count + 1, period)
    return True


class AjaxFormMixin(FormView):
    """Миксин для обработки AJAX-запросов форм"""
    
    def get_success_message(self, cleaned_data):
        return "Спасибо! Мы свяжемся с вами."
    
    def form_valid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'ok',
                'message': self.get_success_message(form.cleaned_data)
            })
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0] if error_list else 'Ошибка'
            return JsonResponse({
                'status': 'error',
                'errors': errors,
                'message': 'Проверьте правильность заполнения формы'
            }, status=400)
        return super().form_invalid(form)


class RateLimitMixin:
    """Миксин для ограничения частоты запросов"""
    
    rate_limit_key = 'form_submit'
    rate_limit_per_hour = 10
    
    def get_rate_limit_key(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        return f"ratelimit_{self.rate_limit_key}_{ip}"
    
    def check_rate_limit(self, request):
        key = self.get_rate_limit_key(request)
        return check_rate_limit_key(key, self.rate_limit_per_hour, period=3600)
    
    def dispatch(self, request, *args, **kwargs):
        if not self.check_rate_limit(request):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': RATE_LIMIT_MESSAGE
                }, status=429)
            return HttpResponse(RATE_LIMIT_MESSAGE, status=429, content_type='text/plain; charset=utf-8')
        return super().dispatch(request, *args, **kwargs)


class HoneypotMixin:
    """Миксин для защиты от ботов через honeypot поле"""
    
    honeypot_field = 'website'
    
    def check_honeypot(self, request):
        if request.POST.get(self.honeypot_field):
            return False
        return True
    
    def post(self, request, *args, **kwargs):
        if not self.check_honeypot(request):
            # Ничего не сохраняем и не логируем как ошибку — просто делаем
            # вид, что всё прошло успешно, не выдавая боту, что он пойман.
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'message': 'Спасибо!'})
            return HttpResponseRedirect(self.get_success_url())
        return super().post(request, *args, **kwargs)
