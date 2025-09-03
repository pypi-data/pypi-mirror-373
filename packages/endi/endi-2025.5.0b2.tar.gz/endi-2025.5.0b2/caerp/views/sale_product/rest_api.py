import logging
from caerp.consts.permissions import PERMISSIONS
from sqlalchemy import (
    or_,
)
import colander
from pyramid.csrf import get_csrf_token

from caerp_base.models.base import DBSESSION

from caerp.models.config import Config
from caerp.models.project import ProjectType
from caerp.models.tva import Tva, Product
from caerp.models.task import WorkUnit
from caerp.models.third_party.supplier import Supplier
from caerp.models.sale_product.category import SaleProductCategory
from caerp.models.sale_product.base import (
    BaseSaleProduct,
    SaleProductStockOperation,
)
from caerp.models.sale_product.sale_product import (
    SaleProductProduct,
    SaleProductMaterial,
    SaleProductServiceDelivery,
    SaleProductWorkForce,
)
from caerp.models.sale_product.work import SaleProductWork
from caerp.models.sale_product.training import (
    GROUP_SIZES_OPTIONS,
    PRESENCE_MODALITY_OPTIONS,
    SaleProductTraining,
    SaleProductVAE,
)
from caerp.models.sale_product.work_item import WorkItem
from caerp.models.company import Company

from caerp.forms.sale_product.sale_product import (
    get_sale_product_add_edit_schema,
    get_sale_product_list_schema,
    get_stock_operation_add_edit_schema,
)
from caerp.forms.sale_product.work import get_work_item_add_edit_schema
from caerp.forms.sale_product.category import (
    get_sale_product_category_add_edit_schema,
)

from caerp.views import (
    BaseRestView,
    RestListMixinClass,
    BaseCsvView,
)
from caerp.views.sale_product.routes import (
    CATALOG_ROUTE,
    CATEGORY_ITEM_API_ROUTE,
    CATEGORY_API_ROUTE,
    PRODUCT_API_ROUTE,
    PRODUCT_ITEM_API_ROUTE,
    WORK_ITEMS_API_ROUTE,
    WORK_ITEMS_ITEM_API_ROUTE,
    STOCK_OPERATIONS_API_ROUTE,
    STOCK_OPERATIONS_ITEM_API_ROUTE,
    CATALOG_API_ROUTE,
)


logger = logging.getLogger(__name__)

# TODO find sqlAlchemy or sql engine max like param length function or
# constant: couldn't find it
# param length > 118 will return empty result
ROUNDED_MAX_LIKE_QUERY_PARAM_LENGTH = 115


