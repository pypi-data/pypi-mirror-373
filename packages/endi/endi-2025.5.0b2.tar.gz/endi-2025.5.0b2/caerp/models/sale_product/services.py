import logging
from caerp_base.models.base import DBSESSION

from caerp.compute.math_utils import compute_tva
from caerp.models.config import Config
from caerp.models.services.injectable_model_formatter import InjectableModelFormatter

logger = logging.getLogger(__name__)


class SaleProductService:

    # Override to build the taskline description from a template stored in config
    taskline_description_template_config_key = None

    @classmethod
    def get_taskline_description(cls, sale_product: "BaseSaleProduct") -> str:
        if cls.taskline_description_template_config_key:
            template = Config.get_value(
                cls.taskline_description_template_config_key, None
            )
        else:
            template = None

        if template:
            formatter = InjectableModelFormatter()
            rendered = formatter.format(template, sale_product)
            if sale_product.description:
                return f"<p>{sale_product.description}</p>{rendered}"
            else:
                return rendered
        else:
            return sale_product.description

    @classmethod
    def is_locked(cls, sale_product):
        from caerp.models.sale_product.work_item import WorkItem
        from caerp.models.price_study import PriceStudyWorkItem, PriceStudyProduct

        if (
            DBSESSION()
            .query(WorkItem.id)
            .filter_by(base_sale_product_id=sale_product.id)
            .count()
            > 0
        ):
            return True

        if (
            DBSESSION()
            .query(PriceStudyProduct.id)
            .filter_by(base_sale_product_id=sale_product.id)
            .count()
            > 0
        ):
            return True
        if (
            DBSESSION()
            .query(PriceStudyWorkItem.id)
            .filter_by(base_sale_product_id=sale_product.id)
            .count()
            > 0
        ):
            return True

        return False

    @classmethod
    def _ensure_tva(cls, product):
        """
        Ensure cohesion between tva and product configuration

        Necessary because we can edit one and not the other leading to undesired
        states
        """
        # We ensure tva/product integrity
        if product.tva_id is None:
            product.product_id = None
        elif product.product is not None and product.product.tva_id != product.tva_id:
            product.product_id = None

    @classmethod
    def _get_computer(cls, sale_product):
        from caerp.models.config import Config

        if sale_product.mode == "ht":
            from caerp.compute.sale_product.ht_mode import (
                SaleProductHtComputer as Computer,
            )
        elif sale_product.mode == "ttc":
            from caerp.compute.sale_product.ttc_mode import (
                SaleProductTtcComputer as Computer,
            )
        else:
            # mode = supplier_ht
            from caerp.compute.sale_product.supplier_ht_mode import (
                SaleProductSupplierHtComputer as Computer,
            )
        return Computer(sale_product, Config)

    @classmethod
    def get_ht(cls, sale_product):
        computer = cls._get_computer(sale_product)
        return computer.unit_ht()

    @classmethod
    def get_ttc(cls, sale_product):
        computer = cls._get_computer(sale_product)
        return computer.unit_ttc()

    @classmethod
    def sync_amounts(cls, sale_product):
        sale_product.ht = cls.get_ht(sale_product)
        sale_product.ttc = cls.get_ttc(sale_product)
        DBSESSION().merge(sale_product)

    @classmethod
    def on_before_commit(cls, sale_product, state, changes=None):
        """
        Launched when the product has been added/modified/deleted

        :param obj sale_product: The current product
        :param str state: add/update/delete
        :param dict changes: The attributes that were changed
        """
        need_sync = False
        if state == "update":
            if changes:
                for i in (
                    "supplier_ht",
                    "ht",
                    "margin_rate",
                    "ttc",
                    "mode",
                    "tva_id",
                ):
                    if i in changes:
                        need_sync = True
                        break
            else:
                need_sync = True

            if "tva_id" in changes:
                cls._ensure_tva(sale_product)

        elif state == "add":
            need_sync = True

        # We sync amounts
        if need_sync:
            cls.sync_amounts(sale_product)


class SaleProductWorkService(SaleProductService):
    @classmethod
    def flat_cost(cls, sale_product):
        """
        Compute the flat cost of a complex sale_product

        1/    Déboursé sec = Total matériaux + Total main d'oeuvre + Total
        matériel affecté
        """
        return sum([item.flat_cost() for item in sale_product.items])

    @classmethod
    def cost_price(cls, sale_product):
        """
        Compute the cost price of the given sale_product work suming the cost of
        its differect items

        Prix de revient = Déboursé sec * ( 1 + Coefficient frais généraux )
        """
        return sum([item.cost_price(unitary=False) for item in sale_product.items])

    @classmethod
    def intermediate_price(cls, sale_product):
        """
        Compute the intermediate price

        3/    Prix intermédiaire = Prix de revient / ( 1 - ( Coefficients marge
        + aléas + risques ) )
        """
        return sum(
            [item.intermediate_price(unitary=False) for item in sale_product.items]
        )

    @classmethod
    def get_ht(cls, sale_product, contribution=None):
        """
        Compute the unit HT amount for this sale_product
        """
        # Coût d'une unité de produit composé
        return sum(
            [item.total_ht for item in sale_product.items if item.total_ht is not None]
        )

    @classmethod
    def get_ttc(cls, sale_product):
        """
        Compute the TTC amount for the given sale_product
        """
        return sum([item.total_ttc(sale_product.tva) for item in sale_product.items])

    @classmethod
    def sync_amounts(cls, work, work_only=False):
        """
        :param work_only: Only sync work's amounts else also items'
        """
        if not work_only:
            for item in work.items:
                item.sync_amounts(work)
        work.ht = cls.get_ht(work)
        work.ttc = cls.get_ttc(work)
        DBSESSION().merge(work)

    @classmethod
    def on_before_commit(cls, work, state, changes=None):
        """
        On before commit we update the ht amount

        :param obj work: The current work
        :param str state: add/update/delete
        :param dict changes: The modified attributes
        """
        need_sync = False
        if state == "update":
            if changes:
                for key in ("items", "tva_id", "margin_rate"):
                    if key in changes:
                        need_sync = True
            else:
                need_sync = True

            if "tva_id" in changes:
                cls._ensure_tva(work)

        if need_sync:
            cls.sync_amounts(work, work_only=True)


