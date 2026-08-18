from datetime import timedelta

from django.db import models
from django.utils import timezone


class PhoneVerificationCode(models.Model):
    """
    Код подтверждения номера телефона на странице AI Lab. Пока это
    заглушка (см. ailab/sms.py) — реального SMS не отправляется, но
    ограничение по времени жизни и числу попыток работает по-настоящему,
    чтобы контракт не менялся при подключении реального провайдера.
    """

    CODE_TTL_MINUTES = 10
    MAX_ATTEMPTS = 5

    phone = models.CharField(max_length=20, db_index=True, verbose_name='Телефон')
    code = models.CharField(max_length=10, verbose_name='Код')
    attempts = models.PositiveSmallIntegerField(default=0, verbose_name='Попыток ввода')
    is_used = models.BooleanField(default=False, verbose_name='Использован')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    expires_at = models.DateTimeField(verbose_name='Истекает')

    class Meta:
        verbose_name = 'Код верификации телефона'
        verbose_name_plural = 'Коды верификации телефона'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=self.CODE_TTL_MINUTES)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f'{self.phone} ({"использован" if self.is_used else "активен"})'
