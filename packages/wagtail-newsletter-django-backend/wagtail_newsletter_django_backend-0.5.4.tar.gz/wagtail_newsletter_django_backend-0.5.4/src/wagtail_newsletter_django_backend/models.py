from collections.abc import Iterable, Sequence
from datetime import datetime
from functools import lru_cache
import hashlib
import hmac
from typing import TYPE_CHECKING, Any, LiteralString, NotRequired, TypedDict, Unpack, override, cast
from django.core.exceptions import ValidationError
from django.urls import reverse
from wagtail.models import Site
from django.db import models
from django.conf import settings
from email.utils import parseaddr, formataddr
import secrets
import string
from wagtail_newsletter import campaign_backends as wncb

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

@lru_cache
def _default_from_parts() -> tuple[str | None, str | None]:
    email = cast(str | None, settings.DEFAULT_FROM_EMAIL)
    name: str | None = None
    if email:
        name, email = parseaddr(email)
        email = email or None
        name = name or None
    return name, email

class SaveDict(TypedDict):
    force_insert: NotRequired[bool]
    force_update: NotRequired[bool]
    using: NotRequired[str]
    update_fields: NotRequired[Iterable[str]]

def patch_blanks(record: models.Model, update_fields: Iterable[str] | None, keys: Iterable[str]) -> None:
    '''Patch blank string fields to None.
    '''
    update_keys: Iterable[str]
    if update_fields is None:
        update_keys = keys
    else:
        update_keys = frozenset(update_fields) | frozenset(keys)

    # Change all blank string fields to NULL
    for key in update_keys:
        if getattr(record, key) == '':
            setattr(record, key, None)

class Audience(models.Model):
    pk: int
    id: int  # pyright: ignore[reportUninitializedInstanceVariable]
    audience_segment_set: 'RelatedManager[AudienceSegment]'  # pyright: ignore[reportUninitializedInstanceVariable]
    subscriber_set: 'RelatedManager[Subscriber]'  # pyright: ignore[reportUninitializedInstanceVariable]

    site: 'models.ForeignKey[Site]' = models.ForeignKey(Site, blank=False, null=False, on_delete=models.CASCADE)
    name: 'models.CharField[str]' = models.CharField(max_length=64, blank=False, null=False)
    description: 'models.TextField[str]' = models.TextField(blank=True, null=False)
    smtp_user: 'models.CharField[str | None]' = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        default=None,
        help_text='The SMTP login user.  If absent, this will not be supplied to send_mail, and EMAIL_HOST_USER will be used instead',
    )
    smtp_password: 'models.CharField[str | None]' = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        default=None,
        help_text='The SMTP login password.  If absent, this will not be supplied to send_mail, and EMAIL_HOST_PASSWORD will be used instead',
    )
    from_email_address: 'models.EmailField[str | None]' = models.EmailField(
        blank=True,
        null=True,
        default=None,
        help_text='The From address for the email.  If not present, this will not be supplied to send_mail, and DEFAULT_FROM_EMAIL will be used instead',
    )
    from_email_name: 'models.CharField[str | None]' = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        default=None,
        help_text='The display name portion of the from email.  This will be wrapped around the from email address.',
    )

    created_at: 'models.DateTimeField[datetime]' = models.DateTimeField(auto_now_add=True)
    updated_at: 'models.DateTimeField[datetime]' = models.DateTimeField(auto_now=True)

    class Meta:
        constraints: Sequence[models.UniqueConstraint] = (
            models.UniqueConstraint(
                fields=('site', 'name'),
                name='unique_site_name',
            ),
        )

    @override
    def __str__(self) -> str:
        return self.name

    _NULLABLE_FIELDS: Sequence[str] = ('smtp_user', 'smtp_password', 'from_email_address', 'from_email_name')

    @override
    def save(self, **kwargs: Unpack[SaveDict]) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        patch_blanks(self, kwargs.get('update_fields'), Audience._NULLABLE_FIELDS)
        return super().save(**kwargs)

    def from_address(self) -> str:
        default_from_name, default_from_email = _default_from_parts()
        from_email = self.from_email_address or default_from_email
        if from_email is None:
            raise RuntimeError('from email address must be set')
        from_name = self.from_email_name or default_from_name
        if from_name:
            return formataddr((from_name, from_email))
        else:
            return from_email

    def smtp_auth(self) -> tuple[str, str]:
        smtp_user = self.smtp_user or cast(str | None, settings.EMAIL_HOST_USER)
        smtp_password = self.smtp_password or cast(str | None, settings.EMAIL_HOST_PASSWORD)
        if smtp_user is None:
            raise RuntimeError('smtp_user must be set')

        if smtp_password is None:
            raise RuntimeError('smtp_password must be set')

        return smtp_user, smtp_password

