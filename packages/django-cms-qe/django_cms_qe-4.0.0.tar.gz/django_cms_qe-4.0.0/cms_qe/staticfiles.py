from django.contrib.staticfiles.storage import ManifestStaticFilesStorage as DjangoManifestStaticFilesStorage


class ManifestStaticFilesStorage(DjangoManifestStaticFilesStorage):
    """
    Custom handle of ``django.contrib.staticfiles.storage.ManifestStaticFilesStorage``
    to create different URLs for every version of static file. Means when you change
    static file, Django's ``collectstatic`` detects that and creates ``staticfiles.json``
    with all hashes and adds them to URLs when tag ``static`` is used.

    It's good to use this when you don't want to have problems with caches--when you
    change static but cache still serves the old one with new generated HTML. Thanks
    to this storage you can be sure that every client will use new resources needed
    by new page.

    This custom version takes care of compatiblity of Django CMS which brings custom
    static tag to add owns version and then Django's storage has problem to cooperate
    with it. In Django 1.10 it has to override ``stored_name`` to ignore this problem
    and in Django 1.11 is brought new attribute ``manifest_strict`` which has to be
    set to ``False`` to work as in Django 1.10.
    """

    manifest_strict = False

    def stored_name(self, name):
        try:
            return super().stored_name(name)
        except ValueError:
            return name
