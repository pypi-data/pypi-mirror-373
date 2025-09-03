"""
Views helper
"""

# Standard Library
import random
from collections import OrderedDict

# Django
from django.contrib.auth.models import Permission, User
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.datetime_safe import datetime
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

# Alliance Auth (External Libs)
from app_utils.django import users_with_permission

# Alliance Auth AFAT
from afat.models import Fat, FatLink, Log
from afat.utils import get_main_character_from_user


def convert_fatlinks_to_dict(  # pylint: disable=too-many-locals
    request: WSGIRequest, fatlink: FatLink, close_esi_redirect: str = None
) -> dict:
    """
    Converts a FatLink object into a dictionary

    :param request:
    :type request:
    :param fatlink:
    :type fatlink:
    :param close_esi_redirect:
    :type close_esi_redirect:
    :return:
    :rtype:
    """

    # Fleet name
    fatlink_fleet = fatlink.fleet if fatlink.fleet is not None else fatlink.hash

    # ESI marker
    via_esi = "No"
    esi_fleet_marker = ""

    # Check for ESI link
    if fatlink.is_esilink:
        via_esi = "Yes"
        esi_fleet_marker_classes = "badge text-bg-secondary afat-label ms-2"

        if fatlink.is_registered_on_esi:
            esi_fleet_marker_classes = "badge text-bg-success afat-label ms-2"

        marker_text = _("ESI")
        esi_fleet_marker += (
            f'<span class="{esi_fleet_marker_classes}">{marker_text}</span>'
        )

    # Fleet type
    fleet_type = fatlink.fleet_type

    # Creator name
    creator_main_character = get_main_character_from_user(user=fatlink.creator)

    # Fleet time
    fleet_time = fatlink.created
    fleet_time_timestamp = fleet_time.timestamp()

    # Action buttons
    actions = ""
    if (
        fatlink.is_esilink
        and fatlink.is_registered_on_esi
        and fatlink.creator == request.user
    ):
        button_close_esi_tracking_url = reverse(
            viewname="afat:fatlinks_close_esi_fatlink", args=[fatlink.hash]
        )

        close_esi_redirect_parameter = (
            f"?next={close_esi_redirect}" if close_esi_redirect is not None else ""
        )

        button_title = _(
            "Clicking here will stop the automatic tracking through ESI for this fleet and close the associated FAT link."  # pylint: disable=line-too-long
        )
        modal_body_text = _(
            f"<p>Are you sure you want to close ESI fleet with ID {fatlink.esi_fleet_id} from {fatlink.character.character_name}?</p>"  # pylint: disable=line-too-long
        )
        modal_confirm_text = _("Stop tracking")

        actions += (
            '<a class="btn btn-afat-action btn-primary btn-sm" '
            f'style="margin-left: 0.25rem;" title="{button_title}" data-bs-toggle="modal" '
            'data-bs-target="#cancelEsiFleetModal" '
            f'data-url="{button_close_esi_tracking_url}{close_esi_redirect_parameter}" '
            f'data-body-text="{modal_body_text}" '
            f'data-confirm-text="{modal_confirm_text}">'
            '<i class="fa-solid fa-times"></i></a>'
        )

    if request.user.has_perm("afat.manage_afat") or request.user.has_perm(
        perm="afat.add_fatlink"
    ):
        button_edit_url = reverse(
            viewname="afat:fatlinks_details_fatlink", args=[fatlink.hash]
        )

        actions += (
            '<a class="btn btn-info btn-sm m-1" '
            f'href="{button_edit_url}"><span class="fa-solid fa-eye"></span></a>'
        )

    if request.user.has_perm(perm="afat.manage_afat"):
        button_delete_url = reverse(
            viewname="afat:fatlinks_delete_fatlink", args=[fatlink.hash]
        )
        button_delete_text = _("Delete")
        modal_body_text = _(
            f"<p>Are you sure you want to delete FAT link {fatlink_fleet}?</p>"
        )

        actions += (
            '<a class="btn btn-danger btn-sm" data-bs-toggle="modal" '
            f'data-bs-target="#deleteFatLinkModal" data-url="{button_delete_url}" '
            f'data-confirm-text="{button_delete_text}" data-body-text="{modal_body_text}">'
            '<i class="fa-solid fa-trash-can fa-fw"></i></a>'
        )

    return {
        "pk": fatlink.pk,
        "fleet_name": fatlink_fleet + esi_fleet_marker,
        "creator_name": creator_main_character,
        "fleet_type": fleet_type,
        "doctrine": fatlink.doctrine,
        "fleet_time": {"time": fleet_time, "timestamp": fleet_time_timestamp},
        "fats_number": fatlink.fats_count,
        "hash": fatlink.hash,
        "is_esilink": fatlink.is_esilink,
        "esi_fleet_id": fatlink.esi_fleet_id,
        "is_registered_on_esi": fatlink.is_registered_on_esi,
        "actions": actions,
        "via_esi": via_esi,
    }


