"""
Test fatlinks views
"""

# Standard Library
from http import HTTPStatus
from unittest.mock import ANY, MagicMock, patch

# Third Party
from pytz import utc

# Django
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils.datetime_safe import datetime

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from app_utils.testing import create_user_from_evecharacter

# Alliance Auth AFAT
from afat.models import Duration, Fat, FatLink, Log, get_hash_on_save
from afat.tests.fixtures.load_allianceauth import load_allianceauth
from afat.utils import get_main_character_from_user

MODULE_PATH = "afat.views.fatlinks"


class TestFatlinksView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()

        # given
        cls.character_1001 = EveCharacter.objects.get(character_id=1001)
        cls.character_1002 = EveCharacter.objects.get(character_id=1002)
        cls.character_1003 = EveCharacter.objects.get(character_id=1003)
        cls.character_1004 = EveCharacter.objects.get(character_id=1004)
        cls.character_1005 = EveCharacter.objects.get(character_id=1005)
        cls.character_1101 = EveCharacter.objects.get(character_id=1101)

        cls.user_without_access, _ = create_user_from_evecharacter(
            character_id=cls.character_1001.character_id
        )

        cls.user_with_basic_access, _ = create_user_from_evecharacter(
            character_id=cls.character_1002.character_id,
            permissions=["afat.basic_access"],
        )

        cls.user_with_manage_afat, _ = create_user_from_evecharacter(
            character_id=cls.character_1003.character_id,
            permissions=["afat.basic_access", "afat.manage_afat"],
        )

        cls.user_with_add_fatlink, _ = create_user_from_evecharacter(
            character_id=cls.character_1004.character_id,
            permissions=["afat.basic_access", "afat.add_fatlink"],
        )

        # Generate some FAT links and FATs
        cls.afat_link_april_1 = FatLink.objects.create(
            fleet="April Fleet 1",
            hash="1231",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            created=datetime(year=2020, month=4, day=1, tzinfo=utc),
        )
        cls.afat_link_april_2 = FatLink.objects.create(
            fleet="April Fleet 2",
            hash="1232",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            created=datetime(year=2020, month=4, day=15, tzinfo=utc),
        )
        cls.afat_link_september = FatLink.objects.create(
            fleet="September Fleet",
            hash="1233",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            created=datetime(year=2020, month=9, day=1, tzinfo=utc),
        )
        cls.afat_link_september_no_fats = FatLink.objects.create(
            fleet="September Fleet 2",
            hash="1234",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            created=datetime(year=2020, month=9, day=1, tzinfo=utc),
        )

        Fat.objects.create(
            character=cls.character_1101,
            fatlink=cls.afat_link_april_1,
            shiptype="Omen",
        )
        Fat.objects.create(
            character=cls.character_1001,
            fatlink=cls.afat_link_april_1,
            shiptype="Omen",
        )
        Fat.objects.create(
            character=cls.character_1002,
            fatlink=cls.afat_link_april_1,
            shiptype="Omen",
        )
        Fat.objects.create(
            character=cls.character_1003,
            fatlink=cls.afat_link_april_1,
            shiptype="Omen",
        )
        Fat.objects.create(
            character=cls.character_1004,
            fatlink=cls.afat_link_april_1,
            shiptype="Omen",
        )
        Fat.objects.create(
            character=cls.character_1005,
            fatlink=cls.afat_link_april_1,
            shiptype="Omen",
        )

        Fat.objects.create(
            character=cls.character_1001,
            fatlink=cls.afat_link_april_2,
            shiptype="Omen",
        )
        Fat.objects.create(
            character=cls.character_1004,
            fatlink=cls.afat_link_april_2,
            shiptype="Thorax",
        )
        Fat.objects.create(
            character=cls.character_1002,
            fatlink=cls.afat_link_april_2,
            shiptype="Thorax",
        )
        Fat.objects.create(
            character=cls.character_1003,
            fatlink=cls.afat_link_april_2,
            shiptype="Omen",
        )

        Fat.objects.create(
            character=cls.character_1001,
            fatlink=cls.afat_link_september,
            shiptype="Omen",
        )
        Fat.objects.create(
            character=cls.character_1004,
            fatlink=cls.afat_link_september,
            shiptype="Guardian",
        )
        Fat.objects.create(
            character=cls.character_1002,
            fatlink=cls.afat_link_september,
            shiptype="Omen",
        )

    def test_should_show_fatlnks_overview(self):
        # given
        self.client.force_login(user=self.user_with_basic_access)

        # when
        url = reverse(viewname="afat:fatlinks_overview")
        res = self.client.get(path=url)

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_fatlnks_overview_with_year(self):
        # given
        self.client.force_login(user=self.user_with_basic_access)

        # when
        url = reverse(viewname="afat:fatlinks_overview", kwargs={"year": 2020})
        res = self.client.get(path=url)

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_add_fatlink_for_user_with_manage_afat(self):
        # given
        self.client.force_login(user=self.user_with_manage_afat)

        # when
        url = reverse(viewname="afat:fatlinks_add_fatlink")
        res = self.client.get(url)

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_add_fatlink_for_user_with_add_fatlinkt(self):
        # given
        self.client.force_login(user=self.user_with_add_fatlink)

        # when
        url = reverse(viewname="afat:fatlinks_add_fatlink")
        res = self.client.get(path=url)

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_fatlink_details_for_user_with_manage_afat(self):
        # given
        self.client.force_login(user=self.user_with_manage_afat)

        # when
        url = reverse(
            viewname="afat:fatlinks_details_fatlink",
            kwargs={"fatlink_hash": self.afat_link_april_1.hash},
        )
        res = self.client.get(path=url)

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_fatlink_details_for_user_with_add_fatlinkt(self):
        # given
        self.client.force_login(user=self.user_with_add_fatlink)

        # when
        url = reverse(
            viewname="afat:fatlinks_details_fatlink",
            kwargs={"fatlink_hash": self.afat_link_april_1.hash},
        )
        res = self.client.get(path=url)

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_not_show_fatlink_details_for_non_existing_fatlink(self):
        # given
        self.client.force_login(user=self.user_with_manage_afat)

        # when
        url = reverse(
            viewname="afat:fatlinks_details_fatlink",
            kwargs={"fatlink_hash": "foobarsson"},
        )
        res = self.client.get(path=url)

        # then
        self.assertNotEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

        messages = list(get_messages(request=res.wsgi_request))

        self.assertRaises(expected_exception=FatLink.DoesNotExist)
        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(
            first=str(messages[0]),
            second="<h4>Warning!</h4><p>The hash provided is not valid.</p>",
        )

    def test_ajax_get_fatlinks_by_year(self):
        # given
        self.maxDiff = None
        self.client.force_login(user=self.user_with_manage_afat)

        fatlink_hash = get_hash_on_save()
        fatlink_created = FatLink.objects.create(
            fleet="April Fleet 1",
            creator=self.user_with_manage_afat,
            character=self.character_1001,
            hash=fatlink_hash,
            is_esilink=True,
            is_registered_on_esi=True,
            esi_fleet_id=3726458287,
            fleet_type="CTA",
            doctrine="Ships",
            created="2021-11-05T13:19:49.676Z",
        )

        Duration.objects.create(fleet=fatlink_created, duration=120)

        # when
        fatlink = (
            FatLink.objects.select_related_default()
            .annotate_fats_count()
            .get(hash=fatlink_hash)
        )

        url_with_year = reverse(
            viewname="afat:fatlinks_ajax_get_fatlinks_by_year",
            kwargs={"year": 2021},
        )
        result = self.client.get(path=url_with_year)

        # then
        self.assertEqual(first=result.status_code, second=HTTPStatus.OK)

        creator_main_character = get_main_character_from_user(user=fatlink.creator)
        fleet_time = fatlink.created
        fleet_time_timestamp = fleet_time.timestamp()
        esi_marker = '<span class="badge text-bg-success afat-label ms-2">ESI</span>'

        close_esi_tracking_url = reverse(
            viewname="afat:fatlinks_close_esi_fatlink", args=[fatlink_hash]
        )
        redirect_url = reverse(viewname="afat:fatlinks_overview")
        edit_url = reverse(
            viewname="afat:fatlinks_details_fatlink", args=[fatlink_hash]
        )
        delete_url = reverse(
            viewname="afat:fatlinks_delete_fatlink", args=[fatlink_hash]
        )

        self.assertJSONEqual(
            raw=str(result.content, encoding="utf8"),
            expected_data=[
                {
                    "pk": fatlink.pk,
                    "fleet_name": fatlink.fleet + esi_marker,
                    "creator_name": creator_main_character,
                    "fleet_type": "CTA",
                    "fleet_time": {
                        "time": "2021-11-05T13:19:49.676Z",
                        "timestamp": fleet_time_timestamp,
                    },
                    "fats_number": 0,
                    "hash": fatlink.hash,
                    "is_esilink": True,
                    "doctrine": "Ships",
                    "esi_fleet_id": fatlink.esi_fleet_id,
                    "is_registered_on_esi": True,
                    "actions": (
                        '<a class="btn btn-afat-action btn-primary btn-sm" '
                        'style="margin-left: 0.25rem;" title="Clicking here will stop '
                        "the automatic tracking through ESI for this fleet and close "
                        'the associated FAT link." data-bs-toggle="modal" '
                        'data-bs-target="#cancelEsiFleetModal" '
                        f'data-url="{close_esi_tracking_url}?next={redirect_url}" '
                        'data-body-text="<p>Are you sure you want to close ESI fleet '
                        'with ID 3726458287 from Bruce Wayne?</p>" '
                        'data-confirm-text="Stop tracking"><i class="fa-solid fa-times">'
                        '</i></a><a class="btn btn-info btn-sm m-1" '
                        f'href="{edit_url}">'
                        '<span class="fa-solid fa-eye"></span></a>'
                        '<a class="btn btn-danger btn-sm" data-bs-toggle="modal" '
                        'data-bs-target="#deleteFatLinkModal" '
                        f'data-url="{delete_url}" '
                        'data-confirm-text="Delete" '
                        'data-body-text="<p>Are you sure you want to delete FAT '
                        'link April Fleet 1?</p>">'
                        '<i class="fa-solid fa-trash-can fa-fw"></i></a>'
                    ),
                    # "actions": "",
                    "via_esi": "Yes",
                }
            ],
        )

    @patch("afat.views.fatlinks.Duration.objects.get")
    @patch("afat.views.fatlinks.Setting.get_setting")
    @patch("afat.views.fatlinks.write_log")
    def test_reopens_fatlink_successfully(
        self, mock_write_log, mock_get_setting, mock_duration_get
    ):
        mock_duration = MagicMock()
        mock_duration.fleet.reopened = False
        mock_duration.fleet.created = datetime(2023, 1, 1, 12, 0, 0)
        mock_duration.fleet.hash = "test_hash"
        mock_get_setting.return_value = 60
        mock_duration_get.return_value = mock_duration

        self.client.force_login(self.user_with_manage_afat)
        response = self.client.get(
            reverse("afat:fatlinks_reopen_fatlink", args=["test_hash"])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse(
                "afat:fatlinks_details_fatlink", kwargs={"fatlink_hash": "test_hash"}
            ),
            target_status_code=HTTPStatus.FOUND,
        )
        mock_duration.save.assert_called_once()
        mock_write_log.assert_called_once()

    @patch("afat.views.fatlinks.Duration.objects.get")
    def test_shows_error_when_fatlink_does_not_exist(self, mock_duration_get):
        mock_duration_get.side_effect = Duration.DoesNotExist

        self.client.force_login(self.user_with_manage_afat)
        response = self.client.get(
            reverse("afat:fatlinks_reopen_fatlink", args=["invalid_hash"])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("afat:dashboard"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "The hash you provided does not match with any FAT link." in str(m)
                for m in messages
            )
        )

    @patch("afat.views.fatlinks.Duration.objects.get")
    def test_shows_warning_when_fatlink_already_reopened(self, mock_duration_get):
        mock_duration = MagicMock()
        mock_duration.fleet.reopened = True
        mock_duration_get.return_value = mock_duration

        self.client.force_login(self.user_with_manage_afat)
        response = self.client.post(
            reverse("afat:fatlinks_reopen_fatlink", args=["test_hash"])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse(
                "afat:fatlinks_details_fatlink",
                kwargs={"fatlink_hash": "test_hash"},
            ),
            target_status_code=HTTPStatus.FOUND,
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("This FAT link has already been re-opened." in str(m) for m in messages)
        )

    @patch("afat.views.fatlinks.FatLink.objects.get")
    def test_closes_esi_fatlink_successfully(self, mock_get_fatlink):
        mock_fatlink = MagicMock()
        mock_get_fatlink.return_value = mock_fatlink

        self.client.force_login(self.user_with_manage_afat)
        response = self.client.get(
            reverse("afat:fatlinks_close_esi_fatlink", args=["test_hash"])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("afat:dashboard"))
        mock_fatlink.save.assert_called_once()
        self.assertFalse(mock_fatlink.is_registered_on_esi)

    @patch("afat.views.fatlinks.FatLink.objects.get")
    def test_handles_nonexistent_fatlink_gracefully(self, mock_get_fatlink):
        mock_get_fatlink.side_effect = FatLink.DoesNotExist

        self.client.force_login(self.user_with_manage_afat)
        response = self.client.get(
            reverse("afat:fatlinks_close_esi_fatlink", args=["nonexistent_hash"])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("afat:dashboard"))

    @patch("afat.views.fatlinks.FatLink.objects.get")
    @patch("afat.views.fatlinks.Fat.objects.get")
    @patch("afat.views.fatlinks.write_log")
    def test_deletes_fat_successfully(
        self, mock_write_log, mock_get_fat, mock_get_fatlink
    ):
        mock_fatlink = MagicMock(hash="test_hash")
        mock_fat = MagicMock(character=MagicMock(character_name="Test Character"))
        mock_get_fatlink.return_value = mock_fatlink
        mock_get_fat.return_value = mock_fat

        self.client.force_login(self.user_with_manage_afat)
        response = self.client.get(
            reverse("afat:fatlinks_delete_fat", args=["test_hash", 1])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse("afat:fatlinks_details_fatlink", args=["test_hash"]),
            target_status_code=HTTPStatus.FOUND,
        )
        mock_fat.delete.assert_called_once()
        mock_write_log.assert_called_once_with(
            request=ANY,
            log_event=Log.Event.DELETE_FAT,
            log_text="The FAT for Test Character has been deleted",
            fatlink_hash="test_hash",
        )

    @patch("afat.views.fatlinks.FatLink.objects.get")
    def test_handles_delete_fat_with_nonexistent_fatlink_gracefully(
        self, mock_get_fatlink
    ):
        mock_get_fatlink.side_effect = FatLink.DoesNotExist

        self.client.force_login(self.user_with_manage_afat)
        response = self.client.get(
            reverse("afat:fatlinks_delete_fat", args=["invalid_hash", 1])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("afat:dashboard"))

    @patch("afat.views.fatlinks.FatLink.objects.get")
    @patch("afat.views.fatlinks.Fat.objects.get")
    def test_handles_nonexistent_fat_gracefully(self, mock_get_fat, mock_get_fatlink):
        mock_fatlink = MagicMock(hash="test_hash")
        mock_get_fatlink.return_value = mock_fatlink
        mock_get_fat.side_effect = Fat.DoesNotExist

        self.client.force_login(self.user_with_manage_afat)
        response = self.client.get(
            reverse("afat:fatlinks_delete_fat", args=["test_hash", 999])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("afat:dashboard"))

    @patch("afat.views.fatlinks.FatLink.objects.get")
    @patch("afat.views.fatlinks.Fat.objects.filter")
    @patch("afat.views.fatlinks.write_log")
    def test_deletes_fatlink_and_associated_fats_successfully(
        self, mock_write_log, mock_fat_filter, mock_fatlink_get
    ):
        mock_fatlink = MagicMock(hash="test_hash", pk=1)
        mock_fat_filter.return_value = MagicMock(delete=MagicMock())
        mock_fatlink_get.return_value = mock_fatlink

        self.client.force_login(self.user_with_manage_afat)
        response = self.client.get(
            reverse("afat:fatlinks_delete_fatlink", args=["test_hash"])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("afat:fatlinks_overview"))
        mock_fat_filter.assert_called_once_with(fatlink_id=mock_fatlink.pk)
        mock_fat_filter.return_value.delete.assert_called_once()
        mock_fatlink.delete.assert_called_once()
        mock_write_log.assert_called_once_with(
            ANY,  # Allow any request object
            log_event=Log.Event.DELETE_FATLINK,
            log_text="FAT link deleted.",
            fatlink_hash="test_hash",
        )

    @patch("afat.views.fatlinks.FatLink.objects.get")
    def test_handles_delete_fatlink_with_nonexistent_fatlink_gracefully(
        self, mock_fatlink_get
    ):
        mock_fatlink_get.side_effect = FatLink.DoesNotExist

        self.client.force_login(self.user_with_manage_afat)
        response = self.client.get(
            reverse("afat:fatlinks_delete_fatlink", args=["invalid_hash"])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("afat:dashboard"))

    @patch("afat.views.fatlinks.Fat.objects.select_related_default")
    @patch("afat.views.fatlinks.convert_fats_to_dict")
    def test_returns_fats_for_valid_fatlink_hash(
        self, mock_convert_fats_to_dict, mock_select_related_default
    ):
        # Create a mock Fat object with realistic attributes
        class MockFat:
            id = 1
            shiptype = "Omen"
            system = "Jita"

            class Character:
                character_name = "Test Character"

            character = Character()

            class FatLink:
                is_esilink = True
                is_registered_on_esi = True
                hash = "test_hash"
                created = datetime(2020, 4, 1, tzinfo=utc)
                fleet = "Test Fleet"
                doctrine = "Test Doctrine"
                fleet_type = "Test Fleet Type"

            fatlink = FatLink()

        mock_fat = MockFat()

        # Mock the queryset returned by select_related_default
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = [mock_fat]
        mock_select_related_default.return_value = mock_queryset

        # Mock the convert_fats_to_dict function to return a JSON-serializable dictionary
        mock_convert_fats_to_dict.return_value = {
            "id": mock_fat.id,
            "character": mock_fat.character.character_name,
            "shiptype": mock_fat.shiptype,
        }

        self.client.force_login(self.user_with_manage_afat)
        response = self.client.get(
            reverse("afat:fatlinks_ajax_get_fats_by_fatlink", args=["1231"])
        )

        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_select_related_default.return_value.filter.assert_called_once_with(
            fatlink__hash="1231"
        )
        mock_convert_fats_to_dict.assert_called_once_with(request=ANY, fat=mock_fat)
        self.assertEqual(
            response.json(),
            [{"id": 1, "character": "Test Character", "shiptype": "Omen"}],
        )

    @patch("afat.views.fatlinks.Duration.objects.get")
    @patch("afat.views.fatlinks.FatLink.objects.select_related_default")
    def test_redirects_to_dashboard_when_invalid_hash_provided(
        self, mock_select_related_default, mock_duration_get
    ):
        mock_select_related_default.return_value.get.side_effect = FatLink.DoesNotExist

        self.client.force_login(self.user_with_manage_afat)
        response = self.client.get(
            reverse("afat:fatlinks_details_fatlink", args=["invalid_hash"])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("afat:dashboard"))
