"""
Base settings for Django CMS and all plugins for Django CMS.
"""

from cms.constants import X_FRAME_OPTIONS_SAMEORIGIN
from django.utils.translation import gettext_lazy as _

# Base Django CMS settings.

# List of base templates to create page from.
CMS_TEMPLATES = [
    ('cms_qe/home.html', 'Home page template'),
]

# Do not show toolbar for not logged users when they append ?edit into URL.
CMS_TOOLBAR_ANONYMOUS_ON = False

# Enables permission to view or edit page only by specific users.
CMS_PERMISSION = True

# Django CMS allow to configure X-FRAME header per page. We don't want to allow nothing
# else than SAMEORIGIN which is set also by Django's setting X_FRAME_OPTIONS.
CMS_DEFAULT_X_FRAME_OPTIONS = X_FRAME_OPTIONS_SAMEORIGIN

# Caching.
CMS_PAGE_CACHE = True
CMS_PLACEHOLDER_CACHE = True
CMS_PLUGIN_CACHE = True

# Enables to set permissions per any folder or file for specific users or groups.
FILER_ENABLE_PERMISSIONS = True

# Django Filer settings.

THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)

TEXT_ADDITIONAL_ATTRIBUTES: dict[str, set] = {"iframe": set()}

# cmsplugin_filer_folder
CMSPLUGIN_FILER_FOLDER_STYLE_CHOICES = (
    ("list", _("List")),
    ("slideshow", _("Slideshow")),
    ("gallery", _("Gallery"))
)

CMSPLUGIN_FILER_IMAGE_DEFAULT_STYLE = 'main'

# Frontend plugins.

DJANGOCMS_FRONTEND_TAG_CHOICES = (
    "div", "section", "article", "header", "footer", "aside", 'p', 'iframe', 'link', 'script', 'hgroup', 'figure',
    'figcaption'
)

DJANGOCMS_FRONTEND_GRID_CONTAINERS = (
    ("container", _("Container")),
    ("container-fluid", _("Fluid container")),
    ("container-full", _("Full container")),
    (" ", "----"),
)

# For example: ["css/bootstrap.min.css", "css/screen.css"]
STYLES_FOR_ALIAS_ADMIN_PREVIEW: list[str] = []
