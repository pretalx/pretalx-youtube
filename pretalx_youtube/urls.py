from django.urls import re_path
from pretalx.event.models.event import SLUG_CHARS

from .views import YouTubeSettings
from .api import YouTubeLinkViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(f"api/events/(?P<event>[{SLUG_CHARS}]+)/p/youtube", YouTubeLinkViewSet)

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>[{SLUG_CHARS}]+)/settings/p/youtube/$",
        YouTubeSettings.as_view(),
        name="settings",
    ),
]
urlpatterns += router.urls
