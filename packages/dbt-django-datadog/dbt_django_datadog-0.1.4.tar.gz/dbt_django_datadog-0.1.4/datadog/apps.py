import logging
from django.apps import AppConfig
from .instrument import configure_datadog

logger = logging.getLogger(__name__)


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "datadog"

    def ready(self):
        logger.info("Configuring datadog")
        configure_datadog()
        logger.info("Datadog configured")
