import csv
import json

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from pretalx.common.mixins.views import PermissionRequired

from .api import YouTubeLinkWriteSerializer
from .forms import FileUploadForm, YouTubeUrlForm


class YouTubeSettings(PermissionRequired, FormView):
    permission_required = "orga.change_settings"
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

    def post(self, *args, **kwargs):
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
