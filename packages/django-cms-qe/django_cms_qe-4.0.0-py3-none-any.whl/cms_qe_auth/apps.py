from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthConfig(AppConfig):
    name = 'cms_qe_auth'
    verbose_name = _('CMS QE Authentiaction')
