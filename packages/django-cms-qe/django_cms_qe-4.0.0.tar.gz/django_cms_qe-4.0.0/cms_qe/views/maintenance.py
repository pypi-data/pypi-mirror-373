from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.utils.module_loading import import_string
from django.views import View

from cms_qe.signals import run_subprocess


class HealthCheckView(View):
    """Health check View."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Apply HTTP GET. Used by uwsgi in docker."""
        # Check database connection.
        site = Site.objects.first()
        if not site.domain:
            raise RuntimeError('db')
        # Check cache.
        key = 'health-check-test'
        cache.set(key, 'OK', 2)
        if cache.get(key) != 'OK':
            raise RuntimeError('cache')
        # More checks if defined in HEALTHCHECK_FUNCTIONS = ["path1.to.fnc, "path2.to.fnc"].
        if hasattr(settings, "HEALTHCHECK_FUNCTIONS"):
            for path in settings.HEALTHCHECK_FUNCTIONS:
                fnc = import_string(path)
                fnc(request, *args, **kwargs)
        return HttpResponse("OK", content_type="text/plain")


class ReloadSiteView(View):
    """Reload site View."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Run subprocess defined in settings."""
        if request.user.is_superuser:
            if settings.RELOAD_SITE:
                msg = str(run_subprocess(settings.RELOAD_SITE))
            else:
                msg = "SKIP: No settings.RELOAD_SITE."
        else:
            msg = "ERROR: User is not is_superuser."
        return HttpResponse(msg, content_type="text/plain")
