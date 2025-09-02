from haystack.forms import ModelSearchForm

from .query import HaystackSearchQuerySet


# https://github.com/django-haystack/django-haystack/blob/v3.2.1/haystack/forms.py#L96
class HaystackSearchForm(ModelSearchForm):
    """Haystack ModelSearchForm."""

    def __init__(self, *args, **kwargs):
        self.searchqueryset = kwargs.pop("searchqueryset", None)
        self.load_all = kwargs.pop("load_all", False)
        super().__init__(*args, **kwargs)
        self.searchqueryset = HaystackSearchQuerySet()

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get("q"):
            return self.no_query_found()

        sqs = self.searchqueryset.post_process_query(self.cleaned_data["q"])

        if self.load_all:
            sqs = sqs.load_all()

        if sqs.count():
            return sqs

        return super().search()
