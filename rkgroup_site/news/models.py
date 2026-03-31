from django.db import models

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    date = models.DateField(verbose_name="Дата")
    short_text = models.TextField(verbose_name="Краткий текст")
    full_text = models.TextField(blank=True, verbose_name="Полный текст")
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-date']