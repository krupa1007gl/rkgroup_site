from django.db import models


class ContactMessage(models.Model):
    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    message = models.TextField('Сообщение')
    created_at = models.DateTimeField('Дата отправки', auto_now_add=True)
    is_read = models.BooleanField('Прочитано', default=False)

    class Meta:
        verbose_name = 'Сообщение с формы'
        verbose_name_plural = 'Сообщения с формы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.created_at.strftime("%d.%m.%Y %H:%M")}'
