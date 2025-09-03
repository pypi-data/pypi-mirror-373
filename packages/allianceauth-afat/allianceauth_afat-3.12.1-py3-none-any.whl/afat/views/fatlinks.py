"""
Fat links related views
"""

# Standard Library
from datetime import timedelta

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required
from allianceauth.eveonline.models import EveCharacter
from allianceauth.eveonline.providers import provider
from allianceauth.services.hooks import get_extension_logger
from esi.decorators import token_required
from esi.models import Token

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# Alliance Auth AFAT
from afat import __title__
from afat.forms import (
    AFatClickFatForm,
    AFatEsiFatForm,
    AFatManualFatForm,
    FatLinkEditForm,
)
from afat.helper.fatlinks import get_doctrines, get_esi_fleet_information_by_user
from afat.helper.time import get_time_delta
from afat.helper.views import convert_fatlinks_to_dict, convert_fats_to_dict
from afat.models import (
    Duration,
    Fat,
    FatLink,
    FleetType,
    Log,
    Setting,
    get_hash_on_save,
)
from afat.providers import esi
from afat.tasks import process_fats
from afat.utils import get_or_create_character, write_log

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


@login_required()
@permission_required("afat.basic_access")
def overview(request: WSGIRequest, year: int = None) -> HttpResponse:
    """
    Fat links view

    :param request:
    :type request:
    :param year:
    :type year:
    :return:
    :rtype:
    """

    if year is None:
        year = datetime.now().year

    context = {
        "year": year,
        "year_current": datetime.now().year,
        "year_prev": int(year) - 1,
        "year_next": int(year) + 1,
    }

    logger.info(msg=f"FAT link list called by {request.user}")

    return render(
        request=request,
        template_name="afat/view/fatlinks/fatlinks-overview.html",
        context=context,
    )


@login_required()
@permission_required("afat.basic_access")
def ajax_get_fatlinks_by_year(request: WSGIRequest, year: int) -> JsonResponse:
    """
    Ajax call :: get all FAT links for a given year

    :param request:
    :type request:
    :param year:
    :type year:
    :return:
    :rtype:
    """

    fatlinks = (
        FatLink.objects.select_related_default()
        .filter(created__year=year)
        .annotate_fats_count()
    )

    fatlink_rows = [
        convert_fatlinks_to_dict(
            request=request,
            fatlink=fatlink,
            close_esi_redirect=reverse(viewname="afat:fatlinks_overview"),
        )
        for fatlink in fatlinks
    ]

    return JsonResponse(data=fatlink_rows, safe=False)


@login_required()
@permissions_required(("afat.manage_afat", "afat.add_fatlink"))
def add_fatlink(request: WSGIRequest) -> HttpResponse:
    """
    Add fat link view

    :param request:
    :type request:
    :return:
    :rtype:
    """

    fleet_types = FleetType.objects.filter(is_enabled=True).order_by("name")

    context = {
        "default_expiry_time": Setting.get_setting(
            Setting.Field.DEFAULT_FATLINK_EXPIRY_TIME
        ),
        "esi_fleet": get_esi_fleet_information_by_user(request.user),
        "esi_fatlink_form": AFatEsiFatForm(),
        "manual_fatlink_form": AFatClickFatForm(),
        "doctrines": get_doctrines(),
        "fleet_types": fleet_types,
    }

    logger.info(msg=f"Add FAT link view called by {request.user}")

    return render(
        request=request,
        template_name="afat/view/fatlinks/fatlinks-add-fatlink.html",
        context=context,
    )


