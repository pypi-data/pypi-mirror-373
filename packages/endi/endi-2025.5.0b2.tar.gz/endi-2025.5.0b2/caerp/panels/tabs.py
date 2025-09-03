"""
Tabs menu panels
"""


def tabs_panel(context, request, menu):
    """
    Collect datas for menu display

    :param obj context: The current context
    :param request: The current request object
    :param obj menu: An instance of utils.menu.Menu
    """
    return {
        "menu": menu,
        "current": menu.current or context,
    }


def tabs_item_panel(context, request, menu_item, bind_params):
    """
    Collect datas for menu entry display

    :param obj context: The current context
    :param request: The current request object
    :param obj menu_item: An instance of utils.menu.MenuItem or
    utils.menu.MenuDropdown
    :param dict bind_params: Binding parameters attached to the parent menu and
    used to dynamically render some attributes
    """
    return {
        "menu_item": menu_item,
        "bind_params": bind_params,
    }


def includeme(config):
    config.add_panel(
        tabs_panel,
        "tabs",
        renderer="/panels/tabs.mako",
    )
    config.add_panel(
        tabs_item_panel,
        "tabs_item",
        renderer="/panels/tabs_item.mako",
    )
