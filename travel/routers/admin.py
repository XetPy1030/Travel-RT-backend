from django.contrib import admin

from .models import Router


@admin.register(Router)
class RouterAdmin(admin.ModelAdmin):
    list_display = ("title", "district", "settlement", "created_at")
    list_filter = ("district", "settlement")
    search_fields = ("title", "short_description")
    fieldsets = (
        (None, {"fields": ("title", "short_description", "full_description")}),
        ("Локация", {"fields": ("district", "settlement")}),
    )
