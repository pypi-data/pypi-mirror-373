"""
Auth plugin
###########

Plugins for Django CMS QE providing authentication. It allows
user to register and login into site.

Usage
*****

Authentication forms are activated by default and is possible to use at
**/auth/login** or **/auth/register** but you can also use login or
registration form anywhere you want. Just from section **Generic** use
**Login form** or **Register form**.

API
***

Django CMS
==========

.. autoclass:: cms_qe_auth.cms_plugins.LoginFormPlugin
    :members:

.. autoclass:: cms_qe_auth.cms_plugins.RegisterFormPlugin
    :members:

.. autoclass:: cms_qe_auth.cms_menus.AuthModifier
    :members:

Models
======

.. autoclass:: cms_qe_auth.models.User
    :members:

Views
=====

.. automodule:: cms_qe_auth.views
    :members:

.. automodule:: cms_qe_auth.forms
    :members:
"""

default_app_config = 'cms_qe_auth.apps.AuthConfig'
