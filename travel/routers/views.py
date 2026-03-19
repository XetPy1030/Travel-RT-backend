import uuid

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..core.pagination import StandardResultsSetPagination
from .models import RouteGenerationJob, Router
from .serializers import (
    RouteGenerateRequestSerializer,
    RouteGenerateStatusSerializer,
    RouterDetailSerializer,
    RouterListSerializer,
)
from .tasks import run_route_generation_pipeline


class RouterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Router.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["district", "settlement", "difficulty"]
    search_fields = ["title", "short_description"]
    ordering_fields = ["title", "created_at"]
    ordering = ["title"]

    def get_queryset(self):
        qs = Router.objects.all()
        if self.action == "list":
            qs = qs.filter(creation_method=Router.CreationMethod.MANUAL)
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RouterDetailSerializer
        return RouterListSerializer


def _build_intent_from_location(district_id=None, settlement_id=None):
    """Строит intent из переданных district_id или settlement_id."""
    from travel.locations.models import District, Settlement

    intent = {
        "location_type": "unknown",
        "location_name": None,
        "duration": None,
        "transport_mode": None,
        "preferred_tags": [],
        "audience": [],
        "budget": None,
        "time_of_day": None,
        "special_requirements": [],
        "missing_info": [],
        "confidence": "high",
        "clarification_question": None,
    }
    if settlement_id:
        s = Settlement.objects.filter(id=settlement_id).first()
        if s:
            intent["location_type"] = "settlement"
            intent["location_name"] = s.name
            return intent
    if district_id:
        d = District.objects.filter(id=district_id).first()
        if d:
            intent["location_type"] = "district"
            intent["location_name"] = d.name
            return intent
    return intent


@api_view(["POST"])
def generate_route(request):
    """POST /api/routers/generate/ — запуск генерации маршрута."""
    from travel.ai.client import call_llm
    from travel.locations.models import District, Settlement
    from travel.places.models import Tag
    from travel.prompts.route_intent import build_intent_prompt
    from travel.routers.services.route_query_builder import (
        get_context_for_llm,
        validate_intent_location,
    )

    serializer = RouteGenerateRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user_text = (data.get("user_text") or "").strip()
    district_id = data.get("district_id")
    settlement_id = data.get("settlement_id")

    if district_id or settlement_id:
        intent = _build_intent_from_location(district_id=district_id, settlement_id=settlement_id)
        if not intent.get("location_name"):
            return Response(
                {"message": "Район или населённый пункт не найден."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        if not user_text:
            return Response(
                {"clarification_question": "Опишите, какой маршрут вы хотите (город/район, пожелания)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        districts = list(District.objects.values_list("name", flat=True).order_by("name"))
        settlements = list(Settlement.objects.values_list("name", flat=True).order_by("name"))
        tags = list(Tag.objects.values_list("slug", flat=True).order_by("slug"))
        prompt = build_intent_prompt(user_text, districts, settlements, tags)
        intent_response = call_llm(prompt, json_mode=True, temperature=0.2)
        if not intent_response or not isinstance(intent_response, dict):
            return Response(
                {"message": "Не удалось разобрать запрос. Попробуйте указать город или район."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        intent = intent_response

    if user_text:
        # Прокидываем исходный запрос пользователя в intent,
        # чтобы генератор маршрута мог учитывать стиль и формулировки.
        intent["user_text"] = user_text

    ok, err_msg = validate_intent_location(intent)
    if not ok:
        return Response(
            {"clarification_question": err_msg},
            status=status.HTTP_400_BAD_REQUEST,
        )

    context = get_context_for_llm(intent)
    if "error" in context:
        return Response(
            {"message": context.get("message", "Нет доступных мест.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    task_id = str(uuid.uuid4())
    job = RouteGenerationJob.objects.create(
        task_id=task_id,
        status=RouteGenerationJob.Status.PENDING,
        intent=intent,
    )
    run_route_generation_pipeline.delay(job.id)

    return Response(
        {"task_id": task_id},
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(["GET"])
def generate_route_status(request, task_id):
    """GET /api/routers/generate/<task_id>/ — статус задачи генерации."""
    job = RouteGenerationJob.objects.filter(task_id=task_id).first()
    if not job:
        return Response(
            {"detail": "Задача не найдена."},
            status=status.HTTP_404_NOT_FOUND,
        )
    serializer = RouteGenerateStatusSerializer(
        {
            "status": job.status,
            "router_id": job.router_id,
            "error_message": job.error_message or None,
        }
    )
    return Response(serializer.data)
