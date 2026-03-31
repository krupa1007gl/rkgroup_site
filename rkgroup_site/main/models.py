from django.db import models

class Partner(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    logo = models.ImageField(upload_to='partners/', blank=True, null=True)
    website = models.URLField(blank=True, verbose_name="Сайт")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Партнер"
        verbose_name_plural = "Партнеры"
        ordering = ['order']