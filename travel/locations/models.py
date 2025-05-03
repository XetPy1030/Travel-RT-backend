from django.db import models


class District(models.Model):
    name = models.CharField("Название района", max_length=100)
    administrative_center = models.ForeignKey(
        "Settlement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="governed_districts",
        verbose_name="Административный центр",
    )

    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Settlement(models.Model):
    class SettlementType(models.TextChoices):
        CITY = "city", "Город"
        TOWN = "town", "Посёлок городского типа"
        VILLAGE = "village", "Село"
        VILLAGE_HAMLET = "village_hamlet", "Деревня"

    name = models.CharField("Название", max_length=100)
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="settlements",
        verbose_name="Район",
    )
    type = models.CharField(
        "Тип населённого пункта",
        max_length=20,
        choices=SettlementType.choices,
        default=SettlementType.CITY,
    )

    @property
    def is_city_district(self):
        return self.district is None

    class Meta:
        verbose_name = "Населённый пункт"
        verbose_name_plural = "Населённые пункты"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
