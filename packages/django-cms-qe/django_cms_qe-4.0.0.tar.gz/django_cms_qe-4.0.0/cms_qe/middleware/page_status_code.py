"""
Use in MIDDLEWARE:
    cms_qe.middleware.page_status_code.restore_status_for_cached_error_page
"""
from typing import Callable

from django.http import HttpRequest, HttpResponse

from ..constants import QE_STATUS_CODE


def restore_status_for_cached_error_page(get_response: Callable) -> Callable:
    """Set middleware for restoring status code of error page."""

    def middleware(request: HttpRequest) -> HttpResponse:
        """Restore page status code saved into the page headers."""
        response = get_response(request)
        status_code = response.get(QE_STATUS_CODE) if hasattr(response, 'headers') else None
        if status_code is not None:
            response.status_code = int(status_code)
            del response[QE_STATUS_CODE]
        return response

    return middleware
