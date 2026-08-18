from django.db import models


class Visit(models.Model):
    """Лог посещений (заменяет прежний Excel-файл visits.xlsx)."""

    ip = models.CharField(max_length=45, blank=True, verbose_name='IP')
    path = models.CharField(max_length=500, verbose_name='URL')
    referer = models.CharField(max_length=500, blank=True, verbose_name='Referer')
    user_agent = models.TextField(blank=True, verbose_name='User-Agent')
    status_code = models.PositiveSmallIntegerField(verbose_name='Статус')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время')

    class Meta:
        verbose_name = 'Посещение'
        verbose_name_plural = 'Посещения'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.path} ({self.ip}) — {self.created_at}'