@login_required()
@permissions_required(perm=("afat.manage_afat", "afat.add_fatlink"))
def create_clickable_fatlink(
    request: WSGIRequest,
) -> HttpResponseRedirect:
    """
    Create a clickable fat link

    :param request:
    :type request:
    :return:
    :rtype:
    """

    if request.method == "POST":
        form = AFatClickFatForm(data=request.POST)

        if form.is_valid():
            fatlink_hash = get_hash_on_save()

            fatlink = FatLink()
            fatlink.fleet = form.cleaned_data["name"]
            fatlink.fleet_type = form.cleaned_data["type"]
            fatlink.doctrine = form.cleaned_data["doctrine"]
            fatlink.creator = request.user
            fatlink.hash = fatlink_hash
            fatlink.created = timezone.now()
            fatlink.save()

            dur = Duration()
            dur.fleet = FatLink.objects.get(hash=fatlink_hash)
            dur.duration = form.cleaned_data["duration"]
            dur.save()

            # Writing DB log
            fleet_type = (
                f" (Fleet type: {fatlink.fleet_type})" if fatlink.fleet_type else ""
            )

            write_log(
                request=request,
                log_event=Log.Event.CREATE_FATLINK,
                log_text=(
                    f'FAT link with name "{form.cleaned_data["name"]}"{fleet_type} and '
                    f'a duration of {form.cleaned_data["duration"]} minutes was created'
                ),
                fatlink_hash=fatlink.hash,
            )

            logger.info(
                msg=(
                    f'FAT link "{fatlink_hash}" with name '
                    f'"{form.cleaned_data["name"]}"{fleet_type} and a duration '
                    f'of {form.cleaned_data["duration"]} minutes was created '
                    f"by {request.user}"
                )
            )

            messages.success(
                request=request,
                message=mark_safe(
                    s=_(
                        "<h4>Success!</h4>"
                        "<p>Clickable FAT link created!</p>"
                        "<p>Make sure to give your fleet members the link to "
                        "click so that they get credit for this fleet.</p>"
                    )
                ),
            )

            return redirect(
                to="afat:fatlinks_details_fatlink", fatlink_hash=fatlink_hash
            )

        messages.error(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Error!</h4>"
                    "<p>Something went wrong when attempting "
                    "to submit your clickable FAT link.</p>"
                )
            ),
        )

        return redirect("afat:fatlinks_add_fatlink")

    messages.warning(
        request=request,
        message=mark_safe(
            s=_(
                "<h4>Warning!</h4>"
                '<p>You must fill out the form on the "Add FAT link" '
                "page to create a clickable FAT link</p>"
            )
        ),
    )

    return redirect(to="afat:fatlinks_add_fatlink")