class AudienceSegment(models.Model):
    pk: int
    id: int  # pyright: ignore[reportUninitializedInstanceVariable]

    audience: 'models.ForeignKey[Audience]' = models.ForeignKey(Audience, blank=False, null=False, on_delete=models.CASCADE, related_name='audience_segment_set', related_query_name='audience_segment')
    name: 'models.CharField[str]' = models.CharField(max_length=64, blank=False, null=False, unique=True)
    description: 'models.TextField[str]' = models.TextField(blank=True, null=False)
    subscribers: 'models.ManyToManyField[Subscriber, Subscription]' = models.ManyToManyField(
        'Subscriber',
        through='Subscription',
        related_name='+',
    )

    created_at: 'models.DateTimeField[datetime]' = models.DateTimeField(auto_now_add=True)
    updated_at: 'models.DateTimeField[datetime]' = models.DateTimeField(auto_now=True)

    class Meta:
        constraints: Sequence[models.UniqueConstraint] = (
            models.UniqueConstraint(
                fields=('audience', 'name'),
                name='unique_audience_name',
            ),
        )

    @override
    def __str__(self) -> str:
        return self.name

_SUBSCRIBER_KEY_CHARS: LiteralString = string.ascii_letters + string.digits

def generate_subscriber_key() -> str:
    return ''.join(secrets.choice(_SUBSCRIBER_KEY_CHARS) for _ in range(64))

class Subscriber(models.Model):
    key: models.CharField[str] = models.CharField(
        max_length=64,
        blank=False,
        null=False,
        default=generate_subscriber_key,
        help_text="The subscriber's lookup key for managing subscriptions",
        unique=True,
    )
    audience: 'models.ForeignKey[Audience]' = models.ForeignKey(Audience, blank=False, null=False, on_delete=models.CASCADE)
    email_address: 'models.EmailField[str]' = models.EmailField(verbose_name="Email Address", blank=False, null=False)
    email_name: 'models.CharField[str | None]' = models.CharField(
        verbose_name="Name",
        max_length=256,
        blank=True,
        null=True,
        default=None,
    )
    audience_segments: 'models.ManyToManyField[AudienceSegment, Subscription]' = models.ManyToManyField(
        AudienceSegment,
        through='Subscription',
        related_name='+',
    )
    verified: models.BooleanField[bool] = models.BooleanField(blank=False, null=False, default=False)
    created_at: 'models.DateTimeField[datetime]' = models.DateTimeField(auto_now_add=True)
    updated_at: 'models.DateTimeField[datetime]' = models.DateTimeField(auto_now=True)

    sent_message_set: 'RelatedManager[SentMessage]'  # pyright: ignore[reportUninitializedInstanceVariable]

    @override
    def __str__(self) -> str:
        return self.email()

    def email(self) -> str:
        if self.email_name:
            return formataddr((self.email_name, self.email_address))
        else:
            return self.email_address

    def pii_hash(self) -> str:
        normalized = self.email_address.lower().strip().encode('utf-8')
        key = cast(str, settings.PII_HASHING_SALT).encode('utf-8')
        return hmac.new(key, normalized, hashlib.sha256).hexdigest()

    class Meta:
        constraints: Sequence[models.UniqueConstraint] = (
            models.UniqueConstraint(
                fields=('audience', 'email_address'),
                name='unique_audience_email_address',
            ),
        )

    _NULLABLE_FIELDS: Sequence[str] = ('email_name',)

    @override
    def save(self, **kwargs: Unpack[SaveDict]) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        patch_blanks(self, kwargs.get('update_fields'), Subscriber._NULLABLE_FIELDS)
        return super().save(**kwargs)

