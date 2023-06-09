from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class PluginApp(AppConfig):
    name = "pretalx_youtube"
    verbose_name = "YouTube integration"

    class PretalxPluginMeta:
        name = gettext_lazy("YouTube integration")
        author = "Tobias Kunze"
        description = gettext_lazy(
            "Embed YouTube videos as session recordings, and retrieve them via an API."
        )
        visible = True
        version = "1.2.0"

    def ready(self):
        from . import signals  # NOQA