@login_required()
@permissions_required(perm=("afat.manage_afat", "afat.add_fatlink"))
@token_required(scopes=["esi-fleets.read_fleet.v1"])
def create_esi_fatlink_callback(  # pylint: disable=too-many-locals
    request: WSGIRequest, token, fatlink_hash: str
) -> HttpResponseRedirect:
    """
    Helper :: create ESI link (callback, used when coming back from character selection)

    :param request:
    :type request:
    :param token:
    :type token:
    :param fatlink_hash:
    :type fatlink_hash:
    :return:
    :rtype:
    """

    # Check if there is a fleet
    try:
        required_scopes = ["esi-fleets.read_fleet.v1"]
        esi_token = Token.get_token(
            character_id=token.character_id, scopes=required_scopes
        )

        fleet_from_esi = esi.client.Fleets.get_characters_character_id_fleet(
            character_id=token.character_id, token=esi_token.valid_access_token()
        ).result()
    except Exception:  # pylint: disable=broad-exception-caught
        # Not in a fleet
        messages.warning(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Warning!</h4>"
                    "<p>To use the ESI function, you need to be in fleet and you need "
                    "to be the fleet boss! You can create a clickable FAT link and "
                    "share it, if you like.</p>"
                )
            ),
        )

        # Return to "Add FAT link" view
        return redirect(to="afat:fatlinks_add_fatlink")

    # check if this character already has a fleet
    creator_character = EveCharacter.objects.get(character_id=token.character_id)
    registered_fleets_for_creator = FatLink.objects.select_related_default().filter(
        is_esilink=True,
        is_registered_on_esi=True,
        character__character_name=creator_character.character_name,
    )

    fleet_already_registered = False
    character_has_registered_fleets = False
    registered_fleets_to_close = []

    if registered_fleets_for_creator.count() > 0:
        character_has_registered_fleets = True

        for registered_fleet in registered_fleets_for_creator:
            if registered_fleet.esi_fleet_id == fleet_from_esi["fleet_id"]:
                # Character already has a fleet
                fleet_already_registered = True
            else:
                registered_fleets_to_close.append(
                    {"registered_fleet": registered_fleet}
                )

    # If the FC already has a fleet, and it is the same as already registered,
    # just throw a warning
    if fleet_already_registered is True:
        messages.warning(
            request=request,
            message=mark_safe(
                s=format_lazy(
                    _(
                        "<h4>Warning!</h4>"
                        '<p>Fleet with ID "{fleet_id}" for your character '
                        "{creator__character_name} has already been registered and "
                        "pilots joining this fleet are automatically tracked.</p>"
                    ),
                    fleet_id=fleet_from_esi["fleet_id"],
                    creator__character_name=creator_character.character_name,
                ),
            ),
        )

        # Return to "Add FAT link" view
        return redirect(to="afat:fatlinks_add_fatlink")

    # If it's a new fleet, remove all former registered fleets, if there are any
    if (
        character_has_registered_fleets is True
        and fleet_already_registered is False
        and len(registered_fleets_to_close) > 0
    ):
        for registered_fleet_to_close in registered_fleets_to_close:
            reason = (
                f"FC has opened a new fleet with the "
                f"character {creator_character.character_name}"
            )

            logger.info(
                msg=(
                    "Closing ESI FAT link with hash "
                    f'"{registered_fleet_to_close["registered_fleet"].hash}". '
                    f"Reason: {reason}"
                )
            )

            registered_fleet_to_close["registered_fleet"].is_registered_on_esi = False
            registered_fleet_to_close["registered_fleet"].save()

    # Check if we deal with the fleet boss here
    try:
        esi_fleet_member = esi.client.Fleets.get_fleets_fleet_id_members(
            fleet_id=fleet_from_esi["fleet_id"],
            token=esi_token.valid_access_token(),
        ).result()
    except Exception:  # pylint: disable=broad-exception-caught
        messages.warning(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Warning!</h4>"
                    "<p>Not Fleet Boss! Only the fleet boss can utilize the ESI "
                    "function. You can create a clickable FAT link and share it, "
                    "if you like.</p>"
                )
            ),
        )

        # Return to "Add FAT link" view
        return redirect(to="afat:fatlinks_add_fatlink")

    creator_character = EveCharacter.objects.get(character_id=token.character_id)

    # Create the fat link
    fatlink = FatLink(
        created=timezone.now(),
        fleet=request.session["fatlink_form__name"],
        doctrine=request.session["fatlink_form__doctrine"],
        creator=request.user,
        character=creator_character,
        hash=fatlink_hash,
        is_esilink=True,
        is_registered_on_esi=True,
        esi_fleet_id=fleet_from_esi["fleet_id"],
        fleet_type=request.session["fatlink_form__type"],
    )

    # Save it
    fatlink.save()

    # Writing DB log
    fleet_type = f"(Fleet type: {fatlink.fleet_type})" if fatlink.fleet_type else ""

    write_log(
        request=request,
        log_event=Log.Event.CREATE_FATLINK,
        log_text=(
            f'ESI FAT link with name "{request.session["fatlink_form__name"]}" '
            f"{fleet_type} was created by {request.user}"
        ),
        fatlink_hash=fatlink.hash,
    )

    logger.info(
        msg=(
            f'ESI FAT link "{fatlink_hash}" with name '
            f'"{request.session["fatlink_form__name"]}" {fleet_type} '
            f"was created by {request.user}"
        )
    )

    # Clear session
    del request.session["fatlink_form__name"]
    del request.session["fatlink_form__type"]

    # Process fleet members in the background
    process_fats.delay(
        data_list=esi_fleet_member, data_source="esi", fatlink_hash=fatlink_hash
    )

    messages.success(
        request=request,
        message=mark_safe(
            s=_(
                "<h4>Success!</h4>"
                "<p>FAT link Created!</p>"
                "<p>FATs have been queued, they may take a few minutes to show up.</p>"
                "<p>Pilots who join later will be automatically added until you "
                "close or leave the fleet in-game.</p>"
            )
        ),
    )

    return redirect(to="afat:fatlinks_details_fatlink", fatlink_hash=fatlink_hash)


