from django.db import models
from common.validators import validate_image_size, validate_image_extension


class Case(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название кейса")
    company = models.CharField(max_length=200, verbose_name="Компания")
    category = models.CharField(max_length=100, blank=True, verbose_name="Категория")
    short_description = models.TextField(verbose_name="Краткое описание")
    full_description = models.TextField(verbose_name="Полное описание")
    image = models.ImageField(
        upload_to='cases/', blank=True, null=True,
        validators=[validate_image_size, validate_image_extension]
    )
    results = models.TextField(blank=True, verbose_name="Результаты")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def get_results_list(self):
        results_list = []
        if self.results:
            for item in self.results.split('|'):
                if ':' in item:
                    key, value = item.split(':', 1)
                    results_list.append({'key': key.strip(), 'value': value.strip()})
        return results_list
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Кейс"
        verbose_name_plural = "Кейсы"
        ordering = ['-created_at']