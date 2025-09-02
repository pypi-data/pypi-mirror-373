"""
Newsletter plugin
#################

Plugin for Django CMS QE providing newsletter. It allows users to subscribe
(simply add email to database) and also possibility to sync with external
sources like MailChimp.

Usage
*****

Add plugin from section **Generic** called **Newsletter subscription form**.

To synchronize emails with MailChimp, `generate a api_key on MailChimp
<http://kb.mailchimp.com/integrations/api-integrations/about-api-keys>`_
and set it with MailChimp username (which you can find or set in `profile settings
<https://admin.mailchimp.com/account/profile/>`_) in admin interface in *Сonstance*.
Then you can synchronize mailing lists in list of mailing lists in admin interface
and use those lists in your plugin.

API
***

Django CMS
==========

.. autoclass:: cms_qe_newsletter.cms_plugins.NewsletterPlugin
    :members:

.. autoclass:: cms_qe_newsletter.models.NewsletterPluginModel
    :members:

Models
======

.. autoclass:: cms_qe_newsletter.models.MailingList
    :members:

.. autoclass:: cms_qe_newsletter.models.Subscriber
    :members:

.. autoclass:: cms_qe_newsletter.models.SubscribeTask
    :members:

Views
=====

.. automodule:: cms_qe_newsletter.views
    :members:

Manage
======

.. autoclass:: cms_qe_newsletter.management.commands.cms_qe_newsletter_sync.Command
    :members:

Services
========

.. automodule:: cms_qe_newsletter.external_services.sync
    :members:

Mailchimp
---------

.. automodule:: cms_qe_newsletter.external_services.mailchimp.sync
    :members:

.. automodule:: cms_qe_newsletter.external_services.mailchimp.client
    :members:
"""

import logging

logger = logging.getLogger(__name__)

default_app_config = 'cms_qe_newsletter.apps.NewsletterConfig'
