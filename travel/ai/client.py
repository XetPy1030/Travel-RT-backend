"""
Единственная точка вызова LLM (OpenRouter). Без промптов и доменной логики.
"""

import json
import logging
from typing import Any

import requests
from django.conf import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

logger = logging.getLogger(__name__)


def call_llm(
    prompt: str,
    *,
    json_mode: bool = True,
    temperature: float = 0.25,
) -> dict[str, Any] | None:
    """
    Отправить промпт в OpenRouter и вернуть распарсенный JSON или None.

    :param prompt: Текст запроса пользователя.
    :param json_mode: Если True, в запрос добавляется response_format json_object.
    :param temperature: Температура генерации (низкая для стабильного JSON).
    :return: Словарь с ответом модели или None при ошибке/невалидном JSON.
    """
    api_key = getattr(settings, "OPENROUTER_API_KEY", "") or ""
    if not api_key:
        logger.warning("OPENROUTER_API_KEY не задан, вызов LLM пропущен")
        return None

    model = getattr(settings, "OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")

    logger.info(
        "LLM запрос: model=%s, prompt_len=%d, json_mode=%s, temperature=%s",
        model,
        len(prompt),
        json_mode,
        temperature,
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=90,
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        logger.info("LLM ответ получен, размер JSON: %d байт", len(content))
        logger.debug(
            "LLM raw response: %s",
            content[:500] + "..." if len(content) > 500 else content,
        )
        return parsed
    except requests.RequestException as e:
        logger.warning("LLM запрос не удался (HTTP/сеть): %s", e)
        if getattr(e, "response", None) is not None:
            try:
                logger.debug("Ответ API: %s", e.response.text[:500])
            except Exception:
                pass
        return None
    except (KeyError, json.JSONDecodeError) as e:
        logger.warning("LLM ответ не удалось распарсить: %s", e)
        return None
