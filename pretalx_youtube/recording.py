from pretalx.agenda.recording import BaseRecordingProvider

from .models import YouTubeLink


class YouTubeProvider(BaseRecordingProvider):
    def get_recording(self, submission):
        youtube = YouTubeLink.objects.filter(submission=submission).first()
        if youtube:
            return {
                "iframe": youtube.iframe,
                "csp_header": "https://www.youtube-nocookie.com/",
            }
