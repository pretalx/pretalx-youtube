from django.db import models


class YouTubeLink(models.Model):
    submission = models.OneToOneField(
        to="submission.Submission",
        on_delete=models.CASCADE,
        related_name="youtube_link",
    )
    video_id = models.CharField(max_length=20)

    @property
    def player_link(self):
        return f"https://www.youtube-nocookie.com/embed/{self.video_id}"

    @property
    def youtube_link(self):
        return f"https://youtube.com/watch?v={self.video_id}"

    @property
    def iframe(self):
        return f'<div class="embed-responsive embed-responsive-16by9"><iframe src="{self.player_link}" frameborder="0" allowfullscreen></iframe></div>'
