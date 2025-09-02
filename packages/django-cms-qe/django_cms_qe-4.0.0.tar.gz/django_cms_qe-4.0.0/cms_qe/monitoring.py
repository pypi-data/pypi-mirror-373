from django.conf import settings
from django.core.cache import cache
from django.db import connections
from django.db.utils import OperationalError


def get_status():
    return {
        'database': check_database(),
        'cache': check_cache(),
    }


def check_database():
    db_conn = connections['default']
    try:
        db_conn.cursor()
    except OperationalError:
        connected = False
    else:
        connected = True
    return connected


def check_cache():
    if 'DummyCache' in settings.CACHES['default']['BACKEND']:
        return True

    try:
        cache.set('_cms_qe_monitoring', 'test', 5)
        return cache.get('_cms_qe_monitoring') == 'test'
    except Exception as exc:  # pylint: disable=broad-except
        return str(exc)
