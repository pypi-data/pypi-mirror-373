from haystack.constants import FILTER_SEPARATOR
from haystack.query import SearchQuerySet

from .inputs import PostProcessQuery


class HaystackSearchQuerySet(SearchQuerySet):
    """Haystack SearchQuerySet."""

    def post_process_query(self, query_string, fieldname=f"content{FILTER_SEPARATOR}contains"):
        """Query contains value."""
        kwargs = {fieldname: PostProcessQuery(query_string)}
        return self.filter(**kwargs)
