"""
Hook into Alliance Auth
"""

# Django
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

# AA Mumble Quick Connect
from aa_mumble_quick_connect import urls
from aa_mumble_quick_connect.dependency_checks import mumble_service_installed


class AaMumbleQuickConnectMenuItem(MenuItemHook):
    """
    This class ensures only authorized users will see the menu entry
    """

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self=self,
            text=str(_("Mumble Quick Connect")),
            classes="fa-solid fa-headphones-simple",
            url_name="aa_mumble_quick_connect:index",
            navactive=["aa_mumble_quick_connect:"],
        )

    def render(self, request):
        """
        Render the menu item
        """

        if not mumble_service_installed():
            return ""

        if request.user.has_perm(
            "aa_mumble_quick_connect.basic_access"
        ) and request.user.has_perm("mumble.access_mumble"):
            return MenuItemHook.render(self=self, request=request)

        return ""


@hooks.register("menu_item_hook")
def register_menu():
    """
    Register the menu item
    """

    return AaMumbleQuickConnectMenuItem()


@hooks.register("url_hook")
def register_urls():
    """
    Register app urls
    """

    return UrlHook(
        urls=urls,
        namespace="aa_mumble_quick_connect",
        base_url=r"^mumble-quick-connect/",
    )
