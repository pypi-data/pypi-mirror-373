"""
URL Configuration
https://docs.djangoproject.com/en/1.11/topics/http/urls/
"""

from django.urls import path

from .views import get_table_choices

urlpatterns = [
    path('cms-qe/table/data', get_table_choices, name='get_table_choices'),
]
