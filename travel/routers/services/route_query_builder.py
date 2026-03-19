"""
Валидация локации и построение контекста для LLM (места, новости, примеры маршрутов).
"""

from travel.locations.models import District, Settlement
from travel.news.models import News
from travel.places.models import Place
from travel.routers.models import Router


def resolve_location(location_type: str | None, location_name: str | None) -> tuple[District | None, Settlement | None]:
    """
    Находит District и/или Settlement по типу и названию.
    Возвращает (district, settlement). Если не найдено — (None, None).
    """
    if not location_name or not location_name.strip():
        return None, None

    name = location_name.strip()
    district = None
    settlement = None

    if location_type == "district":
        district = District.objects.filter(name__icontains=name).first()
        return district, None
    if location_type == "settlement":
        settlement = Settlement.objects.filter(name__icontains=name).first()
        return settlement.district if settlement else None, settlement

    # unknown: пробуем сначала settlement, потом district
    settlement = Settlement.objects.filter(name__icontains=name).first()
    if settlement:
        return settlement.district, settlement
    district = District.objects.filter(name__icontains=name).first()
    return district, None


def validate_intent_location(intent: dict) -> tuple[bool, str | None]:
    """
    Проверяет, что в intent указана валидная локация.
    Возвращает (True, None) при успехе, (False, message) при ошибке.
    """
    location_name = (intent.get("location_name") or "").strip()
    location_type = intent.get("location_type") or "unknown"

    if not location_name:
        clarification = intent.get("clarification_question") or "Укажите город или район для маршрута."
        return False, clarification

    district, settlement = resolve_location(location_type, location_name)
    if district is None and settlement is None:
        return False, "Населённый пункт или район не найден. Проверьте название."
    return True, None


def build_places_queryset(
    intent: dict,
    district: District | None,
    settlement: Settlement | None,
    limit: int = 50,
):
    """
    Строит QuerySet мест по интенту и найденной локации.
    """
    qs = Place.objects.all()

    if district is not None:
        qs = qs.filter(district=district)
    if settlement is not None:
        qs = qs.filter(settlement=settlement)

    preferred_tags = intent.get("preferred_tags") or []
    if preferred_tags:
        qs = qs.filter(tags__slug__in=preferred_tags).distinct()

    audience = intent.get("audience") or []
    for aud in audience:
        qs = qs.filter(tags__slug=aud).distinct()

    budget = intent.get("budget")
    if budget:
        qs = qs.filter(tags__slug=budget).distinct()

    special = intent.get("special_requirements") or []
    for req in special:
        qs = qs.filter(tags__slug=req).distinct()

    return qs.order_by("title")[:limit]


def get_context_for_llm(intent: dict) -> dict:
    """
    Готовит контекст для промпта генерации маршрута.
    Возвращает dict с places, news_facts, existing_route_titles, intent
    или dict с error, message при отсутствии мест.
    """
    location_type = intent.get("location_type") or "unknown"
    location_name = (intent.get("location_name") or "").strip()
    district, settlement = resolve_location(location_type, location_name)

    if district is None and settlement is None and location_name:
        return {
            "error": "location_not_found",
            "message": "Населённый пункт или район не найден.",
        }

    qs = build_places_queryset(intent, district, settlement)
    places_data = []
    for p in qs:
        desc = p.short_description or ""
        full = p.full_description or ""
        if hasattr(full, "source"):
            full = str(full)
        from django.utils.html import strip_tags

        full_plain = strip_tags(full)[:500] if full else ""
        places_data.append(
            {
                "id": p.id,
                "title": p.title,
                "short_description": desc,
                "full_description": full_plain,
            }
        )

    if not places_data:
        loc_name = location_name or "выбранной"
        return {
            "error": "no_places",
            "message": f"В локации «{loc_name}» нет доступных мест.",
        }

    from datetime import timedelta

    from django.utils import timezone

    news_qs = News.objects.filter(published_at__gte=timezone.now() - timedelta(days=90)).order_by("-published_at")[:10]
    news_facts = [f"{n.title}: {(n.description or '')[:150]}" for n in news_qs]

    route_titles = list(
        Router.objects.filter(creation_method=Router.CreationMethod.MANUAL)
        .order_by("?")
        .values_list("title", flat=True)[:3]
    )

    return {
        "places": places_data,
        "news_facts": news_facts,
        "existing_route_titles": route_titles,
        "intent": intent,
        "district": district,
        "settlement": settlement,
    }
