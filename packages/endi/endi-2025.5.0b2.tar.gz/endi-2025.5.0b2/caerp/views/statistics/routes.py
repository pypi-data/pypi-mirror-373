import os

STATISTICS_ROUTE = "/statistics"
STATISTIC_ITEM_ROUTE = os.path.join(STATISTICS_ROUTE, "{id}")
STATISTIC_ITEM_CSV_ROUTE = os.path.join(STATISTICS_ROUTE, "{id}.csv")
ENTRY_ITEM_CSV_ROUTE = os.path.join("/statistics", "entries", "{eid}.csv")

API_ROUTE = "/api/v1/statistics"
API_ITEM_ROUTE = "/api/v1/statistics/{id}"
API_ENTRIES_ROUTE = os.path.join(API_ITEM_ROUTE, "entries")
API_ENTRY_ITEM_ROUTE = os.path.join(API_ENTRIES_ROUTE, "{eid}")
API_CRITERIA_ROUTE = os.path.join(API_ENTRY_ITEM_ROUTE, "criteria")
API_CRITERION_ITEM_ROUTE = os.path.join(API_CRITERIA_ROUTE, "{cid}")


def get_sheet_url(
    request,
    sheet=None,
    _query={},
    suffix="",
    api=False,
):
    if sheet is None:
        sheet = request.context

    route = "/statistics/{id}"
    if api:
        route = "/api/v1{}".format(route)

    if suffix:
        route += suffix

    return request.route_path(route, id=sheet.id, _query=_query)


def includeme(config):
    config.add_route(STATISTICS_ROUTE, STATISTICS_ROUTE)
    config.add_route(API_ROUTE, API_ROUTE)

    traverse = "/statistics/{id}"
    for route in (
        STATISTIC_ITEM_ROUTE,
        STATISTIC_ITEM_CSV_ROUTE,
        API_ITEM_ROUTE,
        API_ENTRIES_ROUTE,
    ):
        rroute = route.replace("id", r"id:\d+")

        config.add_route(route, rroute, traverse=traverse)

    traverse = "/statistic_entries/{eid}"
    for route in (API_ENTRY_ITEM_ROUTE, ENTRY_ITEM_CSV_ROUTE, API_CRITERIA_ROUTE):
        config.add_route(route, route, traverse=traverse)

    config.add_route(
        API_CRITERION_ITEM_ROUTE,
        API_CRITERION_ITEM_ROUTE,
        traverse="/statistic_criteria/{cid}",
    )
