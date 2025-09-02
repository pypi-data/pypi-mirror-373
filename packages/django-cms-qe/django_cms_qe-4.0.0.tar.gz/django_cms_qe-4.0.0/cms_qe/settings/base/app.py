"""
Base settings for Django app.
"""
from .env import ENV

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = 1
CMS_CONFIRM_VERSION4 = True
DJANGOCMS_VERSIONING_ALLOW_DELETING_VERSIONS = True

INTERNAL_IPS = ENV.list("INTERNAL_IPS", default=[])

META_USE_SITES = True
META_SITE_PROTOCOL = 'https'

INSTALLED_APPS = [
    # This app. :-)
    # It is holding at the top of the list, so that allow rewrite the templates in third side applications.
    'cms_qe',
    'cms_qe_auth',
    'cms_qe_breadcrumb',
    'cms_qe_i18n',
    'cms_qe_menu',
    'cms_qe_newsletter',
    'cms_qe_table',
    'cms_qe_video',
    'cms_qe_analytical',
    'cms_qe_plugins',

    # Must be before django.contrib.admin.
    'djangocms_admin_style',

    # Django's defaults.
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Needed by Django CMS.
    'django.contrib.sitemaps',

    # Django CMS's core modules.
    'cms',
    'menus',
    'treebeard',  # Tree structure of pages and plugins.
    'sekizai',  # Static file management.

    'djangocms_text',
    'djangocms_link',
    'djangocms_alias',
    'djangocms_versioning',

    # Other Django CMS's useful modules.
    'djangocms_googlemap',

    # Django Filer's modules.
    'filer',
    'easy_thumbnails',

    # Other Django Files's useful modules.
    'djangocms_file',
    'djangocms_icon',
    'djangocms_picture',

    # Optional django CMS Frontend modules
    'djangocms_frontend',
    'djangocms_frontend.contrib.accordion',
    'djangocms_frontend.contrib.alert',
    'djangocms_frontend.contrib.badge',
    'djangocms_frontend.contrib.card',
    'djangocms_frontend.contrib.carousel',
    'djangocms_frontend.contrib.collapse',
    'djangocms_frontend.contrib.content',
    'djangocms_frontend.contrib.grid',
    'djangocms_frontend.contrib.icon',
    'djangocms_frontend.contrib.image',
    'djangocms_frontend.contrib.jumbotron',
    'djangocms_frontend.contrib.link',
    'djangocms_frontend.contrib.listgroup',
    'djangocms_frontend.contrib.media',
    'djangocms_frontend.contrib.navigation',
    'djangocms_frontend.contrib.tabs',
    'djangocms_frontend.contrib.utilities',

    # Other Django's modules.
    'axes',
    'constance',
    'constance.backends.database',
    'import_export',

    # Aldryn forms
    'aldryn_forms',
    'aldryn_forms.contrib.email_notifications',
    'captcha',

    # Serach engine
    'haystack',
    'standard_form',
    'spurl',
    'aldryn_search',

    # Site REST API
    'rest_framework',
    'knox',
    'django_filters',
    'drf_spectacular',
]

MIDDLEWARE = [
    # Must be the first. Cache is more important, second one is only
    # for development auto-reload also after apphook changes.
    'django.middleware.cache.UpdateCacheMiddleware',
    'cms.middleware.utils.ApphookReloadMiddleware',

    # Django's defaults.
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Locale is mandatory by Django CMS.
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Extra Django's middlewares.
    'django.middleware.common.BrokenLinkEmailsMiddleware',

    # Django CMS's core middlewares.
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',

    # CMS QE middleware.
    'cms_qe.middleware.page_status_code.restore_status_for_cached_error_page',

    # Security middleware.
    'axes.middleware.AxesMiddleware',
    'csp.middleware.CSPMiddleware',

    # Must be the last.
    'django.middleware.cache.FetchFromCacheMiddleware',
]

# Reload site. For example ['uwsgi', '--reload', '/var/run/uwsgi.pid'] or ['touch', 'manage.py'].
RELOAD_SITE: list[str] = []

# API views: [("path/", "module.api.views.RecordViewSet", "api-records"), ...]
# API_VIEWS: list[tuple[str, str, str]] = []
