from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from .forms import TablePluginForm
from .models import TablePluginModel


@plugin_pool.register_plugin
class TablePlugin(CMSPluginBase):
    """
    CMS plugin allowing to add dynamically configured listing of any model.
    """

    form = TablePluginForm
    model = TablePluginModel
    name = _('Table')
    render_template = 'cms_qe/table/table.html'
    cache = False

    def render(self, context: dict, instance: TablePluginModel, placeholder) -> dict:
        context = super().render(context, instance, placeholder)
        if instance.table_exists and instance.columns_exist:
            page_param_name = f'page_{instance.pk}'
            page = context['request'].GET.get(page_param_name, None)
            context.update({
                'header': instance.get_header(),
                'items': instance.get_items(page),
                'page_param_name': page_param_name,
            })
        return context
