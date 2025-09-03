from typing import final
from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup
from .models import Audience, AudienceSegment, Subscriber, Campaign

@final
class AudienceViewSet(ModelViewSet):
    model = Audience
    form_fields = ['site', 'name', 'description', 'smtp_user', 'smtp_password', 'from_email_address', 'from_email_name']
    list_display = ['site', 'name', 'description']  # pyright: ignore[reportAssignmentType]
    icon = 'group'
    add_to_admin_menu = False
    copy_view_enabled = True
    inspect_view_enabled = True

@final
class AudienceSegmentViewSet(ModelViewSet):
    model = AudienceSegment
    form_fields = ['name', 'audience', 'description']
    list_display = ['name', 'audience', 'description']  # pyright: ignore[reportAssignmentType]
    icon = 'tag'
    add_to_admin_menu = False
    copy_view_enabled = True
    inspect_view_enabled = True

@final
class SubscriberViewSet(ModelViewSet):
    model = Subscriber
    form_fields = ['email_address', 'email_name', 'audience', 'audience_segments']
    list_display = ['email_address', 'email_name', 'audience']  # pyright: ignore[reportAssignmentType]
    icon = 'user'
    add_to_admin_menu = False
    copy_view_enabled = True
    inspect_view_enabled = True

@final
class CampaignViewSet(ModelViewSet):
    model = Campaign
    form_fields = ['subject', 'audience_segment', 'send_at', 'sent_at', 'html']
    list_display = ['subject', 'audience_segment']  # pyright: ignore[reportAssignmentType]
    icon = 'mail'
    add_to_admin_menu = False
    copy_view_enabled = True
    inspect_view_enabled = True

@final
class MailingListGroup(ModelViewSetGroup):
    items = (
        AudienceViewSet('audiences'),
        AudienceSegmentViewSet('audience_segments'),
        SubscriberViewSet('subscribers'),
        CampaignViewSet('campaign'),
    )
    menu_icon = 'mail'
    menu_label = 'Mailing List'  # pyright: ignore[reportAssignmentType]

mailing_list_group = MailingListGroup()

# Create your views here.
