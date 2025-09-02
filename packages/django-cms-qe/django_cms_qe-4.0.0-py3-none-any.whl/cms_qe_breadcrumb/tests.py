import pytest

from cms_qe_test import render_plugin

from .cms_plugins import BreadcrumbPlugin


@pytest.mark.skip(reason="Skip until django-cms >= 4.0.")
def test_render():
    """
    ValueError: invalid literal for int() with base 10: 'menu/breadcrumb.html'

    only_visible = 'menu/breadcrumb.html'

    menus/templatetags/menu_tags.py:
        try:
            only_visible = bool(int(only_visible))
        except TypeError:
            only_visible = bool(only_visible)
    """
    assert '<ol>' in render_plugin(BreadcrumbPlugin)
