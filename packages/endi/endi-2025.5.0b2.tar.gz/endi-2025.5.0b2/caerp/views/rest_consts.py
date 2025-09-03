from caerp.compute.math_utils import convert_to_int


def country_rest_view(request):
    from caerp.consts.insee_countries import COUNTRIES

    return COUNTRIES


def department_rest_view(request):
    from caerp.consts.insee_departments import DEPARTMENTS

    return DEPARTMENTS


def street_type_rest_view(request):
    from caerp.consts.street_types import TYPES

    return TYPES


def street_number_complements_rest_view(request):
    from caerp.consts.street_number_complements import LETTERS

    return LETTERS


def config_rest_view(request):
    settings = request.registry.settings
    size = settings.get("caerp.maxfilesize", 2000000)
    max_allowed_file_size = convert_to_int(size, 2000000)
    leaflet_layer_url = settings.get(
        "cearp.leaflet_layer_url", "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    )
    return {
        "max_allowed_file_size": max_allowed_file_size,
        "leaflet_layer_url": leaflet_layer_url,
    }


def includeme(config):
    for label, view in (
        ("countries", country_rest_view),
        ("street_types", street_type_rest_view),
        ("street_number_complements", street_number_complements_rest_view),
        ("departments", department_rest_view),
        ("config", config_rest_view),
    ):
        route = f"/api/v1/consts/{label}"
        config.add_route(route, route)
        config.add_view(
            view,
            route_name=route,
            renderer="json",
            http_cache=3600 * 24,
            request_method="GET",
        )
