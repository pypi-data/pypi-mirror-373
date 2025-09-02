from haystack.inputs import AutoQuery


class PostProcessQuery(AutoQuery):
    """PostProcess query."""

    post_process = True
