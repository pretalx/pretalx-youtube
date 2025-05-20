from django.db import models
from pretalx.agenda.rules import can_view_schedule
from pretalx.event.rules import can_change_event_settings
from rules.contrib.models import RulesModelBase, RulesModelMixin


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
            "create": can_change_event_settings,
            "update": can_change_event_settings,
        }

    @property
    def player_link(self):
        return f"https://www.youtube-nocookie.com/embed/{self.video_id}"

    @property
    def youtube_link(self):
        return f"https://youtube.com/watch?v={self.video_id}"

    @property
    def iframe(self):
        return f'<div class="embed-responsive embed-responsive-16by9"><iframe src="{self.player_link}" frameborder="0" allowfullscreen></iframe></div>'
