from datetime import datetime
from typing import Any, cast, override
from django.db import transaction
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from html2text import HTML2Text
from django.core.mail import get_connection
from django.core.mail.message import EmailMessage, EmailMultiAlternatives
from wagtail_newsletter import campaign_backends as wncb, audiences as wna, models as wnm
import re
from . import models

_unsubscribe_re = re.compile(r'\[\[unsubscribe\]\]|\\[\\[unsubscribe\\]\\]')
_manage_re = re.compile(r'\[\[manage\]\]|\\[\\[manage\\]\\]')

h2t = HTML2Text()
class CampaignBackend(wncb.CampaignBackend):
    name: str = 'Django Backend'

    @override
    def get_audiences(self) -> "list[wna.Audience]":
        return [
            wna.Audience(
                id=str(audience.id),
                pk=str(audience.pk),
                name=audience.name,
                member_count=audience.subscriber_set.count(),
            )
            for audience in models.Audience.objects.all()
        ]

    @override
    def get_audience_segments(
        self,
        audience_id: str
    ) -> "list[wna.AudienceSegment]":
        audience = models.Audience.objects.get(id=int(audience_id))
        return [
            wna.AudienceSegment(
                id=str(audience_segment.id),
                pk=str(audience_segment.pk),
                name=audience_segment.name,
                member_count=audience_segment.subscribers.count(),
            )
            for audience_segment in audience.audience_segment_set.all()
        ]

    @override
    def save_campaign(
        self,
        *,
        campaign_id: str | None = None,
        recipients: "wnm.NewsletterRecipientsBase | None",
        subject: str,
        html: str,
    ) -> str:
        audience_segment: models.AudienceSegment | None = None
        if recipients is not None and recipients.segment:
            audience_segment = models.AudienceSegment.objects.get(id=int(recipients.segment))

        with transaction.atomic():
            campaign: models.Campaign
            if campaign_id:
                campaign = models.Campaign.objects.get(id=int(campaign_id))
                campaign.subject = subject
                campaign.html = html.strip()
                if audience_segment is not None:
                    campaign.audience_segment = audience_segment
                campaign.full_clean()
                campaign.save()
            else:
                campaign = models.Campaign.objects.create(
                    subject=subject,
                    html=html.strip(),
                    audience_segment=audience_segment,
                )
            return str(campaign.id)

    @override
    def get_campaign(self, campaign_id: str) -> wncb.Campaign | None:
        return cast('wncb.Campaign | None', models.Campaign.objects.filter(id=int(campaign_id)).first())

    @override
    def send_test_email(self, *, campaign_id: str, email: str) -> None:
        campaign = models.Campaign.objects.get(id=int(campaign_id))
        audience = campaign.audience_segment.audience

        from_address = audience.from_address()
        user, password = audience.smtp_auth()

        _ = send_mail(
            subject=campaign.subject,
            message=h2t.handle(campaign.html),
            from_email=from_address,
            recipient_list=[email],
            html_message=campaign.html,
            auth_user=user,
            auth_password=password,
        )

    @override
    def send_campaign(self, campaign_id: str) -> None:
        with transaction.atomic():
            campaign = models.Campaign.objects.get(id=int(campaign_id))
            audience = campaign.audience_segment.audience

            site = audience.site
            hostname = site.hostname
            match site.port:
                case 80:
                    url_base = f'http://{hostname}'
                case 443:
                    url_base = f'https://{hostname}'
                case port:
                    url_base = f'http://{hostname}:{port}'

            from_address = audience.from_address()
            user, password = audience.smtp_auth()

            connection: Any = get_connection(  # pyright: ignore[reportAny]
                username=user,
                password=password,
            )

            def subscriber_message(subscriber: models.Subscriber) -> EmailMessage:
                unsubscribe_url = url_base + reverse('wagtail_newsletter_django_backend:newsletter_subscriber_unsubscribe', kwargs={'key': subscriber.key})
                manage_url = url_base + reverse('wagtail_newsletter_django_backend:newsletter_subscriber_manage', kwargs={'key': subscriber.key})
                html = _manage_re.sub(manage_url, _unsubscribe_re.sub(unsubscribe_url, campaign.html))
                message = h2t.handle(html)
                mail = EmailMultiAlternatives(
                    subject=campaign.subject,
                    body=message,
                    from_email=from_address,
                    to=[subscriber.email()],
                    connection=connection,  # pyright: ignore[reportAny]
                    headers={
                        "List-Unsubscribe": unsubscribe_url,
                        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
                    },
                )
                mail.attach_alternative(html, "text/html")
                return mail

            messages = [
                subscriber_message(subscriber)
                for subscriber in campaign.audience_segment.subscribers.filter(verified=True)
            ]

            _ = connection.send_messages(messages)  # pyright: ignore[reportAny]
            campaign.sent_at = timezone.now()
            campaign.save()
            _ = models.SentMessage.objects.bulk_create([
                models.SentMessage(
                    campaign=campaign,
                    subscriber=subscriber,
                    subscriber_hash=subscriber.pii_hash(),
                )
                for subscriber in campaign.audience_segment.subscribers.filter(verified=True)
            ])

    def send_scheduled_campaigns(self) -> None:
        for campaign in models.Campaign.objects.filter(sent_at=None, send_at__gte=timezone.now()):
            self.send_campaign(str(campaign.id))

    @override
    def schedule_campaign(self, campaign_id: str, schedule_time: datetime) -> None:
        with transaction.atomic():
            campaign = models.Campaign.objects.get(id=int(campaign_id))
            campaign.send_at = schedule_time
            campaign.full_clean()
            campaign.save()

    @override
    def unschedule_campaign(self, campaign_id: str) -> None:
        with transaction.atomic():
            campaign = models.Campaign.objects.get(id=int(campaign_id))
            campaign.send_at = None
            campaign.full_clean()
            campaign.save()
