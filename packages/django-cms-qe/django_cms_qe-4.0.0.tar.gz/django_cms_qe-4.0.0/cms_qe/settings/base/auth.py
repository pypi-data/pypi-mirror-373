"""
Settings providing authentication options.
"""

AUTH_USER_MODEL = 'cms_qe_auth.User'

LOGIN_REDIRECT_URL = '/'

LOGIN_URL = '/auth/login'

CMS_QE_AUTH_ENABLED = False  # Enable cms_qe_auth registration.

ALDRYN_FORMS_EMAIL_AVAILABILITY_CHECKER_FNC = 'cms_qe_auth.utils.smtp_server_accepts_email_address'
ALDRYN_FORMS_EMAIL_AVAILABILITY_CHECKER_CLASS = 'cms_qe_auth.utils.SMTPCheckRecipient'
