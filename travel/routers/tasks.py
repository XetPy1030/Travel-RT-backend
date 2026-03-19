import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="routers.run_route_generation_pipeline")
def run_route_generation_pipeline(self, job_id: int):
    """
    Celery-задача: генерация маршрута по задаче RouteGenerationJob.
    Вызывается после POST /api/routers/generate/
    """
    from travel.routers.services import run_pipeline

    run_pipeline(job_id)
