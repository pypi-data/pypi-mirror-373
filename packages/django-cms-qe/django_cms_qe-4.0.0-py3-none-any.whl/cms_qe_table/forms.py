from typing import Any, Optional

from django import forms
from django.template import loader
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import TablePluginModel
from .utils import get_models_choices


class TableWidget(forms.Select):
    """
    Custom widget for table select which reloads choices for columns.
    """

    def render(self, name: str, value: str, attrs: Optional[dict] = None, renderer: Any = None) -> Any:
        select = super().render(name, value, attrs, renderer)
        context = {
            'id': attrs['id'] if attrs else 'table-widget',
            'select': select,
            'value': value,
            'url': reverse('get_table_choices'),
        }
        template = loader.get_template('cms_qe/table/table_widget.html').render(context)
        return mark_safe(template)


class ColumnsWidget(forms.SelectMultiple):
    """
    Custom widget for columns select which provides needed information for
    :any:`cms_qe_table.forms.TableWidget`. Please use both in the same form.
    """

    def render(self, name: str, value: str, attrs: Optional[dict] = None, renderer: Any = None):
        select = super().render(name, value, attrs, renderer)
        context = {
            'id': attrs['id'] if attrs else 'column-widget',
            'select': select,
            'value': value,
        }
        template = loader.get_template('cms_qe/table/columns_widget.html').render(context)
        return mark_safe(template)


class FilterWidget(forms.JSONField.widget):
    """
    Custom widget for columns select which provides needed information for
    :any:`cms_qe_table.forms.TableWidget`. Please use both in the same form.
    """

    def render(self, name: str, value: str, attrs: Optional[dict] = None):  # pylint: disable=W0221
        textarea = super().render(name, value, attrs)
        context = {
            'id': attrs['id'] if attrs else 'filter-widget',
            'textarea': textarea,
            'value': value,
        }
        template = loader.get_template('cms_qe/table/filter_widget.html').render(context)
        return mark_safe(template)


class MultipleChoiceField(forms.MultipleChoiceField):
    """
    Same as Django's ``MultipleChoiceField`` but accept any value because it's
    used without any choices.
    """

    def valid_value(self, value: Any) -> bool:
        return True


class TablePluginForm(forms.ModelForm):
    """
    Configuration form for plugin Table for Django CMS QE.
    """

    table = forms.ChoiceField(choices=get_models_choices(), widget=TableWidget)
    columns = MultipleChoiceField(widget=ColumnsWidget)
    filter = forms.JSONField(widget=FilterWidget)

    class Meta:
        model = TablePluginModel
        fields = ['table', 'columns', 'filter', 'paging_show', 'paging_per_page']
