"""
Table plugin
############

Plugin for Django CMS QE providing table listing. It allows to specify
table, columns, paging and all other attributes including CSS classes
to easily add any view to database without needs to create new plugin.

Usage
*****

Add plugin from section **Generic** called **Table**.

At configuration screen pick which table you want to use. Then specify which
columns to show, in which order and how many items per page to show.

TODO: Later there will be provided options to pre-filter and possibility to
filter on client side by user.

API
***

Django CMS
==========

.. autoclass:: cms_qe_table.cms_plugins.TablePlugin
    :members:

.. autoclass:: cms_qe_table.models.TablePluginModel
    :members:

.. autoclass:: cms_qe_table.forms.TablePluginForm
    :members:

Views
=====

.. automodule:: cms_qe_table.views
    :members:

.. automodule:: cms_qe_table.templatetags.cms_qe_table_filters
    :members:

Utils
=====

.. automodule:: cms_qe_table.utils
    :members:

Exceptions
==========

.. automodule:: cms_qe_table.exceptions
    :members:

"""
