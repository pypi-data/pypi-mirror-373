from django.apps import apps
from django.conf import settings


def check_importlog_model(app_configs=None, **kwargs):
    if app_configs is None:
        importlog_class = getattr(settings, 'IMPORT_LOG_MODEL', 'djimporter.ImportLog')
        apps.get_model(importlog_class)
    else:
        app_label, model_name = settings.IMPORT_LOG_MODEL.split('.')
        for app_config in app_configs:
            if app_config.label == app_label:
                app_config.get_model(model_name)
                break
        else:
            # Checks might be run against a set of app configs that don't
            # include the specified user model. In this case we simply don't
            # perform the checks defined below.
            return []

    return []
