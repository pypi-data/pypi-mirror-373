# Standard Library
from unittest.mock import patch

# Django
from django.contrib import admin
from django.contrib.auth.models import Group
from django.test import TestCase

# AA Discord Announcements
from aa_discord_announcements.admin import PingTargetAdmin, WebhookAdmin
from aa_discord_announcements.models import PingTarget, Webhook


class TestPingTargetAdmin(TestCase):
    """
    Test the PingTargetAdmin class
    """

    @patch(
        "aa_discord_announcements.models._get_discord_group_info",
        return_value={"id": "123456789"},
    )
    def test_displays_correct_name(self, mock_get_discord_group_info):
        """
        Test that the name is displayed correctly in the admin

        :param mock_get_discord_group_info:
        :type mock_get_discord_group_info:
        :return:
        :rtype:
        """

        group = Group.objects.create(name="Test Group")
        ping_target = PingTarget.objects.create(name=group)
        admin_instance = PingTargetAdmin(PingTarget, admin.site)

        self.assertEqual(admin_instance._name(ping_target), "Test Group")

    @patch(
        "aa_discord_announcements.models._get_discord_group_info",
        return_value={"id": "123456789"},
    )
    def test_displays_correct_group_restrictions(self, mock_get_discord_group_info):
        """
        Test that the group restrictions are displayed correctly in the admin

        :return:
        :rtype:
        """

        group1 = Group.objects.create(name="Group 1")
        group2 = Group.objects.create(name="Group 2")
        ping_target = PingTarget.objects.create(name=group1)
        ping_target.restricted_to_group.add(group2)
        admin_instance = PingTargetAdmin(PingTarget, admin.site)

        self.assertEqual(admin_instance._restricted_to_group(ping_target), "Group 2")

    @patch(
        "aa_discord_announcements.models._get_discord_group_info",
        return_value={"id": "123456789"},
    )
    def test_displays_no_group_restrictions_when_none(
        self, mock_get_discord_group_info
    ):
        """
        Test that no group restrictions are displayed when there are none

        :return:
        :rtype:
        """

        group = Group.objects.create(name="Test Group")
        ping_target = PingTarget.objects.create(name=group)
        admin_instance = PingTargetAdmin(PingTarget, admin.site)

        self.assertIsNone(admin_instance._restricted_to_group(ping_target))


class TestWebhookAdmin(TestCase):
    """
    Test the WebhookAdmin class
    """

    @patch(
        "aa_discord_announcements.models._get_discord_group_info",
        return_value={"id": "123456789"},
    )
    def test_displays_correct_name(self, mock_get_discord_group_info):
        """
        Test that the name is displayed correctly in the admin

        :param mock_get_discord_group_info:
        :type mock_get_discord_group_info:
        :return:
        :rtype:
        """

        group = Group.objects.create(name="Test Group")
        webhook = Webhook.objects.create(
            name="Test Webhook", url="https://discord.com/api/webhooks/123456/abcdef"
        )
        webhook.restricted_to_group.set([group])
        admin_instance = WebhookAdmin(Webhook, admin.site)

        self.assertEqual(admin_instance._name(webhook), "Test Webhook")

    @patch(
        "aa_discord_announcements.models._get_discord_group_info",
        return_value={"id": "123456789"},
    )
    def test_displays_correct_url(self, mock_get_discord_group_info):
        """
        Test that the URL is displayed correctly in the admin

        :param mock_get_discord_group_info:
        :type mock_get_discord_group_info:
        :return:
        :rtype:
        """

        group = Group.objects.create(name="Test Group")
        webhook = Webhook.objects.create(
            name="Test Webhook", url="https://discord.com/api/webhooks/123456/abcdef"
        )
        webhook.restricted_to_group.set([group])
        admin_instance = WebhookAdmin(Webhook, admin.site)

        self.assertEqual(
            admin_instance._url(webhook),
            "https://discord.com/api/webhooks/123456/abcdef",
        )

    @patch(
        "aa_discord_announcements.models._get_discord_group_info",
        return_value={"id": "123456789"},
    )
    def test_displays_correct_group_restrictions(self, mock_get_discord_group_info):
        """
        Test that the group restrictions are displayed correctly in the admin

        :param mock_get_discord_group_info:
        :type mock_get_discord_group_info:
        :return:
        :rtype:
        """

        group1 = Group.objects.create(name="Group 1")
        group2 = Group.objects.create(name="Group 2")
        webhook = Webhook.objects.create(
            name="Test Webhook",
            url="https://discord.com/api/webhooks/123456/abcdef",
        )
        webhook.restricted_to_group.add(group1, group2)
        admin_instance = WebhookAdmin(Webhook, admin.site)

        self.assertEqual(
            admin_instance._restricted_to_group(webhook), "Group 1, Group 2"
        )

    @patch(
        "aa_discord_announcements.models._get_discord_group_info",
        return_value={"id": "123456789"},
    )
    def test_displays_no_group_restrictions_when_none(
        self, mock_get_discord_group_info
    ):
        """
        Test that no group restrictions are displayed when there are none

        :param mock_get_discord_group_info:
        :type mock_get_discord_group_info:
        :return:
        :rtype:
        """

        webhook = Webhook.objects.create(
            name="Test Webhook",
            url="https://discord.com/api/webhooks/123456/abcdef",
        )
        admin_instance = WebhookAdmin(Webhook, admin.site)

        self.assertIsNone(admin_instance._restricted_to_group(webhook))
