from typing import final
from django.apps import AppConfig

@final
class WagtailNewsletterDjangoBackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wagtail_newsletter_django_backend'
    verbose_name = 'Wagtail Newsletter Django Backend'
