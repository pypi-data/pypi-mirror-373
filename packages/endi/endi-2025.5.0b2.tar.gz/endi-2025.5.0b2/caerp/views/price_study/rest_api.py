import logging


from caerp.consts.permissions import PERMISSIONS
from caerp.models.sale_product.base import BaseSaleProduct
from caerp.models.sale_product.work import SaleProductWork

from caerp.models.price_study import (
    BasePriceStudyProduct,
    PriceStudyProduct,
    PriceStudyDiscount,
    PriceStudyChapter,
    PriceStudyWork,
    PriceStudyWorkItem,
    PriceStudy,
)
from caerp.utils.rest.apiv1 import RestError

from caerp.forms.price_study import (
    get_chapter_add_edit_schema,
    get_price_study_add_edit_schema,
    get_work_item_add_edit_schema,
    get_discount_add_edit_schema,
    get_product_add_schema,
    get_product_edit_schema,
)
from caerp.views import BaseRestView

from .routes import (
    CHAPTER_API_ROUTE,
    CHAPTER_ITEM_API_ROUTE,
    PRICE_STUDY_ITEM_API_ROUTE,
    PRODUCT_API_ROUTE,
    PRODUCT_ITEM_API_ROUTE,
    DISCOUNT_API_ROUTE,
    DISCOUNT_ITEM_API_ROUTE,
    WORK_ITEMS_ITEM_API_ROUTE,
    WORK_ITEMS_API_ROUTE,
)

logger = logging.getLogger(__name__)


class RestPriceStudyView(BaseRestView):
    """
    Rest service for Price studies, only provide item access

    """

    schema = get_price_study_add_edit_schema()

    def margin_rate_reset_view(self):
        """
        View handling the margin rate reset on the whole document
        """
        margin_rate = self.context.get_company().margin_rate
        if margin_rate:
            for product in self.context.products:
                product.margin_rate = margin_rate
                self.dbsession.merge(product)
        return self.context

    def after_flush(self, entry, edit, attributes):
        self.context.on_before_commit(self.request, "edit", attributes)
        return super().after_flush(entry, edit, attributes)


class RestPriceStudyChapterView(BaseRestView):
    """
    Chapter rest api view
    """

    schema = get_chapter_add_edit_schema()

    def collection_get(self):
        return self.context.chapters

    def post_format(self, entry: "PriceStudyChapter", edit: bool, attributes: dict):
        """
        Associate a newly created element to the parent task
        """
        if not edit:
            entry.price_study = self.context
        return entry

    def after_flush(self, entry: "PriceStudyChapter", edit: bool, attributes: dict):
        """
        Run after flushing modification to entry
        """
        if edit:
            state = "update"
        else:
            state = "add"
        entry.on_before_commit(self.request, state, attributes)
        return super().after_flush(entry, edit, attributes)

    def on_delete(self):
        self.context.on_before_commit(self.request, "delete")


