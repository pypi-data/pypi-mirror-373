CROSS_ORIGINS = (
    'anonymous',
    'use-credentials',
)

LOADING = (
    'eager',
    'lazy',
)

SANDBOX = (
    'allow-forms',
    'allow-pointer-lock',
    'allow-popups',
    'allow-same-origin',
    'allow-scripts',
    'allow-top-navigation',
)

REFERRER_POLICY = (
    'no-referrer',
    'no-referrer-when-downgrade',
    'origin',
    'origin-when-cross-origin',
    'unsafe-url',
)

SCRIPT_REFERRER_POLICY = REFERRER_POLICY + (
    'same-origin',
    'strict-origin',
    'strict-origin-when-cross-origin',
)

REL = (
    'alternate',
    'author',
    'dns-prefetch',
    'help',
    'icon',
    'license',
    'next',
    'pingback',
    'preconnect',
    'prefetch',
    'preload',
    'prerender',
    'prev',
    'search',
    'stylesheet',
)
