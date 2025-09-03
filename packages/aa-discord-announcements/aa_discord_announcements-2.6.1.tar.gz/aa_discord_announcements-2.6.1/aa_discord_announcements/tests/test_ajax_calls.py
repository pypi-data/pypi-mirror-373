"""
Test ajax calls
"""

# Standard Library
import json
from http import HTTPStatus
from unittest.mock import patch

# Django
from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase
from django.urls import reverse

# AA Discord Announcements
from aa_discord_announcements.tests.utils import create_fake_user
from aa_discord_announcements.views import ajax_create_announcement


class TestAjaxCalls(TestCase):
    """
    Test access to ajax calls
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()

        cls.group = Group.objects.create(name="Superhero")

        # User cannot access aa_discord_announcements
        cls.user_1001 = create_fake_user(
            character_id=1001, character_name="Peter Parker"
        )

        # User can access aa_discord_announcements
        cls.user_1002 = create_fake_user(
            character_id=1002,
            character_name="Bruce Wayne",
            permissions=["aa_discord_announcements.basic_access"],
        )

    def setUp(self):
        """
        Setup
        """

        self.factory = RequestFactory()

    def test_ajax_get_announcement_targets_no_access(self):
        """
        Test ajax call to get announcement targets available for the current user without access to it

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_discord_announcements:ajax_get_announcement_targets"
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_ajax_get_announcement_targets_general(self):
        """
        Test ajax call to get announcement targets available for the current user

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1002)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_discord_announcements:ajax_get_announcement_targets"
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_ajax_get_webhooks_no_access(self):
        """
        Test ajax call to get webhooks available for the current user without access to it

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(
            path=reverse(viewname="aa_discord_announcements:ajax_get_webhooks")
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_ajax_get_webhooks_general(self):
        """
        Test ajax call to get webhooks available for the current user

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1002)

        # when
        res = self.client.get(
            path=reverse(viewname="aa_discord_announcements:ajax_get_webhooks")
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_ajax_create_announcement_no_access(self):
        """
        Test ajax call to create an announcement is not available for a user without access to it

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(
            path=reverse(viewname="aa_discord_announcements:ajax_create_announcement")
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_ajax_create_announcement_general(self):
        """
        Test ajax call to create an announcement is available for the current user

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1002)

        # when
        res = self.client.get(
            path=reverse(viewname="aa_discord_announcements:ajax_create_announcement")
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    @patch("aa_discord_announcements.views.get_announcement_context_from_form_data")
    @patch("aa_discord_announcements.views.send_to_discord_webhook")
    def test_creates_announcement_successfully_with_webhook(
        self, mock_send_to_discord_webhook, mock_get_announcement_context
    ):
        """
        Test ajax call to create an announcement is successful with a webhook

        :param mock_send_to_discord_webhook:
        :type mock_send_to_discord_webhook:
        :param mock_get_announcement_context:
        :type mock_get_announcement_context:
        :return:
        :rtype:
        """

        mock_get_announcement_context.return_value = {
            "announcement_target": {
                "group_id": None,
                "group_name": None,
                "at_mention": "@here",
            },
            "announcement_channel": {"webhook": True},
            "announcement_text": "Borg to fight!",
        }

        self.client.force_login(user=self.user_1002)

        form_data = json.dumps(
            {
                "announcement_target": "@here",
                "announcement_channel": "1",
                "announcement_text": "Borg to fight!",
            }
        )
        response = self.client.post(
            path=reverse(viewname="aa_discord_announcements:ajax_create_announcement"),
            data=form_data,
            content_type="application/json",
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
        self.assertTemplateUsed(
            response=response,
            template_name="aa_discord_announcements/partials/announcement/copy-paste-text.html",
        )
        self.assertContains(response=response, text="@here")
        self.assertContains(response=response, text="Borg to fight!")

        mock_send_to_discord_webhook.assert_called_once()

    @patch("aa_discord_announcements.views.get_announcement_context_from_form_data")
    @patch("aa_discord_announcements.views.send_to_discord_webhook")
    def test_creates_announcement_successfully_without_webhook(
        self, mock_send_to_discord_webhook, mock_get_announcement_context
    ):
        """
        Test ajax call to create an announcement is successful without a webhook

        :param mock_send_to_discord_webhook:
        :type mock_send_to_discord_webhook:
        :param mock_get_announcement_context:
        :type mock_get_announcement_context:
        :return:
        :rtype:
        """

        mock_get_announcement_context.return_value = {
            "announcement_target": {
                "group_id": None,
                "group_name": None,
                "at_mention": "@here",
            },
            "announcement_channel": {"webhook": False},
            "announcement_text": "Borg to fight!",
        }

        self.client.force_login(user=self.user_1002)

        form_data = json.dumps(
            {
                "announcement_target": "@here",
                "announcement_channel": "1",
                "announcement_text": "Borg to fight!",
            }
        )
        response = self.client.post(
            path=reverse(viewname="aa_discord_announcements:ajax_create_announcement"),
            data=form_data,
            content_type="application/json",
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
        self.assertTemplateUsed(
            response=response,
            template_name="aa_discord_announcements/partials/announcement/copy-paste-text.html",
        )
        self.assertContains(response=response, text="@here")
        self.assertContains(response=response, text="Borg to fight!")

        mock_send_to_discord_webhook.assert_not_called()

    def test_form_invalid_returns_error(self):
        """
        Test ajax call to create an announcement returns an error if the form is invalid

        :return:
        :rtype:
        """

        request = self.factory.post(
            path=reverse(viewname="aa_discord_announcements:ajax_create_announcement"),
            data=json.dumps(
                {
                    "announcement_target": "800432143549333504",
                    "announcement_channel": "1",
                }
            ),
            content_type="application/json",
        )
        request.user = self.user_1002

        response = ajax_create_announcement(request)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(json.loads(response.content)["success"])
        self.assertEqual(
            json.loads(response.content)["message"],
            "Form invalid. Please check your input.",
        )

    def no_form_data_submitted_returns_error(self):
        """
        Test ajax call to create an announcement returns an error if no form data is submitted

        :return:
        :rtype:
        """

        request = self.factory.post(
            path=reverse(viewname="aa_discord_announcements:ajax_create_announcement"),
            content_type="application/json",
        )
        request.user = self.user_1002

        response = ajax_create_announcement(request)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(json.loads(response.content)["success"])
        self.assertEqual(
            json.loads(response.content)["message"], "No form data submitted."
        )
