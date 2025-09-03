"""
enDI modules management
"""
from caerp.interfaces import IModuleRegistry, IPluginRegistry


def route_exists(request, route_name):
    """
    Check if a route exists in the current registry

    :param obj request: The current pyramid request
    :param str route_name: The name of the route to check

    :returns: True if the route exists
    :rtype: bool
    """
    introspector = request.registry.introspector
    route_intr = introspector.get("routes", route_name)
    return route_intr is not None


def has_module(request, module_name):
    """
    Check if a module has been enabled

    :param obj request: The current pyramid request
    :param str module_name: The name of the module to check

    :returns: True if the module exists
    :rtype: bool
    """
    return module_name in request.registry.getUtility(IModuleRegistry)


def has_plugin(request, plugin_name):
    """
    Check if a plugin has been enabled

    This tool should be used as less as possible to keep code-separated logic

    :param obj request: The current pyramid request
    :param str plugin_name: The name of the plugin to check

    :returns: True if the plugin exists
    :rtype: bool
    """
    return plugin_name in request.registry.getUtility(IPluginRegistry)


def _register_module(config, name):
    if "caerp.views." in name:
        module_name = name.split("views.")[-1]
    else:
        module_name = name
    config.registry.getUtility(IModuleRegistry).append(module_name)


def add_module(config, name):
    """
    Load an caerp module (with include) and add it to the "modules" registry
    """
    _register_module(config, name)
    config.include(name)


def _register_plugin(config, name):
    if "caerp.plugins." in name:
        plugin_name = name.split("caerp.plugins.")[-1]
    else:
        plugin_name = name
    config.registry.getUtility(IPluginRegistry).append(plugin_name)


def add_plugin(config, name):
    """
    Load an caerp module (with include) and add it to the "modules" registry
    """
    _register_plugin(config, name)
    config.include(name)


def includeme(config):
    config.registry.registerUtility([], IModuleRegistry)
    config.registry.registerUtility([], IPluginRegistry)
    config.add_directive("add_module", add_module)
    config.add_directive("add_plugin", add_plugin)
    config.add_request_method(has_module)
    config.add_request_method(has_plugin)
