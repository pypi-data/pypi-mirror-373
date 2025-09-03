"""
Settings for the admin backend
"""

# Django
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# AA Discord Announcements
from aa_discord_announcements.models import PingTarget, Webhook


@admin.register(PingTarget)
class PingTargetAdmin(admin.ModelAdmin):
    """
    DiscordPingTargetsAdmin
    """

    list_display = (
        "_name",
        "discord_id",
        "_restricted_to_group",
        "notes",
        "is_enabled",
    )

    filter_horizontal = ("restricted_to_group",)
    readonly_fields = ("discord_id",)
    ordering = ("name",)

    @admin.display(description=_("Group name"), ordering="name")
    def _name(self, obj):
        return obj.name.name

    @admin.display(
        description=_("Group restrictions"), ordering="restricted_to_group__name"
    )
    def _restricted_to_group(self, obj):
        names = [x.name for x in obj.restricted_to_group.all().order_by("name")]

        return ", ".join(names) if names else None


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """
    WebhookAdmin
    """

    list_display = ("_name", "_url", "_restricted_to_group", "notes", "is_enabled")

    filter_horizontal = ("restricted_to_group",)
    ordering = ("name",)

    @admin.display(description=_("Discord channel"), ordering="name")
    def _name(self, obj):
        return obj.name

    @admin.display(description=_("Webhook URL"), ordering="url")
    def _url(self, obj):
        return obj.url

    @admin.display(
        description=_("Group restrictions"), ordering="restricted_to_group__name"
    )
    def _restricted_to_group(self, obj):
        names = [x.name for x in obj.restricted_to_group.all().order_by("name")]

        return ", ".join(names) if names else None
