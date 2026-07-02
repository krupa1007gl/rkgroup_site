from django.db import models
from .managers import BotManager


class Bot(models.Model):
    class BotType(models.TextChoices):
        VOICE = 'voice', 'Голосовой бот'
        VOICE_CHAT = 'voice_chat', 'Голосовой/чат бот'
        RECORDING = 'recording', 'Бот для записи'
        CONSULTANT = 'consultant', 'Бот-консультант'
        NPS = 'nps', 'Бот для NPS-опросов'
        NOTIFY = 'notify', 'Бот для напоминаний и рассылок'
    
    bot_type = models.CharField(max_length=20, choices=BotType.choices, unique=True)
    name = models.CharField(max_length=200, verbose_name="Название")
    short_description = models.TextField(verbose_name="Краткое описание")
    full_description = models.TextField(verbose_name="Полное описание")
    price_from = models.IntegerField(verbose_name="Цена от (руб)")
    icon = models.CharField(max_length=50, verbose_name="Иконка", default="fa-robot")
    
    cost_reduction = models.CharField(max_length=50, blank=True, verbose_name="Сокращение затрат")
    conversion_increase = models.CharField(max_length=50, blank=True, verbose_name="Рост конверсии")
    time_saving = models.CharField(max_length=50, blank=True, verbose_name="Экономия времени")
    
    advantages = models.TextField(blank=True, verbose_name="Преимущества")
    results = models.TextField(blank=True, verbose_name="Результаты")
    tags = models.TextField(blank=True, verbose_name="Теги")
    integrations = models.TextField(blank=True, verbose_name="Интеграции")
    
    is_active = models.BooleanField(default=True)
    # ❌ УДАЛИ ЭТИ ПОЛЯ — ОНИ НЕ НУЖНЫ
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    
    objects = BotManager()
    
    def get_advantages_list(self):
        return [a.strip() for a in self.advantages.split('\n') if a.strip()] if self.advantages else []
    
    def get_results_list(self):
        return [r.strip() for r in self.results.split('\n') if r.strip()] if self.results else []
    
    def get_tags_list(self):
        return [t.strip() for t in self.tags.split('\n') if t.strip()] if self.tags else []
    
    def get_integrations_list(self):
        return [i.strip() for i in self.integrations.split('\n') if i.strip()] if self.integrations else []
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Бот"
        verbose_name_plural = "Боты"