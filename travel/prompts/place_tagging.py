"""
Промпт для ИИ-тегирования туристических мест. Только формирование строки, без БД и HTTP.
"""

import json
from typing import Any


def build_place_tagging_prompt(place_data: dict[str, Any], available_tags: list[str]) -> str:
    """
    place_data: ключи title, short_description, full_description; опционально id.
    available_tags: список валидных slug'ов тегов (для подстановки в промпт).
    """
    place_id = place_data.get("id")
    title = place_data.get("title", "")
    short_description = place_data.get("short_description", "")
    full_description = place_data.get("full_description", "")

    tags_json = json.dumps(available_tags, ensure_ascii=False)
    place_id_json = "null" if place_id is None else json.dumps(place_id)
    title_escaped = json.dumps(title, ensure_ascii=False)

    return f"""Ты — ассистент для классификации туристических мест.
Твоя задача: проанализировать описание места и подобрать релевантные теги из ПРЕДОТВЕРЖДЁННОГО СПИСКА.

📍 ДАННЫЕ О МЕСТЕ:
Название: {title}
Краткое описание: {short_description}
Полное описание: {full_description}

🏷️ ДОСТУПНЫЕ ТЕГИ (выбирай ТОЛЬКО из этого списка):
{tags_json}

📋 ТРЕБОВАНИЯ К ОТВЕТУ:
1. Верни ТОЛЬКО валидный JSON-объект без пояснений и маркдауна.
2. Структура строго такая:
{{
  "place_id": {place_id_json},
  "place_name": {title_escaped},
  "tags": ["tag1", "tag2"],
  "confidence": "high | medium | low",
  "reasoning": "Кратко, почему выбраны эти теги (1 предложение)"
}}
3. Выбирай от 1 до 5 тегов. Не выбирай все подряд.
4. Если ни один тег не подходит — верни пустой список tags: [].
5. Не выдумывай новые теги. Если подходящего нет — не выбирай ничего.
6. confidence:
   - "high": описание явно соответствует тегу
   - "medium": косвенное соответствие
   - "low": сомнительное соответствие (лучше не выбирать)

🎯 ПРИМЕРЫ ЛОГИКИ:
- "музей", "выставка", "экспозиция" → теги: culture, history, indoor
- "парк", "лес", "озеро", "природа" → теги: nature, outdoor, relaxation
- "детям", "семья", "игровая" → теги: family, kids
- "кафе", "ресторан", "еда" → теги: food, cafe
- "бесплатно", "вход свободный" → теги: free
"""
