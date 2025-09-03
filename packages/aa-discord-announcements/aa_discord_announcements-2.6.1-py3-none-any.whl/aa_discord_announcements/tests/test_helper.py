# Standard Library
import re
from unittest.mock import Mock, patch

# Django
from django.contrib.auth.models import Group, User
from django.test import TestCase

# AA Discord Announcements
from aa_discord_announcements.helper.announcement_context import (
    get_announcement_context_from_form_data,
    get_webhook_announcement_context,
)
from aa_discord_announcements.helper.discord_webhook import send_to_discord_webhook
from aa_discord_announcements.models import PingTarget, Webhook


class TestAnnouncementContext(TestCase):
    """
    Test the get_announcement_context_from_form_data function
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()

        cls.group = Group.objects.create(name="Superhero")

    @patch("aa_discord_announcements.models.PingTarget.objects.get")
    @patch("aa_discord_announcements.models.Webhook.objects.get")
    def test_gets_announcement_context_with_here_mention(
        self, mock_get_webhook, mock_get_ping_target
    ):
        """
        Test the get_announcement_context_from_form_data function with @here mention

        :param mock_get_webhook:
        :type mock_get_webhook:
        :param mock_get_ping_target:
        :type mock_get_ping_target:
        :return:
        :rtype:
        """

        form_data = {
            "announcement_target": "@here",
            "announcement_channel": 1,
            "announcement_text": "Test announcement",
        }

        mock_get_webhook.return_value.url = "http://example.com/webhook"
        context = get_announcement_context_from_form_data(form_data)

        self.assertEqual(context["announcement_target"]["at_mention"], "@here")
        self.assertEqual(
            context["announcement_channel"]["webhook"], "http://example.com/webhook"
        )
        self.assertEqual(context["announcement_text"], "Test announcement")

    @patch("aa_discord_announcements.models.PingTarget.objects.get")
    @patch("aa_discord_announcements.models.Webhook.objects.get")
    def test_gets_announcement_context_with_custom_target(
        self, mock_get_webhook, mock_get_ping_target
    ):
        """
        Test the get_announcement_context_from_form_data function with a custom ping target

        :param mock_get_webhook:
        :type mock_get_webhook:
        :param mock_get_ping_target:
        :type mock_get_ping_target:
        :return:
        :rtype:
        """

        form_data = {
            "announcement_target": self.group,
            "announcement_channel": 1,
            "announcement_text": "Test announcement",
        }

        mock_get_ping_target.return_value = PingTarget(
            discord_id="123456789", name=self.group
        )
        mock_get_webhook.return_value.url = "http://example.com/webhook"

        context = get_announcement_context_from_form_data(form_data)

        self.assertEqual(context["announcement_target"]["group_id"], 123456789)
        self.assertEqual(context["announcement_target"]["group_name"], self.group.name)
        self.assertEqual(
            context["announcement_target"]["at_mention"], f"@{self.group.name}"
        )
        self.assertEqual(
            context["announcement_channel"]["webhook"], "http://example.com/webhook"
        )
        self.assertEqual(context["announcement_text"], "Test announcement")

    @patch("aa_discord_announcements.models.PingTarget.objects.get")
    @patch("aa_discord_announcements.models.Webhook.objects.get")
    def test_handles_nonexistent_custom_target(
        self, mock_get_webhook, mock_get_ping_target
    ):
        """
        Test the get_announcement_context_from_form_data function with a nonexistent custom target

        :param mock_get_webhook:
        :type mock_get_webhook:
        :param mock_get_ping_target:
        :type mock_get_ping_target:
        :return:
        :rtype:
        """

        form_data = {
            "announcement_target": "nonexistent",
            "announcement_channel": 1,
            "announcement_text": "Test announcement",
        }

        mock_get_ping_target.side_effect = PingTarget.DoesNotExist
        mock_get_webhook.return_value.url = "http://example.com/webhook"

        context = get_announcement_context_from_form_data(form_data)

        self.assertIsNone(context["announcement_target"]["group_id"])
        self.assertIsNone(context["announcement_target"]["group_name"])
        self.assertEqual(context["announcement_target"]["at_mention"], "")
        self.assertEqual(
            context["announcement_channel"]["webhook"], "http://example.com/webhook"
        )
        self.assertEqual(context["announcement_text"], "Test announcement")

    @patch("aa_discord_announcements.models.PingTarget.objects.get")
    @patch("aa_discord_announcements.models.Webhook.objects.get")
    def test_handles_nonexistent_webhook(self, mock_get_webhook, mock_get_ping_target):
        """
        Test the get_announcement_context_from_form_data function with a nonexistent webhook

        :param mock_get_webhook:
        :type mock_get_webhook:
        :param mock_get_ping_target:
        :type mock_get_ping_target:
        :return:
        :rtype:
        """

        form_data = {
            "announcement_target": "@here",
            "announcement_channel": "nonexistent",
            "announcement_text": "Test announcement",
        }

        mock_get_webhook.side_effect = Webhook.DoesNotExist

        context = get_announcement_context_from_form_data(form_data)

        self.assertEqual(context["announcement_target"]["at_mention"], "@here")
        self.assertIsNone(context["announcement_channel"]["webhook"])
        self.assertEqual(context["announcement_text"], "Test announcement")


class TestWebhookAnnouncementContext(TestCase):
    """
    Test the get_webhook_announcement_context function
    """

    def test_returns_correct_context_with_group_id(self):
        """
        Test the get_webhook_announcement_context function with a group ID

        :return:
        :rtype:
        """

        announcement_context = {
            "announcement_target": {"group_id": 123456789},
            "announcement_text": "Test announcement",
        }

        result = get_webhook_announcement_context(announcement_context)

        self.assertEqual(result["content"], "<@&123456789>\n\nTest announcement")

    def test_returns_correct_context_with_at_here(self):
        """
        Test the get_webhook_announcement_context function with an @here mention

        :return:
        :rtype:
        """

        announcement_context = {
            "announcement_target": {"group_id": None, "at_mention": "@here"},
            "announcement_text": "Test announcement",
        }

        result = get_webhook_announcement_context(announcement_context)

        self.assertEqual(result["content"], "@here\n\nTest announcement")

    def test_handles_empty_announcement_text(self):
        """
        Test the get_webhook_announcement_context function with an empty announcement text

        :return:
        :rtype:
        """

        announcement_context = {
            "announcement_target": {"group_id": 123456789, "at_mention": ""},
            "announcement_text": "",
        }

        result = get_webhook_announcement_context(announcement_context)

        self.assertEqual(result["content"], "<@&123456789>")

    def test_handles_empty_announcement_target(self):
        """
        Test the get_webhook_announcement_context function with an empty announcement target

        :return:
        :rtype:
        """

        announcement_context = {
            "announcement_target": {"group_id": None, "at_mention": ""},
            "announcement_text": "Test announcement",
        }

        result = get_webhook_announcement_context(announcement_context)

        self.assertEqual(result["content"], "\n\nTest announcement")

    def test_handles_empty_context(self):
        """
        Test the get_webhook_announcement_context function with an empty context

        :return:
        :rtype:
        """

        announcement_context = {
            "announcement_target": {"group_id": None, "at_mention": ""},
            "announcement_text": "",
        }

        result = get_webhook_announcement_context(announcement_context)

        self.assertEqual(result["content"], "")


class TestSendToDiscordWebhook(TestCase):
    """
    Test the send_to_discord_webhook function
    """

    @patch("aa_discord_announcements.helper.discord_webhook.Webhook.execute")
    @patch(
        "aa_discord_announcements.helper.discord_webhook.get_webhook_announcement_context"
    )
    @patch("aa_discord_announcements.helper.discord_webhook.get_user_agent")
    def test_sends_announcement_successfully(
        self, mock_get_user_agent, mock_get_webhook_announcement_context, mock_execute
    ):
        """
        Test the send_to_discord_webhook function sending an announcement successfully

        :param mock_get_user_agent:
        :type mock_get_user_agent:
        :param mock_get_webhook_announcement_context:
        :type mock_get_webhook_announcement_context:
        :param mock_execute:
        :type mock_execute:
        :return:
        :rtype:
        """

        mock_get_user_agent.return_value = "TestUserAgent"
        mock_get_webhook_announcement_context.return_value = {
            "content": "Test announcement content"
        }
        mock_user = Mock(spec=User)
        mock_user.profile.main_character.character_name = "TestCharacter"

        announcement_context = {
            "announcement_channel": {"webhook": "http://example.com/webhook"},
            "announcement_text": "Test announcement",
        }

        send_to_discord_webhook(announcement_context, mock_user)

        # Use regex to match the dynamic timestamp
        expected_content_pattern = re.compile(
            r"Test announcement content\n\n-# _Sent by TestCharacter @ \d{4}-\d{2}-\d{2} \d{2}:\d{2} \(EVE time\)_"
        )
        actual_content = mock_execute.call_args[1]["content"]
        self.assertTrue(expected_content_pattern.match(actual_content))
        mock_execute.assert_called_once_with(
            content=actual_content, wait_for_response=True
        )

    @patch("aa_discord_announcements.helper.discord_webhook.Webhook.execute")
    @patch(
        "aa_discord_announcements.helper.discord_webhook.get_webhook_announcement_context"
    )
    @patch("aa_discord_announcements.helper.discord_webhook.get_user_agent")
    def test_handles_missing_webhook_url(
        self, mock_get_user_agent, mock_get_webhook_announcement_context, mock_execute
    ):
        """
        Test the send_to_discord_webhook function handles a missing webhook URL

        :param mock_get_user_agent:
        :type mock_get_user_agent:
        :param mock_get_webhook_announcement_context:
        :type mock_get_webhook_announcement_context:
        :param mock_execute:
        :type mock_execute:
        :return:
        :rtype:
        """

        mock_get_user_agent.return_value = "TestUserAgent"
        mock_get_webhook_announcement_context.return_value = {
            "content": "Test announcement content"
        }
        mock_user = Mock(spec=User)
        mock_user.profile.main_character.character_name = "TestCharacter"

        announcement_context = {
            "announcement_channel": {"webhook": None},
            "announcement_text": "Test announcement",
        }

        with self.assertRaises(ValueError):
            send_to_discord_webhook(announcement_context, mock_user)

    @patch("aa_discord_announcements.helper.discord_webhook.Webhook.execute")
    @patch(
        "aa_discord_announcements.helper.discord_webhook.get_webhook_announcement_context"
    )
    @patch("aa_discord_announcements.helper.discord_webhook.get_user_agent")
    def handles_empty_announcement_text(
        self, mock_get_user_agent, mock_get_webhook_announcement_context, mock_execute
    ):
        """
        Test the send_to_discord_webhook function handles an empty announcement text

        :param mock_get_user_agent:
        :type mock_get_user_agent:
        :param mock_get_webhook_announcement_context:
        :type mock_get_webhook_announcement_context:
        :param mock_execute:
        :type mock_execute:
        :return:
        :rtype:
        """

        mock_get_user_agent.return_value = "TestUserAgent"
        mock_get_webhook_announcement_context.return_value = {"content": ""}
        mock_user = Mock(spec=User)
        mock_user.profile.main_character.character_name = "TestCharacter"

        announcement_context = {
            "announcement_channel": {"webhook": "http://example.com/webhook"},
            "announcement_text": "",
        }

        send_to_discord_webhook(announcement_context, mock_user)

        mock_execute.assert_called_once_with(
            content="\n\n-# _Sent by TestCharacter @ 2023-10-10 10:10 (EVE time)_",
            wait_for_response=True,
        )
