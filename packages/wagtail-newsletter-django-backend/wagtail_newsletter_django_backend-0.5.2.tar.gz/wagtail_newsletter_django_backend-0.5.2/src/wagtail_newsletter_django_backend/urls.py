# from django.contrib import admin
# from django.urls import include, path
# from wagtail.admin import urls as wagtailadmin_urls
# from wagtail import urls as wagtail_urls
# from wagtail.documents import urls as wagtaildocs_urls

from django.urls import path
from wagtail_newsletter_django_backend import views


app_name = 'wagtail_newsletter_django_backend'
urlpatterns = [
    # The manage and verify route
    path('manage/<str:key>/', views.ManageView.as_view(), name='newsletter_subscriber_manage'),
    path('unsubscribe/<str:key>/', views.UnsubscribeView.as_view(), name='newsletter_subscriber_unsubscribe'),
]

