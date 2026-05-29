import re
from urllib.parse import parse_qs, urlparse

MAX_VIDEO_ID_LENGTH = 20
# YouTube video ids only ever contain these characters. Enforcing the charset
# keeps HTML metacharacters out of the id, which is embedded into iframe markup.
VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def extract_video_id(url):
    """Return the YouTube video id from a URL, or None if nothing usable is found.

    Accepts ``youtube.com``, ``youtu.be`` and ``youtube-nocookie.com`` in their
    common variants (``watch?v=``, ``/embed/``, ``/shorts/``, ``/live/``).
    """
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    video_id = None
    if "youtube.com" in host or "youtube-nocookie.com" in host:
        qs = parse_qs(parsed.query)
        if "v" in qs:
            video_id = qs["v"][0]
        else:
            path_parts = [p for p in parsed.path.split("/") if p]
            video_id = path_parts[-1] if path_parts else None
    elif "youtu.be" in host:
        path_parts = [p for p in parsed.path.split("/") if p]
        video_id = path_parts[0] if path_parts else None
    if not video_id or len(video_id) > MAX_VIDEO_ID_LENGTH:
        return None
    if not VIDEO_ID_RE.match(video_id):
        return None
    return video_id
