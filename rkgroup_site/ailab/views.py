import json
from pathlib import Path

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from common.mixins import check_rate_limit_key
from common.validators import validate_phone
from leads.models import Lead
from leads.services import create_lead

from .sms import sms_provider

FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures'
HONEYPOT_FIELD = 'website'


class AILabPageView(TemplateView):
    template_name = 'ailab/ailab.html'


def _parse_json(request):
    try:
        return json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return None


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0] if xff else request.META.get('REMOTE_ADDR', '')


def _rate_limited_response():
    return JsonResponse({'status': 'error', 'message': 'Слишком много запросов. Попробуйте позже.'}, status=429)


def _serve_fixture(name):
    path = FIXTURES_DIR / name
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data, safe=False)


@require_GET
def scenario_view(request):
    """
    Сценарий-заглушка (состояние 1 AI Lab) — статичные реплики с
    таймингами. Бэкенд тут по ТЗ не нужен, просто отдаём JSON-файл.
    TODO: финальный текст сценария согласовать с продуктом — сейчас
    placeholder (см. ailab/fixtures/scenario.json).
    """
    return _serve_fixture('scenario.json')


@require_GET
def demo_crm_view(request):
    """Статичный демо-контент вкладки «CRM» (до/после), без обращения к реальным данным."""
    return _serve_fixture('demo_crm.json')


@require_GET
def demo_excel_view(request):
    """Статичный демо-контент вкладки «Excel» (до/после), без обращения к реальным данным."""
    return _serve_fixture('demo_excel.json')


class PhoneVerifyStartView(View):
    """
    Приём номера телефона + отправка кода (пока — через SMS-заглушку,
    см. ailab/sms.py). Валидация формата на сервере, honeypot и
    rate limit отдельно по IP и по номеру телефона.
    """

    ip_rate_limit = 10
    phone_rate_limit = 5

    def post(self, request, *args, **kwargs):
        data = _parse_json(request)
        if data is None:
            return JsonResponse({'status': 'error', 'message': 'Некорректный запрос'}, status=400)

        if data.get(HONEYPOT_FIELD):
            # Боту говорим, что всё ок, ничего не отправляем и не логируем.
            return JsonResponse({'status': 'ok'})

        if not check_rate_limit_key(f'ratelimit_ailab_start_ip_{_client_ip(request)}', self.ip_rate_limit):
            return _rate_limited_response()

        phone = data.get('phone', '')
        try:
            phone = validate_phone(phone)
        except ValidationError as exc:
            return JsonResponse({'status': 'error', 'message': exc.messages[0]}, status=400)

        if not check_rate_limit_key(f'ratelimit_ailab_start_phone_{phone}', self.phone_rate_limit):
            return _rate_limited_response()

        sms_provider.send_code(phone)
        return JsonResponse({'status': 'ok', 'message': 'Код отправлен'})


class PhoneVerifyConfirmView(View):
    """Проверка кода — только на сервере, не на фронтенде."""

    ip_rate_limit = 20

    def post(self, request, *args, **kwargs):
        data = _parse_json(request)
        if data is None:
            return JsonResponse({'status': 'error', 'message': 'Некорректный запрос'}, status=400)

        if not check_rate_limit_key(f'ratelimit_ailab_confirm_ip_{_client_ip(request)}', self.ip_rate_limit):
            return _rate_limited_response()

        phone = data.get('phone', '')
        code = data.get('code', '')
        try:
            phone = validate_phone(phone)
        except ValidationError as exc:
            return JsonResponse({'status': 'error', 'message': exc.messages[0]}, status=400)

        if not sms_provider.verify_code(phone, code):
            return JsonResponse({'status': 'error', 'message': 'Неверный или просроченный код'}, status=400)

        source = getattr(request, 'referer', '') or 'AI Lab'
        create_lead(
            lead_type=Lead.LeadType.AI_LAB,
            phone=phone,
            description='Подтверждённый номер телефона со страницы AI Lab',
            source=source,
            phone_verified=True,
        )
        return JsonResponse({'status': 'ok', 'verified': True})


class LiveBotStatusView(View):
    """
    Живой бот на платформе Twin ещё не подключён. Единая точка входа —
    когда интеграция будет готова, здесь появится реальный вызов
    Twin API/виджета, контракт с фронтендом (этот URL) не изменится.
    """

    def get(self, request, *args, **kwargs):
        return JsonResponse({'status': 'coming_soon'})


class LiveBotNotifyMeView(View):
    """«Сообщить, когда запустите живого бота» — сохраняем как лида."""

    ip_rate_limit = 10

    def post(self, request, *args, **kwargs):
        data = _parse_json(request)
        if data is None:
            return JsonResponse({'status': 'error', 'message': 'Некорректный запрос'}, status=400)

        if data.get(HONEYPOT_FIELD):
            return JsonResponse({'status': 'ok'})

        if not check_rate_limit_key(f'ratelimit_ailab_notify_ip_{_client_ip(request)}', self.ip_rate_limit):
            return _rate_limited_response()

        phone = data.get('phone', '')
        try:
            phone = validate_phone(phone)
        except ValidationError as exc:
            return JsonResponse({'status': 'error', 'message': exc.messages[0]}, status=400)

        create_lead(
            lead_type=Lead.LeadType.AI_LAB,
            name=data.get('name', ''),
            phone=phone,
            description='Хочет узнать о запуске живого бота (AI Lab)',
            source='AI Lab',
        )
        return JsonResponse({'status': 'ok'})
