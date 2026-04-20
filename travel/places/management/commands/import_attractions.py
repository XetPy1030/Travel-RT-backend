import json
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.html import strip_tags

from travel.locations.models import District, Settlement
from travel.places.models import Place, PlaceImage

IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
REQUEST_TIMEOUT_SECONDS = 20
MAX_FUZZY_CANDIDATES = 5
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 TravelRTImporter/1.0"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://commons.wikimedia.org/",
}


@dataclass
class ImportStats:
    total: int = 0
    created: int = 0
    updated: int = 0
    skipped_duplicates: int = 0
    skipped_unresolved_location: int = 0
    image_saved: int = 0
    image_failed: int = 0
    errors: int = 0


@dataclass(frozen=True)
class ImportContext:
    district_index: dict[str, list[District]]
    settlement_index: dict[str, list[Settlement]]
    dry_run: bool
    non_interactive: bool


@dataclass(frozen=True)
class PlaceSavePayload:
    record: dict[str, Any]
    title: str
    district: District | None
    settlement: Settlement | None
    duplicate: Place | None
    image_urls: list[str]
    overwrite_existing: bool
    context_label: str


class Command(BaseCommand):
    help = "Импортирует attractions.json в модели Place и PlaceImage."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._district_choice_cache: dict[str, District | None] = {}
        self._settlement_choice_cache: dict[tuple[str, int | None], Settlement | None] = {}
        self._duplicate_action_cache: dict[tuple[str, int | None, int | None], str] = {}

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=str(Path(settings.BASE_DIR) / "attractions.json"),
            help="Путь к JSON-файлу для импорта",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Прогон без записи в БД и без скачивания файлов",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Ограничить число импортируемых записей",
        )
        parser.add_argument(
            "--non-interactive",
            action="store_true",
            help="Остановить импорт при неоднозначностях без вопросов",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"]).expanduser()
        if not file_path.is_absolute():
            file_path = Path(settings.BASE_DIR) / file_path

        dry_run = options["dry_run"]
        limit = options["limit"]
        non_interactive = options["non_interactive"]

        records = self._load_records(file_path=file_path)
        if limit is not None:
            records = records[:limit]

        stats = ImportStats(total=len(records))
        self.stdout.write(
            self.style.NOTICE(
                f"Начинаю импорт: записей={len(records)}, dry_run={dry_run}, non_interactive={non_interactive}"
            )
        )

        context = ImportContext(
            district_index=self._build_district_index(),
            settlement_index=self._build_settlement_index(),
            dry_run=dry_run,
            non_interactive=non_interactive,
        )

        for index, record in enumerate(records, start=1):
            try:
                self._process_record(
                    record=record,
                    index=index,
                    stats=stats,
                    context=context,
                )
            except CommandError:
                raise
            except Exception as exc:
                stats.errors += 1
                name = str(record.get("name") or "Без названия")
                self.stdout.write(self.style.ERROR(f"[{index}] Ошибка при импорте '{name}': {exc}"))

        self._print_summary(stats=stats, dry_run=dry_run)

    def _load_records(self, file_path: Path) -> list[dict[str, Any]]:
        if not file_path.exists():
            raise CommandError(f"Файл не найден: {file_path}")

        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"Некорректный JSON в {file_path}: {exc}") from exc

        if not isinstance(payload, dict):
            raise CommandError("Ожидался JSON-объект нового формата с ключом 'attractions'")

        attractions = payload.get("attractions")
        if not isinstance(attractions, list):
            raise CommandError("В JSON отсутствует список 'attractions' или он имеет неверный тип")

        records: list[dict[str, Any]] = []
        for idx, item in enumerate(attractions, start=1):
            if not isinstance(item, dict):
                raise CommandError(f"Запись #{idx} не является объектом JSON")
            records.append(item)

        return records

    def _build_district_index(self) -> dict[str, list[District]]:
        index: dict[str, list[District]] = {}
        for district in District.objects.all():
            normalized = self._normalize_district_name(district.name)
            index.setdefault(normalized, []).append(district)
        return index

    def _build_settlement_index(self) -> dict[str, list[Settlement]]:
        index: dict[str, list[Settlement]] = {}
        for settlement in Settlement.objects.select_related("district").all():
            normalized = self._normalize_settlement_name(settlement.name)
            index.setdefault(normalized, []).append(settlement)
        return index

    def _process_record(
        self,
        record: dict[str, Any],
        index: int,
        stats: ImportStats,
        context: ImportContext,
    ) -> None:
        title = str(record.get("name") or "").strip()
        if not title:
            stats.errors += 1
            self.stdout.write(self.style.ERROR(f"[{index}] Пропуск записи без name"))
            return

        context_label = f"[{index}] {title}"
        district, settlement = self._resolve_record_location(
            record=record,
            context_label=context_label,
            context=context,
        )
        if not district and not settlement:
            stats.skipped_unresolved_location += 1
            self.stdout.write(
                self.style.WARNING(f"[{index}] Пропуск '{title}': не удалось определить district/settlement")
            )
            return

        duplicate = self._find_duplicate_place(title=title, district=district, settlement=settlement)
        duplicate_action = self._get_duplicate_action(
            duplicate=duplicate,
            context_label=context_label,
            non_interactive=context.non_interactive,
        )
        if duplicate_action == "skip":
            stats.skipped_duplicates += 1
            self.stdout.write(self.style.WARNING(f"[{index}] Пропуск дубликата '{title}'"))
            return

        image_urls = self._extract_photo_urls(record=record)
        if context.dry_run:
            self._report_dry_run(
                index=index,
                title=title,
                duplicate=duplicate,
                image_urls=image_urls,
                stats=stats,
            )
            return

        payload = PlaceSavePayload(
            record=record,
            title=title,
            district=district,
            settlement=settlement,
            duplicate=duplicate,
            image_urls=image_urls,
            overwrite_existing=duplicate_action == "overwrite",
            context_label=context_label,
        )
        self._save_place_with_images(payload=payload, stats=stats)

    def _resolve_record_location(
        self,
        record: dict[str, Any],
        context_label: str,
        context: ImportContext,
    ) -> tuple[District | None, Settlement | None]:
        district_name = str(record.get("district") or "").strip()
        settlement_name = str(record.get("settlement") or "").strip()

        district = self._resolve_district(
            raw_name=district_name,
            district_index=context.district_index,
            non_interactive=context.non_interactive,
            context=context_label,
        )
        settlement = self._resolve_settlement(
            raw_name=settlement_name,
            district=district,
            settlement_index=context.settlement_index,
            non_interactive=context.non_interactive,
            context=context_label,
        )
        return district, settlement

    def _find_duplicate_place(
        self,
        title: str,
        district: District | None,
        settlement: Settlement | None,
    ) -> Place | None:
        return Place.objects.filter(
            title=title,
            district=district,
            settlement=settlement,
        ).first()

    def _get_duplicate_action(
        self,
        duplicate: Place | None,
        context_label: str,
        non_interactive: bool,
    ) -> str:
        if duplicate is None:
            return "create"
        return self._resolve_duplicate_action(
            place=duplicate,
            non_interactive=non_interactive,
            context=context_label,
        )

    def _report_dry_run(
        self,
        index: int,
        title: str,
        duplicate: Place | None,
        image_urls: list[str],
        stats: ImportStats,
    ) -> None:
        if duplicate is None:
            stats.created += 1
            self.stdout.write(self.style.SUCCESS(f"[{index}] DRY-RUN create '{title}'"))
        else:
            stats.updated += 1
            self.stdout.write(self.style.SUCCESS(f"[{index}] DRY-RUN update '{title}'"))

        if image_urls:
            self.stdout.write(self.style.NOTICE(f"[{index}] DRY-RUN: найдено фото URL={len(image_urls)} для '{title}'"))

    def _save_place_with_images(self, payload: PlaceSavePayload, stats: ImportStats) -> None:
        with transaction.atomic():
            place = payload.duplicate if payload.duplicate is not None else Place()
            place.title = payload.title
            place.short_description = self._build_short_description(record=payload.record)
            place.full_description = str(payload.record.get("description_html") or "").strip()
            place.district = payload.district
            place.settlement = payload.settlement
            place.save()

            if payload.duplicate is None:
                stats.created += 1
                self.stdout.write(self.style.SUCCESS(f"{payload.context_label}: создано место"))
            else:
                stats.updated += 1
                self.stdout.write(self.style.SUCCESS(f"{payload.context_label}: обновлено место"))

            if payload.overwrite_existing and payload.image_urls:
                self._delete_place_images(place=place)

            saved_count, failed_count = self._save_images(
                place=place,
                image_urls=payload.image_urls,
                context=payload.context_label,
            )
            stats.image_saved += saved_count
            stats.image_failed += failed_count

    def _resolve_district(
        self,
        raw_name: str,
        district_index: dict[str, list[District]],
        non_interactive: bool,
        context: str,
    ) -> District | None:
        if not raw_name:
            return None

        normalized = self._normalize_district_name(raw_name)
        if normalized in self._district_choice_cache:
            return self._district_choice_cache[normalized]

        exact_matches = district_index.get(normalized, [])
        if len(exact_matches) == 1:
            self._district_choice_cache[normalized] = exact_matches[0]
            return exact_matches[0]
        if len(exact_matches) > 1:
            selected = self._prompt_choice(
                message=f"{context}: несколько district с точным совпадением '{raw_name}'",
                candidates=exact_matches,
                format_candidate=lambda item: f"{item.name} [id={item.id}]",
                non_interactive=non_interactive,
            )
            self._district_choice_cache[normalized] = selected
            return selected

        candidates = self._fuzzy_matches(
            source=normalized,
            candidates=[district for items in district_index.values() for district in items],
            normalizer=self._normalize_district_name,
        )
        selected = self._prompt_choice(
            message=f"{context}: district '{raw_name}' не найден, выберите похожий",
            candidates=candidates,
            format_candidate=lambda item: f"{item.name} [id={item.id}]",
            non_interactive=non_interactive,
        )
        self._district_choice_cache[normalized] = selected
        return selected

    def _resolve_settlement(
        self,
        raw_name: str,
        district: District | None,
        settlement_index: dict[str, list[Settlement]],
        non_interactive: bool,
        context: str,
    ) -> Settlement | None:
        if not raw_name:
            return None

        normalized = self._normalize_settlement_name(raw_name)
        cache_key = (normalized, district.id if district else None)
        if cache_key in self._settlement_choice_cache:
            return self._settlement_choice_cache[cache_key]

        exact_matches = settlement_index.get(normalized, [])
        if district is not None:
            district_exact = [item for item in exact_matches if item.district_id == district.id]
            if district_exact:
                exact_matches = district_exact

        if len(exact_matches) == 1:
            self._settlement_choice_cache[cache_key] = exact_matches[0]
            return exact_matches[0]
        if len(exact_matches) > 1:
            selected = self._prompt_choice(
                message=f"{context}: несколько settlement с точным совпадением '{raw_name}'",
                candidates=exact_matches,
                format_candidate=self._format_settlement,
                non_interactive=non_interactive,
                none_option_label=("Не заполнять settlement" if district is not None else "Пропустить запись"),
            )
            self._settlement_choice_cache[cache_key] = selected
            return selected

        all_settlements = [item for items in settlement_index.values() for item in items]
        if district is not None:
            district_settlements = [
                settlement for settlement in all_settlements if settlement.district_id == district.id
            ]
            if district_settlements:
                all_settlements = district_settlements

        candidates = self._fuzzy_matches(
            source=normalized,
            candidates=all_settlements,
            normalizer=self._normalize_settlement_name,
        )
        selected = self._prompt_choice(
            message=f"{context}: settlement '{raw_name}' не найден, выберите похожий",
            candidates=candidates,
            format_candidate=self._format_settlement,
            non_interactive=non_interactive,
            none_option_label=("Не заполнять settlement" if district is not None else "Пропустить запись"),
        )
        self._settlement_choice_cache[cache_key] = selected
        return selected

    def _resolve_duplicate_action(
        self,
        place: Place,
        non_interactive: bool,
        context: str,
    ) -> str:
        if non_interactive:
            raise CommandError(f"{context}: найден дубликат, нужен интерактивный выбор")

        cache_key = (place.title, place.district_id, place.settlement_id)
        cached_action = self._duplicate_action_cache.get(cache_key)
        if cached_action is not None:
            return cached_action

        self.stdout.write(self.style.WARNING(f"{context}: найден дубликат Place id={place.id}, title='{place.title}'"))
        self.stdout.write("Введите 'o' (overwrite) или 's' (skip), по умолчанию: s")
        answer = self._read_input().lower()

        if answer in {"o", "overwrite"}:
            self._duplicate_action_cache[cache_key] = "overwrite"
            return "overwrite"

        self._duplicate_action_cache[cache_key] = "skip"
        return "skip"

    def _build_short_description(self, record: dict[str, Any]) -> str:
        additional_info = record.get("additional_info") or {}
        if isinstance(additional_info, dict):
            brief = str(additional_info.get("brief_description") or "").strip()
            if brief:
                return brief

        raw_html = str(record.get("description_html") or "").strip()
        fallback = strip_tags(raw_html).strip()
        if not fallback:
            return "Описание отсутствует"
        return fallback[:280]

    def _extract_photo_urls(self, record: dict[str, Any]) -> list[str]:
        urls: list[str] = []

        main_url = str(record.get("photo_url") or "").strip()
        if main_url:
            urls.append(main_url)

        additional_info = record.get("additional_info") or {}
        if isinstance(additional_info, dict):
            nested_urls = additional_info.get("photo_urls") or []
            if isinstance(nested_urls, list):
                for item in nested_urls:
                    candidate = str(item or "").strip()
                    if candidate:
                        urls.append(candidate)

        seen: set[str] = set()
        unique_urls: list[str] = []
        for item in urls:
            if item in seen:
                continue
            seen.add(item)
            unique_urls.append(item)
        return unique_urls

    def _save_images(
        self,
        place: Place,
        image_urls: list[str],
        context: str,
    ) -> tuple[int, int]:
        saved = 0
        failed = 0
        for order, url in enumerate(image_urls):
            try:
                content, extension = self._download_image(url=url)
                filename = self._make_filename(place=place, order=order, extension=extension)
                place_image = PlaceImage(place=place, order=order)
                place_image.image.save(filename, content, save=True)
                saved += 1
            except Exception as exc:
                failed += 1
                self.stdout.write(self.style.WARNING(f"{context}: не удалось загрузить фото '{url}': {exc}"))
        return saved, failed

    def _download_image(self, url: str) -> tuple[ContentFile, str]:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            headers=HTTP_HEADERS,
        )
        if response.status_code in {403, 429}:
            response = requests.get(
                url,
                timeout=REQUEST_TIMEOUT_SECONDS,
                headers={**HTTP_HEADERS, "Cache-Control": "no-cache"},
            )
        if response.status_code >= 400:
            raise ValueError(f"HTTP {response.status_code}")

        content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
        if content_type and content_type not in IMAGE_CONTENT_TYPES:
            raise ValueError(f"Неподдерживаемый content-type: {content_type}")

        extension = self._extract_extension(url=url, content_type=content_type)
        return ContentFile(response.content), extension

    def _extract_extension(self, url: str, content_type: str) -> str:
        parsed_path = Path(urlparse(url).path)
        suffix = parsed_path.suffix.lower().replace(".", "")
        if suffix in {"jpg", "jpeg", "png", "webp", "gif"}:
            return "jpg" if suffix == "jpeg" else suffix

        by_content_type = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
        }
        return by_content_type.get(content_type, "jpg")

    def _make_filename(self, place: Place, order: int, extension: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", self._normalize_text(place.title)).strip("-")
        if not slug:
            slug = f"place-{place.id}"
        return f"{slug}-{order}.{extension}"

    def _delete_place_images(self, place: Place) -> None:
        for image in place.images.all():
            image.image.delete(save=False)
            image.delete()

    def _fuzzy_matches(self, source, candidates, normalizer) -> list[Any]:
        scored: list[tuple[float, Any]] = []
        for candidate in candidates:
            target = normalizer(candidate.name)
            ratio = SequenceMatcher(a=source, b=target).ratio()
            if ratio > 0:
                scored.append((ratio, candidate))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored[:MAX_FUZZY_CANDIDATES]]

    def _prompt_choice(
        self,
        message: str,
        candidates: list[Any],
        format_candidate,
        non_interactive: bool,
        none_option_label: str = "Пропустить запись",
    ) -> Any | None:
        if not candidates:
            return None

        if non_interactive:
            raise CommandError(f"{message}: требуется интерактивный выбор")

        self.stdout.write(self.style.WARNING(message))
        for idx, candidate in enumerate(candidates, start=1):
            self.stdout.write(f"  {idx}. {format_candidate(candidate)}")
        self.stdout.write(f"  0. {none_option_label}")
        self.stdout.write("Введите номер варианта: ")

        while True:
            answer = self._read_input()
            if not answer:
                return None

            if answer.isdigit():
                selected = int(answer)
                if selected == 0:
                    return None
                if 1 <= selected <= len(candidates):
                    return candidates[selected - 1]

            self.stdout.write("Некорректный выбор. Введите номер из списка: ")

    def _read_input(self) -> str:
        try:
            return input().strip()
        except EOFError:
            return ""

    def _format_settlement(self, settlement: Settlement) -> str:
        district_name = settlement.district.name if settlement.district else "Без района"
        return f"{settlement.name} ({district_name}) [id={settlement.id}]"

    def _normalize_district_name(self, value: str) -> str:
        normalized = self._normalize_text(value)
        normalized = re.sub(r"^\d+\s*[\.\-)]\s*", "", normalized)
        normalized = re.sub(r"\bраи[йи]онский\b", "район", normalized)
        normalized = re.sub(r"\bрайон\b", "", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _normalize_settlement_name(self, value: str) -> str:
        normalized = self._normalize_text(value)
        normalized = re.sub(
            r"^(с|д|г|пгт|пос|поселок|посёлок|деревня|село|город)\.?\s+",
            "",
            normalized,
        )
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _normalize_text(self, value: str) -> str:
        result = unicodedata.normalize("NFKC", str(value or "")).casefold()
        result = result.replace("ё", "е")
        return result

    def _print_summary(self, stats: ImportStats, dry_run: bool) -> None:
        mode = "DRY-RUN" if dry_run else "IMPORT"
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE(f"{mode} summary:"))
        self.stdout.write(f"  total: {stats.total}")
        self.stdout.write(f"  created: {stats.created}")
        self.stdout.write(f"  updated: {stats.updated}")
        self.stdout.write(f"  skipped_duplicates: {stats.skipped_duplicates}")
        self.stdout.write(f"  skipped_unresolved_location: {stats.skipped_unresolved_location}")
        self.stdout.write(f"  image_saved: {stats.image_saved}")
        self.stdout.write(f"  image_failed: {stats.image_failed}")
        self.stdout.write(f"  errors: {stats.errors}")
