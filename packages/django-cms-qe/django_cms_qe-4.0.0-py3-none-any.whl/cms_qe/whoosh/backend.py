from haystack.backends.whoosh_backend import WhooshEngine, WhooshSearchBackend, WhooshSearchQuery
from haystack.constants import DJANGO_CT, DJANGO_ID, ID
from haystack.exceptions import SearchBackendError
from haystack.fields import CharField
from whoosh.analysis import CharsetFilter, StemmingAnalyzer
from whoosh.analysis.analyzers import CompositeAnalyzer
from whoosh.fields import BOOLEAN, DATETIME, ID as WHOOSH_ID, IDLIST, KEYWORD, NGRAM, NGRAMWORDS, NUMERIC, TEXT, Schema
from whoosh.support.charset import accent_map


# https://github.com/django-haystack/django-haystack/blob/v3.2.1/haystack/backends/whoosh_backend.py#L77
class AnalyzerWhooshSearchBackend(WhooshSearchBackend):
    """WhooshSearchBackend width analyzer."""

    # This is a copy of parent class function modified by _get_analyzer.
    # https://github.com/django-haystack/django-haystack/blob/v3.2.1/haystack/backends/whoosh_backend.py#L168
    def build_schema(self, fields):  # pylint: disable=too-many-branches
        schema_fields = {
            ID: WHOOSH_ID(stored=True, unique=True),
            DJANGO_CT: WHOOSH_ID(stored=True),
            DJANGO_ID: WHOOSH_ID(stored=True),
        }
        # Grab the number of keys that are hard-coded into Haystack.
        # We'll use this to (possibly) fail slightly more gracefully later.
        initial_key_count = len(schema_fields)
        content_field_name = ""

        for _, field_class in fields.items():
            if field_class.is_multivalued:
                if field_class.indexed is False:
                    schema_fields[field_class.index_fieldname] = IDLIST(
                        stored=True, field_boost=field_class.boost
                    )
                else:
                    schema_fields[field_class.index_fieldname] = KEYWORD(
                        stored=True,
                        commas=True,
                        scorable=True,
                        field_boost=field_class.boost,
                    )
            elif field_class.field_type in ["date", "datetime"]:
                schema_fields[field_class.index_fieldname] = DATETIME(
                    stored=field_class.stored, sortable=True
                )
            elif field_class.field_type == "integer":
                schema_fields[field_class.index_fieldname] = NUMERIC(
                    stored=field_class.stored,
                    numtype=int,
                    field_boost=field_class.boost,
                )
            elif field_class.field_type == "float":
                schema_fields[field_class.index_fieldname] = NUMERIC(
                    stored=field_class.stored,
                    numtype=float,
                    field_boost=field_class.boost,
                )
            elif field_class.field_type == "boolean":
                # Field boost isn't supported on BOOLEAN as of 1.8.2.
                schema_fields[field_class.index_fieldname] = BOOLEAN(
                    stored=field_class.stored
                )
            elif field_class.field_type == "ngram":
                schema_fields[field_class.index_fieldname] = NGRAM(
                    minsize=3,
                    maxsize=15,
                    stored=field_class.stored,
                    field_boost=field_class.boost,
                )
            elif field_class.field_type == "edge_ngram":
                schema_fields[field_class.index_fieldname] = NGRAMWORDS(
                    minsize=2,
                    maxsize=15,
                    at="start",
                    stored=field_class.stored,
                    field_boost=field_class.boost,
                )
            else:
                schema_fields[field_class.index_fieldname] = TEXT(
                    stored=True,
                    # analyzer=field_class.analyzer or StemmingAnalyzer(),  Original.
                    analyzer=_get_analyzer(field_class),  # Modification.
                    field_boost=field_class.boost,
                    sortable=True,
                )

            if field_class.document is True:
                content_field_name = field_class.index_fieldname
                schema_fields[field_class.index_fieldname].spelling = True

        # Fail more gracefully than relying on the backend to die if no fields
        # are found.
        if len(schema_fields) <= initial_key_count:
            raise SearchBackendError(
                "No fields were found in any search_indexes. Please correct this before attempting to search."
            )

        return (content_field_name, Schema(**schema_fields))

    def build_search_kwargs(self, **kwargs):  # pylint: disable=W0221
        """Build search kwargs."""
        # A convenience method most backends should include in order to make extension easier.
        return {}

    def extract_file_contents(self, file_obj):
        """Extract file contents."""


def _get_analyzer(field_class: CharField) -> CompositeAnalyzer:
    """Get analyzer."""
    analyzer = StemmingAnalyzer()
    if field_class is not None and hasattr(field_class, 'analyzer') and field_class.analyzer is not None:
        analyzer = field_class.analyzer
    if field_class.index_fieldname in ['text', 'description', 'title']:
        analyzer |= CharsetFilter(accent_map)
    return analyzer


class AnalyzerWhooshEngine(WhooshEngine):
    backend = AnalyzerWhooshSearchBackend
    query = WhooshSearchQuery
