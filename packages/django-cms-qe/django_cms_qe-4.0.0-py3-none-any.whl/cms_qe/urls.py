"""
URL Configuration
https://docs.djangoproject.com/en/1.11/topics/http/urls/
"""

from cms.sitemaps import CMSSitemap
from django.apps import apps
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

from cms_qe.views.maintenance import HealthCheckView, ReloadSiteView
from cms_qe.views.redirect_to_page import RedirectToPage
from cms_qe.views.search_result import SiteSearchView
from cms_qe.views.security import SecurityTxtView

from . import views

__all__ = (
    'handler403',
    'handler404',
    'handler500',
    'handler503',
    'urlpatterns',
)

# pylint: disable=invalid-name
handler403 = 'cms_qe.views.handler403'
handler404 = 'cms_qe.views.handler404'
handler500 = 'cms_qe.views.handler500'
handler503 = 'cms_qe.views.handler503'

urlpatterns = [
    path('', include('filer.server.urls')),
    path('csp-report', views.csp_report),
    path('', include('cms_qe_table.urls')),
    path('', include('cms_qe_newsletter.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': {'cmspages': CMSSitemap}}),
    path('api/monitoring', views.get_monitoring),
    path('api/v1/', include('cms_qe.api.urls'), name="api-root"),
    path('.well-known/security.txt', SecurityTxtView.as_view(), name='security-txt'),
    path('site-search-result/', SiteSearchView.as_view(), name='site-search-result'),
    path("healthcheck/", HealthCheckView.as_view(), name='healthcheck'),  # Used by uwsgi in docker.
    path("superuser/reload-site/", ReloadSiteView.as_view(), name='reload-site'),
    path('redirect-to-page/', RedirectToPage.as_view(), name='redirect-to-page'),
]

# django-simple-captcha
if apps.is_installed("captcha"):
    urlpatterns += [
        path('captcha/', include('captcha.urls')),  # Aldryn forms
    ]

# During development is error page replaced by Django error page with debug info.
# This is registration special URLs for testing error pages in dev mode.
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
        path('403/', views.handler403),
        path('404/', views.handler404),
        path('503/', views.handler503),
    ]

# Django CMS has to be the last one because it will consume all URLs.
if settings.CMS_QE_AUTH_ENABLED:
    urlpatterns += i18n_patterns(
        path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
        path('jsi18n-aldryn-forms/', JavaScriptCatalog.as_view(packages=['aldryn_forms']), name='js-aldryn-forms'),
        path('admin/', admin.site.urls),
        path('auth/', include('cms_qe_auth.urls')),
        path('', include('cms.urls')),
    )
else:
    urlpatterns += i18n_patterns(
        path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
        path('jsi18n-aldryn-forms/', JavaScriptCatalog.as_view(packages=['aldryn_forms']), name='js-aldryn-forms'),
        path('admin/', admin.site.urls),
        path('', include('cms.urls')),
    )
