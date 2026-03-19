"""
Генерация HTML full_description из ответа LLM и оркестрация пайплайна (Celery).
Основной путь: ИИ оформляет описание в красивый HTML.
Legacy: простая сборка из JSON без второго вызова ИИ.
"""

import html
import logging
import re
from datetime import timedelta

from django.conf import settings

from travel.ai.client import call_llm
from travel.prompts.route_format_html import build_route_format_html_prompt
from travel.prompts.route_generation import build_route_generation_prompt
from travel.routers.models import RouteGenerationJob, Router

from .route_query_builder import get_context_for_llm

logger = logging.getLogger(__name__)


def _escape(text: str) -> str:
    if not text:
        return ""
    return html.escape(str(text))


def _parse_duration(text: str | None) -> timedelta:
    """Парсит строку вида '3-4 часа', '1.5 часа' в timedelta."""
    if not text or not str(text).strip():
        return timedelta(hours=2)
    text = str(text).strip().lower()
    match = re.search(r"(\d+[,.]?\d*)\s*(?:часа?|ч\.?|час)", text)
    if match:
        try:
            h = float(match.group(1).replace(",", "."))
            return timedelta(hours=min(24, max(0.25, h)))
        except ValueError:
            pass
    if "час" in text:
        return timedelta(hours=2)
    return timedelta(hours=2)


def _map_difficulty(text: str | None) -> str:
    """Маппинг текста сложности в easy/medium/hard."""
    if not text:
        return Router.Difficulty.MEDIUM
    t = str(text).strip().lower()
    if "лёгк" in t or "легк" in t or "easy" in t:
        return Router.Difficulty.EASY
    if "сложн" in t or "hard" in t:
        return Router.Difficulty.HARD
    return Router.Difficulty.MEDIUM


def _strip_dangerous_html(raw: str) -> str:
    """Удаляет script/style и их содержимое из HTML."""
    if not raw:
        return ""
    raw = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"<style\b[^>]*>[\s\S]*?</style>", "", raw, flags=re.IGNORECASE)
    return raw.strip()


def build_route_full_description_html_legacy(llm_route: dict) -> str:  # noqa:PLR0912
    """
    Собирает HTML для Router.full_description из ответа LLM (без второго вызова ИИ).
    Структура: <p> описание, затем по каждой точке «Локация N: название» и текст.
    Используется как fallback и как legacy-режим.
    """
    parts = []

    desc = (llm_route.get("description") or "").strip()
    if desc:
        parts.append(f"<p>{_escape(desc)}</p>")

    waypoints = llm_route.get("waypoints") or []
    for wp in sorted(waypoints, key=lambda x: x.get("order", 0)):
        order = wp.get("order", 0)
        name = _escape((wp.get("name") or "").strip())
        if name:
            parts.append(f"<p>Локация {order}: {name}</p>")
        desc_w = (wp.get("description") or "").strip()
        if desc_w:
            parts.append(f"<p>{_escape(desc_w)}</p>")
        duration = (wp.get("recommended_duration") or "").strip()
        if duration:
            parts.append(f"<p>Рекомендуемое время: {_escape(duration)}</p>")
        tips = wp.get("tips") or []
        if tips:
            for t in tips:
                if str(t).strip():
                    parts.append(f"<p>{_escape(str(t).strip())}</p>")
        fact = (wp.get("interesting_fact") or "").strip()
        if fact:
            parts.append(f"<p>{_escape(fact)}</p>")
        parts.append("<p>&nbsp;</p>")

    general_tips = llm_route.get("general_tips") or []
    if general_tips:
        parts.append("<p>Общие советы</p>")
        for t in general_tips:
            if str(t).strip():
                parts.append(f"<p>{_escape(str(t).strip())}</p>")

    total_time = (llm_route.get("total_estimated_time") or "").strip()
    best_time = (llm_route.get("best_time_to_visit") or "").strip()
    if total_time or best_time:
        parts.append("<p>&nbsp;</p>")
        if total_time:
            parts.append(f"<p>Общее время: {_escape(total_time)}</p>")
        if best_time:
            parts.append(f"<p>Лучшее время для посещения: {_escape(best_time)}</p>")

    return "\n".join(parts)


def build_route_full_description_html(llm_route: dict) -> str:
    """
    По умолчанию: ИИ оформляет маршрут в красивый HTML.
    При ROUTE_DESCRIPTION_LEGACY=True или ошибке ИИ используется legacy-сборка.
    """
    if getattr(settings, "ROUTE_DESCRIPTION_LEGACY", False):
        return build_route_full_description_html_legacy(llm_route)
    try:
        prompt = build_route_format_html_prompt(llm_route)
        out = call_llm(prompt, json_mode=True, temperature=0.2)
        if isinstance(out, dict) and out.get("html"):
            html_content = str(out["html"]).strip()
            html_content = _strip_dangerous_html(html_content)
            if len(html_content) > 100:
                logger.info("full_description оформлен через ИИ (format_html)")
                return html_content
        else:
            logger.debug("ИИ не вернул html или ответ пуст, используем legacy")
    except Exception as e:
        logger.warning("Оформление full_description через ИИ не удалось: %s", e)
    return build_route_full_description_html_legacy(llm_route)


def run_pipeline(job_id: int) -> None:
    """
    Выполняет пайплайн генерации маршрута для RouteGenerationJob.
    Вызывается из Celery-задачи.
    """
    job = RouteGenerationJob.objects.filter(id=job_id).first()
    if not job:
        logger.warning("RouteGenerationJob id=%s not found", job_id)
        return

    job.status = RouteGenerationJob.Status.PROCESSING
    job.save(update_fields=["status", "updated_at"])

    intent = job.intent or {}
    try:
        context = get_context_for_llm(intent)
    except Exception as e:
        logger.exception("get_context_for_llm failed: %s", e)
        job.status = RouteGenerationJob.Status.FAILED
        job.error_message = str(e)
        job.save(update_fields=["status", "error_message", "updated_at"])
        return

    if "error" in context:
        job.status = RouteGenerationJob.Status.FAILED
        job.error_message = context.get("message", "Нет доступных мест.")
        job.save(update_fields=["status", "error_message", "updated_at"])
        return

    prompt = build_route_generation_prompt(context)
    llm_response = call_llm(prompt, json_mode=True, temperature=0.25)

    if not llm_response or not isinstance(llm_response, dict):
        job.status = RouteGenerationJob.Status.FAILED
        job.error_message = "Не удалось получить ответ от ИИ."
        job.save(update_fields=["status", "error_message", "updated_at"])
        return

    route_name = (llm_response.get("route_name") or "Маршрут").strip()
    description = (llm_response.get("description") or route_name).strip()
    difficulty = _map_difficulty(llm_response.get("difficulty"))
    duration = _parse_duration(llm_response.get("total_estimated_time"))

    district = context.get("district")
    settlement = context.get("settlement")
    if not district and settlement:
        district = getattr(settlement, "district", None)

    full_description_html = build_route_full_description_html(llm_response)

    router = Router.objects.create(
        title=route_name[:255],
        short_description=description[:500] if description else route_name[:500],
        full_description=full_description_html,
        duration=duration,
        difficulty=difficulty,
        district=district,
        settlement=settlement,
        creation_method=Router.CreationMethod.AI_GENERATED,
    )

    job.router = router
    job.result = llm_response
    job.status = RouteGenerationJob.Status.COMPLETED
    job.error_message = ""
    job.save(update_fields=["router", "result", "status", "error_message", "updated_at"])
    logger.info("Route generated: job_id=%s router_id=%s", job_id, router.id)
