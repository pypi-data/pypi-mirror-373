from collections.abc import Iterable
from typing import Any

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext as _

from cms_qe_newsletter.forms import SubscriberForm

from .models import NewsletterPluginModel


@plugin_pool.register_plugin
class NewsletterPlugin(CMSPluginBase):
    """
    Newsletter Django-CMS plugin. Allow add the form with subscriptions on a page.
    """
    model = NewsletterPluginModel
    name = _('Newsletter subscription form')
    render_template = 'cms_qe/newsletter/newsletter.html'
    fieldsets = [
        (None, {
            'fields': (
                'title',
                'mailing_lists',
                'fullname_show',
                'fullname_require',
            )
        })
    ]
    cache = False

    def render(self, context: dict[str, Any], instance: NewsletterPluginModel, placeholder) -> Iterable:
        request = context['request']
        if request.method == 'POST':
            form = SubscriberForm(fullname_require=instance.fullname_require, data=request.POST)
            if form.is_valid():
                form.save(mailing_lists=instance.mailing_lists.all())
                form.saved = True
        else:
            form = SubscriberForm(fullname_require=instance.fullname_require)
        context.update({
            'instance': instance,
            'form': form,
        })
        return context
