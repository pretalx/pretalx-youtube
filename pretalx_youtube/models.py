import secrets

from django.db import models
from rules.contrib.models import RulesModelBase, RulesModelMixin

from pretalx.agenda.rules import can_view_schedule
from pretalx.event.rules import can_change_event_settings


class YouTubeLink(RulesModelMixin, models.Model, metaclass=RulesModelBase):
    submission = models.OneToOneField(
        to="submission.Submission",
        on_delete=models.CASCADE,
        related_name="youtube_link",
    )
    video_id = models.CharField(max_length=20)

    class Meta:
        rules_permissions = {
            "list": can_view_schedule,
            "view": can_view_schedule,
            "create": can_change_event_settings,
            "update": can_change_event_settings,
        }

    def __str__(self):
        return f"YouTubeLink({self.video_id})"

    @property
    def event(self):
        return self.submission.event

    @property
    def player_link(self):
        return f"https://www.youtube-nocookie.com/embed/{self.video_id}"

    @property
    def youtube_link(self):
        return f"https://youtube.com/watch?v={self.video_id}"

    @property
    def iframe(self):
        return f'<div class="embed-responsive embed-responsive-16by9"><iframe src="{self.player_link}" frameborder="0" allowfullscreen></iframe></div>'


def generate_webhook_token():
    return secrets.token_urlsafe(32)


class YouTubeWebhookSettings(models.Model):
    event = models.OneToOneField(
        to="event.Event",
        on_delete=models.CASCADE,
        related_name="youtube_webhook_settings",
    )
    token = models.CharField(max_length=128, default=generate_webhook_token)

    def __str__(self):
        return f"YouTubeWebhookSettings(event={self.event.slug})"
