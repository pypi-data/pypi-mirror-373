"""
Test models
"""

# Standard Library
from unittest.mock import Mock, patch

# Third Party
from requests.exceptions import HTTPError

# Django
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

# AA Discord Announcements
from aa_discord_announcements.models import (
    General,
    PingTarget,
    Webhook,
    _get_discord_group_info,
)


class TestGetDiscordGroupInfo(TestCase):
    """
    Test _get_discord_group_info function
    """

    @patch(
        "aa_discord_announcements.models.discord_service_installed", return_value=True
    )
    @patch("aa_discord_announcements.models.DiscordUser.objects.group_to_role")
    def test_returns_discord_group_info(
        self, mock_group_to_role, mock_discord_service_installed
    ):
        """
        Test if _get_discord_group_info returns the correct Discord group info

        :param mock_group_to_role:
        :type mock_group_to_role:
        :param mock_discord_service_installed:
        :type mock_discord_service_installed:
        :return:
        :rtype:
        """

        mock_group = Mock(spec=Group)
        mock_group_to_role.return_value = {"id": "123456789"}
        result = _get_discord_group_info(mock_group)

        self.assertEqual(result, {"id": "123456789"})

    @patch(
        "aa_discord_announcements.models.discord_service_installed", return_value=False
    )
    def test_raises_error_if_discord_service_not_installed(
        self, mock_discord_service_installed
    ):
        """
        Test if _get_discord_group_info raises a ValidationError if the Discord service is not installed

        :param mock_discord_service_installed:
        :type mock_discord_service_installed:
        :return:
        :rtype:
        """

        mock_group = Mock(spec=Group)

        with self.assertRaises(ValidationError):
            _get_discord_group_info(mock_group)

    @patch(
        "aa_discord_announcements.models.discord_service_installed", return_value=True
    )
    @patch(
        "aa_discord_announcements.models.DiscordUser.objects.group_to_role",
        side_effect=HTTPError,
    )
    def test_raises_error_if_http_error_occurs(
        self, mock_group_to_role, mock_discord_service_installed
    ):
        """
        Test if _get_discord_group_info raises a ValidationError if an HTTPError occurs

        :param mock_group_to_role:
        :type mock_group_to_role:
        :param mock_discord_service_installed:
        :type mock_discord_service_installed:
        :return:
        :rtype:
        """

        mock_group = Mock(spec=Group)

        with self.assertRaises(ValidationError):
            _get_discord_group_info(mock_group)

    @patch(
        "aa_discord_announcements.models.discord_service_installed", return_value=True
    )
    @patch(
        "aa_discord_announcements.models.DiscordUser.objects.group_to_role",
        return_value=None,
    )
    def test_raises_error_if_group_not_synced(
        self, mock_group_to_role, mock_discord_service_installed
    ):
        """
        Test if _get_discord_group_info raises a ValidationError if the group is not synced to Discord

        :param mock_group_to_role:
        :type mock_group_to_role:
        :param mock_discord_service_installed:
        :type mock_discord_service_installed:
        :return:
        :rtype:
        """

        mock_group = Mock(spec=Group)

        with self.assertRaises(ValidationError):
            _get_discord_group_info(mock_group)


class TestGeneralModel(TestCase):
    """
    Test General model
    """

    def test_can_access_app_permission(self):
        """
        Test if the permission 'basic_access' is in the permissions tuple

        :return:
        :rtype:
        """

        general = General()

        self.assertIn("basic_access", dict(general._meta.permissions))

    def test_is_not_managed(self):
        """
        Test if the model is not managed by Django

        :return:
        :rtype:
        """

        general = General()

        self.assertFalse(general._meta.managed)

    def test_has_no_default_permissions(self):
        """
        Test if the model has no default permissions

        :return:
        :rtype:
        """

        general = General()

        self.assertEqual(general._meta.default_permissions, ())


