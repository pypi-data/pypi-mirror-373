from django.apps import AppConfig


class RaincheckConfig(AppConfig):
    name = "dj_raincheck"
    label = "dj_raincheck"

    def ready(self):
        from dj_raincheck import signals  # noqa: F401, PLC0415
