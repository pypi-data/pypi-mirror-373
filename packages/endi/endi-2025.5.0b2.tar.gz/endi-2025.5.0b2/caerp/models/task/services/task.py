import datetime
import logging
import typing

from caerp_base.models.base import DBSESSION
from sqlalchemy import Integer, cast, or_
from sqlalchemy.orm import load_only
from sqlalchemy.sql.expression import func

from caerp.compute.math_utils import integer_to_amount
from caerp.models.sale_product import BaseSaleProduct
from caerp.models.tva import Product, Tva
from caerp.utils import strings

logger = logging.getLogger(__name__)


def find_internal_product_and_tva() -> (
    typing.Tuple[typing.Optional[int], typing.Optional[int]]
):
    """
    Retrieve default internal product id and tva value
    """
    internal_tva = Tva.get_internal()
    internal_product_id = None
    internal_tva_value = None
    if internal_tva:
        internal_tva_value = internal_tva.value
        internal_products = Product.get_internal()
        if len(internal_products) == 1:
            internal_product_id = internal_products[0].id
    return internal_tva_value, internal_product_id


class TaskService:
    models = None

    @classmethod
    def _new_instance(cls, request, customer, data):
        from caerp.models.project.types import BusinessType

        for key in ["company", "project", "business_type_id"]:
            # On s'assure que les infos nécessaires sont présentes
            assert key in data
        data["customer"] = customer
        data["business_type"] = BusinessType.get(data["business_type_id"])

        factory = cls.get_customer_task_factory(customer)
        logger.debug("  + Creating task of type {} for {}".format(factory, customer))
        instance = factory(**data)
        # On gère les données relatives à l'affaire
        cls._set_business_data(request, instance)
        # On gère les données relatives au type d'affaire
        # Initialise les indicateurs (fichiers requis, mentions)
        instance.initialize_business_type_data()

        request.dbsession.add(instance)
        request.dbsession.flush()

        if "decimal_to_display" not in data:
            instance.decimal_to_display = instance.company.decimal_to_display

        return instance

    @classmethod
    def create(cls, request, customer, data: dict, no_price_study: bool = False):
        instance = cls._new_instance(request, customer, data)
        if not no_price_study and instance.project.project_type.price_study_default():
            logger.debug("   + Adding Price study to {}".format(instance))
            instance.set_price_study(request)

        if "display_ttc" not in data:
            instance.set_display_ttc()
        if "display_units" not in data:
            instance.set_display_units()

        return instance

    @classmethod
    def _set_business_data(cls, request, instance):
        # Une facture a forcément une affaire associée
        if not instance.business and not instance.business_id:
            from caerp.models.project.business import Business

            instance.business = Business.create(
                instance.name, instance.project, instance.business_type
            )
            request.dbsession.merge(instance.business)

        instance.update_indicators()
        instance.business.populate_file_requirements()
        return instance.business

    @classmethod
    def get_customer_task_factory(cls, customer):
        """
        return the appropriate task factory for the given customer
        """
        from caerp.models.task import Task

        return Task

    @classmethod
    def _duplicate_lines(cls, request, original, created):
        created.line_groups = []
        for group in original.line_groups:
            created.line_groups.append(group.duplicate())

        for line in original.discounts:
            created.discounts.append(line.duplicate())
        return created

    @classmethod
    def duplicate(cls, request, original, user, **kw):
        """
        Base duplicate tool common for all invoice/estimation types
        """
        customer = kw["customer"]
        kw["company"] = original.company
        kw["user"] = user
        if "business_type_id" not in kw:
            business_types = kw["project"].get_all_business_types(request)
            if len(business_types) > 0:
                if original.business_type in business_types:
                    kw["business_type_id"] = original.business_type_id
                else:
                    kw["business_type_id"] = business_types[0].id

        for field in (
            "description",
            "mode",
            "display_units",
            "display_ttc",
            "expenses_ht",
            "workplace",
            "payment_conditions",
            "notes",
            "end_date",
            "insurance_id",
            "ttc",
            "ht",
            "tva",
        ):
            value = getattr(original, field)
            kw[field] = value
        kw["mentions"] = [mention for mention in original.mentions if mention.active]

        document = cls._new_instance(request, customer, kw)

        if kw["project"].project_type.include_price_study and original.price_study:
            # Si on a une étude de prix, les TaskLine et TaskLineGroup sont générés
            # depuis les éléments de l'étude
            #  Duplication de l'étude
            price_study = original.price_study.duplicate()
            price_study.task = document
            # On vide la nouvelle Task qui a un groupe par défaut
            cls._clean_task(request, document)
            # On synchronise les éléments de la nouvelle étude avec la Task
            price_study.sync_with_task(request)
        else:
            # On synchronise les différentes lignes (TaskLine/Discount/ ...)
            cls._duplicate_lines(request, original, document)
        document.cache_totals(request)
        return document

    @classmethod
    def post_duplicate(cls, request, original, created, user, **kw):
        """
        To be called by subclasses
        """
        # On assure qu'on utilise les tvas "internes" lorsque l'on duplique un
        # document 'externe' vers un client interne à la CAE
        if created.customer.is_internal() and not original.customer.is_internal():
            (
                internal_tva_value,
                internal_product_id,
            ) = find_internal_product_and_tva()
            for group in created.line_groups:
                for line in group.lines:
                    line.tva = internal_tva_value
                    line.product_id = internal_product_id

        return created

    @classmethod
    def cache_totals(cls, request, task_obj):
        logger.debug("TaskService.cache_totals()")

        task_obj.ht = task_obj.total_ht()
        logger.debug(
            f" + Setting TTC {task_obj.ttc} TVA : {task_obj.tva} HT : {task_obj.ht}"
        )
        task_obj.tva = task_obj.tva_amount()
        task_obj.ttc = task_obj.total()
        task_obj.updated_at = datetime.datetime.now()
        if request is None:
            dbsession = DBSESSION()
        else:
            dbsession = request.dbsession
        dbsession.merge(task_obj)

    @classmethod
    def json_totals(cls, request, task) -> dict:
        """
        Build a dict with the different computed values concerning this task

        :param obj request: The pyramid request
        :param obj task: Task instance
        """
        tvas = task.get_tvas()
        tvas = dict(
            (integer_to_amount(tva, 2), integer_to_amount(tva_amount, 5))
            for tva, tva_amount in tvas.items()
        )
        discount = task.discount_total_ht()
        result = {
            "ht": integer_to_amount(task.ht, 5),
            "ttc": integer_to_amount(task.ttc, 5),
            "discount_total_ht": integer_to_amount(discount, 5),
            "tvas": tvas,
        }
        ht_before_discount = task.groups_total_ht()
        result["ht_before_discounts"] = integer_to_amount(ht_before_discount, 5)
        if task.mode == "ttc":
            ttc_before_discount = task.groups_total_ttc()
            result["ttc_before_discounts"] = integer_to_amount(ttc_before_discount, 5)
        total_due = task.total_due()
        result["total_due"] = integer_to_amount(total_due, 5)

        if task.price_study:
            result["price_study"] = task.price_study.json_totals(request)

        return result

    @classmethod
    def get_tva_objects(cls, task_obj):
        """
        :param task_obj: The Task object we want to collect tvas for
        :returns: tva stored by amount
        :rtype: dict
        """
        tva_values = set()
        for group in task_obj.line_groups:
            for line in group.lines:
                tva_values.add(line.tva)

        # Cas des certificats énergie
        # (on peut avoir une remise à 0% de tva indépendamment des taux de tva
        # du document)
        for discount in task_obj.discounts:
            tva_values.add(discount.tva)

        tvas = Tva.query().filter(Tva.value.in_(list(tva_values))).all()
        return dict([(tva.value, tva) for tva in tvas])

    @classmethod
    def _query_invoices(cls, task_cls, *args, **kwargs):
        """
        Query invoices

        :param **args: List of fields passed to the Task.query method
        :param **kwargs: Other args

            doctypes

                Options to list all invoices, only internal ones or only
                "external" ones (real invoices)
        """
        from caerp.models.task import (
            CancelInvoice,
            InternalCancelInvoice,
            InternalInvoice,
            Invoice,
        )

        query = super(task_cls, task_cls).query(*args)

        doctypes = kwargs.get("doctypes", "all")
        if doctypes == "all":
            classes = [Invoice, CancelInvoice, InternalInvoice]
            types = [
                "invoice",
                "cancelinvoice",
                "internalinvoice",
                "internalcancelinvoice",
            ]
            query = query.with_polymorphic(classes)
            query = query.filter(task_cls.type_.in_(types))
        elif doctypes == "internal":
            classes = [InternalInvoice, InternalCancelInvoice]
            query = query.with_polymorphic(classes)
            types = ["internalinvoice", "internalcancelinvoice"]
            query = query.filter(task_cls.type_.in_(types))
        else:
            classes = [Invoice, CancelInvoice]
            types = ["invoice", "cancelinvoice"]
            query = query.with_polymorphic(classes)
            query = query.filter(task_cls.type_.in_(types))

        return query

    @classmethod
    def get_valid_invoices(cls, task_cls, *args, **kwargs):
        query = cls._query_invoices(task_cls, *args, **kwargs)
        query = query.filter(task_cls.status == "valid")
        return query

    @staticmethod
    def get_valid_estimations(cls, *args):
        from caerp.models.task import Estimation

        query = Estimation.query(*args)
        query = query.filter_by(status="valid")
        return query

    @classmethod
    def get_waiting_estimations(cls, *args):
        from caerp.models.task import Estimation

        query = Estimation.query(*args)
        query = query.filter(Estimation.status == "wait")
        query = query.order_by(Estimation.status_date)
        return query

    @classmethod
    def get_waiting_invoices(cls, task_cls, *args):
        query = cls._query_invoices(task_cls, *args)
        query = query.filter(task_cls.status == "wait")
        query = query.order_by(task_cls.type_).order_by(task_cls.status_date)
        return query

    @classmethod
    def get_task_class(cls):
        raise NotImplementedError("%s.get_task_class" % cls.__name__)

    @classmethod
    def _clean_task(cls, request, task):
        logger.debug("Cleaning the task")
        # On vide la task avant d'ajouter une étude de prix
        for group in task.line_groups:
            request.dbsession.delete(group)
        task.line_groups = []

        for discount in task.discounts:
            request.dbsession.delete(discount)
        task.discounts = []

        task.expenses_ht = 0
        request.dbsession.merge(task)
        request.dbsession.flush()

    @classmethod
    def set_price_study(cls, request, task):
        """
        Initialize a price study using the task's current datas
        """
        if task.price_study is None:
            from caerp.models.price_study import PriceStudy, PriceStudyChapter

            cls._clean_task(request, task)
            price_study = PriceStudy(
                general_overhead=task.company.general_overhead,
                task=task,
            )
            chapter = PriceStudyChapter()
            price_study.chapters.append(chapter)

            request.dbsession.add(price_study)
            request.dbsession.flush()
            price_study.sync_with_task(request)

        return task.price_study

    @classmethod
    def unset_price_study(cls, request, task):
        """
        Remove the price study and ensure the task has the appropriate line groups
        """
        request.dbsession.delete(task.price_study)
        if len(task.line_groups) == 0:
            task.add_default_task_line_group()
        task.cache_totals(request)
        request.dbsession.merge(task)

    @classmethod
    def set_progress_invoicing_plan(cls, request, task):
        """
        Initialize a price study using the task's current datas
        """
        task.invoicing_mode = task.PROGRESS_MODE
        request.dbsession.merge(task)
        if task.progress_invoicing_plan is None:
            from caerp.models.progress_invoicing import ProgressInvoicingPlan

            cls._clean_task(request, task)
            progress_invoicing_plan = ProgressInvoicingPlan(
                business=task.business,
                task=task,
            )
            request.dbsession.add(progress_invoicing_plan)
            request.dbsession.flush()
        return task.progress_invoicing_plan

    @classmethod
    def unset_progress_invoicing_plan(cls, request, task):
        """
        Remove the price study and ensure the task has the appropriate line groups
        """
        request.dbsession.delete(task.progress_invoicing_plan)
        if len(task.line_groups) == 0:
            task.add_default_task_line_group()
        task.cache_totals(request)
        request.dbsession.merge(task)

    @classmethod
    def find_task_status_date(
        cls, taskclass, official_number: str, year: typing.Optional[int] = None
    ):
        """
        Query the database to retrieve a task with the given number and year
        and returns its status_date

        :param str official_number: The official number
        :param int year: The financial year associated to the invoice
        :returns: The document's status_date
        :rtype: datetime.dateime
        """
        from caerp.models.task import CancelInvoice, Invoice

        query = (
            DBSESSION()
            .query(taskclass)
            .with_polymorphic([Invoice, CancelInvoice])
            .options(load_only("status_date"))
            .filter_by(official_number=official_number)
        )
        if year:
            query = query.filter(
                or_(
                    Invoice.financial_year == year,
                    CancelInvoice.financial_year == year,
                )
            )
        return query.one().status_date

    @classmethod
    def format_amount(cls, task, amount, trim=True, grouping=True, precision=2):
        """
        Return a formatted amount in the context of the current task

        if the amount is not supposed to be trimmed, we retrieve the Task's
        decimal_to_show and pass it to the format_amount function

        :param obj task: Instance of class <caerp.models.task.Task>
        :param int amount: The amount for format
        """
        display_precision = None
        if not trim:
            display_precision = task.decimal_to_display
        return strings.format_amount(
            amount,
            trim=trim,
            grouping=grouping,
            precision=precision,
            display_precision=display_precision,
        )

    @staticmethod
    def query_by_antenne_id(cls, antenne_id: int, query=None, payment=False):
        from caerp.models.company import Company
        from caerp.models.task import BaseTaskPayment, Task

        if query is None:
            query = cls.query()

        # -2 means situation_antenne_id = NULL
        if antenne_id == -2:
            antenne_id = None

        if payment:
            query = query.outerjoin(Task, cls.id == BaseTaskPayment.task_id)

        query = query.join(Company, cls.company_id == Company.id)
        query = query.filter(Company.antenne_id == antenne_id)

        return query

    @staticmethod
    def query_by_follower_id(cls, follower_id: int, query=None, payment=False):
        from caerp.models.company import Company
        from caerp.models.task import BaseTaskPayment, Task

        if query is None:
            query = cls.query()

        # -2 means situation_follower_id = NULL
        if follower_id == -2:
            follower_id = None

        if payment:
            query = query.outerjoin(Task, cls.id == BaseTaskPayment.task_id)

        query = query.join(Company, cls.company_id == Company.id)
        query = query.filter(Company.follower_id == follower_id)

        return query

    @staticmethod
    def query_by_validator_id(cls, validator_id: int, query=None):
        from caerp.models.status import StatusLogEntry

        if not query:
            query = cls.query()

        query = query.outerjoin(cls.statuses)
        query = query.filter(
            StatusLogEntry.status == "valid",
            StatusLogEntry.state_manager_key == "status",
        )
        query = query.filter(StatusLogEntry.user_id == validator_id)
        return query

    @staticmethod
    def total_income(cls, column_name="ht") -> int:
        column = getattr(cls, column_name)
        return cls.get_valid_invoices().with_entities(
            cast(
                func.ifnull(func.sum(column), 0),
                Integer,
            )
        )

    @staticmethod
    def total_estimated(cls, column_name="ht") -> int:
        """
        Renvoi le montant total (HT ou TTC) des devis validés de l'affaire
        à l'exception de ceux marqués comme étant "Annulés"
        """
        column = getattr(cls, column_name)
        return (
            cls.get_valid_estimations()
            .filter(cls.signed_status != "aborted")
            .with_entities(
                cast(
                    func.ifnull(func.sum(column), 0),
                    Integer,
                )
            )
        )

    @classmethod
    def get_rate(cls, task, rate_name: str) -> float:
        """
        Récupère un taux à appliquer en fonction du nom du module
        d'écriture comptable concerné

        :param obj task: Facture/Avoir
        :param str rate_name: Le nom du module d'écriture pour lequel on
        récupère le taux

        :rtype: float or None
        """
        from caerp.models.company import Company

        configured = getattr(task, rate_name, None)

        if configured:
            return configured.rate
        else:
            return Company.get_rate(task.company_id, rate_name, task.prefix)

    @classmethod
    def get_rate_level(cls, task, rate_name: str) -> str:
        """
        Récupère le niveau auquel le taux à appliquer est défini

        :param obj task: Facture/Avoir
        :param str rate_name: Le nom du module d'écriture pour lequel on
        récupère le taux

        :rtype: float or None
        """
        from caerp.models.company import Company

        configured = getattr(task, rate_name, None)

        if configured:
            return "document"
        else:
            return Company.get_rate_level(task.company_id, rate_name, task.prefix)

    @classmethod
    def on_before_commit(cls, request, task, action: str, changes: dict):
        """
        Run some actions before modifications applied to the Task are run
        """
        from caerp.models.config import Config

        logger.debug("On before commit Task {}".format(task))
        if action == "update":
            if (
                "insurance_id" in changes
                and task.has_price_study()
                and Config.get_value(
                    "price_study_uses_insurance", default=True, type_=bool
                )
            ):
                logger.debug("Insurance id changed Syncing EDP")
                task.price_study.sync_amounts(sync_down=True)
                task.price_study.sync_with_task(request)
        if action == "delete":
            task.business.on_task_delete(request, task)
        return task


