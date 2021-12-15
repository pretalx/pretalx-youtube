from django.contrib import messages
from django.http import Http404, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from pretalx.common.mixins.views import PermissionRequired
from pretalx.submission.models import Submission

from .forms import YouTubeUrlForm
from .models import YouTubeLink


class YouTubeSettings(PermissionRequired, TemplateView):
    permission_required = "orga.change_settings"
    template_name = "pretalx_youtube/settings.html"

    def get_success_url(self):
        return self.request.path

    def get_object(self):
        return self.request.event

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        code = action[len("url_") :]
        try:
            submission = request.event.submissions.get(code=code)
        except Submission.DoesNotExist:
            messages.error(request, _("Could not find this talk."))
            return super().get(request, *args, **kwargs)

        form = YouTubeUrlForm(request.POST, submission=submission)
        if not form.is_valid():
            messages.error(request, form.errors)
            return super().get(request, *args, **kwargs)
        else:
            form.save()
            messages.success(request, _("The URL for this talk was updated."))
            return super().get(request, *args, **kwargs)

        return super().post(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["url_forms"] = [
            YouTubeUrlForm(submission=submission)
            for submission in self.request.event.talks
        ]
        return kwargs


def check_api_access(request):
    if "pretalx_youtube" not in request.event.plugin_list:
        raise Http404()
    if not (
        request.user.has_perm("agenda.view_schedule", request.event)
        or request.user.has_perm("orga.view_submissions")
    ):
        raise Http404()


def api_list(request, event):
    check_api_access(request)
    return JsonResponse(
        {
            "results": [
                link.serialize()
                for link in YouTubeLink.objects.filter(submission__event=request.event)
            ]
        }
    )


def api_single(request, event, code):
    check_api_access(request)
    submission = request.event.submissions.filter(code__iexact=code).first()
    if not submission:
        raise Http404()
    link = getattr(submission, "youtube_link", None)
    return JsonResponse(link.serialize() if link else {})