@login_required()
def create_esi_fatlink(
    request: WSGIRequest,
) -> HttpResponseRedirect:
    """
    Create an ESI fat link

    :param request:
    :type request:
    :return:
    :rtype:
    """

    fatlink_form = AFatEsiFatForm(data=request.POST)

    if fatlink_form.is_valid():
        fatlink_hash = get_hash_on_save()

        request.session["fatlink_form__name"] = fatlink_form.cleaned_data["name_esi"]
        request.session["fatlink_form__doctrine"] = fatlink_form.cleaned_data[
            "doctrine_esi"
        ]
        request.session["fatlink_form__type"] = fatlink_form.cleaned_data["type_esi"]

        return redirect(
            to="afat:fatlinks_create_esi_fatlink_callback", fatlink_hash=fatlink_hash
        )

    messages.error(
        request=request,
        message=mark_safe(
            s=_(
                "<h4>Error!</h4>"
                "<p>Something went wrong when attempting to "
                "submit your ESI FAT link.</p>"
            )
        ),
    )

    return redirect(to="afat:fatlinks_add_fatlink")


@login_required()
@permission_required(perm="afat.basic_access")
@token_required(
    scopes=[
        "esi-location.read_location.v1",
        "esi-location.read_ship_type.v1",
        "esi-location.read_online.v1",
    ]
)
def add_fat(
    request: WSGIRequest, token, fatlink_hash: str = None
) -> HttpResponseRedirect:
    """
    Click fat link helper
    :param request:
    :type request:
    :param token:
    :type token:
    :param fatlink_hash:
    :type fatlink_hash:
    :return:
    :rtype:
    """

    if fatlink_hash is None:
        messages.warning(
            request=request,
            message=mark_safe(
                s=_("<h4>Warning!</h4><p>No FAT link hash provided.</p>")
            ),
        )

        return redirect(to="afat:dashboard")

    try:
        fleet = FatLink.objects.get(hash=fatlink_hash, is_esilink=False)
    except FatLink.DoesNotExist:
        messages.warning(
            request=request,
            message=mark_safe(
                s=_("<h4>Warning!</h4><p>The hash provided is not valid.</p>")
            ),
        )

        return redirect(to="afat:dashboard")

    dur = Duration.objects.get(fleet=fleet)
    now = timezone.now() - timedelta(minutes=dur.duration)

    if now >= fleet.created:
        messages.warning(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Warning!</h4>"
                    "<p>Sorry, that FAT link is expired. "
                    "If you were on that fleet, contact your FC about "
                    "having your FAT manually added.</p>"
                )
            ),
        )

        return redirect(to="afat:dashboard")

    character = EveCharacter.objects.get(character_id=token.character_id)

    try:
        required_scopes = [
            "esi-location.read_location.v1",
            "esi-location.read_online.v1",
            "esi-location.read_ship_type.v1",
        ]
        esi_token = Token.get_token(
            character_id=token.character_id, scopes=required_scopes
        )
    except Exception:  # pylint: disable=broad-exception-caught
        messages.warning(
            request=request,
            message=mark_safe(
                s=format_lazy(
                    _(
                        "<h4>Warning!</h4>"
                        "<p>There was an issue with the ESI token for {character_name}. "
                        "Please try again.</p>"
                    ),
                    character_name=character.character_name,
                )
            ),
        )

        return redirect(to="afat:dashboard")

    # Check if character is online
    character_online = esi.client.Location.get_characters_character_id_online(
        character_id=token.character_id, token=esi_token.valid_access_token()
    ).result()

    if character_online["online"] is True:
        # Character location
        location = esi.client.Location.get_characters_character_id_location(
            character_id=token.character_id,
            token=esi_token.valid_access_token(),
        ).result()

        # Current ship
        ship = esi.client.Location.get_characters_character_id_ship(
            character_id=token.character_id,
            token=esi_token.valid_access_token(),
        ).result()

        # System information
        system = esi.client.Universe.get_universe_systems_system_id(
            system_id=location["solar_system_id"]
        ).result()["name"]

        ship_name = provider.get_itemtype(type_id=ship["ship_type_id"]).name

        try:
            Fat(
                fatlink=fleet,
                character=character,
                system=system,
                shiptype=ship_name,
                corporation_eve_id=character.corporation_id,
                alliance_eve_id=character.alliance_id,
            ).save()
        except IntegrityError:
            messages.warning(
                request=request,
                message=mark_safe(
                    s=format_lazy(
                        _(
                            "<h4>Warning!</h4>"
                            "<p>The selected charcter ({character_name}) is already "
                            "registered for this FAT link.</p>"
                        ),
                        character_name=character.character_name,
                    )
                ),
            )
        else:
            if fleet.fleet is not None:
                fleet_name = fleet.fleet
            else:
                fleet_name = fleet.hash

            messages.success(
                request=request,
                message=mark_safe(
                    s=format_lazy(
                        _(
                            "<h4>Success!</h4>"
                            '<p>FAT registered for {character_name} at "{fleet_name}"</p>'
                        ),
                        character_name=character.character_name,
                        fleet_name=fleet_name,
                    )
                ),
            )

            logger.info(
                msg=(
                    f'Participation for fleet "{fleet_name}" registered for '
                    f"pilot {character.character_name}"
                )
            )
    else:
        messages.warning(
            request=request,
            message=mark_safe(
                s=format_lazy(
                    _(
                        "<h4>Warning!</h4>"
                        "<p>Cannot register the fleet participation for "
                        "{character_name}. The character needs to be online.</p>"
                    ),
                    character_name=character.character_name,
                )
            ),
        )

    return redirect(to="afat:dashboard")


