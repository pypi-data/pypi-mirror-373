"""
Caching setting by default in-memory without need to configure anything.
"""

# Caching
# https://docs.djangoproject.com/en/4.2/topics/cache/

# https://pypi.org/project/python-environ/
#   Supported types / cache_url

from .env import ENV

CACHES = {
    "default": ENV.cache("CACHE_URL", default="pymemcache://127.0.0.1:11211"),
}
