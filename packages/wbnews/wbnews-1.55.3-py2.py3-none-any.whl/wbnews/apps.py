from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class NewConfig(AppConfig):
    name = "wbnews"

    def ready(self) -> None:
        autodiscover_modules("news")