class TestPingTargetModel(TestCase):
    """
    Test the PingTarget model
    """

    @patch(
        "aa_discord_announcements.models.discord_service_installed", return_value=True
    )
    @patch("aa_discord_announcements.models._get_discord_group_info")
    def test_saves_with_valid_discord_group(
        self, mock_get_discord_group_info, mock_discord_service_installed
    ):
        """
        Test if the PingTarget model saves with a valid Discord group

        :param mock_get_discord_group_info:
        :type mock_get_discord_group_info:
        :param mock_discord_service_installed:
        :type mock_discord_service_installed:
        :return:
        :rtype:
        """

        mock_get_discord_group_info.return_value = {"id": "123456789"}
        group = Group.objects.create(name="Test Group")
        ping_target = PingTarget(name=group)
        ping_target.save()

        self.assertEqual(ping_target.discord_id, "123456789")

    @patch(
        "aa_discord_announcements.models.discord_service_installed", return_value=False
    )
    def test_raises_error_if_discord_service_not_installed_on_save(
        self, mock_discord_service_installed
    ):
        """
        Test if the PingTarget model raises a ValidationError if the Discord service is not installed

        :param mock_discord_service_installed:
        :type mock_discord_service_installed:
        :return:
        :rtype:
        """

        group = Group.objects.create(name="Test Group")
        ping_target = PingTarget(name=group)

        with self.assertRaises(ValidationError):
            ping_target.save()

    @patch(
        "aa_discord_announcements.models.discord_service_installed", return_value=True
    )
    @patch(
        "aa_discord_announcements.models._get_discord_group_info",
        side_effect=ValidationError("This group has not been synced to Discord yet."),
    )
    def test_raises_error_if_discord_group_not_synced_on_save(
        self, mock_get_discord_group_info, mock_discord_service_installed
    ):
        """
        Test if the PingTarget model raises a ValidationError if the Discord group is not synced

        :param mock_get_discord_group_info:
        :type mock_get_discord_group_info:
        :param mock_discord_service_installed:
        :type mock_discord_service_installed:
        :return:
        :rtype:
        """

        group = Group.objects.create(name="Test Group")
        ping_target = PingTarget(name=group)
        with self.assertRaises(ValidationError):
            ping_target.save()

    @patch(
        "aa_discord_announcements.models.discord_service_installed", return_value=True
    )
    @patch("aa_discord_announcements.models._get_discord_group_info")
    def test_cleans_with_valid_discord_group(
        self, mock_get_discord_group_info, mock_discord_service_installed
    ):
        """
        Test if the PingTarget model cleans with a valid Discord group

        :param mock_get_discord_group_info:
        :type mock_get_discord_group_info:
        :param mock_discord_service_installed:
        :type mock_discord_service_installed:
        :return:
        :rtype:
        """

        mock_get_discord_group_info.return_value = {"id": "123456789"}
        group = Group.objects.create(name="Test Group")
        ping_target = PingTarget(name=group)
        ping_target.clean()

    @patch(
        "aa_discord_announcements.models.discord_service_installed", return_value=False
    )
    def test_raises_error_if_discord_service_not_installed_on_clean(
        self, mock_discord_service_installed
    ):
        """
        Test if the PingTarget model raises a ValidationError if the Discord service is not installed when cleaning the model

        :param mock_discord_service_installed:
        :type mock_discord_service_installed:
        :return:
        :rtype:
        """

        group = Group.objects.create(name="Test Group")
        ping_target = PingTarget(name=group)

        with self.assertRaises(ValidationError):
            ping_target.clean()

    @patch(
        "aa_discord_announcements.models.discord_service_installed", return_value=True
    )
    @patch(
        "aa_discord_announcements.models._get_discord_group_info",
        side_effect=ValidationError("This group has not been synced to Discord yet."),
    )
    def test_raises_error_if_discord_group_not_synced_on_clean(
        self, mock_get_discord_group_info, mock_discord_service_installed
    ):
        """
        Test if the PingTarget model raises a ValidationError if the Discord group is not synced when cleaning the model

        :param mock_get_discord_group_info:
        :type mock_get_discord_group_info:
        :param mock_discord_service_installed:
        :type mock_discord_service_installed:
        :return:
        :rtype:
        """

        group = Group.objects.create(name="Test Group")
        ping_target = PingTarget(name=group)

        with self.assertRaises(ValidationError):
            ping_target.clean()

    def test_should_return_ping_target_model_string_name(self):
        """
        Test should return the PingTarget model string name

        :return:
        :rtype:
        """

        group = Group.objects.create(name="Test Group")
        ping_target = PingTarget(name=group)

        self.assertEqual(first=str(ping_target), second=group.name)


