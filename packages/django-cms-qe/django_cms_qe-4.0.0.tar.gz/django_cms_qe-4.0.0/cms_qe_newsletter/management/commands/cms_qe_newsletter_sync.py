from django.core.management.base import BaseCommand

from cms_qe_newsletter import logger
from cms_qe_newsletter.external_services.sync import sync_tasks


class Command(BaseCommand):
    """
    Command processes the queue to subscribing and unsubscribing
    on the external services. Usage of command with ``manage.py``::

        python -m manage.py cms_qe_newsletter_sync
    """

    def handle(self, *args, **options):
        logger.info('Newsletter sync started...')

        for task_result, task_message in sync_tasks():
            if task_result is None:
                logger.warning(task_message)
            elif task_result is False:
                logger.error(task_message)
            else:
                logger.info(task_message)

        logger.info('Newsletter sync finished...')