@login_required()
@permissions_required(perm=("afat.manage_afat", "afat.add_fatlink"))
def details_fatlink(  # pylint: disable=too-many-statements too-many-branches too-many-locals
    request: WSGIRequest, fatlink_hash: str
) -> HttpResponse:
    """
    Fat link view

    :param request:
    :type request:
    :param fatlink_hash:
    :type fatlink_hash:
    :return:
    :rtype:
    """

    try:
        link = FatLink.objects.select_related_default().get(hash=fatlink_hash)
    except FatLink.DoesNotExist:
        messages.warning(
            request=request,
            message=mark_safe(
                s=_("<h4>Warning!</h4><p>The hash provided is not valid.</p>")
            ),
        )

        return redirect(to="afat:dashboard")

    if request.method == "POST":
        fatlink_edit_form = FatLinkEditForm(data=request.POST)
        manual_fat_form = AFatManualFatForm(data=request.POST)

        if fatlink_edit_form.is_valid():
            link.fleet = fatlink_edit_form.cleaned_data["fleet"]
            link.save()

            # Writing DB log
            write_log(
                request=request,
                log_event=Log.Event.CHANGE_FATLINK,
                log_text=f'FAT link changed. Fleet name was set to "{link.fleet}"',
                fatlink_hash=link.hash,
            )

            logger.info(
                msg=(
                    f'FAT link with hash "{link.hash}" changed. '
                    f'Fleet name was set to "{link.fleet}" by {request.user}'
                )
            )

            messages.success(
                request=request,
                message=mark_safe(
                    s=_("<h4>Success!</h4><p>Fleet name successfully changed.</p>")
                ),
            )
        elif manual_fat_form.is_valid():
            character_name = manual_fat_form.cleaned_data["character"]
            system = manual_fat_form.cleaned_data["system"]
            shiptype = manual_fat_form.cleaned_data["shiptype"]
            character = get_or_create_character(name=character_name)

            if character is not None:
                afat_object, created = Fat.objects.get_or_create(
                    fatlink=link,
                    character=character,
                    defaults={
                        "system": system,
                        "shiptype": shiptype,
                    },
                )

                if created is True:
                    messages.success(
                        request=request,
                        message=mark_safe(
                            s=format_lazy(
                                _(
                                    "<h4>Success!</h4><p>Manual FAT processed.<br>"
                                    "{character_name} has been added flying a {shiptype} "
                                    "in {system}</p>"
                                ),
                                character_name=character.character_name,
                                shiptype=shiptype,
                                system=system,
                            )
                        ),
                    )

                    # Writing DB log
                    write_log(
                        request=request,
                        log_event=Log.Event.MANUAL_FAT,
                        log_text=(
                            f"Pilot {character.character_name} "
                            f"flying a {shiptype} was manually added"
                        ),
                        fatlink_hash=link.hash,
                    )

                    logger.info(
                        msg=(
                            f"Pilot {character.character_name} flying a {shiptype} was "
                            "manually added to FAT link with "
                            f'hash "{link.hash}" by {request.user}'
                        )
                    )
                else:
                    messages.info(
                        request=request,
                        message=mark_safe(
                            s=format_lazy(
                                _(
                                    "<h4>Information</h4>"
                                    "<p>Pilot is already registered for this FAT link.</p>"
                                    "<p>Name: {character_name}<br>System: {system}<br>Ship: {shiptype}</p>"
                                ),
                                character_name=character.character_name,
                                system=afat_object.system,
                                shiptype=afat_object.shiptype,
                            )
                        ),
                    )
            else:
                messages.error(
                    request=request,
                    message=mark_safe(
                        s=_(
                            "<h4>Oh No!</h4>"
                            "<p>Manual FAT processing failed! "
                            "The character name you entered was not found.</p>"
                        )
                    ),
                )
        else:
            messages.error(
                request=request,
                message=mark_safe(s=_("<h4>Oh No!</h4><p>Something went wrong!</p>")),
            )

    logger.info(msg=f'FAT link "{fatlink_hash}" details view called by {request.user}')

    # Let's see if the link is still valid or has expired already and can be re-opened
    # and FATs can be manually added
    # (only possible for 24 hours after creating the FAT link)
    link_ongoing = True
    link_can_be_reopened = False
    link_expires = None
    manual_fat_can_be_added = False

    # Time dependant settings
    try:
        dur = Duration.objects.get(fleet=link)
    except Duration.DoesNotExist:
        # ESI link
        link_ongoing = False
    else:
        link_expires = link.created + timedelta(minutes=dur.duration)
        now = timezone.now()

        if link_expires <= now:
            # Link expired
            link_ongoing = False

            if link.reopened is False and get_time_delta(
                then=link_expires, now=now, interval="minutes"
            ) < Setting.get_setting(Setting.Field.DEFAULT_FATLINK_REOPEN_GRACE_TIME):
                link_can_be_reopened = True

        # Manual fat still possible?
        # Only possible if the FAT link has not been re-opened
        # and has been created within the last 24 hours
        if (
            link.reopened is False
            and get_time_delta(then=link.created, now=now, interval="hours") < 24
        ):
            manual_fat_can_be_added = True

    is_clickable_link = False
    if link.is_esilink is False:
        is_clickable_link = True

    if link.is_esilink and link.is_registered_on_esi:
        link_ongoing = True

    context = {
        "link": link,
        "is_esi_link": link.is_esilink,
        "is_clickable_link": is_clickable_link,
        "link_expires": link_expires,
        "link_ongoing": link_ongoing,
        "link_can_be_reopened": link_can_be_reopened,
        "manual_fat_can_be_added": manual_fat_can_be_added,
        "reopen_grace_time": Setting.get_setting(
            Setting.Field.DEFAULT_FATLINK_REOPEN_GRACE_TIME
        ),
        "reopen_duration": Setting.get_setting(
            Setting.Field.DEFAULT_FATLINK_REOPEN_DURATION
        ),
    }

    return render(
        request=request,
        template_name="afat/view/fatlinks/fatlinks-details-fatlink.html",
        context=context,
    )


