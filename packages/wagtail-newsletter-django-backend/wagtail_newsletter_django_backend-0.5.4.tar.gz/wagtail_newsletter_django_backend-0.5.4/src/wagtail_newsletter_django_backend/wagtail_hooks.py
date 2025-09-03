from wagtail import hooks
from .admin_viewsets import MailingListGroup, mailing_list_group

@hooks.register('register_admin_viewset')  # pyright: ignore[reportOptionalCall, reportUntypedFunctionDecorator, reportUnknownMemberType]
def register_viewset() -> MailingListGroup:
    return mailing_list_group

