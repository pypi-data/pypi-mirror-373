"""
Test cases for the `aa_discord_announcements.helper.discord_webhook` module.
"""

# Standard Library
from unittest import TestCase

# AA Discord Announcements
from aa_discord_announcements import __version__
from aa_discord_announcements.constants import APP_NAME, GITHUB_URL
from aa_discord_announcements.helper.discord_webhook import get_user_agent


class TestUserAgent(TestCase):
    """
    Test cases for the `UserAgent` class
    """

    def test_create_useragent(self):
        """
        Test creating a user agent

        :return:
        :rtype:
        """

        obj = get_user_agent()

        self.assertEqual(first=obj.name, second=APP_NAME)
        self.assertEqual(first=obj.url, second=GITHUB_URL)
        self.assertEqual(first=obj.version, second=__version__)

    def test_useragent_str(self):
        """
        Test the string representation of the user agent

        :return:
        :rtype:
        """

        obj = get_user_agent()

        self.assertEqual(
            first=str(obj), second=f"{APP_NAME} ({GITHUB_URL}, {__version__})"
        )
