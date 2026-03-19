from django.contrib import admin

from .models import RouteGenerationJob, Router


@admin.register(Router)
class RouterAdmin(admin.ModelAdmin):
    list_display = ("title", "creation_method", "district", "settlement", "created_at")
    list_filter = ("creation_method", "district", "settlement")
    search_fields = ("title", "short_description")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "short_description",
                    "full_description",
                    "image",
                    "duration",
                    "difficulty",
                    "creation_method",
                )
            },
        ),
        ("Локация", {"fields": ("district", "settlement")}),
    )


@admin.register(RouteGenerationJob)
class RouteGenerationJobAdmin(admin.ModelAdmin):
    list_display = ("task_id", "status", "router", "created_at")
    list_filter = ("status",)
    search_fields = ("task_id",)
    readonly_fields = ("task_id", "status", "result", "router", "intent", "created_at", "updated_at")
