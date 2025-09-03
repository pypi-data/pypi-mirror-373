import os
from caerp.views import API_ROUTE

PLAN_API_ROUTE = os.path.join(API_ROUTE, "progress_invoicing_plans")
PLAN_ITEM_API_ROUTE = os.path.join(PLAN_API_ROUTE, "{id}")

CHAPTER_API_ROUTE = os.path.join(PLAN_ITEM_API_ROUTE, "chapters")
CHAPTER_ITEM_API_ROUTE = os.path.join(CHAPTER_API_ROUTE, "{cid}")

PRODUCT_API_ROUTE = os.path.join(CHAPTER_ITEM_API_ROUTE, "products")
PRODUCT_ITEM_API_ROUTE = os.path.join(PRODUCT_API_ROUTE, "{pid}")

WORK_ITEMS_API_ROUTE = os.path.join(PRODUCT_ITEM_API_ROUTE, "work_items")
WORK_ITEMS_ITEM_API_ROUTE = os.path.join(WORK_ITEMS_API_ROUTE, "{wid}")


def includeme(config):
    for route in (
        PLAN_ITEM_API_ROUTE,
        CHAPTER_API_ROUTE,
    ):
        config.add_route(
            route,
            route,
            traverse="/progress_invoicing_plans/{id}",
        )
    for route in (CHAPTER_ITEM_API_ROUTE, PRODUCT_API_ROUTE):
        config.add_route(
            route,
            route,
            traverse="/progress_invoicing_chapters/{cid}",
        )
    config.add_route(
        PRODUCT_ITEM_API_ROUTE,
        PRODUCT_ITEM_API_ROUTE,
        traverse="/progress_invoicing_base_products/{pid}",
    )
    config.add_route(
        WORK_ITEMS_API_ROUTE,
        WORK_ITEMS_API_ROUTE,
        traverse="/progress_invoicing_base_products/{pid}",
    )
    config.add_route(
        WORK_ITEMS_ITEM_API_ROUTE,
        WORK_ITEMS_ITEM_API_ROUTE,
        traverse="/progress_invoicing_work_items/{wid}",
    )
