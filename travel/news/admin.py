from django.contrib import admin

from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "published_at", "creation_method", "created_by")
    list_filter = ("published_at", "creation_method", "created_by")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "created_by")
    fieldsets = (
        (None, {"fields": ("title", "image", "description", "content")}),
        ("Публикация", {"fields": ("published_at", "creation_method")}),
        ("Метаданные", {"fields": ("created_at", "created_by")}),
    )

    def save_model(self, request, obj, form, change):
        if not change and obj.created_by is None and getattr(request, "user", None) and request.user.is_authenticated:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
