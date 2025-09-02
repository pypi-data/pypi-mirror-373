import re

from constance import config
from django.views.generic import RedirectView


class RedirectToPage(RedirectView):
    """Redirect to page according to settings in constance."""

    url = "/"

    def get_from_host(self):
        return self.request.GET.get("fromhost")

    def get_redirect_url(self, *args, **kwargs):
        from_host = self.get_from_host()
        for line in re.split("\n+", config.REDIRECT_TO_PAGE):
            line = line.strip()
            groups = re.match(r"(?P<path>\S+)(\s+(?P<host>\S+))?", line.strip())
            if groups is None:
                continue
            if groups['host'] is None:
                return groups['path']
            if groups['host'] == from_host:
                return groups['path']
            continue
        return self.url
