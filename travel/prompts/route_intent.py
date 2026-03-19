"""
Промпт для извлечения параметров (intent) из свободного текста пользователя.
Только формирование строки, без БД и HTTP.
"""

import json


def build_intent_prompt(
    user_text: str,
    available_districts: list[str],
    available_settlements: list[str],
    available_tags: list[str],
) -> str:
    """
    Формирует промпт для извлечения структурированных параметров из запроса пользователя.
    Списки передаются уже готовыми (из сервиса).
    """
    districts_json = json.dumps(available_districts, ensure_ascii=False)
    settlements_json = json.dumps(available_settlements, ensure_ascii=False)
    tags_json = json.dumps(available_tags, ensure_ascii=False)

    return f"""Ты — ассистент для обработки запросов туристов.
Твоя задача: извлечь структурированные параметры из свободного текста пользователя.

🗣️ ЗАПРОС ПОЛЬЗОВАТЕЛЯ:
"{user_text}"

📍 ДОСТУПНЫЕ ЛОКАЦИИ (выбирай ТОЛЬКО из этих списков):
Районы (District): {districts_json}
Населённые пункты (Settlement): {settlements_json}

🏷️ ДОСТУПНЫЕ ТЕГИ (для фильтрации мест): {tags_json}

📋 ТРЕБОВАНИЯ К ОТВЕТУ:
1. Верни ТОЛЬКО валидный JSON-объект, без пояснений и маркдауна
2. Структура строго такая:
{{
  "location_type": "district | settlement | unknown",
  "location_name": "Название из доступных списков или null",
  "duration": "short | medium | long | full_day | null",
  "transport_mode": "pedestrian | car | public_transport | null",
  "preferred_tags": ["tag1", "tag2"],
  "audience": ["family", "couples", "solo", ...] или [],
  "budget": "free | budget | mid_range | premium | null",
  "time_of_day": "morning | afternoon | evening | night | null",
  "special_requirements": ["wheelchair_accessible", "pet_friendly", ...] или [],
  "missing_info": ["Что неясно из запроса"] или [],
  "confidence": "high | medium | low",
  "clarification_question": "Вопрос пользователю если чего-то не хватает или null"
}}
3. location_name — ТОЛЬКО из доступных списков. Если не найдено — null
4. preferred_tags — ТОЛЬКО из available_tags. Максимум 5 тегов.
5. duration: "час", "быстро" → short; "полдня", "несколько часов" → medium; "день" → long; "целый день" → full_day
6. Если локация не указана — location_type = "unknown", location_name = null
7. missing_info — что критично отсутствует (например, локация)
8. clarification_question — задавай только если missing_info не пуст
"""