class RestPriceStudyProductView(BaseRestView):
    def get_schema(self, submitted):
        if isinstance(self.context, PriceStudyChapter):
            type_ = submitted["type_"]
            # It's an add view
            schema = get_product_add_schema(type_)
        else:
            schema = get_product_edit_schema(self.context.__class__)
        return schema

    def post_format(self, entry: BasePriceStudyProduct, edit: bool, attributes: dict):
        if not edit:
            entry.chapter = self.context

        return entry

    def after_flush(self, entry: BasePriceStudyProduct, edit: bool, attributes: dict):
        """
        Ensure the current edited context (and its related) keep coherent
        values

        If we're adding an element based on an existing catalog element, we
        also attach respective PriceStudyWorkItem

        :param obj entry: the new Product instance
        :param bool edit: Are we editing ?
        :param dict attributes: The submitted attributes
        """
        logger.debug("{}.after_flush()".format(self.__class__))
        if edit:
            state = "update"
        else:
            state = "add"

        entry.on_before_commit(self.request, state, attributes)
        entry = self.dbsession.merge(entry)
        self.dbsession.flush()
        return entry

    def load_from_catalog_view(self):
        logger.debug("Loading datas from catalog")
        sale_products: dict = self.request.json_body.get("sale_products", {})
        logger.debug(f"sale_products : {sale_products}")

        lines = []
        for id_, quantity in sale_products.items():
            sale_product = BaseSaleProduct.get(id_)
            if sale_product:
                if isinstance(sale_product, SaleProductWork):
                    factory = PriceStudyWork
                else:
                    factory = PriceStudyProduct
                entry = factory.from_sale_product(sale_product)
                entry.quantity = quantity
                self.context.products.append(entry)
                self.dbsession.add(entry)
                self.dbsession.flush()
                entry.on_before_commit(self.request, "add")
                lines.append(entry)
            else:
                logger.error("Unkown sale_product {}".format(id_))
        return lines

    def collection_get(self):
        return self.context.products

    def duplicate_view(self):
        duplicate = self.context.duplicate()
        self.dbsession.add(duplicate)
        self.dbsession.flush()
        self.context.on_before_commit(self.request, "add")
        return duplicate

    def on_delete(self):
        self.context.on_before_commit(self.request, "delete")


class RestWorkItemView(BaseRestView):
    """
    Json api for Work Items

    Collection views have a PriceStudyWork context

    Context views have a PriceStudyWorkItem context
    """

    def get_schema(self, submitted):
        return get_work_item_add_edit_schema()

    def collection_get(self):
        return self.context.items

    def post_format(self, entry, edit, attributes):
        if not edit:
            self.context.items.append(entry)
        return entry

    def after_flush(self, entry, edit, attributes):
        """
        Keep data integrity, launches several computations if needed
        """
        if edit:
            state = "update"
        else:
            state = "add"
        entry.on_before_commit(self.request, state, attributes)
        entry = self.dbsession.merge(entry)
        self.dbsession.flush()
        return entry

    def load_from_catalog_view(self):
        logger.debug("Loading work items from catalog")
        sale_products = self.request.json_body.get("sale_products", [])
        logger.debug(f"sale_products {sale_products}")

        lines = []
        for id_, quantity in sale_products.items():
            sale_product = BaseSaleProduct.get(id_)
            if sale_product:
                entry = PriceStudyWorkItem.from_sale_product(sale_product)
                entry.work_unit_quantity = quantity
                self.context.items.append(entry)
                self.dbsession.add(entry)
                self.dbsession.flush()
                entry.on_before_commit(self.request, "add")
                lines.append(entry)
            else:
                logger.error("Unkown sale_product {}".format(id_))

        return lines

    def on_delete(self):
        self.context.on_before_commit(self.request, "delete")

    def duplicate_view(self):
        duplicate = self.context.duplicate()
        self.dbsession.add(duplicate)
        self.dbsession.flush()
        self.context.on_before_commit(self.request, "add")
        return duplicate


class RestPriceStudyDiscountView(BaseRestView):
    def get_schema(self, submitted):
        if "type_" in submitted:
            schema = get_discount_add_edit_schema(submitted["type_"])
        elif isinstance(self.context, PriceStudyDiscount):
            schema = get_discount_add_edit_schema(self.context.type_)
        else:
            raise RestError("Missing mandatory argument type_")
        return schema

    def post_format(self, entry, edit, attributes):
        if not edit:
            entry.price_study = self.context

        return entry

    def after_flush(self, entry, edit, attributes):
        """
        Ensure the current edited context (and its related) keep coherent
        values

        If we're adding an element based on an existing catalog element, we
        also attach respective PriceStudyWorkItem

        :param obj entry: the new Product instance
        :param bool edit: Are we editing ?
        :param dict attributes: The submitted attributes
        """
        if not edit:
            state = "add"
        else:
            state = "update"

        entry.on_before_commit(self.request, state, attributes)
        entry = self.dbsession.merge(entry)
        self.dbsession.flush()
        return entry

    def collection_get(self):
        return self.context.discounts

    def on_delete(self):
        self.context.on_before_commit(self.request, "delete")


