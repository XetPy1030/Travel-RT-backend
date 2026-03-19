"""
Промпт для генерации маршрута по контексту (места, новости, интент).
Только формирование строки, без БД и HTTP.
"""

import json
from typing import Any


def build_route_generation_prompt(context: dict[str, Any]) -> str:
    """
    context: places (list of dict с id, title, short_description),
              news_facts (list of str),
              existing_route_titles (list of str),
              intent (dict с transport_mode, preferred_tags и т.д.)
    """
    places = context.get("places", [])
    news_facts = context.get("news_facts", [])
    existing_titles = context.get("existing_route_titles", [])
    intent = context.get("intent", {})

    user_text = (intent.get("user_text") or "").strip()
    user_request = user_text or (intent.get("location_name", "") or "маршрут")
    if not user_text and intent.get("preferred_tags"):
        user_request += " (теги: " + ", ".join(intent["preferred_tags"]) + ")"
    transport_mode = intent.get("transport_mode") or "pedestrian"

    transport_labels = {
        "pedestrian": "пешком",
        "car": "на машине",
        "public_transport": "на общественном транспорте",
    }
    transport_label = transport_labels.get(transport_mode, transport_mode)

    places_text = "\n".join(
        f"• id={p.get('id')}, title={json.dumps(p.get('title', ''), ensure_ascii=False)} — {(p.get('short_description') or '')[:200]}"
        for p in places
    )
    news_text = "\n".join(f"• {f}" for f in news_facts) if news_facts else "• Нет."
    titles_text = "\n".join(f"• {t}" for t in existing_titles[:5])

    return f"""Ты — профессиональный туристический гид. Составь детальный маршрут.

🎯 ЗАПРОС: {user_request}
🚗 СПОСОБ ПЕРЕДВИЖЕНИЯ: {transport_label}

🏛️ ДОСТУПНЫЕ МЕСТА (выбирай точки ТОЛЬКО из этого списка; name в waypoints должен совпадать с title):
{places_text}

📰 ПОСЛЕДНИЕ НОВОСТИ (используй в описании ТОЛЬКО если новость по смыслу подходит к маршруту или к точке; не вставляй ради упоминания):
{news_text}

🗺️ ПРИМЕРЫ НАЗВАНИЙ МАРШРУТОВ (для стиля):
{titles_text}

📋 ТРЕБОВАНИЯ К ОТВЕТУ:
1. Верни ТОЛЬКО валидный JSON-объект, без пояснений и маркдауна.
2. Структура строго такая:
{{
  "route_name": "Краткое привлекательное название маршрута",
  "description": "2-3 предложения: что ждёт туриста",
  "transport_mode": "{transport_mode}",
  "waypoints": [
    {{
      "order": 1,
      "name": "Название места (строго одно из title из списка мест)",
      "description": "Почему стоит посетить, что посмотреть",
      "recommended_duration": "30-45 минут",
      "tips": ["Совет 1", "Совет 2"],
      "interesting_fact": "Короткий факт о месте"
    }}
  ],
  "total_estimated_time": "3-4 часа",
  "best_time_to_visit": "Утро / День / Вечер",
  "general_tips": ["Совет по маршруту", "Что взять с собой"],
  "difficulty": "Лёгкий / Средний / Сложный",
  "budget_estimate": "Бесплатно / Недорого / Средний / Премиум"
}}
3. Включи 3-7 точек маршрута в логическом порядке. waypoints[].name — только из переданного списка мест (поле title).
4. Не выдумывай места. Если подходящих мало — используй только их.
5. Новости упоминай только если релевантны маршруту или точке.
6. description и tips пиши дружелюбно и понятно для обычного туриста:
   - избегай канцелярита и сухих формулировок;
   - используй простой человеческий язык;
   - добавляй практичные детали (что увидеть, когда лучше прийти, на что обратить внимание).
"""
