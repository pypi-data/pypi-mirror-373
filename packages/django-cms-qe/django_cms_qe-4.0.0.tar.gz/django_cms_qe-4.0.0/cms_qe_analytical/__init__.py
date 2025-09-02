"""
Analytics service integration
=============================

Integration with Google-Analytic_ and Piwik_ services.

This module is made using the django-analytical_ project.

.. _Google-Analytic : https://www.google.com/analytics/
.. _Piwik: https://piwik.org/
.. _django-analytical: https://pythonhosted.org/django-analytical_


Usage
-----
You can find all settings for analytics services in **Administration › Constance › Config** page.

Google Analytic
---------------

Setting the property ID
:::::::::::::::::::::::
Every website you track with Google Analytics gets its own property ID, and the google_analytics tag will include it in
the rendered Javascript code. You can find the web property ID on the overview page of your account.
ID should looks like **UA-123456-1**. Set **GOOGLE_ANALYTICS_PROPERTY_ID** in the config page.

If you do not set the site ID the tracking code will not be rendered.


Display Advertising
:::::::::::::::::::
Display Advertising allows you to view Demographics and Interests reports, add Remarketing Lists and support
DoubleClick Campain Manager integration.

You can enable Display Advertising features by setting the **GOOGLE_ANALYTICS_DISPLAY_ADVERTISING**.

Tracking site speed
:::::::::::::::::::
You can view page load times in the Site Speed report by setting the **GOOGLE_ANALYTICS_SITE_SPEED**
configuration setting.

By default, page load times are not tracked.

Anonymize IPs
:::::::::::::
You can enable the IP anonymization feature by setting the **GOOGLE_ANALYTICS_ANONYMIZE_IP** configuration setting.

This may be mandatory for deployments in countries that have a firm policies concerning data privacy (e.g. Germany).
By default, IPs are not anonymized.

Sample Rate
:::::::::::
You can configure the Sample Rate feature by setting the **GOOGLE_ANALYTICS_SAMPLE_RATE** configuration setting.

The value is a percentage and can be between 0 and 100 and can be a string or decimal value of with upto two decimal
places.

Site Speed Sample Rate
::::::::::::::::::::::
You can configure the Site Speed Sample Rate feature by setting the **GOOGLE_ANALYTICS_SITE_SPEED_SAMPLE_RATE**
configuration setting.

The value is a percentage and can be between 0 and 100 and can be a string or decimal value of with up to two decimal
places.

Session Cookie Timeout
::::::::::::::::::::::
You can configure the Session Cookie Timeout feature by setting the **GOOGLE_ANALYTICS_SESSION_COOKIE_TIMEOUT**
configuration setting:

The value is the session cookie timeout in milliseconds or 0 to delete the cookie when the browser is closed.

Visitor Cookie Timeout
::::::::::::::::::::::
You can configure the Visitor Cookie Timeout feature by setting the **GOOGLE_ANALYTICS_VISITOR_COOKIE_TIMEOUT**
configuration setting.

The value is the visitor cookie timeout in milliseconds or 0 to delete the cookie when the browser is closed.

Piwik
-----
Before you can use the Piwik integration, you must first define domain name and optional URI path to your Piwik server,
as well as the Piwik ID of the website you’re tracking with your Piwik server, in your project settings.

Setting the domain
::::::::::::::::::
Your Django project needs to know where your Piwik server is located. Typically, you’ll have Piwik installed
on a subdomain of its own (e.g. piwik.example.com), otherwise it runs in a subdirectory of a website of yours
(e.g. www.example.com/piwik). Set **PIWIK_DOMAIN_PATH** in the config page:

If you do not set a domain the tracking code will not be rendered.

Setting the site ID
:::::::::::::::::::
Your Piwik server can track several websites. Each website has its site ID (this is the idSite parameter in the query
string of your browser’s address bar when you visit the Piwik Dashboard). Set **PIWIK_SITE_ID** in the config page.

If you do not set the site ID the tracking code will not be rendered.
"""

# The code for this application was copied from https://github.com/jcassee/django-analytical v2.2.2
# and fixed to work with constance

__author__ = "Joost Cassee"
__email__ = "joost@cassee.net"
__version__ = "2.2.2"
__copyright__ = "Copyright (C) 2011-2016 Joost Cassee and others"
__license__ = "MIT License"