class TaskLineGroupService:
    @classmethod
    def from_price_study_product(cls, group_class, product):
        from caerp.models.price_study.product import PriceStudyProduct
        from caerp.models.price_study.work import PriceStudyWork
        from caerp.models.task.task import TaskLine

        group = group_class()
        if isinstance(product, PriceStudyProduct):
            group.lines = [TaskLine.from_price_study_product(product)]
        elif isinstance(product, PriceStudyWork):
            group.title = product.title
            if product.display_details:
                group.description = product.description
                for item in product.items:
                    group.lines.append(TaskLine.from_price_study_work_item(item))
            else:
                # On crée une seule ligne directement depuis le ProductWork
                group.lines = [TaskLine.from_price_study_work(product)]

        return group

    @classmethod
    def from_sale_product_work(cls, group_class, product, document=None, quantity=1):
        from caerp.models.task.task import TaskLine

        group = group_class()
        group.title = product.title
        group.description = product.get_taskline_description()

        for item in product.items:
            group.lines.append(
                TaskLine.from_sale_product_work_item(
                    item,
                    document=document,
                    quantity=quantity,
                )
            )
        return group

    @classmethod
    def gen_cancelinvoice_group(cls, request, group):
        from caerp.models.task import TaskLineGroup

        result = TaskLineGroup(
            title=group.title,
            description=group.description,
            order=group.order,
            display_details=group.display_details,
        )
        request.dbsession.add(result)
        request.dbsession.flush()
        for line in group.lines:
            new_line = line.gen_cancelinvoice_line()
            result.lines.append(new_line)

        return result

    @classmethod
    def duplicate(cls, group):
        from caerp.models.task import TaskLineGroup

        group = TaskLineGroup(
            title=group.title,
            description=group.description,
            task_id=group.task_id,
            lines=[line.duplicate() for line in group.lines],
            order=group.order,
            display_details=group.display_details,
        )
        return group

    @classmethod
    def on_before_commit(cls, request, task_line_group, state, attributes=None):
        """
        Handle actions before commit

        :param obj request: Pyramid request
        :param obj task_line: A TaskLineGroup instance
        :param str state: A str (add/update/delete)
        :param dict attributes: The attributes that were recently modified
        (default None)
        """
        should_sync = False
        task = task_line_group.task

        if state == "delete":
            if task and task_line_group in task.line_groups:
                task.line_groups.remove(task_line_group)
            should_sync = True
        elif state == "add":
            should_sync = True

        if should_sync and task:
            task.cache_totals(request)
        return task_line_group


