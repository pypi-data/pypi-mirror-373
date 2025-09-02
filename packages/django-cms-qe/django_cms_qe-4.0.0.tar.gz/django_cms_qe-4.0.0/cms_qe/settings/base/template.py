"""
Base settings for Django templates.
"""

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                # Django's defaults.
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',  # Needed by Django CMS.

                # Django CMS's core context processors.
                'cms.context_processors.cms_settings',
                'sekizai.context_processors.sekizai',  # Static file management for template blocks.

                # Other Django's modules.
                'constance.context_processors.config',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]