class RestSaleProductView(BaseRestView, RestListMixinClass):
    """
    Full REST CRUD viewset :

    - detail views GET/PUT/POST/DELETE
    - list views GET
    """

    list_schema = get_sale_product_list_schema()
    sort_columns = {
        "current_stock": "current_stock",
        "ht": "ht",
        "id": "id",
        "label": "label",
        "ref": "ref",
        "search": "label",
        "supplier_id": "supplier_id",
        "updated_at": "updated_at",
        "supplier_ref": "supplier_ref",
    }

    factories = dict(
        (c.__tablename__, c)
        for c in (
            SaleProductWork,
            SaleProductMaterial,
            SaleProductWorkForce,
            SaleProductServiceDelivery,
            SaleProductTraining,
            SaleProductVAE,
            SaleProductProduct,
        )
    )

    def query(self):
        return BaseSaleProduct.query().filter_by(company_id=self.context.id)

    def filter_type_(self, query, appstruct):
        type_ = appstruct.get("type_")
        if type_ not in (None, colander.null, ""):
            logger.debug("Filtering by type_ : {}".format(type_))
            query = query.filter(BaseSaleProduct.type_ == type_)
        return query

    def filter_label(self, query, appstruct):
        label = appstruct.get("search")
        if label not in (None, colander.null, ""):
            logger.debug("Filtering by label : {}".format(label))
            query = query.filter(BaseSaleProduct.label.like("%{}%".format(label)))
        return query

    def filter_description_and_notes(self, query, appstruct):
        description = appstruct.get("description")
        if description not in (None, colander.null, ""):
            logger.debug("Filtering by description : {}".format(description))
            query = query.filter(
                or_(
                    BaseSaleProduct.description.like(
                        "%{}%".format(description[:ROUNDED_MAX_LIKE_QUERY_PARAM_LENGTH])
                    ),
                    BaseSaleProduct.notes.like(
                        "%{}%".format(description[:ROUNDED_MAX_LIKE_QUERY_PARAM_LENGTH])
                    ),
                )
            )
        return query

    def filter_supplier_ref(self, query, appstruct):
        supplier_ref = appstruct.get("supplier_ref")
        if supplier_ref not in (None, colander.null, ""):
            logger.debug("Filtering by supplier_ref : {}".format(supplier_ref))
            query = query.filter(
                BaseSaleProduct.supplier_ref.like("%{}%".format(supplier_ref))
            )
        return query

    def filter_category_id(self, query, appstruct):
        category_id = appstruct.get("category_id")
        if category_id not in (None, colander.null):
            logger.debug("Filtering by category_id : {}".format(category_id))
            query = query.filter_by(category_id=category_id)
        return query

    def filter_ref(self, query, appstruct):
        ref = appstruct.get("ref")
        if ref not in (None, colander.null):
            logger.debug("Filtering by ref : {}".format(ref))
            query = query.filter(BaseSaleProduct.ref.like("%{}%".format(ref)))
        return query

    def filter_supplier_id(self, query, appstruct):
        supplier_id = appstruct.get("supplier_id")
        if supplier_id not in (None, colander.null):
            logger.debug("Filtering by supplier_id : {}".format(supplier_id))
            query = query.filter_by(supplier_id=supplier_id)
        return query

    def filter_types(self, query, appstruct):
        """
        Filter by product type_
        """
        simple_only = appstruct.get("simple_only", False)
        if simple_only is True:
            types = BaseSaleProduct.SIMPLE_TYPES
            logger.debug("Filtering by type_ : {}".format(types))
            query = query.filter(BaseSaleProduct.type_.in_(types))
        return query

    def filter_mode(self, query, appstruct):
        """ """
        mode = appstruct.get("mode")
        if mode not in (None, colander.null):
            logger.debug("Filtering by mode : {}".format(mode))
            query = query.filter(BaseSaleProduct.mode == mode)
        return query

    def _collect_distinct_attribute_values(self, attrname):
        """
        Collect distinct values of attrname used by the current company for its
        BaseSaleProduct
        Also clean void values

        :param str attrname: The BaseSaleProduct column name
        :rtype: list
        """
        column = getattr(BaseSaleProduct, attrname)
        query = DBSESSION().query(column.distinct())
        query = query.filter(
            BaseSaleProduct.company_id == self.context.id,
        )
        query = query.filter(column != None)
        query = query.filter(column != "")
        return [val[0] for val in query]

    def _collect_references(self):
        return self._collect_distinct_attribute_values("ref")

    def _collect_labels(self):
        return self._collect_distinct_attribute_values("label")

    def _collect_descriptions_and_notes(self):
        descriptions = self._collect_distinct_attribute_values("description")
        notes = self._collect_distinct_attribute_values("notes")
        return descriptions + notes

    def _collect_suppliers_refs(self):
        return self._collect_distinct_attribute_values("supplier_ref")

    def _collect_modes(self):
        return self._collect_distinct_attribute_values("mode")

    def _collect_product_types(self, trainer):
        """
        Collect product types a user can add
        """
        values = list(zip(BaseSaleProduct.ALL_TYPES, BaseSaleProduct.TYPE_LABELS))
        return [
            {"value": value[0], "label": value[1]}
            for value in values
            if not (
                value[0] in ("sale_product_training", "sale_product_vae")
                and not trainer
            )
        ]

    def _collect_presence_modalities(self):
        return [
            dict(value=value, label=label) for value, label in PRESENCE_MODALITY_OPTIONS
        ]

    def _collect_group_sizes(self):
        return [dict(value=value, label=label) for value, label in GROUP_SIZES_OPTIONS]

    def _get_form_options(self):
        """
        The view for company products options load

        :param obj context: The context : The company object
        :param obj request: the Pyramid's request object
        """
        default_tva = Tva.get_default()
        if default_tva:
            tva_id = default_tva.id
        else:
            tva_id = ""

        trainer = self.context.has_trainer()
        product_types = self._collect_product_types(trainer)
        ttc_mode_enabled = ProjectType.with_ttc_exists()
        tva_mode_enabled = not self.request.config.get_value(
            "sale_catalog_notva_mode", default=False, type_=bool
        )
        margin_rate_enabled = self.context.use_margin_rate_in_catalog

        return dict(
            tvas=Tva.query().all(),
            unities=WorkUnit.query().all(),
            products=Product.query()
            .filter(Product.internal == False)
            .all(),  # noqa: E712 E501
            categories=SaleProductCategory.query()
            .filter_by(company_id=self.context.id)
            .all(),
            suppliers=Supplier.query().filter_by(company_id=self.context.id).all(),
            references=self._collect_references(),
            product_labels=self._collect_labels(),
            product_descriptions=self._collect_descriptions_and_notes(),
            product_suppliers_refs=self._collect_suppliers_refs(),
            modes=self._collect_modes(),
            product_types=product_types,
            presence_modalities=self._collect_presence_modalities(),
            group_sizes=self._collect_group_sizes(),
            base_product_types=[
                ptype
                for ptype in product_types
                if ptype["value"] in BaseSaleProduct.SIMPLE_TYPES
            ],
            trainer=trainer,
            csrf_token=get_csrf_token(self.request),
            ttc_mode_enabled=ttc_mode_enabled,
            tva_mode_enabled=tva_mode_enabled,
            margin_rate_enabled=margin_rate_enabled,
            defaults={
                "tva_id": tva_id,
            },
            computing_info={
                "use_contribution": Config.get_value(
                    "price_study_uses_contribution", default=True, type_=bool
                ),
                "use_insurance": Config.get_value(
                    "price_study_uses_insurance", default=True, type_=bool
                ),
                "general_overhead": self.context.general_overhead or 0,
                "margin_rate": self.context.margin_rate or 0,
                "insurance": Company.get_rate(self.context.id, "insurance"),
                "contribution": Company.get_rate(self.context.id, "contribution"),
            },
            csv_export_url=self.request.route_path(
                PRODUCT_API_ROUTE,
                id=self.context.id,
                _query=dict(action="export_csv"),
            ),
            json_export_url=self.request.route_path(
                CATALOG_ROUTE,
                id=self.context.id,
                _query=dict(action="export_json"),
            ),
            json_import_url=self.request.route_path(
                CATALOG_ROUTE,
                id=self.context.id,
                _query=dict(action="import_json"),
            ),
        )

    def form_config(self):
        result = {"options": self._get_form_options()}
        return result

    def pre_format(self, submitted, edit):
        # Si on édite un SaleProductWork, on ne valide pas les work_items (ils
        # ont déjà été associés dynamiquement
        if "types" in submitted:
            if not isinstance(submitted["types"], list):
                submitted["types"] = [type_ for type_ in [submitted["types"]]]
        if edit and "items" in submitted:
            submitted.pop("items")

        if edit and "type_" in submitted and submitted["type_"] != self.context.type_:
            logger.debug("Try to change a sale product type, silly hack here to switch")
            self.new_type = submitted.pop("type_")
        return submitted

    def get_schema(self, submitted):
        """
        Retrieve a colander validation schema regarding if it's an add or edit
        view

        For add form only treat label and type_ fields

        For edit form returns a schema specific to the context

        sale_product_work : specific treatment

        sale_product_product
        sale_product_material
        sale_product_service_delivery
        sale_product_work_force

        :param dict submitted: The submitted form datas
        :returns: A colanderalechmy.SQLAlchemySchemaNode
        """
        if isinstance(self.context, Company):
            type_ = submitted["type_"]
            factory = self.factories[type_]
            # NB : ici on ajoute les champs general_overhead/margin_rate/mode même si
            # ils ne sont pas dans les données envoyées par le client afin que leur
            # valeur par défaut soient settées via le schéma colander
            schema = get_sale_product_add_edit_schema(
                factory,
                includes=("label", "type_", "general_overhead", "margin_rate", "mode"),
                edit=False,
            )
        else:
            schema = get_sale_product_add_edit_schema(self.context.__class__)
        return schema

    def post_format(self, entry, edit, attributes):
        """
        Allows to apply post formatting to the model before flushing
        it_customize_tasklinegroup_fields
        """
        if not edit:
            entry.company_id = self.context.id

        if hasattr(self, "new_type"):
            logger.debug("We change the product type, duplicate/delete/set id")
            new_class = self.factories.get(self.new_type)
            new_instance = entry.duplicate(dest_class=new_class)
            new_instance.label = entry.label
            entry_id = entry.id
            self.dbsession.delete(entry)
            self.dbsession.flush()
            new_instance.id = entry_id
            self.dbsession.add(new_instance)
            self.dbsession.flush()
            return new_instance

        return entry

    def after_flush(self, entry, edit, attributes):
        """
        Launched after the BaseSaleProduct was added
        """
        # Si l'on ajoute un SaleProductWork on s'assure que les work_item ont
        # un sale_product associé
        if not edit and isinstance(entry, SaleProductWork) and "items" in attributes:
            # NB : pas sûr que l'on puisse passer ici via l'ui existante
            logger.debug("In the after flush method of RestSaleProductView")
            for index, item in enumerate(entry.items):
                # On récupère le label depuis les données reçues
                label = attributes["items"][index]["label"]

                if item.base_sale_product_id is None:
                    # create a base sale product if doesn't exists
                    new_sale_product = item.generate_sale_product(
                        label=label,
                        category_id=entry.category_id,
                        company_id=entry.company_id,
                    )
                    self.dbsession.add(new_sale_product)
                    self.dbsession.flush()
                    item.base_sale_product_id = new_sale_product.id
                    self.dbsession.merge(item)

        if edit:
            state = "update"
        else:
            state = "add"

        entry.on_before_commit(state, attributes)
        entry = self.dbsession.merge(entry)

        return entry

    def duplicate_view(self):
        duplicate = self.context.duplicate()
        self.dbsession.add(duplicate)
        self.dbsession.flush()
        return duplicate

    def catalog_get_view(self):
        type_ = self.request.params.get("type_")
        if type_ not in ("product", "work"):
            raise Exception("Wrong type_ option for catalog %s" % type_)

        if type_ == "work":
            query = SaleProductWork.query()
        else:
            query = BaseSaleProduct.query().filter(
                BaseSaleProduct.type_.in_(BaseSaleProduct.SIMPLE_TYPES)
            )

        query = query.filter_by(company_id=self.context.id)
        return query.all()

    def on_delete(self):
        self.context.on_before_commit("delete")


