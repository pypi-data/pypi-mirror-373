import json
import os

from background_task import background
from django.utils.module_loading import import_string

from . import get_importlog_model

ImportLog = get_importlog_model()


@background(schedule=0)
def run_importer(csv_model, csv_filepath, log_id, context={}, delimiter=None, headers_mapping=None, warning_mode=False):
    """
    csv_model: should be string dotted_path e.g. 'djimporter.FooCsv'
    context: should be serializable
    """
    importer_class = import_string(csv_model)
    # mark task as running
    log = ImportLog.objects.get(id=log_id)
    log.status = ImportLog.RUNNING
    log.save()

    # run importer
    try:
        importer = importer_class(
            csv_filepath, context=context, delimiter=delimiter, headers_mapping=headers_mapping, log=log,
            warning_mode=warning_mode,
        )
        importer.is_valid(log)
        importer.save()

        # update log with import result
        if importer.errors:
            if importer.warning_mode:
                log.status = ImportLog.PARTIAL_WITH_ERRORS
            else:
                log.status = ImportLog.FAILED

            log.errors = json.dumps(importer.errors)
        else:
            log.status = ImportLog.COMPLETED
            log.num_rows = len(importer.list_objs)

        log.progress = 100


    except Exception as e:
        # Not controlled errors will be thrown to log
        errors = [{'line': 1, 'field': 'Internal Error', 'message': e.args}]
        log.status = ImportLog.FAILED
        log.errors = json.dumps(errors)
        log.progress = 100

    log.save()

    # clean up
    os.remove(csv_filepath)
