"""
The views
"""

# Standard Library
import json

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from app_utils.urls import site_absolute_url

# AA Discord Announcements
from aa_discord_announcements import __title__
from aa_discord_announcements.forms import AnnouncementForm
from aa_discord_announcements.helper.announcement_context import (
    get_announcement_context_from_form_data,
)
from aa_discord_announcements.helper.discord_webhook import send_to_discord_webhook
from aa_discord_announcements.models import PingTarget, Webhook

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required(perm="aa_discord_announcements.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view
    """

    logger.info(msg=f"Discord Announcements view called by user {request.user}")

    context = {
        "title": __title__,
        "webhooks_configured": Webhook.objects.filter(
            Q(restricted_to_group__in=request.user.groups.all())
            | Q(restricted_to_group__isnull=True),
            is_enabled=True,
        ).exists(),
        "site_url": site_absolute_url(),
        "main_character": request.user.profile.main_character,
        "form": AnnouncementForm,
    }

    return render(
        request=request,
        template_name="aa_discord_announcements/index.html",
        context=context,
    )


@login_required
@permission_required(perm="aa_discord_announcements.basic_access")
def ajax_get_announcement_targets(request: WSGIRequest) -> HttpResponse:
    """
    Get announcement targets for the current user
    :param request:
    :return:
    """

    logger.info(msg=f"Getting announcement targets for user {request.user}")

    additional_discord_announcement_targets = (
        PingTarget.objects.filter(
            Q(restricted_to_group__in=request.user.groups.all())
            | Q(restricted_to_group__isnull=True),
            is_enabled=True,
        )
        .distinct()
        .order_by("name")
    )

    return render(
        request=request,
        template_name="aa_discord_announcements/partials/form/segments/announcement-targets.html",
        context={"announcement_targets": additional_discord_announcement_targets},
    )


@login_required
@permission_required(perm="aa_discord_announcements.basic_access")
def ajax_get_webhooks(request: WSGIRequest) -> HttpResponse:
    """
    Get webhooks for the current user
    :param request:
    :return:
    """

    logger.info(msg=f"Getting webhooks for user {request.user}")

    webhooks = (
        Webhook.objects.filter(
            Q(restricted_to_group__in=request.user.groups.all())
            | Q(restricted_to_group__isnull=True),
            is_enabled=True,
        ).distinct()
        # .order_by("type", "name")
    )

    return render(
        request=request,
        template_name="aa_discord_announcements/partials/form/segments/announcement-channel.html",
        context={"webhooks": webhooks},
    )


@login_required
@permission_required(perm="aa_discord_announcements.basic_access")
def ajax_create_announcement(request: WSGIRequest) -> HttpResponse:
    """
    Create the announcement

    :param request:
    :return:
    """

    context = {}

    if request.method == "POST":
        form = AnnouncementForm(data=json.loads(request.body))

        if form.is_valid():
            logger.info(msg="Discord announcement received")

            logger.debug(msg=f"Announcement form data: {form.cleaned_data}")

            # Get ping context
            announcement_context = get_announcement_context_from_form_data(
                form_data=form.cleaned_data
            )

            logger.debug(msg=f"Announcement context: {announcement_context}")

            # If we have a Discord webhook, ping it
            if announcement_context["announcement_channel"]["webhook"]:
                send_to_discord_webhook(
                    announcement_context=announcement_context, user=request.user
                )

            logger.info(msg=f"Discord announcement created by user {request.user}")

            context["announcement_context"] = render_to_string(
                template_name="aa_discord_announcements/partials/announcement/copy-paste-text.html",
                context=announcement_context,
            )
            context["success"] = True
        else:
            context["message"] = str(_("Form invalid. Please check your input."))
            context["success"] = False
    else:
        context["message"] = str(_("No form data submitted."))
        context["success"] = False

    return HttpResponse(content=json.dumps(context), content_type="application/json")
