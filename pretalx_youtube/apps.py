from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class PluginApp(AppConfig):
    name = "pretalx_youtube"
    verbose_name = "YouTube integration"

    class PretalxPluginMeta:
        name = gettext_lazy("YouTube integration")
        author = "Tobias Kunze"
        description = gettext_lazy(
            "Show YouTube videos embedded on talk pages. Set URLs manually or via API."
        )
        visible = True
        version = "1.3.0"

    def ready(self):
        from . import signals  # NOQA