class TaskLineService:
    @classmethod
    def from_price_study_product(cls, line_class, product):
        from caerp.models.tva import Tva

        result = line_class()
        result.description = product.description
        result.cost = product.ht
        result.unity = product.unity
        result.quantity = product.quantity
        if product.tva:
            result.tva = product.tva.value
        else:
            result.tva = Tva.get_default().value
        result.product_id = product.product_id
        return result

    @classmethod
    def from_price_study_work(cls, line_class, product_work):
        from caerp.models.tva import Tva

        result = line_class()
        result.description = product_work.description
        result.cost = product_work.ht
        result.unity = product_work.unity
        result.quantity = product_work.quantity

        tva = product_work.tva
        if tva:
            result.tva = tva.value
        else:
            result.tva = Tva.get_default().value
        result.product_id = product_work.product_id
        return result

    @classmethod
    def from_price_study_work_item(cls, line_class, work_item):
        from caerp.models.tva import Tva

        result = line_class()
        result.description = work_item.description
        result.cost = work_item.ht
        result.unity = work_item.unity
        result.quantity = work_item.total_quantity
        return result

    @classmethod
    def from_sale_product_work_item(
        cls, line_class, work_item, document=None, quantity=1
    ):
        result = line_class()
        result.description = work_item.description

        if document:
            mode = document.mode
        else:
            mode = "ht"

        if mode == "ht":
            result.cost = work_item.ht
        else:
            result.cost = work_item.total_ttc()
        result.mode = mode
        result.unity = work_item.unity
        result.quantity = quantity * work_item.quantity
        cls._set_tva_and_product(result, work_item.sale_product_work, document)
        return result

    @classmethod
    def from_sale_product(
        cls, line_class, sale_product: BaseSaleProduct, document=None, quantity=1
    ):
        result = line_class()
        result.description = sale_product.get_taskline_description()
        if document:
            mode = document.mode
        else:
            mode = "ht"

        if mode == "ht":
            result.cost = sale_product.ht
        else:
            result.cost = sale_product.ttc

        result.mode = mode
        result.unity = sale_product.unity
        result.quantity = quantity

        cls._set_tva_and_product(result, sale_product, document)
        return result

    @classmethod
    def _set_internal_tva_and_product(cls, task_line):
        """
        Set the internal product or tva
        """
        (
            internal_tva_value,
            internal_product_id,
        ) = find_internal_product_and_tva()
        task_line.tva = internal_tva_value
        task_line.product_id = internal_product_id

    @classmethod
    def _set_tva_and_product(cls, task_line, sale_product_entry, document=None):
        if document and document.internal:
            cls._set_internal_tva_and_product(task_line)
        else:
            if sale_product_entry.tva:
                task_line.tva = sale_product_entry.tva.value
                task_line.product_id = sale_product_entry.product_id
            else:
                task_line.tva = Tva.get_default().value

            if task_line.tva and not task_line.product_id:
                task_line.product_id = Product.first_by_tva_value(task_line.tva)

    @classmethod
    def duplicate(cls, task_line):
        from caerp.models.task import TaskLine

        newone = TaskLine(
            order=task_line.order,
            mode=task_line.mode,
            cost=task_line.cost,
            tva=task_line.tva,
            description=task_line.description,
            quantity=task_line.quantity,
            unity=task_line.unity,
            product_id=task_line.product_id,
        )
        return newone

    @classmethod
    def gen_cancelinvoice_line(cls, task_line):
        result = cls.duplicate(task_line)
        result.cost = -1 * result.cost
        return result

    @classmethod
    def on_before_commit(cls, request, task_line, state, attributes=None):
        """
        Handle actions before commit

        :param obj request: Pyramid request
        :param obj task_line: A TaskLine instance
        :param str state: A str (add/update/delete)
        :param dict attributes: The attributes that were recently modified (default None)
        """
        should_sync = False
        task = None
        group = task_line.group
        if group:
            task = group.task

        if state == "add":
            should_sync = True
        elif state == "update":
            if attributes:
                for field in ("cost", "mode", "tva", "quantity"):
                    if field in attributes:
                        should_sync = True
            else:
                should_sync = True

        elif state == "delete":
            if group and task_line in group.lines:
                group.lines.remove(task_line)
            should_sync = True

        if should_sync and task:
            task.cache_totals(request)
        return task_line


