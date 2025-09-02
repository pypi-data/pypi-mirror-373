import logging
from collections import namedtuple

from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.http import Http404, HttpResponse
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from import_export import fields, resources, widgets
from tablib import Dataset

ExportType = namedtuple("ExportType", ("mimetype", "label"))

# Map from supported export types to their content type used for file to download.
# {extension: (mimetype, label), ...}
EXPORT_TYPES_TO_CONTENT_TYPES = {
    'csv': ExportType('text/csv', _('Export selected as CSV')),
    'tsv': ExportType('text/tab-separated-values', _('Export selected as TSV (Tab-Separated Values)')),
    'xls': ExportType('application/vnd.ms-excel', _('Export selected as XLS')),
    'xlsx': ExportType('application/vnd.ms-excel', _('Export selected as XLSX')),
    'ods': ExportType('application/vnd.oasis.opendocument.spreadsheet', _('Export selected as ODS')),
    'json': ExportType('application/json', _('Export selected as JSON')),
    'yaml': ExportType('text/plain', _('Export selected as YAML')),
    'html': ExportType('text/html', _('Export selected as HTML')),
    'latex': ExportType('application/x-latex', _('Export selected as LATEX (LaTeX Source Document)')),
    'rst': ExportType('text/x-rst', _('Export selected as RST (reStructuredText)')),
}

logger = logging.getLogger(__name__)


def get_supported_export_types():
    """
    Get only the export types supported by this operating system.
    """
    dataset = Dataset()
    available_types = {}
    for ext, item in EXPORT_TYPES_TO_CONTENT_TYPES.items():
        try:
            getattr(dataset, ext)
            available_types[ext] = item
        except (ImportError, AttributeError) as error:
            logger.info(error)
    return available_types


def register_export_action(export_type, label):
    """
    Helper to register export action to specific type. It dynamically
    creates action function and register it as ``admin.site.add_action``
    with passed label.
    """

    # pylint: disable=unused-argument
    # Warning: Some admin pages can add more arguments to actions.
    def wrapper(modeladmin, request, queryset, *args, **kwargs):
        return export_file(export_type, modeladmin, queryset)

    wrapper.__name__ = f'export_selected_objects_as_{export_type}'
    wrapper.short_description = label

    admin.site.add_action(wrapper, wrapper.__name__)

    return wrapper


def export_file(export_type, modeladmin, queryset):
    """
    Same as :any:`cms_qe.export.export_data` but wraps it into
    :any:`django.http.HttpResponse` as file to download.
    """
    export_types = get_supported_export_types()
    if export_type not in export_types:
        raise Http404(f'Type {export_type} is not supported')

    content_type = export_types[export_type].mimetype
    data = export_data(export_type, modeladmin, queryset)
    response = HttpResponse(data, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="export.{export_type}"'
    return response


def export_data(export_type, modeladmin, queryset):
    """
    Export data as ``export_type``. Supported are only those from
    function ``get_supported_export_types``.
    """
    if hasattr(modeladmin, "export_data"):
        return modeladmin.export_data(export_type, queryset)

    model_fields = queryset.model._meta.get_fields()

    class ObjectResourceMeta(resources.ModelDeclarativeMetaclass):
        """
        When model has field with choices, we want to export verbose names
        instead of keys in database. For that on resource object has to be
        field with it's list of choices. ``ModelResource`` uses metaclass
        to collect those data so we need to override that metaclass and
        pass it manually. Assign it to class after creation is late.
        """
        def __new__(cls, name, bases, attrs):  # pylint: disable=bad-mcs-classmethod-argument
            for field in model_fields:
                choices = getattr(field, 'choices', None)
                if not choices:
                    continue
                attrs[field.name] = fields.Field(
                    attribute=field.name,  # Warning: attribute has to be here.
                    widget=ChoicesWidget(choices),
                )

            # ModelAdmin can specify extra fields which could be property on
            # the model or method on the ModelAdmin. Because those fields
            # are visible on the web to the user, it's good to include them
            # in the export as well.
            for field_name in modeladmin.list_display:
                if field_name in attrs or field_name[:2] == '__':
                    continue
                attrs[field_name] = AdminField(
                    attribute=field_name,
                    modeladmin=modeladmin,
                )

            return super().__new__(cls, name, bases, attrs)

    # pylint: disable=too-few-public-methods
    class ObjectResource(resources.ModelResource, metaclass=ObjectResourceMeta):
        class Meta:
            model = queryset.model

            # After adding some extra fields, it will break order.
            # Django's ``get_fields`` keeps order but we need to exclude
            # all auto created back references.
            # Warning: ID is also auto created.
            export_order = [
                field.name
                for field in model_fields
                if not field.auto_created or field.name == 'id'
            ]

        def get_export_headers(self, selected_fields=None) -> list:
            """
            As header use verbose name which is better than database name.
            """
            return [self.get_model_field_verbose_name(field) for field in self.get_export_fields()]

        def get_model_field_verbose_name(self, field) -> str:
            name = self.get_field_name(field)
            try:
                field = queryset.model._meta.get_field(name)
            except FieldDoesNotExist:
                pass
            else:
                name = force_str(field.verbose_name)
            return name

        def export_field(self, field, instance, **kwargs):
            value = super().export_field(field, instance, **kwargs)
            if '__proxy__' in value.__class__.__name__:
                value = force_str(value)
            return value

    dataset = ObjectResource().export(queryset)
    return getattr(dataset, export_type)


class AdminField(fields.Field):
    """
    Field to support including extra fields defined in the variable
    `ModelAdmin.list_display`. Original `fields.Field` is capable
    to get property so we need to only add support of extra fields
    defined on the ModelAdmin itself.
    """

    def __init__(self, *args, **kwds):
        modeladmin = kwds.pop('modeladmin')
        self.get_modeladmin = lambda: modeladmin
        super().__init__(*args, **kwds)

    def get_value(self, instance):
        admin_property = getattr(self.get_modeladmin(), self.attribute, None)
        if admin_property:
            return admin_property(instance)
        return super().get_value(instance)


# Taken from https://github.com/django-import-export/django-import-export/issues/525#issuecomment-303046691
class ChoicesWidget(widgets.Widget):
    """
    Widget that uses choice display values in place of database values
    """

    # pylint:disable=unused-argument
    def __init__(self, choices, *args, **kwargs):
        """
        Creates a self.choices dict with a key, display value, and value,
        db value, e.g. {'Chocolate': 'CHOC'}
        """
        self.choices = dict(choices)
        self.revert_choices = {v: k for k, v in self.choices.items()}
        super().__init__()

    # pylint: disable=keyword-arg-before-vararg
    def clean(self, value, row=None, *args, **kwargs):
        """Returns the db value given the display value"""
        return self.revert_choices.get(value, value) if value else None

    def render(self, value, obj=None, **kwargs):
        """Returns the display value given the db value"""
        return self.choices.get(value, '')
