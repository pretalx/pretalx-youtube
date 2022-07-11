from django.urls import re_path
from pretalx.event.models.event import SLUG_CHARS

from .views import YouTubeSettings, api_list, api_single

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>[{SLUG_CHARS}]+)/settings/p/youtube/$",
        YouTubeSettings.as_view(),
        name="settings",
    ),
    re_path(
        rf"^api/events/(?P<event>[{SLUG_CHARS}]+)/p/youtube/$",
        api_list,
        name="api_list",
    ),
    re_path(
        rf"^api/events/(?P<event>[{SLUG_CHARS}]+)/submissions/(?P<code>[A-Z0-9]+)/p/youtube/$",
        api_single,
        name="api_single",
    ),
]
