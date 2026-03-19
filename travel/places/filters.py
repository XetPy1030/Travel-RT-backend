from django_filters import CharFilter, FilterSet

from .models import Place


class PlaceFilterSet(FilterSet):
    tags = CharFilter(method="filter_by_tag_slugs", label="Теги (slug через запятую)")

    class Meta:
        model = Place
        fields = ["district", "settlement", "tags"]

    @staticmethod
    def filter_by_tag_slugs(queryset, name, value):
        if not value:
            return queryset
        slugs = [s.strip() for s in value.split(",") if s.strip()]
        if not slugs:
            return queryset
        return queryset.filter(tags__slug__in=slugs).distinct()
