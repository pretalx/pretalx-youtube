import copy
from urllib.parse import parse_qs, urlparse

from django import forms
from django.utils.translation import gettext_lazy as _

from pretalx.common.forms.renderers import InlineFormRenderer

from .models import YouTubeLink


class FileUploadForm(forms.Form):
    default_renderer = InlineFormRenderer

    file = forms.FileField(label=_("File"))


class YouTubeUrlForm(forms.Form):
    def __init__(self, *args, event, **kwargs):
        super().__init__(*args, **kwargs)

        if not event or not event.current_schedule:
            return

        self.talks = (
            event.current_schedule.talks.all()
            .filter(is_visible=True, submission__isnull=False)
            .order_by("start")
        )
        youtube_data = {
            v.submission.code: v.youtube_link
            for v in YouTubeLink.objects.filter(submission__event=event)
        }
        s = _("Go to video.")
        p = _("Go to talk page.")
        for talk in self.talks:
            link = youtube_data.get(talk.submission.code)
            help_text = f'<a href="{talk.submission.urls.public.full()}" target="_blank">{p}</a>'
            if link:
                help_text += f' | <a href="{link}" target="_blank">{s}</a>'

            self.fields[f"video_id_{talk.submission.code}"] = forms.URLField(
                required=False,
                label=talk.submission.title,
                widget=forms.TextInput(attrs={"placeholder": ""}),
                initial=link,
                help_text=help_text,
            )

    def clean(self):
        result = {}
        for key, value in copy.copy(self.cleaned_data).items():
            if not value:
                result[key] = None
                continue
            video_id = None
            try:
                url = urlparse(value)
                if "youtube.com" in (url.netloc or ""):
                    qs = parse_qs(url.query)
                    if "v" in qs:
                        video_id = qs["v"][0]
                    else:
                        # /embed/<id>, /shorts/<id>, /live/<id>
                        path_parts = [p for p in url.path.split("/") if p]
                        if path_parts:
                            video_id = path_parts[-1]
                elif "youtu.be" in (url.netloc or ""):
                    path_parts = [p for p in url.path.split("/") if p]
                    if path_parts:
                        video_id = path_parts[0]
            except Exception:  # noqa: BLE001
                self.add_error(key, _("Failed to parse the URL!"))
                continue
            if not video_id:
                self.add_error(key, _("Please provide a YouTube URL!"))
            elif len(video_id) > 20:
                self.add_error(key, _("Failed to parse the URL!"))
            else:
                result[key] = video_id
        return result

    def save(self):
        for talk in self.talks:
            video_id = self.cleaned_data.get(f"video_id_{talk.submission.code}")
            if video_id:
                YouTubeLink.objects.update_or_create(
                    submission=talk.submission, defaults={"video_id": video_id}
                )
            else:
                YouTubeLink.objects.filter(submission=talk.submission).delete()
