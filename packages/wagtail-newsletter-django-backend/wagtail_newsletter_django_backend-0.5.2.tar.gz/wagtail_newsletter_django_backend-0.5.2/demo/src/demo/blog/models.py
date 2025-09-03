from django.contrib import messages
from django.db import models
from django.shortcuts import redirect
from django.conf import settings
from wagtail import models as wt_models
from wagtail import fields as wt_fields
from wagtail.models.pages import HttpRequest, HttpResponse
from wagtail_newsletter.models import NewsletterPageMixin
import requests
from wagtail_newsletter_django_backend.forms import SignupForm
from wagtail_newsletter_django_backend.models import Audience, Subscriber

class BlogIndexPage(wt_models.Page):
    intro = wt_fields.RichTextField(blank=True)

    content_panels = wt_models.Page.content_panels + ["intro"]

class BlogPage(NewsletterPageMixin, wt_models.Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = wt_fields.RichTextField(blank=True)

    content_panels = wt_models.Page.content_panels + ["date", "intro", "body"]

    newsletter_template = 'blog/blog_page_newsletter.html'

class NewsletterSignup(wt_models.Page):
    intro = wt_fields.RichTextField(blank=True)

    audience = models.ForeignKey(Audience, blank=False, null=False, on_delete=models.CASCADE)

    content_panels = wt_models.Page.content_panels + ["intro", 'audience']

    form: SignupForm | None = None

    def serve(self, request: HttpRequest) -> HttpResponse:
        if request.method != 'POST':
            self.form = SignupForm(initial={'audience': self.audience}, audience=self.audience)
            return super().serve(request=request)
        self.form = SignupForm(request.POST, audience=self.audience)
        token = request.POST['h-captcha-response']
        params = {
           "secret": settings.HCAPTCHA_SECRET,
           "response": token
        }
        # TODO: add remoteip: https://docs.hcaptcha.com/#server
        response = requests.post("https://hcaptcha.com/siteverify", data=params)
        response.raise_for_status()
        data = response.json()
        if data['success']:
            if self.form.is_valid():
                _ = self.form.save()
                messages.success(request, 'You have successfully signed up for the newsletter, and a welcome email has been sent.  You will not receive any messages until you validate your email address.')
            else:
                messages.error(request, 'form failed validation')
        else:
            messages.error(request, 'Captcha validation failed.  Error codes: ' + '\n'.join(data['error-codes']))
        return super().serve(request=request)

    def hcaptcha_site_id(self):
        return settings.HCAPTCHA_SITE_ID

