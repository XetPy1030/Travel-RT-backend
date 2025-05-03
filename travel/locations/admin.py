from django.contrib import admin

from .models import District, Settlement


class UrbanDistrictFilter(admin.SimpleListFilter):
    title = "Городской округ"
    parameter_name = "is_urban_district"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Да"),
            ("no", "Нет"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(district__isnull=True)
        if self.value() == "no":
            return queryset.filter(district__isnull=False)
        return queryset


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "administrative_center")
    list_filter = ("name",)
    search_fields = ("name",)
    autocomplete_fields = ("administrative_center",)


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "district")
    list_filter = ("type", "district", UrbanDistrictFilter)
    search_fields = ("name",)
    autocomplete_fields = ("district",)
