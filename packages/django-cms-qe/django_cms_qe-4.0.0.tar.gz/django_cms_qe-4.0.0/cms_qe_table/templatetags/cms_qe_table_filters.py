from django.template import Library, TemplateDoesNotExist, loader

register = Library()


@register.filter
def cms_qe_table_value(value: str) -> str:
    """
    Django template filter to customize displaying of values by their type.
    If value is of type bool, then is used template ``cms_qe/table/table_value_bool.html``.
    Every boilerplate or concrete app can customize this. When no template exists
    for given value type standard value represenation is used.
    """
    value_type = type(value).__name__
    template_name = f'cms_qe/table/table_value_{value_type}.html'
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return value
    context = {
        'value': value,
    }
    return template.render(context)
