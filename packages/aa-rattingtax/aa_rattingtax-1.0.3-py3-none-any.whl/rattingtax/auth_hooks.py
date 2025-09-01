from django.utils.translation import gettext_lazy as _
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook
from rattingtax import urls


class RattingTaxMenuItem(MenuItemHook):
    """Ensure only authorized users will see the menu entry"""

    def __init__(self):
        MenuItemHook.__init__(
            self,
            _("Ratting tax"),
            "fas fa-coins fa-fw",
            "rattingtax:dashboard",
            navactive=["rattingtax:"],
        )

    def render(self, request):
        if request.user.has_perm("rattingtax.basic_access"):
            return super().render(request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return RattingTaxMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "rattingtax", r"^rattingtax/")
