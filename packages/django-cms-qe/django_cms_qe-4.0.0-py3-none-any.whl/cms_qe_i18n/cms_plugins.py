import re
from operator import itemgetter

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.conf import settings
from django.utils.translation import get_language, gettext_lazy as _


@plugin_pool.register_plugin
class LanguageSwitcherPlugin(CMSPluginBase):
    """
    CMS plugin allowing to add dynamically configured listing of any model.
    """

    name = _('Language switcher')
    render_template = 'cms_qe/i18n/language_switcher.html'
    text_enabled = True
    cache = True

    def render(self, context: dict, instance, placeholder) -> dict:
        context = super().render(context, instance, placeholder)
        context.update({
            'path': self.path_without_language(context),
            'language': get_language(),
            'languages': self.sorted_languages,
        })
        return context

    def path_without_language(self, context):
        return re.sub(r'^/[a-z]{2}/', '/', context['request'].path)

    @property
    def sorted_languages(self):
        return sorted(settings.LANGUAGES, key=itemgetter(0))