@login_required()
@permissions_required(perm=("afat.manage_afat", "afat.add_fatlink"))
def ajax_get_fats_by_fatlink(request: WSGIRequest, fatlink_hash) -> JsonResponse:
    """
    Ajax call :: get all FATs for a given FAT link hash

    :param request:
    :type request:
    :param fatlink_hash:
    :type fatlink_hash:
    :return:
    :rtype:
    """

    fats = Fat.objects.select_related_default().filter(fatlink__hash=fatlink_hash)

    fat_rows = [convert_fats_to_dict(request=request, fat=fat) for fat in fats]

    return JsonResponse(data=fat_rows, safe=False)


@login_required()
@permission_required(perm="afat.manage_afat")
def delete_fatlink(request: WSGIRequest, fatlink_hash: str) -> HttpResponseRedirect:
    """
    Delete fat link helper

    :param request:
    :type request:
    :param fatlink_hash:
    :type fatlink_hash:
    :return:
    :rtype:
    """

    try:
        link = FatLink.objects.get(hash=fatlink_hash)
    except FatLink.DoesNotExist:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4>"
                    "<p>The FAT link hash provided is either invalid "
                    "or the FAT link has already been deleted.</p>"
                )
            ),
        )

        return redirect("afat:dashboard")

    # Delete associated FATs and the FAT link
    Fat.objects.filter(fatlink_id=link.pk).delete()
    link.delete()

    # Log the deletion
    write_log(
        request,
        log_event=Log.Event.DELETE_FATLINK,
        log_text="FAT link deleted.",
        fatlink_hash=fatlink_hash,
    )

    messages.success(
        request,
        mark_safe(
            format_lazy(
                _(
                    "<h4>Success!</h4>"
                    '<p>The FAT link "{fatlink_hash}" and all associated FATs have '
                    "been successfully deleted.</p>"
                ),
                fatlink_hash=fatlink_hash,
            )
        ),
    )

    logger.info(
        f'Fat link "{fatlink_hash}" and all associated FATs have been deleted by {request.user}'
    )

    return redirect("afat:fatlinks_overview")


