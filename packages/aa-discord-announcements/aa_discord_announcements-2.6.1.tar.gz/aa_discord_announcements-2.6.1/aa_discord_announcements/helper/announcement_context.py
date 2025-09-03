"""
Handling announcement context data
"""

# AA Discord Announcements
from aa_discord_announcements.models import PingTarget, Webhook


def get_announcement_context_from_form_data(form_data: dict) -> dict:
    """
    Getting announcement context from form data

    :param form_data: The form data from the announcement form
    :type form_data: dict
    :return: The announcement context
    :rtype: dict
    """

    announcement_target_group_id = None
    announcement_target_group_name = None
    announcement_target_at_mention = None

    announcement_target = form_data.get("announcement_target")

    if announcement_target:
        if announcement_target in ["@here", "@everyone"]:
            announcement_target_at_mention = str(announcement_target)
        else:
            try:
                # Check if we deal with a custom announcement target
                target = PingTarget.objects.get(discord_id=announcement_target)
                announcement_target_group_id = int(target.discord_id)
                announcement_target_group_name = str(target.name)
                announcement_target_at_mention = (
                    str(target.name)
                    if str(target.name).startswith("@")
                    else f"@{target.name}"
                )
            except PingTarget.DoesNotExist:
                pass

    # Check for webhooks
    announcement_channel_webhook = None
    announcement_channel = form_data.get("announcement_channel")

    if announcement_channel:
        try:
            channel = Webhook.objects.get(pk=announcement_channel)
            announcement_channel_webhook = channel.url
        except Webhook.DoesNotExist:
            pass

    announcement_context = {
        "announcement_target": {
            "group_id": announcement_target_group_id,
            "group_name": announcement_target_group_name,
            "at_mention": announcement_target_at_mention or "",
        },
        "announcement_channel": {"webhook": announcement_channel_webhook},
        "announcement_text": str(form_data.get("announcement_text", "")),
    }

    return announcement_context


def get_webhook_announcement_context(announcement_context: dict) -> dict:
    """
    Getting the webhook announcement context

    :param announcement_context: The announcement context
    :type announcement_context: dict
    :return: The webhook announcement context
    :rtype: dict
    """

    webhook_announcement_text_content = ""
    webhook_announcement_text_footer = ""
    webhook_announcement_target = ""

    # Ping target
    announcement_target_at_mention = (
        f'<@&{announcement_context["announcement_target"]["group_id"]}>'
        if announcement_context["announcement_target"]["group_id"]
        else f'{announcement_context["announcement_target"]["at_mention"]}'
    )

    if announcement_target_at_mention:
        webhook_announcement_text_content += announcement_target_at_mention

    if announcement_context["announcement_text"]:
        webhook_announcement_text_content += (
            f'\n\n{announcement_context["announcement_text"]}'
        )

    return {
        "target": webhook_announcement_target,
        "content": webhook_announcement_text_content,
        "footer": webhook_announcement_text_footer,
    }
