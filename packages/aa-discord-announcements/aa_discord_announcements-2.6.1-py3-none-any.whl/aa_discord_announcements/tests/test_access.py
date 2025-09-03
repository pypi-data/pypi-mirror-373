"""
Test checks for access to aa_discord_announcements
"""

# Standard Library
from http import HTTPStatus

# Django
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

# AA Discord Announcements
from aa_discord_announcements.tests.utils import create_fake_user


class TestAccess(TestCase):
    """
    Test access to the module
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

    def test_has_no_access(self):
        """
        Test that a user without access gets a 302
        :return:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(path=reverse(viewname="aa_discord_announcements:index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_has_access(self):
        """
        Test that a user with access gets to see it
        :return:
        """

        # given
        self.client.force_login(user=self.user_1002)

        # when
        res = self.client.get(path=reverse(viewname="aa_discord_announcements:index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
