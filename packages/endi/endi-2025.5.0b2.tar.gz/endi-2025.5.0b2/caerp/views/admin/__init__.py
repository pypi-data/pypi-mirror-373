from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin.tools import BaseAdminIndexView

BASE_URL = "/admin"


class AdminIndexView(BaseAdminIndexView):
    title = "Configuration de votre instance enDI"
    route_name = BASE_URL
    children = []


def add_admin_view(config, *args, **kwargs):
    view = args[0]
    if "renderer" not in kwargs:
        kwargs["renderer"] = "caerp:templates/admin/base_view.mako"

    if "permission" not in kwargs:
        permission = getattr(view, "permission", PERMISSIONS["global.access_admin"])
        kwargs["permission"] = permission

    if "layout" not in kwargs:
        kwargs["layout"] = "admin"

    if "parent" in kwargs:
        parent = kwargs.pop("parent")
        parent.add_child(view)

    if "route_name" not in kwargs:
        kwargs["route_name"] = view.route_name

    config.add_view(*args, **kwargs)


def includeme(config):
    config.include(".layout")
    config.add_directive("add_admin_view", add_admin_view)
    config.add_route(BASE_URL, BASE_URL)
    config.add_admin_view(AdminIndexView)

    config.include(".main")
    config.include(".sale")
    config.include(".expense")
