from django.urls import re_path
from rest_framework import routers

from pretalx.event.models.event import SLUG_REGEX

from .api import YouTubeLinkViewSet
from .views import C3VOCWebhookView, YouTubeSettings

router = routers.SimpleRouter()
router.register(
    f"api/events/(?P<event>{SLUG_REGEX})/p/youtube",
    YouTubeLinkViewSet,
    basename="youtube",
)

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/settings/p/youtube/$",
        YouTubeSettings.as_view(),
        name="settings",
    ),
    re_path(
        rf"^(?P<event>{SLUG_REGEX})/p/youtube/c3voc/$",
        C3VOCWebhookView.as_view(),
        name="c3voc_webhook",
    ),
]
urlpatterns += router.urls
