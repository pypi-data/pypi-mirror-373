from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from .models import MenuPluginModel


@plugin_pool.register_plugin
class MenuPlugin(CMSPluginBase):
    """
    CMS plugin allowing to add menu at any place.
    """

    model = MenuPluginModel
    module = _('Menu')
    name = _('Menu')
    render_template = 'cms_qe/menu/menu_tag.html'
    cache = False
