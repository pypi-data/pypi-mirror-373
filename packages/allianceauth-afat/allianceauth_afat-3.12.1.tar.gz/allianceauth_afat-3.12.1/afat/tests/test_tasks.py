"""
Test cases for the task in the afat module.
"""

# Standard Library
import unittest
from datetime import timedelta
from unittest.mock import ANY, MagicMock, patch

# Third Party
import kombu

# Django
from django.utils.datetime_safe import datetime

# Alliance Auth (External Libs)
from app_utils.esi import EsiStatus

# Alliance Auth AFAT
from afat.models import FatLink
from afat.tasks import (
    _close_esi_fleet,
    _esi_fatlinks_error_handling,
    _process_esi_fatlink,
    logrotate,
    process_fats,
    update_esi_fatlinks,
)


class TestLogrotateTask(unittest.TestCase):
    """
    Test cases for the logrotate task.
    """

    @patch("afat.tasks.Setting.get_setting")
    @patch("afat.tasks.Log.objects.filter")
    def test_logrotate_removes_old_logs(self, mock_filter, mock_get_setting):
        """
        Test that the logrotate task removes logs older than the specified duration.

        :param mock_filter:
        :type mock_filter:
        :param mock_get_setting:
        :type mock_get_setting:
        :return:
        :rtype:
        """

        mock_get_setting.return_value = 30
        mock_filter.return_value.delete.return_value = None

        logrotate()

        mock_filter.assert_called_once_with(log_time__lte=ANY)
        mock_filter.return_value.delete.assert_called_once()

    @patch("afat.tasks.Setting.get_setting")
    @patch("afat.tasks.Log.objects.filter")
    def test_logrotate_handles_no_old_logs(self, mock_filter, mock_get_setting):
        """
        Test that the logrotate task handles the case where there are no old logs.

        :param mock_filter:
        :type mock_filter:
        :param mock_get_setting:
        :type mock_get_setting:
        :return:
        :rtype:
        """

        mock_get_setting.return_value = 30
        mock_filter.return_value.delete.return_value = None

        logrotate()

        mock_filter.assert_called_once_with(log_time__lte=ANY)
        mock_filter.return_value.delete.assert_called_once()


class UpdateEsiFatlinksTests(unittest.TestCase):
    """
    Test cases for the update_esi_fatlinks task.
    """

    @patch("afat.tasks.fetch_esi_status")
    @patch("afat.tasks.logger")
    def test_checking_esi_fat_links_when_esi_is_offline(
        self, mock_logger, mock_fetch_esi_status
    ):
        """
        Test that the update_esi_fatlinks task handles the case when ESI is offline.

        :param mock_logger:
        :type mock_logger:
        :param mock_fetch_esi_status:
        :type mock_fetch_esi_status:
        :return:
        :rtype:
        """

        mock_fetch_esi_status.return_value = EsiStatus(is_online=False)
        update_esi_fatlinks()
        mock_logger.warning.assert_called_once_with(
            "ESI doesn't seem to be available at this time. Aborting."
        )

    @patch("afat.tasks.fetch_esi_status")
    @patch("afat.tasks.FatLink.objects.select_related_default")
    @patch("afat.tasks.logger")
    def test_checking_esi_fat_links_when_no_fatlinks(
        self, mock_logger, mock_fatlink_queryset, mock_fetch_esi_status
    ):
        """
        Test that the update_esi_fatlinks task handles the case when there are no ESI FAT links.

        :param mock_logger:
        :type mock_logger:
        :param mock_fatlink_queryset:
        :type mock_fatlink_queryset:
        :param mock_fetch_esi_status:
        :type mock_fetch_esi_status:
        :return:
        :rtype:
        """

        mock_fetch_esi_status.return_value = EsiStatus(is_online=True)
        mock_fatlink_queryset.return_value.filter.return_value.distinct.return_value = (
            []
        )
        update_esi_fatlinks()
        mock_logger.debug.assert_any_call(msg="Found 0 ESI FAT links to process")

    @patch("afat.tasks.fetch_esi_status")
    @patch("afat.tasks.FatLink.objects.select_related_default")
    @patch("afat.tasks.logger")
    @patch("afat.tasks._process_esi_fatlink")
    def test_checking_esi_fat_links_when_fatlinks_exist(
        self,
        mock_process_esi_fatlink,
        mock_logger,
        mock_fatlink_queryset,
        mock_fetch_esi_status,
    ):
        """
        Test that the update_esi_fatlinks task handles the case when there are ESI FAT links.

        :param mock_process_esi_fatlink:
        :type mock_process_esi_fatlink:
        :param mock_logger:
        :type mock_logger:
        :param mock_fatlink_queryset:
        :type mock_fatlink_queryset:
        :param mock_fetch_esi_status:
        :type mock_fetch_esi_status:
        :return:
        :rtype:
        """

        mock_fetch_esi_status.return_value = EsiStatus(is_online=True)
        mock_fatlink_queryset.return_value.filter.return_value.distinct.return_value = [
            MagicMock()
        ]
        update_esi_fatlinks()
        mock_process_esi_fatlink.assert_called_once()
        mock_logger.debug.assert_any_call(msg="Found 1 ESI FAT links to process")


