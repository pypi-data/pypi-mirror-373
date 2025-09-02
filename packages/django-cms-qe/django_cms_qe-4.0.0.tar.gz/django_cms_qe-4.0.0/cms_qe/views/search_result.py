from aldryn_search.views import AldrynSearchView

from cms_qe.haystack.forms import HaystackSearchForm


class SiteSearchView(AldrynSearchView):  # pylint: disable=too-many-ancestors
    """Site Search View."""

    form_class = HaystackSearchForm
    template_name = "cms_qe/search_result.html"
