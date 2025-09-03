import logging

from caerp.compute import math_utils
from caerp_base.models.base import DBSESSION


logger = logging.getLogger(__name__)


class PlanService:
    @classmethod
    def sync_with_task(cls, plan, task=None):
        if task is None:
            task = plan.task
        for chapter in plan.chapters:
            chapter.sync_with_task(task)
        task.cache_totals()


class ChapterService:
    @classmethod
    def sync_with_task(cls, chapter, task=None, sync_products=True):
        if chapter.task_line_group is None:
            from caerp.models.task import TaskLineGroup

            group = TaskLineGroup(
                description=chapter.status.source_task_line_group.description,
                title=chapter.status.source_task_line_group.title,
                order=chapter.status.source_task_line_group.order,
                task=task,
            )
            DBSESSION().add(group)
            chapter.task_line_group = group
            DBSESSION().merge(chapter)
        else:
            group = chapter.task_line_group

        if task:
            group.task_id = task.id

        DBSESSION().merge(group)
        DBSESSION().flush()
        if sync_products:
            for product in chapter.products:
                product.sync_with_task(group)
        return group


class BaseProductService:
    @classmethod
    def sync_with_task(cls, product, task_line_group=None) -> "TaskLine":
        logger.debug("BaseProductService.sync_with_task")
        if product.task_line is None:
            line = product.status.source_task_line.duplicate()
            line.group = task_line_group
            line.quantity = 1
            DBSESSION().add(line)
            DBSESSION().flush()
            product.task_line = line
            DBSESSION().merge(product)
        else:
            line = product.task_line

        line.cost = cls.total_ht(product)
        logger.debug(f"  + Setting line cost {line.cost}")
        DBSESSION().merge(line)
        DBSESSION().flush()
        return line

    @classmethod
    def total_ht(cls, product):
        percentage = product.percentage or 0
        already_invoiced_percentage = product.already_invoiced or 0
        percent_left = math_utils.round(100 - already_invoiced_percentage, 2)
        return product.status.get_cost(percentage, product, percent_left)

    @classmethod
    def on_before_commit(cls, request, product, state="update", attributes=None):
        if state == "update":
            plan = product.plan
            if plan:
                plan.sync_with_task()


class ProductService(BaseProductService):
    pass


class WorkService(BaseProductService):
    @classmethod
    def total_ht(cls, work):
        if work.status.locked:
            return super().total_ht(work)
        else:
            return sum(item.total_ht() for item in work.items)

    @classmethod
    def _set_locked(cls, work, value):
        work.locked = value
        work.status.locked = value
        DBSESSION().merge(work)
        DBSESSION().merge(work.status)
        DBSESSION().flush()

    @classmethod
    def unlock(cls, work):
        cls._set_locked(work, False)

    @classmethod
    def on_before_commit(cls, request, work, state="update", attributes=None):
        logger.debug(f"WorkService.on_before_commit : {state}")
        return super().on_before_commit(request, work, state, attributes)


class WorkItemService:
    @classmethod
    def total_ht(cls, work_item):
        percentage = work_item.percentage or 0
        already_invoiced_percentage = work_item.already_invoiced or 0
        percent_left = math_utils.round(100 - already_invoiced_percentage, 2)
        return work_item.status.get_cost(percentage, work_item, percent_left)

    @classmethod
    def total_tva(cls, work_item, ht=None):
        if ht is None:
            ht = cls.total_ht(work_item)
        from caerp.models.task import TaskLine

        computer = TaskLine(cost=ht, tva=work_item.work.task_line.tva, description="")
        return computer.tva_amount()

    @classmethod
    def total_ttc(cls, work_item, ht=None):
        if ht is None:
            ht = cls.total_ht(work_item)
        from caerp.models.task import TaskLine

        computer = TaskLine(cost=ht, tva=work_item.work.task_line.tva, description="")
        return computer.total()

    @classmethod
    def on_before_commit(cls, request, work_item, state="update", attributes=None):
        """
        on before commit

        - we update the work locked status
        - we update the Task
        """
        logger.debug(f"WorkItemService.on_before_commit : {state} {attributes}")
        if state == "update" and "_percentage" in attributes:
            work_item.work.unlock()
            work_item.plan.sync_with_task()
