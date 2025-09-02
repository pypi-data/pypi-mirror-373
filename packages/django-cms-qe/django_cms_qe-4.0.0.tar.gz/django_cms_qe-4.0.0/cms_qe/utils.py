from collections.abc import Iterable
from importlib import import_module
from typing import Optional, Union

from django.apps import apps
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import get_template


# pylint:disable=invalid-name
def get_email(template: str, subject: str, to: Union[str, Iterable[str]], from_email: Optional[str] = None, **kwargs):
    """
    Returns a ``EmailMultiAlternatives`` instance from  ``django.core.mail``.

    Template should be without extension and you should create both ``.txt`` and ``.html`` version.
    Second one is not mandatory but is good to provide it as well.

    """
    template_txt = get_template(template + '.txt')

    msg = EmailMultiAlternatives(
        subject,
        template_txt.render(kwargs),
        from_email or settings.DEFAULT_FROM_EMAIL,
        [to] if isinstance(to, str) else to,
    )
    try:
        template_html = get_template(template + '.html')
        msg.attach_alternative(template_html.render(kwargs), "text/html")
    except TemplateDoesNotExist:
        pass

    return msg


def get_base_url(request) -> str:
    """
    Helper to get absolute URL of application. It requires to set
    correctly domain of site framework.
    """
    protocol = settings.META_SITE_PROTOCOL
    domain = get_current_site(request)
    return f'{protocol}://{domain}'


def get_functions(module_name: str, function_name: str) -> Iterable[tuple[str, object]]:
    """
    Get function by ``function_name`` of ``module_name`` for every installed
    Django app. Returns tuple of ``app_name`` and ``function``. Example usage:

    .. code-block:: python

        for app, func in get_functions('monitoring', 'get_status'):
            # ...
    """
    for app_name, module in get_modules(module_name):
        function = getattr(module, function_name, None)
        if function:
            yield (app_name, function)


def get_modules(module_name: str) -> Iterable[tuple[str, object]]:
    """
    Get module by ``module_name`` for every installed Django app.
    Returns tuple of ``app_name`` and ``module``. Example usage:

    .. code-block:: python

        for app, module in get_modules('models'):
            # ...
    """
    for app in apps.get_app_configs():
        module = get_module(app.name, module_name)
        if module:
            yield (app.name, module)


def get_module(app_name: str, module_name: str) -> object:
    """
    Helper to load module by ``module_name`` of Django app ``app_name``.
    Returns ``None`` if module does not exist.
    """
    import_module(app_name)  # The app has to exists.
    module_name = f'{app_name}.{module_name}'
    try:
        return import_module(module_name)
    except ImportError:
        return None
