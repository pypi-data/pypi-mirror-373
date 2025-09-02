import json
import logging
from typing import Any

from constance import config
from django.http import Http404, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import View

__all__ = ('csp_report',)


@csrf_exempt
@require_POST
def csp_report(request: HttpRequest) -> HttpResponse:
    """
    View handling reports by CSP headers. When there is problem by CSP,
    then browser fire request to this view with JSON data describing
    problem. It's simply just logged as warning for later analyzing.
    """
    data = request.read()
    data = json.loads(str(data, 'utf8', 'replace'))
    logging.warning(data)
    return HttpResponse('OK')


class SecurityTxtView(View):
    """Provide file security.txt."""

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Serve content of security.txt."""
        if not config.SECURITY_TXT_CONTENT:
            raise Http404()
        return HttpResponse(config.SECURITY_TXT_CONTENT, content_type="text/plain")
