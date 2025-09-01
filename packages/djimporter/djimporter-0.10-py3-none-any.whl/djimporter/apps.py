from django.apps import AppConfig
from django.core import checks

from .checks import check_importlog_model


class ImporterConfig(AppConfig):
    name = 'djimporter'

    def ready(self):
        checks.register(check_importlog_model, checks.Tags.models)
