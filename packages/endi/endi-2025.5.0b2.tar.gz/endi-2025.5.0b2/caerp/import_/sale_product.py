from typing import (
    Callable,
    Dict,
    Iterable,
    Optional,
    Tuple,
)

import colander
from sqlalchemy.exc import MultipleResultsFound

from caerp.export.sale_product import (
    CaerpSalesCatalogExportSchema,
    walk_and_replace,
)
from caerp.models.company import Company
from caerp.models.expense.types import ExpenseType
from caerp.models.sale_product import (
    BaseSaleProduct,
    SaleProductCategory,
    SaleProductWork,
)
from caerp.models.task import WorkUnit
from caerp.models.third_party import Supplier
from caerp.models.tva import (
    Product,
    Tva,
)
from caerp_base.models import DBBASE


class PendingInstancesCache:
    """
    Simple cache to store instances pending database insertion

    It allows ID querying of instances not yet inserted.
    Note tha the IDs used here are the remote IDs (those from the system that exported).
    Locally, those IDs are temporary cache-IDs, not DB IDs.
    """

    def __init__(self):
        self.categories: Dict[int, SaleProductCategory] = {}
        self.sale_products: Dict[int, BaseSaleProduct] = {}

    @staticmethod
    def _store(obj, id_: int, collection: Dict[int, DBBASE]):
        if obj.id is not None:
            raise ValueError(
                "This cache is intended for objects pending insertion into"
                f" db, but {obj} seems to already have an id."
            )
        else:
            collection[id_] = obj

    def get_category(self, id_: int) -> Optional[SaleProductCategory]:
        return self.categories.get(id_)

    def store_category(self, category: SaleProductCategory, id_: int):
        self._store(category, id_, self.categories)

    def get_sale_product(self, id_: int) -> Optional[BaseSaleProduct]:
        return self.sale_products.get(id_)

    def store_sale_product(self, sale_product: BaseSaleProduct, id_: int):
        self._store(sale_product, id_, self.sale_products)


