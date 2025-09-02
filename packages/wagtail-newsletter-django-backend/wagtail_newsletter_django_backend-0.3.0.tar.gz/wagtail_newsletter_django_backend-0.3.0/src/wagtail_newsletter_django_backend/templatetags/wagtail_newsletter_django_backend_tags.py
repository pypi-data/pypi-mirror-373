from django import template

from wagtail_newsletter_django_backend.forms import ManageForm

register = template.Library()

@register.inclusion_tag("wagtail_newsletter_django_backend/manage_tag.html")
def subscriber_manage_form(subscriber):
    return {
        'form': ManageForm(instance=subscriber),
    }

@register.inclusion_tag("wagtail_newsletter_django_backend/unsubscribe_tag.html")
def subscriber_unsubscribe_form(subscriber):
    return {
        'subscriber': subscriber,
    }