class RestWorkItemView(BaseRestView):
    """
    Json api for Work Items

    Collection views have a SaleProductWork context

    Context views have a BaseRestView context
    """

    def get_schema(self, submitted):
        if isinstance(self.context, SaleProductWork):
            # It's an add view
            add = True
        else:
            add = False
        return get_work_item_add_edit_schema(add=add)

    def collection_get(self):
        return self.context.items

    def post_load_from_catalog_view(self):
        """
        View handling load_from_catalog

        expects base_sale_product_quantities: {id1: quantity1, id2: quantity2} as json POST params
        """
        logger.debug("post_load_from_catalog_view")
        sale_products: dict = self.request.json_body.get("sale_products", {})
        logger.debug(f"sale_products {sale_products}")

        items = []
        for id_, quantity in sale_products.items():
            sale_product = BaseSaleProduct.get(id_)
            work_item = WorkItem.from_base_sale_product(sale_product)
            work_item.sale_product_work_id = self.context.id
            work_item.quantity = quantity
            self.dbsession.add(work_item)
            self.dbsession.flush()
            work_item.on_before_commit("add")
            items.append(work_item)

        return items

    def _manage_hybrid_properties(self, entry, attributes):
        """
        Manage the hybrid properties affectation that isn't managed by colander
        alchemy

        :param obj entry: The Current WorkItem instance
        :param dict attributes: The validated form values
        """
        for key, value in attributes.items():
            setattr(entry, key, value)

    def post_format(self, entry, edit, attributes):
        """
        Generate a base_sale_product if there isn't one yet
        """
        logger.debug("In the work item post format view")
        if not edit:
            entry.sale_product_work_id = self.context.id
            entry.sale_product_work = self.context

            if entry.base_sale_product_id is None:
                logger.debug("Creating a new base_sale_product")
                # create a base sale product if doesn't exists
                new_sale_product = entry.generate_sale_product(
                    category_id=self.context.category_id,
                    company=self.context.company,
                    **attributes,
                )
                self.dbsession.add(new_sale_product)
                self.dbsession.flush()
                new_sale_product.on_before_commit("add")
                entry.base_sale_product = new_sale_product
                entry.base_sale_product_id = new_sale_product.id

        return entry

    def after_flush(self, entry, edit, attributes):
        """
        Sync base_sale_product if needed
        """
        if edit:
            self._manage_hybrid_properties(entry, attributes)
            self.dbsession.merge(entry)
            if attributes.get("sync_catalog", False):
                base_sale_product = entry.sync_base_sale_product()
                self.dbsession.merge(base_sale_product)
                self.dbsession.flush()

        if edit:
            state = "update"
        else:
            state = "add"

        entry.on_before_commit(state, attributes)
        entry = self.dbsession.merge(entry)
        self.dbsession.flush()

        return entry

    def on_delete(self):
        self.context.on_before_commit("delete")


