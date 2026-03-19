"""
Сервис ИИ-тегирования мест: сбор данных, вызов промпта и LLM, применение тегов.
"""

from django.utils.html import strip_tags

from travel.ai.client import call_llm
from travel.places.models import Place, Tag
from travel.prompts.place_tagging import build_place_tagging_prompt


def suggest_place_tags(place: Place) -> dict | None:
    """
    Получить от ИИ предложение тегов для места.

    :return: Словарь с ключами tags (list[str]), confidence, reasoning
     или None при ошибке.
    """
    full_description = place.full_description or ""
    if hasattr(full_description, "source"):  # CKEditor может вернуть объект
        full_description = str(full_description)
    full_description_plain = strip_tags(full_description)

    place_data = {
        "id": place.pk,
        "title": place.title,
        "short_description": place.short_description or "",
        "full_description": full_description_plain,
    }

    available_tags = list(Tag.objects.values_list("slug", flat=True))
    if not available_tags:
        return {"tags": [], "confidence": "low", "reasoning": "Нет тегов в БД."}

    prompt = build_place_tagging_prompt(place_data, available_tags)
    result = call_llm(prompt, json_mode=True, temperature=0.25)
    if not result or not isinstance(result, dict):
        return None

    tags = result.get("tags")
    if not isinstance(tags, list):
        tags = []
    # Оставляем только slug'и, которые есть в БД
    valid_slugs = set(available_tags)
    tags = [t for t in tags if isinstance(t, str) and t in valid_slugs]

    return {
        "tags": tags,
        "confidence": result.get("confidence", "medium"),
        "reasoning": result.get("reasoning", ""),
    }


def apply_suggested_tags(place: Place, tag_slugs: list[str]) -> None:
    """Применить к месту теги по списку slug'ов."""
    if not tag_slugs:
        place.tags.clear()
        return
    tags = list(Tag.objects.filter(slug__in=tag_slugs))
    place.tags.set(tags)
