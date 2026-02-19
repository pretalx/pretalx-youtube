from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from . import __version__


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
        version = __version__
        category = "RECORDING"
        settings_links = [
            (gettext_lazy("Settings"), "plugins:pretalx_youtube:settings", {}),
        ]

    def ready(self):
        from . import signals  # noqa: F401, PLC0415