class RestStockOperationView(BaseRestView):
    """
    Json api for stock operations

    Collection views have a BaseSaleProduct context
    Context views have a BaseRestView context
    """

    def get_schema(self, submitted):
        return get_stock_operation_add_edit_schema()

    def pre_format(self, appstruct, edit):
        product_id = None
        if isinstance(self.context, BaseSaleProduct):
            if self.context.id is not None:
                product_id = self.context.id
        elif isinstance(self.context, SaleProductStockOperation):
            if self.context.base_sale_product.id is not None:
                product_id = self.context.base_sale_product.id
        appstruct["base_sale_product_id"] = product_id
        return appstruct

    def collection_get(self):
        return self.context.stock_operations


class RestCurrentStockView(BaseRestView):
    """
    Rest api for getting sale product's current stock
    """

    def get_current_stock(self):
        return self.context.get_current_stock()


class RestSaleProductCategoryView(BaseRestView):
    """
    Json api for SaleProductCategory
    """

    schema = get_sale_product_category_add_edit_schema()

    # Context is the company
    def collection_get(self):
        categories = SaleProductCategory.query()
        categories = categories.filter_by(company_id=self.context.id)
        return categories.all()

    def pre_format(self, appstruct, edit):
        """
        Force the company_id in the appstruct
        """
        logger.info("Preformatting the appstruct")
        if self.context.__name__ == "company":
            appstruct["company_id"] = self.context.id
        return appstruct


