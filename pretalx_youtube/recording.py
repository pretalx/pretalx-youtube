from pretalx.agenda.recording import BaseRecordingProvider


class YouTubeProvider(BaseRecordingProvider):
    def get_recording(self, submission):
        youtube = getattr(submission, "youtube_link", None)
        if youtube:
            return {
                "iframe": youtube.iframe,
                "csp_header": "https://www.youtube-nocookie.com/",
            }
