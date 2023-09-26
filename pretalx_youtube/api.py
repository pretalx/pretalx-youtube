import csv

from pretalx.api.permissions import ApiPermission, PluginPermission
from pretalx.submission.models import Submission
from rest_framework import parsers, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import YouTubeLink


class YouTubeLinkSerializer(serializers.ModelSerializer):
    submission = serializers.SlugRelatedField(
        slug_field="code", queryset=Submission.objects.none()
    )
    youtube_link = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = kwargs.get("context", {}).get("request")
        if not request:
            return
        self.event = request.event

    def get_youtube_link(self, obj):
        return obj.youtube_link

    class Meta:
        model = YouTubeLink
        fields = ["submission", "youtube_link", "video_id"]


class YouTubeLinkWriteSerializer(YouTubeLinkSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not getattr(self, "event", None):
            return
        # We only set this here as to not leak all submissions to the API interface
        if self.instance and getattr(self.instance, "submission", None):
            self.fields["submission"].queryset = self.event.submissions.all().filter(
                pk=self.instance.submission.pk
            )
        else:
            self.fields["submission"].queryset = self.event.submissions.all()

    def validate_video_id(self, value):
        # Strip out any URL parts
        if "/" in value:
            parts = [p for p in value.split("/") if p]
            value = parts[-1]
        return value

    def save(self, **kwargs):
        if not self.instance:
            # We need to check if there is already a link for this submission
            # as we don't want to create duplicates
            # (And save() logic is too complex to just override it entirely)
            self.instance = YouTubeLink.objects.filter(
                submission=self.validated_data["submission"]
            ).first()
        return super().save(**kwargs)

    class Meta(YouTubeLinkSerializer.Meta):
        fields = ["submission", "video_id"]


class YouTubeLinkViewSet(viewsets.ModelViewSet):
    serializer_class = YouTubeLinkSerializer
    queryset = YouTubeLink.objects.none()
    permission_classes = [ApiPermission & PluginPermission]
    plugin_required = "pretalx_youtube"
    read_permission_required = "agenda.view_schedule"
    write_permission_required = "orga.change_settings"
    lookup_field = "submission__code"

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return YouTubeLinkWriteSerializer
        return YouTubeLinkSerializer

    def get_queryset(self):
        event = self.request.event
        if not event:
            return YouTubeLink.objects.none()
        return YouTubeLink.objects.filter(submission__event=event).select_related(
            "submission"
        )

    def get_permission_object(self):
        return self.request.event

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=["post"], url_path="import", url_name="import")
    def bulk_import(self, request, *args, **kwargs):
        data = None
        if request.content_type == "application/json":
            data = request.data
        if not data:
            # Parse uploaded file. We're generous and doing this even when
            # the content type is not set correctly.
            parser = parsers.FileUploadParser()
            data = parser.parse(request, parser_context={"request": request})
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(data, list):
            # The parser has found a single file and returned a single object, as it wasn't
            # a JSON file. Let's hope it's CSV!
            if len(data) > 1:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            try:
                data = [
                    line
                    for line in csv.DictReader(list(data.values())[0].splitlines())
                    if any(line.values())
                ]
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        # We aren't using many=True because making sure that we are always
        # running get_or_create() is not trivial with many=True
        for row in data:
            serializer = YouTubeLinkWriteSerializer(
                data=row, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(status=status.HTTP_201_CREATED)
