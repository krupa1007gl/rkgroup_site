import logging
from abc import ABC, abstractmethod

from django.conf import settings

from .models import PhoneVerificationCode

logger = logging.getLogger(__name__)


class BaseSmsProvider(ABC):
    """
    Контракт SMS-провайдера. Вызывающий код (ailab/views.py) работает
    только через send_code()/verify_code() — при подключении реального
    провайдера меняется только реализация этого класса, URL-схема и
    вьюхи не трогаются.
    """

    @abstractmethod
    def send_code(self, phone):
        ...

    @abstractmethod
    def verify_code(self, phone, code):
        ...


class StubSmsProvider(BaseSmsProvider):
    """
    Заглушка на время, пока реальный SMS-провайдер не подключён.
    Код фиксированный (settings.AILAB_STUB_OTP_CODE, по умолчанию
    "0000") — реального SMS не отправляется, только пишется в лог.
    Решение зафиксировано осознанно: фиксированный тестовый код проще
    поддерживать для ручного QA/демо, чем случайный код, который
    негде увидеть без реальной отправки.

    TODO: заменить на реальную интеграцию, когда будет выбран провайдер.
    Кандидаты с покрытием РФ: SMS.ru, SMSC.ru, Twilio.
    """

    def send_code(self, phone):
        code = getattr(settings, 'AILAB_STUB_OTP_CODE', '0000')
        PhoneVerificationCode.objects.filter(phone=phone, is_used=False).update(is_used=True)
        PhoneVerificationCode.objects.create(phone=phone, code=code)
        logger.info('AI Lab: код для %s сгенерирован (заглушка, SMS не отправляется)', phone)

    def verify_code(self, phone, code):
        entry = (
            PhoneVerificationCode.objects
            .filter(phone=phone, is_used=False)
            .order_by('-created_at')
            .first()
        )
        if entry is None or entry.is_expired or entry.attempts >= entry.MAX_ATTEMPTS:
            return False

        entry.attempts += 1
        if entry.code != code:
            entry.save(update_fields=['attempts'])
            return False

        entry.is_used = True
        entry.save(update_fields=['attempts', 'is_used'])
        return True


sms_provider = StubSmsProvider()
