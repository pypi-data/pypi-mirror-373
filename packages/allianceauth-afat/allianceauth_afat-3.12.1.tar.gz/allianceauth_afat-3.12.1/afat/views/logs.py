"""
Logs related views
"""

# Django
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# Alliance Auth AFAT
from afat import __title__
from afat.helper.views import convert_logs_to_dict
from afat.models import FatLink, Log, Setting

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


@login_required()
@permissions_required(perm=("afat.manage_afat", "afat.log_view"))
def overview(request: WSGIRequest) -> HttpResponse:
    """
    Logs view

    :param request:
    :type request:
    :return:
    :rtype:
    """

    logger.info(msg=f"Log view called by {request.user}")

    context = {"log_duration": Setting.get_setting(Setting.Field.DEFAULT_LOG_DURATION)}

    return render(
        request=request,
        template_name="afat/view/logs/logs-overview.html",
        context=context,
    )


@login_required()
@permissions_required(perm=("afat.manage_afat", "afat.log_view"))
def ajax_get_logs(
    request: WSGIRequest,  # pylint: disable=unused-argument
) -> JsonResponse:
    """
    Ajax call :: get all log entries

    :param request:
    :type request:
    :return:
    :rtype:
    """

    logs = Log.objects.select_related("user", "user__profile__main_character").all()
    fatlink_hashes = set(FatLink.objects.values_list("hash", flat=True))

    log_rows = [
        convert_logs_to_dict(log=log, fatlink_exists=log.fatlink_hash in fatlink_hashes)
        for log in logs
    ]

    return JsonResponse(data=log_rows, safe=False)
