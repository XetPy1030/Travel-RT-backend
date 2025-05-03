from django.core.exceptions import ValidationError
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from travel.locations.models import District, Settlement


class Place(models.Model):
    title = models.CharField("Название", max_length=255)
    short_description = models.TextField("Краткое описание")
    full_description = CKEditor5Field("Полное описание", config_name="extends")
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="places",
        verbose_name="Район",
    )
    settlement = models.ForeignKey(
        Settlement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="places",
        verbose_name="Населённый пункт",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Интересное место"
        verbose_name_plural = "Интересные места"
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


class PlaceImage(models.Model):
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Место",
    )
    image = models.ImageField(
        "Изображение",
        upload_to="places/images/",
    )
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Изображение места"
        verbose_name_plural = "Изображения мест"
        ordering = ["order"]

    def __str__(self):
        return f"Изображение для {self.place.title}"
