from django.core.management.base import BaseCommand, CommandError
from wagtail_newsletter_django_backend.campaign_backend import CampaignBackend

class Command(BaseCommand):
    help = "Sends scheduled campaigns that are due"

    def handle(self, *args, **options):
        CampaignBackend().send_scheduled_campaigns()
