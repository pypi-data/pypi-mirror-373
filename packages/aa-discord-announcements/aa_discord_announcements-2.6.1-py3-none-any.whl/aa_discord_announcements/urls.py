"""
Pages url config
"""

# Django
from django.urls import include, path

# AA Discord Announcements
from aa_discord_announcements import views
from aa_discord_announcements.constants import INTERNAL_URL_PREFIX

app_name: str = "aa_discord_announcements"

# Ajax URLs
ajax_urls = path(
    route="ajax/",
    view=include(
        [
            path(
                route="get-announcement-targets-for-user/",
                view=views.ajax_get_announcement_targets,
                name="ajax_get_announcement_targets",
            ),
            path(
                route="get-webhooks-for-user/",
                view=views.ajax_get_webhooks,
                name="ajax_get_webhooks",
            ),
            path(
                route="create-announcement/",
                view=views.ajax_create_announcement,
                name="ajax_create_announcement",
            ),
        ]
    ),
)

urlpatterns = [
    path(route="", view=views.index, name="index"),
    # Internal URLs
    path(
        route=f"{INTERNAL_URL_PREFIX}/",
        view=include([ajax_urls]),
    ),
]