class ProcessEsiFatlinkTests(unittest.TestCase):
    """
    Test cases for the _process_esi_fatlink function.
    """

    @patch("afat.tasks.logger")
    @patch("afat.tasks._close_esi_fleet")
    def test_processing_esi_fatlink_when_no_creator(
        self, mock_close_esi_fleet, mock_logger
    ):
        """
        Test that the _process_esi_fatlink function handles the case when there is no creator.

        :param mock_close_esi_fleet:
        :type mock_close_esi_fleet:
        :param mock_logger:
        :type mock_logger:
        :return:
        :rtype:
        """

        fatlink = MagicMock()
        fatlink.creator.profile.main_character = None
        _process_esi_fatlink(fatlink)
        mock_close_esi_fleet.assert_called_once_with(
            fatlink=fatlink, reason="No FAT link creator available."
        )

    @patch("afat.tasks.logger")
    @patch("afat.tasks._check_for_esi_fleet")
    def test_processing_esi_fatlink_when_no_fleet(
        self, mock_check_for_esi_fleet, mock_logger
    ):
        """
        Test that the _process_esi_fatlink function handles the case when there is no fleet.

        :param mock_check_for_esi_fleet:
        :type mock_check_for_esi_fleet:
        :param mock_logger:
        :type mock_logger:
        :return:
        :rtype:
        """

        fatlink = MagicMock()
        fatlink.creator.profile.main_character = MagicMock()
        mock_check_for_esi_fleet.return_value = None
        _process_esi_fatlink(fatlink)
        mock_check_for_esi_fleet.assert_called_once_with(fatlink=fatlink)


class EsiFatlinksErrorHandlingTests(unittest.TestCase):
    """
    Test cases for the _esi_fatlinks_error_handling function.
    """

    @patch("afat.tasks.timezone.now")
    @patch("afat.tasks._close_esi_fleet")
    def test_handles_error_within_grace_period(self, mock_close_fleet, mock_now):
        """
        Test that the _esi_fatlinks_error_handling function handles the case when an error occurs within the grace period.

        :param mock_close_fleet:
        :type mock_close_fleet:
        :param mock_now:
        :type mock_now:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        error_key = MagicMock()
        error_key.label = "Test Error"
        now = datetime(2023, 10, 1, 12, 0, 0)
        mock_now.return_value = now
        fatlink.last_esi_error = error_key
        fatlink.last_esi_error_time = now - timedelta(seconds=30)
        fatlink.esi_error_count = 3

        _esi_fatlinks_error_handling(error_key, fatlink)

        mock_close_fleet.assert_called_once_with(
            fatlink=fatlink, reason=error_key.label
        )
        fatlink.save.assert_not_called()

    @patch("afat.tasks.timezone.now")
    def test_increments_error_count(self, mock_now):
        """
        Test that the _esi_fatlinks_error_handling function increments the error count.

        :param mock_now:
        :type mock_now:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        error_key = MagicMock()
        error_key.label = "Test Error"
        now = datetime(2023, 10, 1, 12, 0, 0)
        mock_now.return_value = now
        fatlink.last_esi_error = error_key
        fatlink.last_esi_error_time = now - timedelta(seconds=30)
        fatlink.esi_error_count = 2

        _esi_fatlinks_error_handling(error_key, fatlink)

        self.assertEqual(fatlink.esi_error_count, 3)
        fatlink.save.assert_called_once()

    @patch("afat.tasks.timezone.now")
    def test_resets_error_count_after_grace_period(self, mock_now):
        """
        Test that the _esi_fatlinks_error_handling function resets the error count after the grace period.

        :param mock_now:
        :type mock_now:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        error_key = MagicMock()
        error_key.label = "Test Error"
        now = datetime(2023, 10, 1, 12, 0, 0)
        mock_now.return_value = now
        fatlink.last_esi_error = error_key
        fatlink.last_esi_error_time = now - timedelta(seconds=100)
        fatlink.esi_error_count = 2

        _esi_fatlinks_error_handling(error_key, fatlink)

        self.assertEqual(fatlink.esi_error_count, 1)
        fatlink.save.assert_called_once()

    @patch("afat.tasks.timezone.now")
    def test_handles_new_error(self, mock_now):
        """
        Test that the _esi_fatlinks_error_handling function handles a new error.

        :param mock_now:
        :type mock_now:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        error_key = MagicMock()
        error_key.label = "Test Error"
        now = datetime(2023, 10, 1, 12, 0, 0)
        mock_now.return_value = now
        fatlink.last_esi_error = None
        fatlink.last_esi_error_time = None
        fatlink.esi_error_count = 0

        _esi_fatlinks_error_handling(error_key, fatlink)

        self.assertEqual(fatlink.esi_error_count, 1)
        self.assertEqual(fatlink.last_esi_error, error_key)
        self.assertEqual(fatlink.last_esi_error_time, mock_now.return_value)
        fatlink.save.assert_called_once()