class Subscription(models.Model):
    audience_segment: 'models.ForeignKey[AudienceSegment]' = models.ForeignKey(AudienceSegment, on_delete=models.CASCADE)
    subscriber: 'models.ForeignKey[Subscriber]' = models.ForeignKey(Subscriber, on_delete=models.CASCADE)

    created_at: 'models.DateTimeField[datetime]' = models.DateTimeField(auto_now_add=True)
    updated_at: 'models.DateTimeField[datetime]' = models.DateTimeField(auto_now=True)

    class Meta:
        constraints: Sequence[models.UniqueConstraint] = (
            models.UniqueConstraint(
                fields=['audience_segment', 'subscriber'],
                name='unique_audience_segment_subscriber',
            ),
        )

    @override
    def __str__(self) -> str:
        return f'{self.subscriber} -> {self.audience_segment}'

    @override
    def clean(self) -> None:
        if self.audience_segment.audience != self.subscriber.audience:
            raise ValidationError('The audience_segment and subscriber must have the same audience')

class Campaign(models.Model):
    pk: int
    id: int # pyright: ignore[reportUninitializedInstanceVariable]

    send_at: 'models.DateTimeField[datetime | None]' = models.DateTimeField(blank=True, null=True, default=None)
    sent_at: 'models.DateTimeField[datetime | None]' = models.DateTimeField(blank=True, null=True, default=None)
    subject: 'models.TextField[str]' = models.TextField(blank=False, null=False)
    html: 'models.TextField[str]' = models.TextField(blank=False, null=False)
    audience_segment: models.ForeignKey[AudienceSegment] = models.ForeignKey(AudienceSegment, blank=False, null=False, on_delete=models.CASCADE)

    created_at: 'models.DateTimeField[datetime]' = models.DateTimeField(auto_now_add=True)
    updated_at: 'models.DateTimeField[datetime]' = models.DateTimeField(auto_now=True)

    @property
    def is_sent(self) -> bool:
        return self.sent_at is not None

    @property
    def is_scheduled(self) -> bool:
        return self.sent_at is None and self.send_at is not None

    @property
    def url(self) -> str:
        return reverse('campaign:edit', args=[self.pk])

    @property
    def status(self) -> str:
        if self.sent_at is not None:
            return 'Sent'
        elif self.send_at is not None:
            return 'Scheduled'
        else:
            return 'Saved'

    def get_report(self) -> dict[str, Any]:
        report = {
            'id': self.id,
            'emails_sent': SentMessage.objects.filter(campaign=self).count(),
            'send_time': self.sent_at,
            'bounces': 0,
            'delivery_status': {
                'status': 'poop',
            },
        }
        if self.send_at is not None:
            report['send_time'] = self.send_at
        return report

    @override
    def __str__(self) -> str:
        return self.subject

_ = wncb.Campaign.register(Campaign)

class SentMessage(models.Model):
    pk: int
    id: int # pyright: ignore[reportUninitializedInstanceVariable]

    # Null if the subscriber has unsubscribed, deleting their email address
    campaign: 'models.ForeignKey[Campaign]' = models.ForeignKey(Campaign, blank=False, null=False, on_delete=models.CASCADE, related_name='sent_message_set', related_query_name='sent_message')
    subscriber: 'models.ForeignKey[Subscriber | None]' = models.ForeignKey(Subscriber, blank=True, null=True, on_delete=models.SET_NULL, related_name='sent_message_set', related_query_name='sent_message')
    subscriber_hash: 'models.CharField[str]' = models.CharField(max_length = 64, null=False, blank=False, db_index=True)

    created_at: 'models.DateTimeField[datetime]' = models.DateTimeField(auto_now_add=True)
    updated_at: 'models.DateTimeField[datetime]' = models.DateTimeField(auto_now=True)

    @override
    def save(self, **kwargs: Unpack[SaveDict]) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if self.subscriber is not None and self.subscriber_hash is None:  # pyright: ignore[reportUnnecessaryComparison]
            self.subscriber_hash = self.subscriber.pii_hash()
        super().save(**kwargs)
