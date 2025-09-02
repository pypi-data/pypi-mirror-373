from cms_qe_test import render_plugin

from .cms_plugins import MenuPlugin


def test_render_menu():
    assert '<ul>' in render_plugin(MenuPlugin)
