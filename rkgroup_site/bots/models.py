from django.db import models

class Bot(models.Model):
    BOT_TYPES = [
        ('voice', 'Голосовой бот'),
        ('voice_chat', 'Голосовой/чат бот'),
        ('recording', 'Бот для записи'),
        ('consultant', 'Бот-консультант'),
        ('nps', 'Бот для NPS-опросов'),
        ('notify', 'Бот для напоминаний и рассылок'),
    ]
    
    bot_type = models.CharField(max_length=20, choices=BOT_TYPES, unique=True)
    name = models.CharField(max_length=200, verbose_name="Название")
    short_description = models.TextField(verbose_name="Краткое описание")
    full_description = models.TextField(verbose_name="Полное описание")
    price_from = models.IntegerField(verbose_name="Цена от (руб)")
    icon = models.CharField(max_length=50, verbose_name="Иконка", default="fa-robot")
    
    # Метрики для бизнеса
    cost_reduction = models.CharField(max_length=50, blank=True, verbose_name="Сокращение затрат")
    conversion_increase = models.CharField(max_length=50, blank=True, verbose_name="Рост конверсии")
    time_saving = models.CharField(max_length=50, blank=True, verbose_name="Экономия времени")
    
    # Преимущества (хранятся как текст с разделением по строкам)
    advantages = models.TextField(blank=True, verbose_name="Преимущества (каждое с новой строки)")
    
    # Результаты внедрения (хранятся как текст с разделением по строкам)
    results = models.TextField(blank=True, verbose_name="Результаты (каждый с новой строки)")
    
    # Теги (хранятся как текст с разделением по строкам)
    tags = models.TextField(blank=True, verbose_name="Теги (каждый с новой строки)")
    
    # Интеграции
    integrations = models.TextField(blank=True, verbose_name="Интеграции (каждая с новой строки)")
    
    is_active = models.BooleanField(default=True)
    
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