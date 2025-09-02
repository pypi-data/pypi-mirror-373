"""
Settings which is able to set from admin by user.
"""
from collections import OrderedDict

from django.utils.safestring import mark_safe

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_DATABASE_CACHE_BACKEND = 'default'

CONSTANCE_ADDITIONAL_FIELDS = {
    'short_str': ['django.forms.fields.CharField', {'required': False}],
}


GOOGLE_ANALYTICS_CONSTANCE_CONFIG = (
    ('GOOGLE_ANALYTICS_PROPERTY_ID', (
        '',
        'Every website you track with Google Analytics gets its own property ID.\n'
        'You can find the web property ID on the overview page of your account.\n',
        'short_str'
    )),
    ('GOOGLE_ANALYTICS_DISPLAY_ADVERTISING', (
        False,
        'Display Advertising allows you to view Demographics and Interests reports,\n'
        'add Remarketing Lists and support DoubleClick Campain Manager integration.',
        bool
    )),
    ('GOOGLE_ANALYTICS_SITE_SPEED', (
        False,
        mark_safe('Allow you view page load times in the '
                  '<a href="https://support.google.com/analytics/answer/1205784">Site Speed</a> report.'),
        bool
    )),
    ('GOOGLE_ANALYTICS_ANONYMIZE_IP', (
        False,
        mark_safe('<a href="https://support.google.com/analytics/answer/2763052?hl=en">IP Anonymization</a>'),
        bool
    )),
    ('GOOGLE_ANALYTICS_SAMPLE_RATE', (
        '',
        mark_safe(
            '<a href="https://developers.google.com/analytics/devguides/collection/gajs/methods/'
            'gaJSApiBasicConfiguration#_setsamplerate">Sample Rate </a>'
        ),
        'short_str'
    )),
    ('GOOGLE_ANALYTICS_SITE_SPEED_SAMPLE_RATE', (
        '',
        mark_safe(
            '<a href="https://developers.google.com/analytics/devguides/collection/gajs/methods/'
            'gaJSApiBasicConfiguration#_setsitespeedsamplerate">Site Speed Sample Rate</a>\n'
            'The value is a percentage and can be between 0 and 100'
        ),
        'short_str')),
    ('GOOGLE_ANALYTICS_SESSION_COOKIE_TIMEOUT', (
        '',
        mark_safe(
            '<a href="https://developers.google.com/analytics/devguides/collection/gajs/methods/'
            'gaJSApiBasicConfiguration#_setsessioncookietimeout">Session cookie timeout</a> in milliseconds.'
        ),
        'short_str'
    )),
    ('GOOGLE_ANALYTICS_VISITOR_COOKIE_TIMEOUT', (
        '',
        mark_safe(
            '<a href="https://developers.google.com/analytics/devguides/collection/gajs/methods/'
            'gaJSApiBasicConfiguration#_setvisitorcookietimeout">Google Analytics visitor cookie expiration </a>'
            'in milliseconds.'),
        'short_str'
    )),
)

GOOGLE_TAG_MANAGER_CONSTANCE_CONFIG = (
    ('GOOGLE_TAG_MANAGER_ID', (
        '',
        mark_safe(
            'The Google tag (<a href="https://developers.google.com/tag-platform/gtagjs/install">gtag.js</a>) '
            'is a single tag you can add to your website to use a variety of Google products.\n'
            'The tag code is inserved into the page after the ID is set. '
            """<pre style="color:#e83e8c; font-size:80%">
&lt;!-- Google tag (gtag.js) --&gt;
&lt;script async src="https://www.googletagmanager.com/gtag/js?id={{ GOOGLE_TAG_MANAGER_ID }}"&gt;&lt;/script&gt;
&lt;script&gt;
    window.dataLayer = window.dataLayer || [];
    function gtag() {dataLayer.push(arguments)}
    gtag('js', new Date());
    gtag('config', '{{ GOOGLE_TAG_MANAGER_ID }}');
    {{ GOOGLE_TAG_MANAGER_SCRIPT|safe }}
&lt;/script&gt;
            </pre>"""),
        'short_str'
    )),
    ('GOOGLE_TAG_MANAGER_SCRIPT', (
        '',
        mark_safe(
            'Javascript code inside <code style="color:#e83e8c">&lt;script&gt;</code> '
            'with <code style="color:#e83e8c">gtag</code> functions. For more see '
            '<a href="https://developers.google.com/tag-platform/gtagjs/configure">Tags - Configure</a>.'
        ),
        str
    )),
)

