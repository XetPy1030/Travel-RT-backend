from django.contrib import admin

from .models import Place, PlaceImage


class PlaceImageInline(admin.TabularInline):
    model = PlaceImage
    extra = 1


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('title', 'district', 'settlement', 'created_at')
    list_filter = ('district', 'settlement')
    search_fields = ('title', 'short_description')
    inlines = [PlaceImageInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'short_description', 'full_description')
        }),
        ('Локация', {
            'fields': ('district', 'settlement')
        }),
    )


@admin.register(PlaceImage)
class PlaceImageAdmin(admin.ModelAdmin):
    list_display = ('place', 'order')
    list_filter = ('place',)
    ordering = ('place', 'order') 