@login_required()
@permissions_required(perm=("afat.manage_afat", "afat.delete_afat"))
def delete_fat(
    request: WSGIRequest, fatlink_hash: str, fat_id: int
) -> HttpResponseRedirect:
    """
    Delete fat helper

    :param request:
    :type request:
    :param fatlink_hash:
    :type fatlink_hash:
    :param fat_id:
    :type fat_id:
    :return:
    :rtype:
    """

    try:
        link = FatLink.objects.get(hash=fatlink_hash)
        fat_details = Fat.objects.get(pk=fat_id, fatlink_id=link.pk)
    except FatLink.DoesNotExist:
        messages.error(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Error!</h4>"
                    "<p>The hash provided is either invalid or has been deleted.</p>"
                )
            ),
        )

        return redirect(to="afat:dashboard")
    except Fat.DoesNotExist:
        messages.error(
            request=request,
            message=mark_safe(
                s=_("<h4>Error!</h4><p>The hash and FAT ID do not match.</p>")
            ),
        )

        return redirect(to="afat:dashboard")

    fat_details.delete()

    write_log(
        request=request,
        log_event=Log.Event.DELETE_FAT,
        log_text=f"The FAT for {fat_details.character.character_name} has been deleted",
        fatlink_hash=link.hash,
    )

    messages.success(
        request=request,
        message=mark_safe(
            s=format_lazy(
                _(
                    "<h4>Success!</h4>"
                    "<p>The FAT for {character_name} has been successfully deleted "
                    'from FAT link "{fatlink_hash}".</p>'
                ),
                character_name=fat_details.character.character_name,
                fatlink_hash=fatlink_hash,
            )
        ),
    )

    logger.info(
        msg=(
            f"The FAT for {fat_details.character.character_name} has "
            f'been deleted from FAT link "{fatlink_hash}" by {request.user}.'
        )
    )

    return redirect(to="afat:fatlinks_details_fatlink", fatlink_hash=fatlink_hash)


