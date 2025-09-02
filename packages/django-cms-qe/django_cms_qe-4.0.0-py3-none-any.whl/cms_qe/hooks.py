from types import MethodType

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.db import InternalError, connection
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from djangocms_alias.models import AliasContent
from menus.menu_pool import MenuRenderer, menu_pool


def pg_is_in_recovery():
    """Return True when database is slave or False when database is master."""
    with connection.cursor() as cursor:
        if cursor.db.vendor != 'postgresql':
            return False
        cursor.execute("SELECT pg_is_in_recovery()")
        return cursor.fetchone()[0]


class PgIsInRecoveryLoginView(LoginView):
    template_name = 'admin/login.html'
    url_page_name = "login"

    def get(self, request, *args, **kwargs):
        if pg_is_in_recovery():
            messages.add_message(request, messages.WARNING,
                                 _('The database is in recovery mode. Unable to login. Try it later.'))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if pg_is_in_recovery():
            messages.add_message(request, messages.ERROR, _('Login failed. The database is in recovery mode.'))
            return HttpResponseRedirect(reverse(self.url_page_name))
        return super().post(request, *args, **kwargs)

    def get_template_names(self):
        if pg_is_in_recovery():
            return ['pg_is_in_recovery_login.html']
        return self.template_name


class PgIsInRecoveryMenuRenderer(MenuRenderer):

    def get_nodes(self, namespace=None, root_id=None, breadcrumb=False):
        try:
            return super().get_nodes(namespace, root_id, breadcrumb)
        except InternalError:
            if pg_is_in_recovery():
                return []
            raise


def render_alias_content(request: HttpRequest, alias_content: AliasContent) -> TemplateResponse:
    """Render alias content with additionad css class alias-$name.

    This is the same function as on the url
    https://github.com/django-cms/djangocms-alias/blob/master/djangocms_alias/rendering.py#L4,
    it just uses a different template. In the template, a css class is added by the alias name.
    This is necessary so that the appropriate styles can be linked to it.
    """
    template = "cms_qe/alias_content_preview.html"
    context = {
        "alias_content": alias_content,
        "site_styles": settings.STYLES_FOR_ALIAS_ADMIN_PREVIEW,
    }
    return TemplateResponse(request, template, context)


def get_renderer(self, request: HttpRequest) -> PgIsInRecoveryMenuRenderer:
    self.discover_menus()
    return PgIsInRecoveryMenuRenderer(pool=self, request=request)


def patch_menu_pool_cachekey():
    """Skip exception when MenuRenderer attempts to write to read only database."""
    menu_pool.get_renderer = MethodType(get_renderer, menu_pool)


def patch_alias():
    """Patch alias template preview."""
    try:
        extension = apps.get_app_config('cms').cms_extension
        extension.toolbar_enabled_models[AliasContent] = render_alias_content
    except KeyError:
        pass
