from django.conf import settings
from django.urls import path
from django.views.static import serve

from cms_qe.urls import handler403, handler404, handler500, handler503, urlpatterns


def serve_favicon(request):
    """Serve favicon.ico."""
    return serve(request, 'favicon.ico', settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += [
        path('favicon.ico', serve_favicon),
    ]
