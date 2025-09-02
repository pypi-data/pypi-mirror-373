from django.apps import AppConfig


class CmsQEConfig(AppConfig):
    name = 'cms_qe'

    def ready(self):
        from cms.signals import urls_need_reloading  # pylint: disable=import-outside-toplevel

        from .signals import reload_site  # pylint: disable=import-outside-toplevel

        urls_need_reloading.connect(reload_site)
