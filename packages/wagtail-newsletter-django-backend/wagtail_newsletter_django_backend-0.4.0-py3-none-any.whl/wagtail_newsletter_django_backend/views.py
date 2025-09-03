from contextlib import _RedirectStream
from typing import Any, override
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.http.response import HttpResponseRedirectBase
from django.urls import reverse
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from .forms import ManageForm
from django.shortcuts import get_object_or_404
from django.contrib import messages
from . import models

class ManageView(FormView):  # pyright: ignore[reportMissingTypeArgument]
    template_name = 'wagtail_newsletter_django_backend/manage.html'
    form_class = ManageForm

    def get_object(self):
        """Get the subscriber instance from the URL key parameter."""
        key = self.kwargs['key']
        return get_object_or_404(models.Subscriber, key=key)
    
    def get_form_kwargs(self):
        """Add the subscriber instance to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs
    
    def form_valid(self, form):
        """Save the form and redirect on success."""
        form.save()
        messages.success(self.request, 'Your subscription preferences have been updated successfully!')

        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect back to the same page after successful form submission."""
        return self.request.path

    def get(self, request: HttpRequest, *args, **kwargs):
        """Handle GET request and verify subscriber if needed."""
        subscriber = self.get_object()
        
        # Verify the subscriber if not already verified
        if not subscriber.verified:
            subscriber.verified = True
            subscriber.save(update_fields=['verified'])
            messages.success(request, 'Your email address has been successfully verified!')
        
        return super().get(request, *args, **kwargs)

class HttpResponseSeeOther(HttpResponseRedirectBase):
    status_code: int = 303

class UnsubscribeView(TemplateView):
    template_name = 'wagtail_newsletter_django_backend/unsubscribe.html'
    subscriber: models.Subscriber | None = None
    method: str | None = None

    @override
    def setup(self, request: HttpRequest, key: str, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.subscriber = models.Subscriber.objects.filter(key=key).first()
        self.method = request.method

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:  # pyright: ignore[reportAny]
        data = super().get_context_data(**kwargs)
        data['subscriber'] = self.subscriber
        if self.method:
            data['method'] = self.method.lower()
        return data

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if self.subscriber is not None:
            _ = self.subscriber.delete()
            self.subscriber = None
        messages.success(request, 'This subscriber has been successfully deleted')
        return HttpResponseSeeOther(reverse('wagtail_newsletter_django_backend:newsletter_subscriber_unsubscribe', args=args, kwargs=kwargs))
        