def includeme(config):
    config.add_rest_service(
        RestPriceStudyView,
        PRICE_STUDY_ITEM_API_ROUTE,
        context=PriceStudy,
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_price_study"],
        delete_rights=PERMISSIONS["context.edit_price_study"],
    )
    config.add_view(
        RestPriceStudyView,
        attr="form_config",
        route_name=PRICE_STUDY_ITEM_API_ROUTE,
        request_param="form_config",
        renderer="json",
        context=PriceStudy,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        RestPriceStudyView,
        attr="margin_rate_reset_view",
        route_name=PRICE_STUDY_ITEM_API_ROUTE,
        request_param="reset_margin_rate",
        renderer="json",
        request_method="POST",
        context=PriceStudy,
        permission=PERMISSIONS["context.edit_price_study"],
    )
    config.add_rest_service(
        RestPriceStudyChapterView,
        CHAPTER_ITEM_API_ROUTE,
        collection_route_name=CHAPTER_API_ROUTE,
        collection_context=PriceStudy,
        context=PriceStudyChapter,
        add_rights=PERMISSIONS["context.edit_price_study"],
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_price_study"],
        delete_rights=PERMISSIONS["context.edit_price_study"],
    )
    config.add_rest_service(
        RestPriceStudyProductView,
        PRODUCT_ITEM_API_ROUTE,
        collection_route_name=PRODUCT_API_ROUTE,
        collection_context=PriceStudyChapter,
        context=BasePriceStudyProduct,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_price_study"],
        edit_rights=PERMISSIONS["context.edit_price_study"],
        delete_rights=PERMISSIONS["context.edit_price_study"],
    )
    config.add_rest_service(
        RestPriceStudyDiscountView,
        DISCOUNT_ITEM_API_ROUTE,
        collection_route_name=DISCOUNT_API_ROUTE,
        collection_context=PriceStudy,
        context=PriceStudyDiscount,
        collection_view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_price_study"],
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_price_study"],
        delete_rights=PERMISSIONS["context.edit_price_study"],
    )
    config.add_view(
        RestPriceStudyProductView,
        attr="load_from_catalog_view",
        route_name=PRODUCT_API_ROUTE,
        request_param="action=load_from_catalog",
        request_method="POST",
        renderer="json",
        context=PriceStudyChapter,
        permission=PERMISSIONS["context.edit_price_study"],
    )
    config.add_view(
        RestPriceStudyProductView,
        attr="duplicate_view",
        route_name=PRODUCT_ITEM_API_ROUTE,
        request_param="action=duplicate",
        request_method="POST",
        renderer="json",
        context=BasePriceStudyProduct,
        permission=PERMISSIONS["context.edit_price_study"],
    )
    config.add_rest_service(
        RestWorkItemView,
        WORK_ITEMS_ITEM_API_ROUTE,
        collection_route_name=WORK_ITEMS_API_ROUTE,
        collection_context=PriceStudyWork,
        context=PriceStudyWorkItem,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_price_study"],
        edit_rights=PERMISSIONS["context.edit_price_study"],
        delete_rights=PERMISSIONS["context.edit_price_study"],
    )
    config.add_view(
        RestWorkItemView,
        attr="duplicate_view",
        route_name=WORK_ITEMS_ITEM_API_ROUTE,
        request_param="action=duplicate",
        request_method="POST",
        renderer="json",
        context=PriceStudyWorkItem,
        permission=PERMISSIONS["context.edit_price_study"],
    )
    config.add_view(
        RestWorkItemView,
        attr="load_from_catalog_view",
        route_name=WORK_ITEMS_API_ROUTE,
        request_param="action=load_from_catalog",
        request_method="POST",
        renderer="json",
        context=PriceStudyWork,
        permission=PERMISSIONS["context.edit_price_study"],
    )