class DiscountLineService:
    @classmethod
    def from_price_study_discount(cls, price_study_discount):
        from caerp.models.task import DiscountLine

        for tva, ht in list(price_study_discount.ht_by_tva().items()):
            result = DiscountLine()
            result.description = price_study_discount.description
            result.amount = ht
            result.tva = tva.value
            yield result

    @classmethod
    def on_before_commit(cls, request, discount, state, attributes=None):
        """
        Handle actions before commit

        :param obj request: Pyramid request
        :param obj discount: A Discount instance
        :param str state: A str (add/update/delete)
        :param dict attributes: The attributes that were recently modified
        (default None)
        """
        should_sync = False
        task = discount.task

        if state == "add":
            should_sync = True
        elif state == "update":
            if attributes:
                for field in ("amount", "tva"):
                    if field in attributes:
                        should_sync = True
            else:
                should_sync = True

        elif state == "delete":
            if task and discount in task.discounts:
                task.discounts.remove(discount)
            should_sync = True

        if should_sync and task:
            logger.debug("Syncing task totals")
            logger.debug(discount.total_ht())
            task.cache_totals(request)
        return discount


class PostTTCLineService:
    @classmethod
    def on_before_commit(cls, request, post_ttc_line, state, attributes=None):
        """
        Handle actions before commit

        :param obj request: Pyramid request
        :param obj post_ttc_line: A PostTTCLine instance
        :param str state: A str (add/update/delete)
        :param dict attributes: The attributes that were recently modified (default None)
        """
        task = post_ttc_line.task

        if state == "delete":
            if task and post_ttc_line in task.post_ttc_lines:
                task.post_ttc_lines.remove(post_ttc_line)

        return post_ttc_line