class CatalogInstancesAdapter:
    """
    Transform a collection of appstruct in a TO-DO list of what we want to import

    Our input is a list of instances, and our output also.
    This class implement the import strategy to convert the remote object list
    to a local object list, ready to be added to a dbsession.

    What can be done here :
    - do not keep remote IDs that have no meaning locally
    - we enforce strategies on nested objects :
        - how to map them to local db objects
        - if they do not map to local objects, apply a policy :
          - create on the fly
          - NULL the field (and record a warning)
    """

    def __init__(self, company: Company):
        self.pending_cache = PendingInstancesCache()
        self.company = company
        self.warnings = set()  # avoid duplicates

        self._adapters = [
            (SaleProductWork, self._adapt_sale_product_work),
            (BaseSaleProduct, self._adapt_base_sale_product),
        ]

    def adapt(self, instance: DBBASE) -> DBBASE:
        """
         Adapts the instance before import in local dbsession

         The transformation includes local fields (id…) and nested objects (relationships / fk handling).

        This implementation may have been done in Schemas directly overloading objectify() and using colander.deferred

         :param instance: the instance to **mutate** as decoded from the export. It looks like an exact copy (including `id` field)
            of what is present on export serveur, and thus cannot be imported as-is.
        :return: the mutated instance (same object as argument)
        """
        adapter = self._get_adapter(instance)
        adapter(instance)
        return instance

    def record_warning(self, s: str):
        self.warnings.add(s)

    def _adapt_sale_product_work(self, instance: SaleProductWork):
        self._adapt_base_sale_product(instance)
        for work_item in instance.items:
            work_item.company = self.company
            if work_item._unity:
                work_item._unity = self._lookup_unit_or_none(work_item._unity)

            cached_sale_product = self.pending_cache.get_sale_product(
                work_item.base_sale_product_id
            )
            if not cached_sale_product:
                raise ValueError(
                    f"Cannot find any BaseSaleProduct in Import JSON matching remote ID ={work_item.base_sale_product_id}"
                )

            work_item.base_sale_product_id = None
            work_item.base_sale_product = cached_sale_product

    def _adapt_base_sale_product(self, instance: BaseSaleProduct):
        # Category can be created on the fly if missing
        if instance.category:
            local_category = SaleProductCategory.get_by_title(
                instance.category.title, self.company
            )

            if local_category:
                instance.category = local_category
            else:
                cached_category = self.pending_cache.get_category(instance.category.id)
                if cached_category is None:
                    # We do not know this Category yet -> store it in cache
                    remote_category_id = instance.category.id

                    instance.category.company_id = self.company.id
                    instance.category.id = None

                    self.pending_cache.store_category(
                        instance.category, remote_category_id
                    )
                else:
                    instance.category = cached_category

        # All other related obj are queried, and nulled in non existant locally
        if instance.unity:
            instance.unity = self._lookup_unit_or_none(instance.unity)

        instance.product = self._find_local_instance(
            instance.product,
            local_rel_query=lambda rel_obj: Product.query()
            .filter(
                Tva.value == rel_obj.tva.value,
                Product.compte_cg == rel_obj.compte_cg,
                Product.name == rel_obj.name,
            )
            .one_or_none(),
            warning_tmpl=(
                'Compte produit "{remote_rel_obj.name}" + ({remote_rel_obj.compte_cg}) '
                "+ TVA {remote_rel_obj.tva.value}"
            ),
        )

        instance.tva = self._find_local_instance(
            instance.tva,
            local_rel_query=lambda rel_obj: Tva.by_value(rel_obj.value, or_none=True),
            warning_tmpl="TVA {remote_rel_obj.value}",
        )
        instance.supplier = self._find_local_instance(
            instance.supplier,
            local_rel_query=lambda rel_obj: Supplier.get_by_label(
                rel_obj.label, self.company
            ),
            warning_tmpl="Fournisseur {remote_rel_obj.label}",
        )

        instance.purchase_type = self._find_local_instance(
            instance.purchase_type,
            local_rel_query=lambda rel_obj: ExpenseType.get_by_label(rel_obj.label),
            warning_tmpl="Type de dépense {remote_rel_obj.label}",
        )
        # Locally, this is a new instance -> DB will pick an ID
        remote_instance_id = instance.id
        instance.company = self.company
        instance.id = None

        self.pending_cache.store_sale_product(instance, remote_instance_id)

    def _get_adapter(self, instance: DBBASE) -> Callable[[DBBASE], DBBASE]:
        for klass, adapter in self._adapters:
            if isinstance(instance, klass):
                return adapter
        raise ValueError(
            f"This type is unknown to me ; I have no adapter for type f{type(instance)}."
        )

    def _find_local_instance(
        self,
        remote_rel_obj,
        local_rel_query: Callable,
        warning_tmpl: str,
    ) -> Optional[DBBASE]:
        """
        Look for (query) an existing local object that looks like the related object.

        If not found, a warning is recorded and None returned.
        """
        if remote_rel_obj:
            try:
                local_rel_obj = local_rel_query(remote_rel_obj)
                if local_rel_obj:
                    return local_rel_obj
                else:
                    self.record_warning(
                        "Impossible de trouver l'objet "
                        + warning_tmpl.format(remote_rel_obj=remote_rel_obj)
                        + " (champ mis à zéro)"
                    )
                    return None
            except MultipleResultsFound:
                self.record_warning(
                    "Plusieurs objects trouvés pour "
                    + warning_tmpl.format(remote_rel_obj=remote_rel_obj)
                    + " (champ mis à zéro)"
                )
                return None
        else:
            return None

    def _lookup_unit_or_none(self, unit_label: str) -> Optional[str]:
        out = self._find_local_instance(
            unit_label,
            lambda remote_obj: WorkUnit.get_by_label(remote_obj),
            'Unité "{remote_rel_obj}"',
        )
        if out:
            return out.label
        else:
            return None


def deserialize_catalog(
    company: Company, data: dict
) -> Tuple[Iterable[BaseSaleProduct], Iterable[str]]:
    """
    :param: dicts-and-lists nested structure, as JSON decoded it.
    :return: two iterables :
      - one with BaseSaleProduct (or descendants), ready to be added to a dbsession
      - one with strings representing warnings, they are already deduplicated
    """
    schema = CaerpSalesCatalogExportSchema()
    walk_and_replace(data, None, colander.null)

    # No extra care is given to deserialization errors, they are handled
    # by a validator at upload time

    deserialized = schema.deserialize(data)

    ret_instances = []

    # Order matters, base_sale_products must be first
    # (complex products may include items from the first list)
    data_keys = [
        "base_sale_products",
        "sale_products_works",
        "sale_products_trainings",
        "sale_products_vaes",
    ]

    adapter = CatalogInstancesAdapter(company=company)

    for data_key in data_keys:
        sub_schema = schema["data"][data_key].children[0]

        instances = (sub_schema.objectify(i) for i in deserialized["data"][data_key])
        for obj in instances:
            adapter.adapt(obj)
            ret_instances.append(obj)

    return ret_instances, list(adapter.warnings)
