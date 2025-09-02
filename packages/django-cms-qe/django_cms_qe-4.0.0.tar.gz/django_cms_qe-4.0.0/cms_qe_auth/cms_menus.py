from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from menus.base import Modifier, NavigationNode
from menus.menu_pool import menu_pool

URL_NAME_TO_TITLE = {
    'login': _('Login'),
    'logout': _('Logout'),
    'password_change': _('Change password'),
    'password_change_done': _('Change password'),
    'password_reset': _('Reset pasword'),
    'password_reset_done': _('Reset pasword'),
    'password_reset_confirm': _('Reset pasword'),
    'password_reset_complete': _('Reset pasword'),
    'register': _('Register'),
}


@menu_pool.register_modifier
class AuthModifier(Modifier):
    """
    This modifier adds to breadcrumb all authentication URLs.
    """
    # pylint: disable=too-many-arguments
    def modify(
            self,
            request: HttpRequest,
            nodes: NavigationNode,
            namespace: str,
            root_id: int,
            post_cut: bool,
            breadcrumb: bool,
    ) -> NavigationNode:
        if not (
                breadcrumb
                and request.resolver_match
                and request.resolver_match.url_name in URL_NAME_TO_TITLE
        ):
            return nodes

        root_nodes = [node for node in nodes if node.attr.get('is_home')]
        if root_nodes:
            root = root_nodes[0]
        else:
            root = NavigationNode('Home', '/', 'rootnodeid')
            root.selected = True

        title = URL_NAME_TO_TITLE[request.resolver_match.url_name]
        node = NavigationNode(title, request.path, 'extranodeid')
        node.selected = True
        node.parent = root
        root.children = [node]

        return [root, node]
