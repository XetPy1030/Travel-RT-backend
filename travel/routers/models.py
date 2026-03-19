from django.core.exceptions import ValidationError
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from travel.locations.models import District, Settlement


class Router(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Легкий"
        MEDIUM = "medium", "Средний"
        HARD = "hard", "Сложный"

    class CreationMethod(models.TextChoices):
        MANUAL = "manual", "Вручную"
        AI_GENERATED = "ai_generated", "Сгенерирован ИИ"

    title = models.CharField("Название", max_length=255)
    creation_method = models.CharField(
        "Способ создания",
        max_length=20,
        choices=CreationMethod.choices,
        default=CreationMethod.MANUAL,
    )
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
            raise ValidationError("Место должно иметь либо район, либо населенный пункт")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class RouteGenerationJob(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает"
        PROCESSING = "processing", "В обработке"
        COMPLETED = "completed", "Завершён"
        FAILED = "failed", "Ошибка"

    task_id = models.CharField("ID задачи", max_length=64, unique=True, db_index=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    result = models.JSONField("Результат LLM", null=True, blank=True)
    router = models.OneToOneField(
        Router,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generation_job",
        verbose_name="Созданный маршрут",
    )
    error_message = models.TextField("Сообщение об ошибке", blank=True)
    intent = models.JSONField("Intent (параметры запроса)", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Задача генерации маршрута"
        verbose_name_plural = "Задачи генерации маршрутов"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task_id} ({self.status})"
