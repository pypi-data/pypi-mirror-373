from typing import override
from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "demo.blog"

    @override
    def ready(self):
        from . import signals
