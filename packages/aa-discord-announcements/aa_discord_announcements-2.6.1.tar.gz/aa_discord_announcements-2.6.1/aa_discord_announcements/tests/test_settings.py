"""
Test the settings
"""

# Django
from django.test import TestCase, modify_settings, override_settings

# AA Discord Announcements
from aa_discord_announcements.app_settings import (
    debug_enabled,
    discord_service_installed,
)


class TestSettings(TestCase):
    """
    Test the settings
    """

    @modify_settings(INSTALLED_APPS={"append": "allianceauth.services.modules.discord"})
    def test_discord_service_installed_should_return_true(self) -> None:
        """
        Test discord_service_installed should return True with discord service enabled

        :return:
        :rtype:
        """

        self.assertTrue(expr=discord_service_installed())

    @modify_settings(INSTALLED_APPS={"remove": "allianceauth.services.modules.discord"})
    def test_discord_service_installed_should_return_false(self) -> None:
        """
        Test discord_service_installed should return False without discord service enabled

        :return:
        :rtype:
        """

        self.assertFalse(expr=discord_service_installed())

    @override_settings(DEBUG=True)
    def test_debug_enabled_with_debug_true(self) -> None:
        """
        Test debug_enabled with DEBUG = True

        :return:
        :rtype:
        """

        self.assertTrue(debug_enabled())

    @override_settings(DEBUG=False)
    def test_debug_enabled_with_debug_false(self) -> None:
        """
        Test debug_enabled with DEBUG = False

        :return:
        :rtype:
        """

        self.assertFalse(debug_enabled())
