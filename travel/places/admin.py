from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse

from .models import Place, PlaceImage, Tag
from .services.tagging import apply_suggested_tags, suggest_place_tags


class PlaceImageInline(admin.TabularInline):
    model = PlaceImage
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("title", "district", "settlement", "created_at")
    list_filter = ("district", "settlement", "tags")
    search_fields = ("title", "short_description")
    inlines = [PlaceImageInline]
    change_form_template = "admin/places/place/change_form.html"
    fieldsets = (
        (None, {"fields": ("title", "short_description", "full_description")}),
        ("Теги", {"fields": ("tags",)}),
        ("Локация", {"fields": ("district", "settlement")}),
    )
    actions = ["action_ai_tag_places"]

    @admin.action(description="Подобрать теги с помощью ИИ")
    def action_ai_tag_places(self, request, queryset):
        from django.conf import settings

        if not getattr(settings, "OPENROUTER_API_KEY", ""):
            self.message_user(
                request,
                "Задайте OPENROUTER_API_KEY в настройках.",
                level=messages.ERROR,
            )
            return
        success = 0
        for place in queryset:
            result = suggest_place_tags(place)
            if result and result.get("tags"):
                apply_suggested_tags(place, result["tags"])
                success += 1
        if success:
            self.message_user(
                request,
                f"Теги подобраны для {success} мест.",
                level=messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "Не удалось подобрать теги (проверьте ключ API и наличие тегов в БД).",
                level=messages.WARNING,
            )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<path:object_id>/ai-tag/",
                self.admin_site.admin_view(self.ai_tag_view),
                name="places_place_ai_tag",
            ),
        ]
        return custom + urls

    def ai_tag_view(self, request, object_id):
        from django.conf import settings
        from django.shortcuts import get_object_or_404

        place = get_object_or_404(Place, pk=object_id)
        if not getattr(settings, "OPENROUTER_API_KEY", ""):
            self.message_user(
                request,
                "Задайте OPENROUTER_API_KEY в настройках.",
                level=messages.ERROR,
            )
            return HttpResponseRedirect(reverse("admin:places_place_change", args=[object_id]))
        result = suggest_place_tags(place)
        if result and result.get("tags"):
            apply_suggested_tags(place, result["tags"])
            self.message_user(request, "Теги успешно подобраны и применены.", level=messages.SUCCESS)
        else:
            self.message_user(
                request,
                "ИИ не подобрал теги или произошла ошибка.",
                level=messages.WARNING,
            )
        return HttpResponseRedirect(reverse("admin:places_place_change", args=[object_id]))


@admin.register(PlaceImage)
class PlaceImageAdmin(admin.ModelAdmin):
    list_display = ("place", "order")
    list_filter = ("place",)
    ordering = ("place", "order")
