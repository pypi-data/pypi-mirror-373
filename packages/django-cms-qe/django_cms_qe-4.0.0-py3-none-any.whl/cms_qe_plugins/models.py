from cms.models.pluginmodel import CMSPlugin
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from .attributes import CROSS_ORIGINS, LOADING, REFERRER_POLICY, REL, SANDBOX, SCRIPT_REFERRER_POLICY
from .utils import make_choices, make_opt_choices
from .validators import validate_url_or_path


class Script(CMSPlugin):
    """HTML Script tag."""

    src = models.CharField(
        max_length=255, validators=[validate_url_or_path],
        help_text="Specifies the location of the linked script.")
    asyncf = models.BooleanField(
        default=False,
        verbose_name='async',
        help_text='Specifies that the script is downloaded in parallel to parsing the page, and executed as soon as it '
                  'is available (before parsing completes) (only for external scripts)'
        )
    cross_origin = models.CharField(
        max_length=15, null=True, blank=True, choices=make_opt_choices(CROSS_ORIGINS), default=None,
        help_text="Sets the mode of the request to an HTTP CORS Request.")
    defer = models.BooleanField(
        default=False,
        help_text='Specifies that the script is downloaded in parallel to parsing the page, and executed after '
                  'the page has finished parsing (only for external scripts)'
    )
    integrity = models.CharField(
        max_length=255, null=True, blank=True,
        help_text='Allows a browser to check the fetched script to ensure that the code is never loaded '
                  'if the source has been manipulated'
    )
    nomodule = models.BooleanField(
        default=False,
        help_text='Specifies that the script should not be executed in browsers supporting ES2015 modules.'
    )
    referrer_policy = models.CharField(
        max_length=50, null=True, blank=True, choices=make_opt_choices(SCRIPT_REFERRER_POLICY), default=None,
        help_text="Specifies which referrer to use when fetching the resource.")
    type = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Specifies the media type of the script.")
    attributes = models.JSONField(
        null=True, blank=True, encoder=DjangoJSONEncoder,
        help_text='More attributes as JSON data. E.g. {"data-name": "value", "id": 42}')

    def __str__(self):
        return self.src


class Link(CMSPlugin):
    """HTML Link tag."""

    href = models.CharField(
        max_length=255, validators=[validate_url_or_path],
        help_text="Specifies the location of the linked document.")
    rel = models.CharField(
        max_length=30, choices=make_choices(REL), default='stylesheet',
        help_text="Required. Specifies the relationship between the current document and the linked document.")
    cross_origin = models.CharField(
        max_length=15, null=True, blank=True, choices=make_opt_choices(CROSS_ORIGINS), default=None,
        help_text="Specifies how the element handles cross-origin requests.")
    hreflang = models.CharField(
        max_length=30, null=True, blank=True, help_text="Specifies the language of the text in the linked document.")
    media = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Specifies on what device the linked document will be displayed.")
    referrer_policy = models.CharField(
        max_length=50, null=True, blank=True, choices=make_opt_choices(REFERRER_POLICY), default=None,
        help_text="Specifies which referrer to use when fetching the resource.")
    sizes = models.CharField(
        max_length=255, null=True, blank=True,
        help_text='Specifies the size of the linked resource. Only for rel="icon".')
    title = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Defines a preferred or an alternate stylesheet.")
    type = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Specifies the media type of the linked document. E.g. 'text/css'.")
    attributes = models.JSONField(
        null=True, blank=True, encoder=DjangoJSONEncoder,
        help_text='More attributes as JSON data. E.g. {"data-name": "value", "id": 42}')

    def __str__(self):
        return self.href


class Iframe(CMSPlugin):
    """HTML Iframe tag."""

    src = models.CharField(
        max_length=255, validators=[validate_url_or_path],
        help_text="Specifies the address of the document to embed in the &lt;iframe&gt;.")
    allow = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Specifies a feature policy for the &lt;iframe&gt;. Form more see "
                  "<a href='https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#allow' target='_blank'>"
                  "IFrame attributes.</a>.")
    allow_full_screen = models.BooleanField(
        null=True, blank=True,
        help_text='Set to true if the &lt;iframe&gt; can activate fullscreen mode by calling the requestFullscreen() '
                  'method.'
    )
    allow_payment_request = models.BooleanField(
        null=True, blank=True,
        help_text='Set to true if a cross-origin &lt;iframe&gt; should be allowed to invoke the Payment Request API.'
    )
    height = models.IntegerField(
        null=True, blank=True,
        help_text='Specifies the height of an &lt;iframe&gt;. Default height is 150 pixels.')
    width = models.IntegerField(
        null=True, blank=True,
        help_text='Specifies the width of an &lt;iframe&gt;. Default width is 300 pixels.')
    loading = models.CharField(
        max_length=255, null=True, blank=True, choices=make_opt_choices(LOADING), default=None,
        help_text="Specifies whether a browser should load an iframe immediately or to defer loading of iframes "
                  "until some conditions are met.")
    name = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Specifies the name of an &lt;iframe&gt;.")
    referrer_policy = models.CharField(
        max_length=50, null=True, blank=True, choices=make_opt_choices(SCRIPT_REFERRER_POLICY), default=None,
        help_text="Specifies which referrer information to send when fetching the iframe.")
    sandbox = models.CharField(
        max_length=50, null=True, blank=True, choices=make_opt_choices(SANDBOX), default=None,
        help_text="Enables an extra set of restrictions for the content in an &lt;iframe&gt;.")
    src_doc = models.TextField(
        null=True, blank=True, help_text="Specifies the HTML content of the page to show in the &lt;iframe&gt;."
    )
    attributes = models.JSONField(
        null=True, blank=True, encoder=DjangoJSONEncoder,
        help_text='More attributes as JSON data. E.g. {"data-name": "value", "id": 42}')

    def __str__(self):
        return self.src