class TestWebhookModel(TestCase):
    """
    Test the Webhook model
    """

    def test_saves_with_valid_data(self):
        """
        Test if the Webhook model saves with valid data

        :return:
        :rtype:
        """

        webhook = Webhook.objects.create(
            name="Test Channel", url="https://discord.com/api/webhooks/123456/abcdef"
        )
        self.assertEqual(webhook.name, "Test Channel")
        self.assertEqual(webhook.url, "https://discord.com/api/webhooks/123456/abcdef")

    def test_raises_error_with_invalid_url(self):
        """
        Test if the Webhook model raises a ValidationError with an invalid URL

        :return:
        :rtype:
        """

        webhook = Webhook(name="Test Channel", url="invalid_url")

        with self.assertRaises(ValidationError):
            webhook.clean()

    def test_cleans_with_valid_url(self):
        """
        Test if the Webhook model cleans with a valid URL

        :return:
        :rtype:
        """

        webhook = Webhook(
            name="Test Channel", url="https://discord.com/api/webhooks/123456/abcdef"
        )
        webhook.clean()

        self.assertEqual(webhook.url, "https://discord.com/api/webhooks/123456/abcdef")

    def test_webhook_url_is_unique(self):
        """
        Test if the Webhook model raises an IntegrityError if the URL is not unique

        :return:
        :rtype:
        """

        Webhook.objects.create(
            name="Test Channel 1",
            url="https://discord.com/api/webhooks/123456/abcdef",
        )

        with self.assertRaises(IntegrityError):
            Webhook.objects.create(
                name="Test Channel 2",
                url="https://discord.com/api/webhooks/123456/abcdef",
            )

    def test_saves_with_restricted_groups(self):
        """
        Test if the Webhook model saves with restricted groups

        :return:
        :rtype:
        """

        group = Group.objects.create(name="Test Group")
        webhook = Webhook.objects.create(
            name="Test Channel", url="https://discord.com/api/webhooks/123456/abcdef"
        )
        webhook.restricted_to_group.add(group)

        self.assertIn(group, webhook.restricted_to_group.all())

    def test_saves_with_notes(self):
        """
        Test if the Webhook model saves with notes

        :return:
        :rtype:
        """

        webhook = Webhook.objects.create(
            name="Test Channel",
            url="https://discord.com/api/webhooks/123456/abcdef",
            notes="Test notes",
        )

        self.assertEqual(webhook.notes, "Test notes")

    def test_saves_with_is_enabled(self):
        """
        Test if the Webhook model saves with is_enabled

        :return:
        :rtype:
        """

        webhook = Webhook.objects.create(
            name="Test Channel",
            url="https://discord.com/api/webhooks/123456/abcdef",
            is_enabled=False,
        )

        self.assertFalse(webhook.is_enabled)

    def test_should_return_webhook_model_string_name(self):
        """
        Test should return the Webhook model string name

        :return:
        :rtype:
        """

        webhook = Webhook(
            name="Test Channel",
            url="https://discord.com/api/webhooks/123456/abcdef",
        )

        webhook.save()

        self.assertEqual(first=str(webhook), second="Test Channel")
