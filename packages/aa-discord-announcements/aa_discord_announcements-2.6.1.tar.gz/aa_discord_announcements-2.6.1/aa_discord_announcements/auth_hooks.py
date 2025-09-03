"""
Hook into AA
"""

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

# AA Discord Announcements
from aa_discord_announcements import __title__, urls


class AaDiscordAnnouncementsMenuItem(
    MenuItemHook
):  # pylint: disable=too-few-public-methods
    """
    This class ensures only authorized users will see the menu entry
    """

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            text=__title__,
            classes="fa-regular fa-bell",
            url_name="aa_discord_announcements:index",
            navactive=["aa_discord_announcements:"],
        )

    def render(self, request):
        """
        Check if the user has the permission to view this app
        :param request:
        :return:
        """

        return (
            MenuItemHook.render(self, request=request)
            if request.user.has_perm(perm="aa_discord_announcements.basic_access")
            else ""
        )


@hooks.register("menu_item_hook")
def register_menu():
    """
    Register our menu item
    :return:
    """

    return AaDiscordAnnouncementsMenuItem()


@hooks.register("url_hook")
def register_urls():
    """
    Register our base url
    :return:
    """

    return UrlHook(
        urls=urls,
        namespace="aa_discord_announcements",
        base_url=r"^discord-announcements/",
    )