PIWIK_CONSTANCE_CONFIG = (
    ('PIWIK_DOMAIN_PATH', (
        '',
        'URL of your Piwik server. Typically, you’ll have Piwik installed on a subdomain or subdirectory\n '
        '(e.g. piwik.your_site.com or www.your_site.com/piwik).',
        'short_str'
    )),
    ('PIWIK_SITE_ID', (
        '',
        'Your Piwik server can track several websites.\n Each website has its site ID (this is the idSite parameter '
        'in the query string of your browser’s address bar when you visit the Piwik Dashboard). ',
        'short_str'
    )),
)

DJANGOCMS_GOOGLEMAP_CONSTANCE_CONFIG = (
    ('DJANGOCMS_GOOGLEMAP_API_KEY', (
        '',
        'API key of your project to use Google maps. You can generate key here:\n'
        'https://developers.google.com/maps/documentation/javascript/get-api-key'
    )),
)

MAILCHIMP_CONSTANCE_CONFIG = (
    ('MAILCHIMP_API_KEY', (
        '',
        'API key of your app to synchronize mail lists with MailChimp. More about MailChimp API keys:'
        'http://kb.mailchimp.com/integrations/api-integrations/about-api-keys',
    )),
    ('MAILCHIMP_USERNAME', (
        '',
        'Your username on MailChimp. You can find or change the username in profile settings:'
        'https://admin.mailchimp.com/account/profile/',
    )),
)

REDIRECT_TO_PAGE = (
    ('REDIRECT_TO_PAGE', (
        '',
        mark_safe('<div>Redirect to page from path <code>/redirect-to-page/</code>.</div>'
                  '<div>Example: <pre>/path/one/\n/path/two/ localhost:8000</pre></div>'),
    )),
)

# The content ready for .well-known/security.txt
SECURITY_TXT_CONTENT = None  # "Contact: mailto:abuse@nic.cz"

SECURITY_TXT_CONFIG = (
    ('SECURITY_TXT_CONTENT', [  # This list is of type List so that the default value can be redefined.
        '',  # Default value. If the value is empty, the file security.txt is reported as http 404.
        mark_safe("""
            Content of <a href="/.well-known/security.txt">.well-known/security.txt</a>.
            <a href="https://datatracker.ietf.org/doc/html/draft-foudil-securitytxt-12">
                A File Format to Aid in Security Vulnerability Disclosure
            </a>.
            <a href="https://securitytxt.org/#genform">Create content online.</a>
            If the value is empty, the file security.txt is reported as http 404.
        """)
    ]),
)


CONSTANCE_CONFIG = OrderedDict(
    GOOGLE_ANALYTICS_CONSTANCE_CONFIG +   # type: ignore
    GOOGLE_TAG_MANAGER_CONSTANCE_CONFIG +   # type: ignore
    PIWIK_CONSTANCE_CONFIG +   # type: ignore
    DJANGOCMS_GOOGLEMAP_CONSTANCE_CONFIG +   # type: ignore
    MAILCHIMP_CONSTANCE_CONFIG +  # type: ignore
    REDIRECT_TO_PAGE +   # type: ignore
    SECURITY_TXT_CONFIG  # type: ignore
)

CONSTANCE_CONFIG_FIELDSETS = {
    'General options': ('DJANGOCMS_GOOGLEMAP_API_KEY',),
    'Google analytics options': dict(GOOGLE_ANALYTICS_CONSTANCE_CONFIG).keys(),
    'Google tag manager options': dict(GOOGLE_TAG_MANAGER_CONSTANCE_CONFIG).keys(),
    'Piwik options': dict(PIWIK_CONSTANCE_CONFIG).keys(),
    'Mailchimp options': dict(MAILCHIMP_CONSTANCE_CONFIG).keys(),
    'Redirect to page': dict(REDIRECT_TO_PAGE).keys(),
    'Security.txt': dict(SECURITY_TXT_CONFIG).keys(),
}


def _lazy_constance(constance_name):
    """
    Config from library constance cannot be imported in settings
    because it already need initialized settings. That's why it
    has to be done lazily.
    """

    def get_constance_value():
        """
        Simple function just to import config and get value. This
        function will be called later when settings is alread initialized.
        """
        from constance import config  # pylint: disable=import-outside-toplevel
        return getattr(config, constance_name)

    # pylint: disable=too-few-public-methods
    class Template:
        """
        Simple objcet wrapping real value. It's just proxy to real
        value. It works only with values which are not validated
        against realy base data types.
        """

        def __getattr__(self, item):
            return getattr(get_constance_value(), item)

        def __str__(self):
            return str(get_constance_value())

    return Template()


DJANGOCMS_GOOGLEMAP_API_KEY = _lazy_constance('DJANGOCMS_GOOGLEMAP_API_KEY')
