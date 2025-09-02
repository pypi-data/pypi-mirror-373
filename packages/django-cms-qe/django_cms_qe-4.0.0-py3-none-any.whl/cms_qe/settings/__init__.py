"""
Settings is stored in ``cms_qe.settings``. You can find few prepared ready-to-use environments:

 * prod,
 * dev
 * and test.

First one is for production use. It means at your app you should just import everything from
there and add what you have to change (your paths and database for example). Actually the
minimum config is for example this one:

.. code-block:: python

    import os

    from cms_qe.settings.prod import *


    INSTALLED_APPS += [
        'example',
    ]

    ROOT_URLCONF = 'example.urls'
    WSGI_APPLICATION = 'example.wsgi.application'

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

Security
--------

.. automodule:: cms_qe.settings.base.security

"""
