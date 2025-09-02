import logging
from typing import Callable

from cms.views import details
from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.http.response import HttpResponseBase
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.csrf import requires_csrf_token

from ..constants import QE_STATUS_CODE

__all__ = ('handler403', 'handler404', 'handler500', 'handler503', 'get_error_handler')


def get_error_handler(code: int) -> Callable[[HttpRequest], HttpResponseBase]:
    """
    Decorator creating error handler for specific HTTP status code.

    When CMS page with slug ``errorCODE`` exists, then is shown that
    page, otherwise generic one. Page is not cached because of that.

    Possible slugs:

     * error403 (forbidden)
     * error404 (not found)
     * error503 (service unavailable)
    """

    # pylint: disable=missing-docstring,unused-argument
    # https://docs.djangoproject.com/en/1.11/ref/csrf/#csrfviewmiddleware-process-view-not-used
    @requires_csrf_token
    def error_handler(request: HttpRequest, *args, **kwds) -> HttpResponseBase:
        slug = f'error{code}'

        if hasattr(request, '_current_page_cache'):
            delattr(request, '_current_page_cache')

        try:
            response = details(request, slug)
        except Http404:
            response = render(request, 'cms_qe/error.html', context={'slug': slug})

        # Save page status code into the page headers for later restore in middleware when page is cached.
        response[QE_STATUS_CODE] = code

        # In debug any response with status_code 404 is transformed to Django error
        # page and is not possible to check that page. We want to be able to check
        # not found page in debug as well.
        if response and not settings.DEBUG:
            response.status_code = code

        return response

    return error_handler


# pylint: disable=invalid-name
handler403 = get_error_handler(403)
handler404 = get_error_handler(404)
handler503 = get_error_handler(503)


@requires_csrf_token
def handler500(request: HttpRequest) -> HttpResponseBase:
    """
    When application fail on internal error, Django CMS has problem
    to render any page. They don't have any API for rendering any page
    so it's impossible to get it right. Solution could be just redirect
    to page with given slug but it could also hang in infinite loop of
    redirection if there would be problem on page with slug error500.

    That's why we simply just use different template which cannot be
    changed in admin by user. To override default template, just create
    your own ``cms_qe/internal_error.html`` or change ``handler500``
    to your own view.
    """
    try:
        return render(request, 'cms_qe/internal_error.html', status=500)
    except Exception:  # pylint: disable=broad-except
        logging.exception('Exception while rendering page 500')
        title, message = _('Internal error'), _('Something went very wrong. Please try again later.')
        return HttpResponse(f'<h1>{title}</h1><p>{message}</p>', status=500)
