from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from rest_framework.exceptions import ValidationError

from travel.locations.models import District, Settlement


class Router(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Легкий"
        MEDIUM = "medium", "Средний"
        HARD = "hard", "Сложный"

    title = models.CharField("Название", max_length=255)
    short_description = models.TextField("Краткое описание")
    full_description = CKEditor5Field("Полное описание", config_name="extends")
    image = models.ImageField(
        "Изображение",
        upload_to="routers/images/",
        null=True,
        blank=True,
        help_text="Загрузите изображение для маршрута",
    )
    duration = models.DurationField(
        "Продолжительность маршрута",
        help_text="Укажите продолжительность маршрута в формате ЧЧ:ММ:СС",
    )
    difficulty = models.CharField(
        "Сложность",
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM,
        help_text="Выберите уровень сложности маршрута",
    )

    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="routers",
        verbose_name="Район",
    )
    settlement = models.ForeignKey(
        Settlement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="routers",
        verbose_name="Населённый пункт",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"
        ordering = ["title"]

    def clean(self):
        if not self.district and not self.settlement:
            raise ValidationError(
                "Место должно иметь либо район, либо населенный пункт"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
