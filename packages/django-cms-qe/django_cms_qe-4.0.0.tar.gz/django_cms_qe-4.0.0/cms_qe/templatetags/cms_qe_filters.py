import re

from django import template

register = template.Library()


@register.filter
def add_str(value, arg):
    """
    Same as :py:func:`django.template.defaultfilters.add` but always convert to ``str``.
    """
    return str(value) + str(arg)


@register.filter
def split_by_delimiter(value, delimiter):
    """
    Split the value by the delimiter.
    """
    return value.split(delimiter)


@register.filter
def get_sequence_item(value, position):
    """
    Get sequence item at the position.
    """
    try:
        return value[position]
    except IndexError:
        return ""


@register.filter
def matches_pattern(value, pattern):
    """
    The value matches pattern.
    """
    if value is None:
        return False
    return bool(re.match(pattern, value))