@login_required()
@permissions_required(perm=("afat.manage_afat", "afat.add_fatlink"))
def close_esi_fatlink(request: WSGIRequest, fatlink_hash: str) -> HttpResponseRedirect:
    """
    Ajax call to close an ESI fat link

    :param request:
    :type request:
    :param fatlink_hash:
    :type fatlink_hash:
    :return:
    :rtype:
    """

    try:
        fatlink = FatLink.objects.get(hash=fatlink_hash)
        fatlink.is_registered_on_esi = False
        fatlink.save()

        logger.info(
            msg=(
                f'Closing ESI FAT link with hash "{fatlink_hash}". '
                "Reason: Closed by manual request"
            )
        )
    except FatLink.DoesNotExist:
        logger.info(msg=f'ESI FAT link with hash "{fatlink_hash}" does not exist')

    next_view = request.GET.get("next", reverse("afat:dashboard"))

    return HttpResponseRedirect(redirect_to=next_view)


@login_required()
@permissions_required(perm=("afat.manage_afat", "afat.add_fatlink"))
def reopen_fatlink(request: WSGIRequest, fatlink_hash: str) -> HttpResponseRedirect:
    """
    Re-open fat link

    :param request:
    :type request:
    :param fatlink_hash:
    :type fatlink_hash:
    :return:
    :rtype:
    """

    try:
        fatlink_duration = Duration.objects.get(fleet__hash=fatlink_hash)
    except Duration.DoesNotExist:
        messages.error(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Error!</h4>"
                    "<p>The hash you provided does not match with any FAT link.</p>"
                )
            ),
        )

        return redirect(to="afat:dashboard")

    if not fatlink_duration.fleet.reopened:
        created_at = fatlink_duration.fleet.created
        now = datetime.now()

        default_reopen_duration = Setting.get_setting(
            Setting.Field.DEFAULT_FATLINK_REOPEN_DURATION
        )
        time_difference_in_minutes = get_time_delta(
            then=created_at, now=now, interval="minutes"
        )
        new_duration = time_difference_in_minutes + default_reopen_duration

        fatlink_duration.duration = new_duration
        fatlink_duration.save()

        fatlink_duration.fleet.reopened = True
        fatlink_duration.fleet.save()

        # writing DB log
        write_log(
            request=request,
            log_event=Log.Event.REOPEN_FATLINK,
            log_text=f"FAT link re-opened for a duration of {default_reopen_duration} minutes",
            fatlink_hash=fatlink_duration.fleet.hash,
        )

        logger.info(
            msg=(
                f'FAT link with hash "{fatlink_hash}" re-opened by {request.user} '
                f"for a duration of {default_reopen_duration} minutes"
            )
        )

        messages.success(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Success!</h4>"
                    "<p>The FAT link has been successfully re-opened.</p>"
                )
            ),
        )
    else:
        messages.warning(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Warning!</h4>"
                    "<p>This FAT link has already been re-opened. "
                    "FAT links can be re-opened only once!</p>"
                )
            ),
        )

    return redirect(to="afat:fatlinks_details_fatlink", fatlink_hash=fatlink_hash)