class InternalProcessService:
    """
    Manage the processing of internal documents insid'enDI
    """

    @classmethod
    def _generate_pdf(cls, document, request):
        from caerp.export.task_pdf import ensure_task_pdf_persisted

        ensure_task_pdf_persisted(document, request)

    @classmethod
    def _generate_supplier(cls, document, request):
        logger.info(f"  + Generating the supplier {document.customer.label}")
        company = document.company
        customer = document.customer
        if not customer.is_internal() or not customer.source_company:
            logger.error(
                "The customer is not internal or the company is not the right one"
            )
            raise Exception(
                "This document is not attached to an internal customer "
                "(or it has no source company)"
            )
        from caerp_base.models.base import DBSESSION

        from caerp.models.third_party.supplier import Supplier

        supplier = Supplier.from_company(company, customer.source_company)
        DBSESSION().merge(supplier)
        DBSESSION().flush()
        logger.info("  + Done")
        return supplier

    @classmethod
    def _generate_supplier_document(cls, document, request, supplier):
        raise NotImplementedError("InternalProcessService._generate_supplier_document")

    @classmethod
    def sync_with_customer(cls, document, request):
        """
        Synchronize the current internal document creating its counterpart in
        the customer's environment

        :param obj request: The PyramidRequest
        :param obj document: The caerp internal Task instance
        """
        # We need to enforce the status of the document before generating a PDF
        document.status = "valid"
        DBSESSION().merge(document)
        DBSESSION().flush()
        cls._generate_pdf(document, request)

        supplier = cls._generate_supplier(document, request)
        supplier_document = cls._generate_supplier_document(document, request, supplier)
        return supplier_document
