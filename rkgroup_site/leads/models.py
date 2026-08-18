from django.db import models


class Lead(models.Model):
    """
    Единая таблица заявок сайта — объединяет обратный звонок, контакты,
    консультации по ботам, заявки на партнёрство и подтверждённые номера
    AI Lab (см. lead_type). Раньше все они писались в один и тот же лист
    "Заявки" в Excel — структура полей сохранена при переносе в БД.
    """

    class LeadType(models.TextChoices):
        CALLBACK = 'callback', 'Обратный звонок'
        CONTACT = 'contact', 'Контакты'
        CONSULTATION = 'consultation', 'Консультация по боту'
        PARTNER = 'partner', 'Партнёрство'
        AI_LAB = 'ai_lab', 'AI Lab'

    class Status(models.TextChoices):
        NOT_PROCESSED = 'not_processed', 'Не обработано'
        PROCESSED = 'processed', 'Обработано'
        REPLIED = 'replied', 'Отвечено'
        EXPIRED = 'expired', 'Просрочено'

    lead_type = models.CharField(max_length=20, choices=LeadType.choices, verbose_name='Тип заявки')
    name = models.CharField(max_length=200, blank=True, verbose_name='Имя')
    email = models.EmailField(blank=True, verbose_name='Почта')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    company = models.CharField(max_length=200, blank=True, verbose_name='Компания')
    bot_name = models.CharField(max_length=200, blank=True, verbose_name='Бот')
    description = models.TextField(blank=True, verbose_name='Описание')
    source = models.CharField(max_length=200, blank=True, verbose_name='Источник')

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NOT_PROCESSED, verbose_name='Статус заявки'
    )

    phone_verified = models.BooleanField(default=False, verbose_name='Телефон подтверждён через AI Lab')
    phone_verified_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата подтверждения телефона')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_lead_type_display()}: {self.name or self.phone or self.email}'
