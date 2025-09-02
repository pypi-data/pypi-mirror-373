"""
Menu plugin
###########

Plugin for Django CMS QE providing menu. It allows include menu at any
place so it can be moved without support of developers.

Usage
*****

Add plugin from section **Generic** called **Menu**. When used, you
are asked which page you want to use as top of the menu tree. That
is set by page ID in advanced setting. Also how deep it menu should
be. Keep in mind that normally menu supports only one level because
on mobile devices are deeper menus harder to use. Use deeper level
only when your design supports it.

API
***

.. autoclass:: cms_qe_menu.cms_plugins.MenuPlugin
    :members:

.. autoclass:: cms_qe_menu.models.MenuPluginModel
    :members:

"""
