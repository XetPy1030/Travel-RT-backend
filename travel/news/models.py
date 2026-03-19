from django.db import models
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.


class News(models.Model):
    class CreationMethod(models.TextChoices):
        MANUAL = "manual", "Вручную"
        PARSING = "parsing", "Парсинг"

    title = models.CharField("Заголовок", max_length=255)
    image = models.ImageField("Изображение", upload_to="news_images/", null=True, blank=True)
    description = models.TextField("Описание")
    content = CKEditor5Field("Содержание", config_name="extends")
    published_at = models.DateTimeField("Дата публикации", default=timezone.now)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Создано пользователем",
    )
    creation_method = models.CharField(
        "Способ создания",
        max_length=20,
        choices=CreationMethod.choices,
        default=CreationMethod.MANUAL,
    )

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def __str__(self):
        return self.title
