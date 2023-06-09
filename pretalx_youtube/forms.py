from urllib.parse import parse_qs, urlparse

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import YouTubeLink


class YouTubeUrlForm(forms.Form):
    video_id = forms.URLField(required=False)

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop("submission")

        youtube = getattr(self.submission, "youtube_link", None)
        if youtube:
            initial = kwargs.get("initial", dict())
            initial["video_id"] = f"https://youtube.com/watch?v={youtube.video_id}"
            kwargs["initial"] = initial
        super().__init__(*args, **kwargs)
        self.fields["video_id"].label = self.submission.title

    def clean_video_id(self):
        data = self.cleaned_data["video_id"]
        if not data:
            return data
        # Get ID from youtube.com and youtu.be URLs
        if "youtube.com" in data:
            try:
                url = urlparse(data)
                qs = parse_qs(url.query)
                return qs["v"][0]
            except Exception as e:
                raise forms.ValidationError(_("Failed to parse the URL!") + f" {e}")
        elif "youtu.be" in data:
            try:
                return data.split("/")[-1]
            except Exception as e:
                raise forms.ValidationError(_("Failed to parse the URL!") + f" {e}")
        else:
            raise forms.ValidationError(_("Please provide a YouTube URL!"))

    def save(self):
        video_id = self.cleaned_data.get("video_id")
        if video_id:
            YouTubeLink.objects.update_or_create(
                submission=self.submission, defaults={"video_id": video_id}
            )
        else:
            YouTubeLink.objects.filter(submission=self.submission).delete()

    class Meta:
        model = YouTubeLink
        fields = ("video_id",)
