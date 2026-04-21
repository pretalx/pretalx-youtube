import base64
import csv
import hmac
import json
import logging

from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView

from pretalx.common.views.mixins import PermissionRequired

from .api import YouTubeLinkWriteSerializer
from .forms import FileUploadForm, YouTubeUrlForm
from .models import YouTubeLink, YouTubeWebhookSettings, generate_webhook_token
from .utils import extract_video_id

logger = logging.getLogger(__name__)


class YouTubeSettings(PermissionRequired, FormView):
    permission_required = "event.update_event"
    template_name = "pretalx_youtube/settings.html"
    form_class = YouTubeUrlForm

    def get_success_url(self):
        return self.request.path

    def get_object(self):
        return self.request.event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["event"] = self.request.event
        return kwargs

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["file_form"] = FileUploadForm()
        webhook_settings, _created = YouTubeWebhookSettings.objects.get_or_create(
            event=self.request.event
        )
        ctx["webhook_settings"] = webhook_settings
        ctx["webhook_url"] = self.request.build_absolute_uri(
            reverse(
                "plugins:pretalx_youtube:c3voc_webhook",
                kwargs={"event": self.request.event.slug},
            )
        )
        return ctx

    def handle_upload(self):
        # There needs to be exactly one file
        if not self.request.FILES or len(self.request.FILES) > 1:
            messages.error(self.request, _("You need to select a file to upload!"))
            return self.get(self.request)

        # Parse the json or csv file
        file = self.request.FILES["file"]
        if file.name.endswith(".json"):
            data = json.load(file)
        elif file.name.endswith(".csv"):
            data = csv.DictReader(file.read().decode("utf-8").splitlines())
        else:
            messages.error(
                self.request, _("You need to select a JSON or CSV file to upload!")
            )
            return self.get(self.request)

        for row in data:
            serializer = YouTubeLinkWriteSerializer(
                data=row, context={"request": self.request}
            )
            if not serializer.is_valid():
                messages.error(
                    self.request,
                    _("The file you uploaded is not valid: ") + str(serializer.errors),
                )
                return self.get(self.request)
            serializer.save()

        messages.success(self.request, _("The YouTube URLs were updated."))
        return self.get(self.request)

    def handle_rotate_token(self):
        webhook_settings, _created = YouTubeWebhookSettings.objects.get_or_create(
            event=self.request.event
        )
        webhook_settings.token = generate_webhook_token()
        webhook_settings.save()
        messages.success(self.request, _("A new webhook token has been generated."))
        return redirect(self.request.path)

    def post(self, *args, **kwargs):
        if self.request.POST.get("action", "") == "rotate_token":
            return self.handle_rotate_token()
        if not self.request.event.current_schedule:
            messages.error(self.request, _("Please create a schedule first!"))
            return self.get(self.request, *args, **kwargs)
        if self.request.POST.get("action", "") == "upload":
            return self.handle_upload()
        form = self.get_form()
        if not form.is_valid():
            messages.error(self.request, _("Please fix the errors below."))
            return self.get(self.request, *args, **kwargs)
        form.save()
        messages.success(self.request, _("The YouTube URLs were updated."))
        return super().get(self.request, *args, **kwargs)


def _extract_token(request):
    """Return the plaintext token from the Authorization header, or None.

    Matches the two schemes voctopublish sends
    (see ``voctopublish/api_client/webhook_client.py``):

    - ``Authorization: Basic base64(user:token)`` when a webhook user is set,
    - ``Authorization: <token>`` (bare, no scheme prefix) when only the
      password is set.

    Any other header value is returned as-is and will simply fail the
    constant-time token comparison in the caller.
    """
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth:
        return None
    if auth.lower().startswith("basic "):
        try:
            decoded = base64.b64decode(auth.split(" ", 1)[1], validate=True).decode(
                "utf-8", errors="strict"
            )
        except (ValueError, UnicodeDecodeError):
            return None
        if ":" not in decoded:
            return None
        _user, _, password = decoded.partition(":")
        return password or None
    return auth


def _find_submission(event, payload):
    """Match a c3voc webhook payload to a Submission of the given event.

    Uses only identifiers that pretalx itself exports (id, frab slug).
    """
    fahrplan = payload.get("fahrplan") or {}
    conference = fahrplan.get("conference")
    if conference and conference != event.slug:
        return None

    # Try the integer fahrplan id (pretalx exports submission.pk here).
    # Reject bools — isinstance(True, int) is True in Python.
    fahrplan_id = fahrplan.get("id")
    if isinstance(fahrplan_id, int) and not isinstance(fahrplan_id, bool):
        submission = event.submissions.filter(pk=fahrplan_id).first()
        if submission:
            return submission

    # Fall back to parsing the frab slug: "{event.slug}-{pk}[...]".
    slug = fahrplan.get("slug")
    if slug and slug.startswith(f"{event.slug}-"):
        remainder = slug[len(event.slug) + 1 :]
        pk_part = remainder.split("-", 1)[0]
        if pk_part.isdigit():
            submission = event.submissions.filter(pk=int(pk_part)).first()
            if submission:
                return submission

    return None


@method_decorator(csrf_exempt, name="dispatch")
class C3VOCWebhookView(View):
    """Receive ``voctopublish`` publishing notifications.

    Pretalx's ``EventMiddleware`` has already resolved ``request.event`` and
    returned 404 if the event does not exist or does not have this plugin
    enabled, so this view can assume both.
    """

    http_method_names = ["post"]

    def post(self, request, event):
        webhook_settings = YouTubeWebhookSettings.objects.filter(
            event=request.event
        ).first()
        if not webhook_settings or not webhook_settings.token:
            return HttpResponseForbidden()

        provided = _extract_token(request)
        if not provided:
            return HttpResponseForbidden()
        if not hmac.compare_digest(provided, webhook_settings.token):
            return HttpResponseForbidden()

        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return HttpResponseBadRequest("invalid json")
        if not isinstance(payload, dict):
            return HttpResponseBadRequest("invalid payload")

        youtube = payload.get("youtube") or {}
        if not youtube.get("enabled"):
            # Nothing for us to do — acknowledge so voctopublish does not retry.
            return HttpResponse(status=204)
        urls = youtube.get("urls") or []
        if not isinstance(urls, list) or not urls:
            return HttpResponseBadRequest("no youtube urls")

        video_id = None
        for url in urls:
            if not isinstance(url, str):
                continue
            video_id = extract_video_id(url)
            if video_id:
                break
        if not video_id:
            return HttpResponseBadRequest("no valid youtube url")

        submission = _find_submission(request.event, payload)
        if not submission:
            return HttpResponse(status=404)
        YouTubeLink.objects.update_or_create(
            submission=submission, defaults={"video_id": video_id}
        )

        logger.info(
            "c3voc webhook: set YouTube video %s for submission %s (event %s)",
            video_id,
            submission.code,
            request.event.slug,
        )
        return HttpResponse(status=204)