class RestSaleProductsExport(RestSaleProductView, BaseCsvView):
    """
    Product csv view
    """

    model = BaseSaleProduct

    @property
    def filename(self):
        return "catalogue.csv"

    def query(self):
        return BaseSaleProduct.query().filter_by(company_id=self.context.id)


def includeme(config):
    config.add_view(
        RestSaleProductView,
        attr="form_config",
        route_name=PRODUCT_API_ROUTE,
        request_param="form_config",
        renderer="json",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        RestSaleProductView,
        attr="catalog_get_view",
        route_name=CATALOG_API_ROUTE,
        renderer="json",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )

    config.add_rest_service(
        RestSaleProductCategoryView,
        CATEGORY_ITEM_API_ROUTE,
        collection_route_name=CATEGORY_API_ROUTE,
        collection_context=Company,
        context=SaleProductCategory,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_sale_product_category"],
        add_rights=PERMISSIONS["context.add_sale_product_category"],
        delete_rights=PERMISSIONS["context.delete_sale_product_category"],
    )

    config.add_rest_service(
        RestSaleProductView,
        PRODUCT_ITEM_API_ROUTE,
        collection_route_name=PRODUCT_API_ROUTE,
        collection_context=Company,
        context=BaseSaleProduct,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_sale_product"],
        add_rights=PERMISSIONS["context.add_sale_product"],
        delete_rights=PERMISSIONS["context.edit_sale_product"],
    )

    config.add_rest_service(
        RestWorkItemView,
        WORK_ITEMS_ITEM_API_ROUTE,
        collection_route_name=WORK_ITEMS_API_ROUTE,
        collection_context=SaleProductWork,
        context=WorkItem,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_sale_product"],
        add_rights=PERMISSIONS["context.edit_sale_product"],
        delete_rights=PERMISSIONS["context.edit_sale_product"],
    )
    config.add_view(
        RestWorkItemView,
        route_name=WORK_ITEMS_API_ROUTE,
        attr="post_load_from_catalog_view",
        request_method="POST",
        request_param="action=load_from_catalog",
        renderer="json",
        context=SaleProductWork,
        permission=PERMISSIONS["context.edit_sale_product"],
    )

    config.add_rest_service(
        RestStockOperationView,
        STOCK_OPERATIONS_ITEM_API_ROUTE,
        collection_route_name=STOCK_OPERATIONS_API_ROUTE,
        collection_context=BaseSaleProduct,
        context=SaleProductStockOperation,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_sale_product"],
        add_rights=PERMISSIONS["context.edit_sale_product"],
        delete_rights=PERMISSIONS["context.edit_sale_product"],
    )
    config.add_view(
        RestCurrentStockView,
        route_name=PRODUCT_ITEM_API_ROUTE,
        attr="get_current_stock",
        request_method="GET",
        request_param="action=get_current_stock",
        renderer="json",
        context=BaseSaleProduct,
        permission=PERMISSIONS["company.view"],
    )

    config.add_view(
        RestSaleProductView,
        attr="duplicate_view",
        route_name=PRODUCT_ITEM_API_ROUTE,
        request_param="action=duplicate",
        request_method="POST",
        renderer="json",
        context=BaseSaleProduct,
        permission=PERMISSIONS["context.edit_sale_product"],
    )

    config.add_view(
        RestSaleProductsExport,
        route_name=PRODUCT_API_ROUTE,
        request_param="action=export_csv",
        request_method="GET",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )
