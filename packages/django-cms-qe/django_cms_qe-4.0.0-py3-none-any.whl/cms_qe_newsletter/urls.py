"""
URL Configuration
https://docs.djangoproject.com/en/1.11/topics/http/urls/
"""

from django.urls import path

from .views import update_lists

urlpatterns = [
    path('cms-qe/newsletter/sync-lists', update_lists, name='sync_mailing_lists'),
]
