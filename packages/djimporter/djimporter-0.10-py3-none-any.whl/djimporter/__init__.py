"""
Package metadata definition.
"""
VERSION = (0, 10, 0, 'final', 0)


default_app_config = 'djimporter.apps.ImporterConfig'


def get_version():
    "Returns a PEP 386-compliant version number from VERSION."
    if (len(VERSION) != 5 or
            VERSION[3] not in ('alpha', 'beta', 'rc', 'final')):
        raise ValueError(
            "{} is not PEP 386-compliant version number".format(VERSION))

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|c}N - for alpha, beta and rc releases

    parts = 2 if VERSION[2] == 0 else 3
    main = '.'.join(str(x) for x in VERSION[:parts])

    sub = ''

    if VERSION[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[VERSION[3]] + str(VERSION[4])

    return str(main + sub)


def get_importlog_model():
    """
    Return the ImportLog model that is active in this project.
    """
    # avoid circular dependencies (setup.py calls get_version())
    from django.apps import apps as django_apps
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured

    importlog_class = getattr(settings, 'IMPORT_LOG_MODEL', 'djimporter.ImportLog')
    try:
        return django_apps.get_model(importlog_class, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("IMPORT_LOG_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "IMPORT_LOG_MODEL refers to model '%s' that has not been installed" % settings.IMPORT_LOG_MODEL
        )
