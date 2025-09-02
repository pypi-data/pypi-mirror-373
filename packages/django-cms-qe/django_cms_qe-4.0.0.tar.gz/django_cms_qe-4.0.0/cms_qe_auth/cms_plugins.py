from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _


@plugin_pool.register_plugin
class LoginButtonPlugin(CMSPluginBase):
    """
    CMS plugin showing link to login or logout.
    """

    module = _('Auth')
    name = _('Login button')
    render_template = 'cms_qe/auth/login_button_plugin.html'
    text_enabled = True
    cache = False


@plugin_pool.register_plugin
class LoginFormPlugin(CMSPluginBase):
    """
    CMS plugin allowing the user to log into site.
    """

    module = _('Auth')
    name = _('Login form')
    render_template = 'cms_qe/auth/login_form_plugin.html'
    cache = False

    def render(self, context: dict, instance: CMSPlugin, placeholder) -> dict:
        context = super().render(context, instance, placeholder)
        context.update({
            'form': AuthenticationForm(),
        })
        return context


@plugin_pool.register_plugin
class RegisterFormPlugin(CMSPluginBase):
    """
    CMS plugin allowing the user to register into site.
    """

    module = _('Auth')
    name = _('Register form')
    render_template = 'cms_qe/auth/register_plugin.html'
    cache = False

    def render(self, context: dict, instance: CMSPlugin, placeholder) -> dict:
        context = super().render(context, instance, placeholder)
        context.update({
            'form': UserCreationForm(),
        })
        return context
