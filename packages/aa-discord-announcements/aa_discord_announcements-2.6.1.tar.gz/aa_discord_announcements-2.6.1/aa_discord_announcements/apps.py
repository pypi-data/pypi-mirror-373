"""
App config
"""

# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# AA Discord Announcements
from aa_discord_announcements import __version__


class AaDiscordAnnouncementsConfig(AppConfig):
    """
    Application config
    """

    name = "aa_discord_announcements"
    label = "aa_discord_announcements"
    # Translators: This is the app name and version, which will appear in the Django Backend
    verbose_name = _(f"Discord Announcements v{__version__}")