class WorkItemService:
    @classmethod
    def _get_computer(cls, product):
        from caerp.models.config import Config

        if product.mode == "ht":
            from caerp.compute.sale_product import (
                SaleProductWorkItemHtComputer as Computer,
            )
        else:
            # mode = supplier_ht
            from caerp.compute.sale_product import (
                SaleProductWorkItemSupplierHtComputer as Computer,
            )
        return Computer(product, Config)

    @classmethod
    def flat_cost(cls, work_item, unitary=False):
        """
        Collect the flat cost for this work item

        :param bool unitary: Unitary cost ?

        :rtype: int
        """
        computer = cls._get_computer(work_item)
        if unitary:
            return computer.flat_cost()
        else:
            return computer.full_flat_cost()

    @classmethod
    def cost_price(cls, work_item, unitary=False):
        """
        Compute the cost price of the given sale_product work item
        Uses the company's general overhead

        :param bool unitary: Unitary cost ?
        :returns: The result in 10*5 format

        :rtype: int
        """
        computer = cls._get_computer(work_item)
        if unitary:
            return computer.cost_price()
        else:
            return computer.full_cost_price()

    @classmethod
    def intermediate_price(cls, work_item, unitary=False):
        """
        Compute the intermediate price of a work item

        3/    Prix intermédiaire = Prix de revient / ( 1 - ( Coefficients marge
        + aléas + risques ) )

        :param bool unitary: Unitary cost ?
        """
        computer = cls._get_computer(work_item)
        if unitary:
            return computer.intermediate_price()
        else:
            return computer.full_intermediate_price()

    @classmethod
    def price_with_contribution(cls, work_item, unitary=False, base_price=None):
        computer = cls._get_computer(work_item)
        if unitary:
            return computer.price_with_contribution(base_price)
        else:
            return computer.full_price_with_contribution(base_price)

    @classmethod
    def price_with_insurance(cls, work_item, unitary=False, base_price=None):
        computer = cls._get_computer(work_item)
        if unitary:
            return computer.price_with_insurance(base_price)
        else:
            return computer.full_price_with_insurance(base_price)

    @classmethod
    def unit_ht(cls, work_item):
        """
        Compute the ht value for the given work item
        """
        computer = cls._get_computer(work_item)
        return computer.unit_ht()

    @classmethod
    def compute_total_ht(cls, work_item):
        """
        Compute the total ht for the given work_item
        """
        ht = cls.unit_ht(work_item)
        quantity = work_item.quantity or 1
        return ht * quantity

    @classmethod
    def total_ttc(cls, work_item, tva=None):
        """
        Compute the total ttc for this Work item using the TVA passed in argument

        :param obj tva: Tva instance
        """
        if tva is None and work_item.sale_product_work:
            tva = work_item.sale_product_work.tva

        ht = cls.compute_total_ht(work_item)
        if tva and tva.value > 0:
            return ht + compute_tva(ht, tva.value)
        else:
            return ht

    @classmethod
    def sync_amounts(cls, work_item, work=None):
        """
        Sync the current work item amounts

        :param obj work_item: The current work_item
        :param obj work: Optionnal work which called this sync_amounts func
        """
        logger.debug("Updating WorkItem unit_ht")
        # Ici on set le _ht et pas ht, voir la classe WorkItem pour mieux
        # comprendre
        work_item._ht = work_item.unit_ht()
        logger.debug(f"Updating the work_item _ht {work_item._ht}")

        work_item.total_ht = work_item.compute_total_ht()
        logger.debug(f"Updating WorkItem.total_ht {work_item.total_ht}")

        DBSESSION().merge(work_item)

        if work is None and work_item.sale_product_work is not None:
            work_item.sale_product_work.sync_amounts(work_only=True)
            logger.debug("SaleProductWork ht : %s" % work_item.sale_product_work.ht)
            DBSESSION().merge(work_item.sale_product_work)

    @classmethod
    def on_before_commit(cls, work_item, state, changes=None):
        """
        Launched when the product has been flushed yet
        """
        if state == "delete":
            parent = work_item.sale_product_work
            if work_item in parent.items:
                parent.items.remove(work_item)
            parent.sync_amounts()
        else:
            # We sync amounts
            cls.sync_amounts(work_item)


class SaleProductTrainingService(SaleProductWorkService):
    taskline_description_template_config_key = (
        "sale_catalog_sale_product_training_taskline_template"
    )


class SaleProductVAEService(SaleProductWorkService):
    taskline_description_template_config_key = (
        "sale_catalog_sale_product_vae_taskline_template"
    )