class CloseEsiFleetTests(unittest.TestCase):
    """
    Test cases for the _close_esi_fleet function.
    """

    @patch("afat.tasks.logger.info")
    def test_closes_fleet_successfully(self, mock_logger_info):
        """
        Test that the _close_esi_fleet function closes the fleet successfully.

        :param mock_logger_info:
        :type mock_logger_info:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        fatlink.hash = "test_hash"

        _close_esi_fleet(fatlink=fatlink, reason="Test Reason")

        fatlink.is_registered_on_esi = False
        fatlink.save.assert_called_once()
        mock_logger_info.assert_called_once_with(
            msg='Closing ESI FAT link with hash "test_hash". Reason: Test Reason'
        )

    @patch("afat.tasks.logger.info")
    def test_handles_empty_reason(self, mock_logger_info):
        """
        Test that the _close_esi_fleet function handles an empty reason.

        :param mock_logger_info:
        :type mock_logger_info:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        fatlink.hash = "test_hash"

        _close_esi_fleet(fatlink=fatlink, reason="")

        fatlink.is_registered_on_esi = False
        fatlink.save.assert_called_once()
        mock_logger_info.assert_called_once_with(
            msg='Closing ESI FAT link with hash "test_hash". Reason: '
        )

    @patch("afat.tasks.logger.info")
    def test_handles_none_reason(self, mock_logger_info):
        """
        Test that the _close_esi_fleet function handles a None reason.

        :param mock_logger_info:
        :type mock_logger_info:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        fatlink.hash = "test_hash"

        _close_esi_fleet(fatlink=fatlink, reason=None)

        fatlink.is_registered_on_esi = False
        fatlink.save.assert_called_once()
        mock_logger_info.assert_called_once_with(
            msg='Closing ESI FAT link with hash "test_hash". Reason: None'
        )


class ProcessFatsTests(unittest.TestCase):
    """
    Test cases for the process_fats function.
    """

    @patch("afat.tasks.process_character.si")
    @patch("afat.tasks.group")
    def test_processes_fat_link_data_from_esi(
        self, mock_group, mock_process_character_si
    ):
        """
        Test that the process_fats function processes FAT link data from ESI.

        :param mock_group:
        :type mock_group:
        :param mock_process_character_si:
        :type mock_process_character_si:
        :return:
        :rtype:
        """

        data_list = [
            {"character_id": 1, "solar_system_id": 100, "ship_type_id": 200},
            {"character_id": 2, "solar_system_id": 101, "ship_type_id": 201},
        ]
        fatlink_hash = "test_hash"
        mock_group.return_value.delay = MagicMock()

        process_fats(data_list, "esi", fatlink_hash)

        self.assertEqual(mock_process_character_si.call_count, 2)
        mock_group.assert_called_once()
        mock_group.return_value.delay.assert_called_once()

    @patch("afat.tasks.process_character.si")
    @patch("afat.tasks.group")
    def test_processes_fat_link_data_with_no_tasks(
        self, mock_group, mock_process_character_si
    ):
        """
        Test that the process_fats function handles the case when there are no tasks to process.

        :param mock_group:
        :type mock_group:
        :param mock_process_character_si:
        :type mock_process_character_si:
        :return:
        :rtype:
        """

        data_list = []
        fatlink_hash = "test_hash"

        process_fats(data_list, "esi", fatlink_hash)

        mock_process_character_si.assert_not_called()
        mock_group.assert_not_called()

    @patch("afat.tasks.process_character.si")
    @patch("afat.tasks.group")
    def test_handles_kombu_encode_error(self, mock_group, mock_process_character_si):
        data_list = [
            {"character_id": 1, "solar_system_id": 100, "ship_type_id": 200},
        ]
        fatlink_hash = "test_hash"
        mock_group.return_value.delay.side_effect = kombu.exceptions.EncodeError

        process_fats(data_list, "esi", fatlink_hash)

        self.assertEqual(mock_process_character_si.call_count, 1)
        mock_group.assert_called_once()
        mock_group.return_value.delay.assert_called_once()
