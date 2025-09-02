import typing
from urllib import parse

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@typing.no_type_check
@register.filter(name='cms_qe_video_url_to_embed')
@stringfilter
def cms_qe_video_url_to_embed(url: str) -> str:
    """
    Django template filter to change video URL to make it embed.
    A little hack for popular video hosting services.
    """

    url = parse.urlparse(url)
    if 'vimeo.com' in url.netloc:  # pylint: disable=R1705
        return parse.urlunparse((url.scheme, 'player.vimeo.com', '/video' + url.path, [], {}, ''))
    if 'youtube.com' in url.netloc or 'youtu.be' in url.netloc:
        # url: ParseResult(scheme='https', netloc='youtu.be', path='/ccicicV2yJ8', params='', query='', fragment='')
        video_id = None
        if url.query:
            params = parse.parse_qs(url.query)
            if 'v' in params:
                video_id = params['v'][0]
        if video_id is None:
            video_id = url.path.lstrip('/')
        return parse.urlunparse((url.scheme, 'www.youtube.com', '/embed/' + video_id, [], {}, ''))

    return parse.urlunparse(url)