def convert_fats_to_dict(request: WSGIRequest, fat: Fat) -> dict:
    """
    Converts an AFat object into a dictionary

    :param request:
    :type request:
    :param fat:
    :type fat:
    :return:
    :rtype:
    """

    # ESI marker
    via_esi = "No"
    esi_fleet_marker = ""

    if fat.fatlink.is_esilink:
        via_esi = "Yes"
        esi_fleet_marker_classes = "badge text-bg-secondary afat-label ms-2"

        if fat.fatlink.is_registered_on_esi:
            esi_fleet_marker_classes = "badge text-bg-success afat-label ms-2"

        marker_text = _("ESI")
        esi_fleet_marker += (
            f'<span class="{esi_fleet_marker_classes}">{marker_text}</span>'
        )

    # Actions
    actions = ""
    if request.user.has_perm(perm="afat.manage_afat"):
        button_delete_fat = reverse(
            viewname="afat:fatlinks_delete_fat", args=[fat.fatlink.hash, fat.id]
        )
        button_delete_text = _("Delete")
        modal_body_text = _(
            f"<p>Are you sure you want to remove {fat.character.character_name} from this FAT link?</p>"  # pylint: disable=line-too-long
        )

        actions += (
            '<a class="btn btn-danger btn-sm" '
            'data-bs-toggle="modal" '
            'data-bs-target="#deleteFatModal" '
            f'data-url="{button_delete_fat}" '
            f'data-confirm-text="{button_delete_text}" '
            f'data-body-text="{modal_body_text}">'
            '<i class="fa-solid fa-trash-can fa-fw"></i>'
            "</a>"
        )

    fleet_time = fat.fatlink.created
    fleet_time_timestamp = fleet_time.timestamp()
    fleet_name = (
        fat.fatlink.fleet if fat.fatlink.fleet is not None else fat.fatlink.hash
    )

    summary = {
        "system": fat.system,
        "ship_type": fat.shiptype,
        "character_name": fat.character.character_name,
        "fleet_name": fleet_name + esi_fleet_marker,
        "doctrine": fat.fatlink.doctrine,
        "fleet_time": {"time": fleet_time, "timestamp": fleet_time_timestamp},
        "fleet_type": fat.fatlink.fleet_type,
        "via_esi": via_esi,
        "actions": actions,
    }

    return summary


def convert_logs_to_dict(log: Log, fatlink_exists: bool = False) -> dict:
    """
    Convert AFatLog to dict

    :param log:
    :type log:
    :param fatlink_exists:
    :type fatlink_exists:
    :return:
    :rtype:
    """

    log_time = log.log_time
    log_time_timestamp = log_time.timestamp()

    # User name
    user_main_character = get_main_character_from_user(user=log.user)

    fatlink_html = _(f"{log.fatlink_hash} (Deleted)")
    if fatlink_exists is True:
        fatlink_link = reverse(
            viewname="afat:fatlinks_details_fatlink", args=[log.fatlink_hash]
        )
        fatlink_html = f'<a href="{fatlink_link}">{log.fatlink_hash}</a>'

    fatlink = {"html": fatlink_html, "hash": log.fatlink_hash}

    summary = {
        "log_time": {"time": log_time, "timestamp": log_time_timestamp},
        "log_event": Log.Event(log.log_event).label,
        "user": user_main_character,
        "fatlink": fatlink,
        "description": log.log_text,
    }

    return summary


def get_random_rgba_color():
    """
    Get a random RGB(a) color

    :return:
    :rtype:
    """

    red = random.randint(a=0, b=255)
    green = random.randint(a=0, b=255)
    blue = random.randint(a=0, b=255)
    alpha = 1

    return f"rgba({red}, {green}, {blue}, {alpha})"


def characters_with_permission(permission: Permission) -> models.QuerySet:
    """
    Returns queryset of characters that have the given permission
    in Auth through due to their associated user

    :param permission:
    :type permission:
    :return:
    :rtype:
    """

    # First, we need the users that have the permission
    users_qs = users_with_permission(permission=permission)

    # Now get their characters ... and sort them by userprofile and character name
    charater_qs = EveCharacter.objects.filter(
        character_ownership__user__in=users_qs
    ).order_by("-userprofile", "character_name")

    return charater_qs


def user_has_any_perms(user: User, perm_list, obj=None):
    """
    Return True if the user has each of the specified permissions. If
    an object is passed, check if the user has all required perms for it.
    """

    # Active superusers have all permissions.
    if user.is_active and user.is_superuser:
        return True

    return any(user.has_perm(perm=perm, obj=obj) for perm in perm_list)


def current_month_and_year() -> tuple[int, int]:
    """
    Return the current month and year

    :return: Month and year
    :rtype: Tuple[(int) Current Month, (int) Current Year]
    """

    current_month = datetime.now().month
    current_year = datetime.now().year

    return current_month, current_year


def get_fats_per_hour(fats) -> list:
    """
    Get the FATs per hour from the fats queryset

    :param fats:
    :type fats:
    :return:
    :rtype:
    """

    data_time = {i: fats.filter(fatlink__created__hour=i).count() for i in range(24)}

    return [
        list(data_time.keys()),
        list(data_time.values()),
        [get_random_rgba_color()],
    ]


def get_fat_per_weekday(fats) -> list:
    """
    Get the FATs per weekday from the fats queryset

    :param fats:
    :type fats:
    :return:
    :rtype:
    """

    return [
        [
            _("Monday"),
            _("Tuesday"),
            _("Wednesday"),
            _("Thursday"),
            _("Friday"),
            _("Saturday"),
            _("Sunday"),
        ],
        [fats.filter(fatlink__created__iso_week_day=i).count() for i in range(1, 8)],
        [get_random_rgba_color()],
    ]


def get_average_fats_by_corporations(
    fats: QuerySet[Fat], corporations: QuerySet[EveCorporationInfo]
) -> list:
    """
    Get the average FATs per corporation

    :param fats:
    :type fats:
    :param corporations:
    :type corporations:
    :return:
    :rtype:
    """

    data_avgs = {
        corp.corporation_name: round(
            fats.filter(corporation_eve_id=corp.corporation_id).count()
            / corp.member_count,
            2,
        )
        for corp in corporations
    }

    data_avgs = OrderedDict(sorted(data_avgs.items(), key=lambda x: x[1], reverse=True))

    return [
        list(data_avgs.keys()),
        list(data_avgs.values()),
        get_random_rgba_color(),
    ]
