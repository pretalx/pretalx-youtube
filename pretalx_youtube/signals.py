from django.dispatch import receiver
from django.urls import reverse
from pretalx.agenda.signals import register_recording_provider
from pretalx.orga.signals import nav_event_settings


@receiver(register_recording_provider)
def youtube_provider(sender, **kwargs):
    from .recording import YouTubeProvider

    return YouTubeProvider(sender)


@receiver(nav_event_settings)
def youtube_settings(sender, request, **kwargs):
    if not request.user.has_perm("orga.change_settings", request.event):
        return []
    return [
        {
            "label": "YouTube",
            "url": reverse(
                "plugins:pretalx_youtube:settings",
                kwargs={"event": request.event.slug},
            ),
            "active": request.resolver_match.url_name
            == "plugins:pretalx_youtube:settings",
        }
    ]
