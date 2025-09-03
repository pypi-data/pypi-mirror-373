"""
Test AFAT helpers
"""

# Standard Library
from datetime import timedelta

# Django
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from app_utils.testing import add_character_to_user, create_user_from_evecharacter

# Alliance Auth AFAT
from afat.helper.fatlinks import get_esi_fleet_information_by_user
from afat.helper.time import get_time_delta
from afat.helper.views import (
    convert_fatlinks_to_dict,
    convert_fats_to_dict,
    convert_logs_to_dict,
)
from afat.models import Duration, Fat, FatLink, Log, get_hash_on_save
from afat.tests.fixtures.load_allianceauth import load_allianceauth
from afat.utils import get_main_character_from_user, write_log

MODULE_PATH = "afat.views.fatlinks"


class TestHelpers(TestCase):
    """
    Test Helpers
    """

    @classmethod
    def setUpClass(cls):
        """
        Setup

        :return:
        :rtype:
        """

        super().setUpClass()
        load_allianceauth()

        cls.factory = RequestFactory()

        # given
        cls.character_1001 = EveCharacter.objects.get(character_id=1001)
        cls.character_1002 = EveCharacter.objects.get(character_id=1002)
        cls.character_1003 = EveCharacter.objects.get(character_id=1003)
        cls.character_1004 = EveCharacter.objects.get(character_id=1004)
        cls.character_1005 = EveCharacter.objects.get(character_id=1005)
        cls.character_1101 = EveCharacter.objects.get(character_id=1101)

        cls.user_with_add_fatlink, _ = create_user_from_evecharacter(
            character_id=cls.character_1001.character_id,
            permissions=["afat.basic_access", "afat.add_fatlink"],
        )

        add_character_to_user(
            user=cls.user_with_add_fatlink, character=cls.character_1101
        )

        cls.user_with_manage_afat, _ = create_user_from_evecharacter(
            character_id=cls.character_1002.character_id,
            permissions=["afat.basic_access", "afat.manage_afat"],
        )

        add_character_to_user(
            user=cls.user_with_add_fatlink, character=cls.character_1003
        )

    def test_helper_get_esi_fleet_information_by_user(self):
        # given
        fatlink_hash_fleet_1 = get_hash_on_save()
        fatlink_1 = FatLink.objects.create(
            created=timezone.now(),
            fleet="April Fleet 1",
            creator=self.user_with_add_fatlink,
            character=self.character_1001,
            hash=fatlink_hash_fleet_1,
            is_esilink=True,
            is_registered_on_esi=True,
            esi_fleet_id="3726458287",
        )

        fatlink_hash_fleet_2 = get_hash_on_save()
        fatlink_2 = FatLink.objects.create(
            created=timezone.now(),
            fleet="April Fleet 2",
            creator=self.user_with_add_fatlink,
            character=self.character_1101,
            hash=fatlink_hash_fleet_2,
            is_esilink=True,
            is_registered_on_esi=True,
            esi_fleet_id="372645827",
        )

        self.client.force_login(user=self.user_with_add_fatlink)

        # when
        response = get_esi_fleet_information_by_user(user=self.user_with_add_fatlink)

        # then
        self.assertDictEqual(
            d1=response,
            d2={
                "has_open_esi_fleets": True,
                "open_esi_fleets_list": [fatlink_1, fatlink_2],
            },
        )

    def test_helper_get_time_delta(self):
        # given
        duration = 1812345
        now = timezone.now()
        expires = timedelta(minutes=duration) + now

        self.client.force_login(user=self.user_with_add_fatlink)

        # when
        total = get_time_delta(then=now, now=expires)
        years = get_time_delta(then=now, now=expires, interval="years")
        days = get_time_delta(then=now, now=expires, interval="days")
        hours = get_time_delta(then=now, now=expires, interval="hours")
        minutes = get_time_delta(then=now, now=expires, interval="minutes")
        seconds = get_time_delta(then=now, now=expires, interval="seconds")

        # then
        self.assertEqual(
            first=total, second="3 years, 163 days, 13 hours, 45 minutes and 0 seconds"
        )
        self.assertEqual(first=years, second=3)
        self.assertEqual(first=days, second=1258)
        self.assertEqual(first=hours, second=30205)
        self.assertEqual(first=minutes, second=1812345)
        self.assertEqual(first=seconds, second=108740700)

    def test_helper_convert_fatlinks_to_dict(self):
        # given
        self.client.force_login(user=self.user_with_manage_afat)
        request = self.factory.get(path=reverse(viewname="afat:dashboard"))
        request.user = self.user_with_manage_afat

        fatlink_hash_fleet_1 = get_hash_on_save()
        fatlink_1_created = FatLink.objects.create(
            created=timezone.now(),
            fleet="April Fleet 1",
            creator=self.user_with_manage_afat,
            character=self.character_1001,
            hash=fatlink_hash_fleet_1,
            is_esilink=True,
            is_registered_on_esi=True,
            esi_fleet_id="3726458287",
            doctrine="Ships",
        )
        Fat.objects.create(
            character=self.character_1101, fatlink=fatlink_1_created, shiptype="Omen"
        )

        fatlink_hash_fleet_2 = get_hash_on_save()
        fatlink_2_created = FatLink.objects.create(
            created=timezone.now(),
            fleet="April Fleet 2",
            creator=self.user_with_add_fatlink,
            character=self.character_1101,
            hash=fatlink_hash_fleet_2,
            fleet_type="CTA",
            doctrine="Ships",
        )
        Fat.objects.create(
            character=self.character_1001, fatlink=fatlink_2_created, shiptype="Omen"
        )

        # when
        fatlink_1 = (
            FatLink.objects.select_related_default()
            .annotate_fats_count()
            .get(hash=fatlink_hash_fleet_1)
        )
        close_esi_tracking_url = reverse(
            viewname="afat:fatlinks_close_esi_fatlink", args=[fatlink_1.hash]
        )
        edit_url_1 = reverse(
            viewname="afat:fatlinks_details_fatlink", args=[fatlink_1.hash]
        )
        delete_url_1 = reverse(
            viewname="afat:fatlinks_delete_fatlink", args=[fatlink_1.hash]
        )

        fatlink_2 = (
            FatLink.objects.select_related_default()
            .annotate_fats_count()
            .get(hash=fatlink_hash_fleet_2)
        )
        edit_url_2 = reverse(
            viewname="afat:fatlinks_details_fatlink", args=[fatlink_2.hash]
        )
        delete_url_2 = reverse(
            viewname="afat:fatlinks_delete_fatlink", args=[fatlink_2.hash]
        )

        result_1 = convert_fatlinks_to_dict(request=request, fatlink=fatlink_1)
        result_2 = convert_fatlinks_to_dict(request=request, fatlink=fatlink_2)

        # then
        fleet_time_1 = fatlink_1.created
        fleet_time_timestamp_1 = fleet_time_1.timestamp()
        creator_main_character_1 = get_main_character_from_user(user=fatlink_1.creator)

        self.maxDiff = None

        self.assertDictEqual(
            d1=result_1,
            d2={
                "pk": fatlink_1.pk,
                "fleet_name": (
                    'April Fleet 1<span class="badge text-bg-success afat-label ms-2">ESI</span>'
                ),
                "creator_name": creator_main_character_1,
                "fleet_type": "",
                "doctrine": "Ships",
                "fleet_time": {
                    "time": fleet_time_1,
                    "timestamp": fleet_time_timestamp_1,
                },
                "fats_number": fatlink_1.fats_count,
                "hash": fatlink_1.hash,
                "is_esilink": True,
                "esi_fleet_id": 3726458287,
                "is_registered_on_esi": True,
                "actions": (
                    '<a class="btn btn-afat-action btn-primary btn-sm" '
                    'style="margin-left: 0.25rem;" title="Clicking here will '
                    "stop the automatic tracking through ESI for this fleet "
                    'and close the associated FAT link." data-bs-toggle="modal" '
                    'data-bs-target="#cancelEsiFleetModal" '
                    f'data-url="{close_esi_tracking_url}" '
                    'data-body-text="<p>Are you sure you want to close ESI '
                    'fleet with ID 3726458287 from Bruce Wayne?</p>" '
                    'data-confirm-text="Stop tracking"><i class="fa-solid '
                    'fa-times"></i></a><a class="btn btn-info btn-sm m-1" '
                    f'href="{edit_url_1}"><span class="fa-solid '
                    'fa-eye"></span></a><a class="btn btn-danger btn-sm" '
                    'data-bs-toggle="modal" data-bs-target="#deleteFatLinkModal" '
                    f'data-url="{delete_url_1}" '
                    'data-confirm-text="Delete" data-body-text="<p>Are you '
                    "sure you want to delete FAT link April Fleet "
                    '1?</p>"><i class="fa-solid fa-trash-can fa-fw"></i></a>'
                ),
                "via_esi": "Yes",
            },
        )

        fleet_time_2 = fatlink_2.created
        fleet_time_timestamp_2 = fleet_time_2.timestamp()
        creator_main_character_2 = get_main_character_from_user(user=fatlink_2.creator)

        self.assertDictEqual(
            d1=result_2,
            d2={
                "pk": fatlink_2.pk,
                "fleet_name": "April Fleet 2",
                "creator_name": creator_main_character_2,
                "fleet_type": "CTA",
                "doctrine": "Ships",
                "fleet_time": {
                    "time": fleet_time_2,
                    "timestamp": fleet_time_timestamp_2,
                },
                "fats_number": fatlink_2.fats_count,
                "hash": fatlink_2.hash,
                "is_esilink": False,
                "esi_fleet_id": None,
                "is_registered_on_esi": False,
                "actions": (
                    '<a class="btn btn-info btn-sm m-1" '
                    f'href="{edit_url_2}"><span '
                    'class="fa-solid fa-eye"></span></a><a class="btn btn-danger '
                    'btn-sm" data-bs-toggle="modal" '
                    'data-bs-target="#deleteFatLinkModal" '
                    f'data-url="{delete_url_2}" '
                    'data-confirm-text="Delete" data-body-text="<p>Are you sure you '
                    'want to delete FAT link April Fleet 2?</p>"><i class="fa-solid '
                    'fa-trash-can fa-fw"></i></a>'
                ),
                "via_esi": "No",
            },
        )

    def test_helper_convert_fats_to_dict(self):
        # given
        self.client.force_login(user=self.user_with_manage_afat)
        request = self.factory.get(path=reverse(viewname="afat:dashboard"))
        request.user = self.user_with_manage_afat

        fatlink_hash = get_hash_on_save()
        fatlink_created = FatLink.objects.create(
            created=timezone.now(),
            fleet="April Fleet 1",
            creator=self.user_with_manage_afat,
            character=self.character_1001,
            hash=fatlink_hash,
            is_esilink=True,
            is_registered_on_esi=True,
            esi_fleet_id="3726458287",
            fleet_type="CTA",
            doctrine="Ships",
        )
        fat = Fat.objects.create(
            character=self.character_1101, fatlink=fatlink_created, shiptype="Omen"
        )

        # when
        result = convert_fats_to_dict(request=request, fat=fat)

        esi_marker = '<span class="badge text-bg-success afat-label ms-2">ESI</span>'
        fleet_time = fat.fatlink.created
        fleet_time_timestamp = fleet_time.timestamp()

        button_delete_fat = reverse(
            viewname="afat:fatlinks_delete_fat", args=[fat.fatlink.hash, fat.id]
        )
        button_delete_text = "Delete"
        modal_body_text = (
            "<p>Are you sure you want to remove "
            f"{fat.character.character_name} from this FAT link?</p>"
        )

        self.maxDiff = None
        # then
        self.assertDictEqual(
            d1=result,
            d2={
                "system": fat.system,
                "ship_type": fat.shiptype,
                "character_name": fat.character.character_name,
                "doctrine": "Ships",
                "fleet_name": fat.fatlink.fleet + esi_marker,
                "fleet_time": {"time": fleet_time, "timestamp": fleet_time_timestamp},
                "fleet_type": "CTA",
                "via_esi": "Yes",
                "actions": (
                    '<a class="btn btn-danger btn-sm" data-bs-toggle="modal" '
                    'data-bs-target="#deleteFatModal" '
                    f'data-url="{button_delete_fat}" '
                    f'data-confirm-text="{button_delete_text}" '
                    f'data-body-text="{modal_body_text}">'
                    '<i class="fa-solid fa-trash-can fa-fw"></i></a>'
                ),
            },
        )

    def test_helper_convert_logs_to_dict(self):
        # given
        self.client.force_login(user=self.user_with_manage_afat)
        request = self.factory.get(path=reverse(viewname="afat:dashboard"))
        request.user = self.user_with_manage_afat

        fatlink_hash = get_hash_on_save()
        fatlink_created = FatLink.objects.create(
            created=timezone.now(),
            fleet="April Fleet 1",
            creator=self.user_with_manage_afat,
            character=self.character_1001,
            hash=fatlink_hash,
            is_esilink=True,
            is_registered_on_esi=True,
            esi_fleet_id="3726458287",
            fleet_type="CTA",
        )

        duration = Duration.objects.create(fleet=fatlink_created, duration=120)

        fleet_type = " (Fleet type: CTA)"

        write_log(
            request=request,
            log_event=Log.Event.CREATE_FATLINK,
            log_text=(
                f'FAT link with name "{fatlink_created.fleet}"{fleet_type} and '
                f"a duration of {duration.duration} minutes was created"
            ),
            fatlink_hash=fatlink_created.hash,
        )

        # when
        log = Log.objects.get(fatlink_hash=fatlink_hash)
        log_time = log.log_time
        log_time_timestamp = log_time.timestamp()
        user_main_character = get_main_character_from_user(user=log.user)
        fatlink_link = reverse(
            viewname="afat:fatlinks_details_fatlink", args=[log.fatlink_hash]
        )
        fatlink_html = f'<a href="{fatlink_link}">{log.fatlink_hash}</a>'

        result = convert_logs_to_dict(log=log, fatlink_exists=True)

        # then
        self.assertDictEqual(
            d1=result,
            d2={
                "log_time": {"time": log_time, "timestamp": log_time_timestamp},
                "log_event": Log.Event(log.log_event).label,
                "user": user_main_character,
                "fatlink": {"html": fatlink_html, "hash": log.fatlink_hash},
                "description": log.log_text,
            },
        )
