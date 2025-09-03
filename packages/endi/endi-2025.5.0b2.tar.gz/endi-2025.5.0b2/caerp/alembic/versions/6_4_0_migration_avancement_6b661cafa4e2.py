"""6.4.0 migration_avancement

Revision ID: 6b661cafa4e2
Revises: 61d0d891d3c2
Create Date: 2022-03-21 19:11:58.318303

"""

# revision identifiers, used by Alembic.
revision = "6b661cafa4e2"
down_revision = "7d2c6cb2724f"

from alembic import op
import sqlalchemy as sa


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    from caerp.models.progress_invoicing import (
        ProgressInvoicingChapterStatus,
        ProgressInvoicingProductStatus,
        ProgressInvoicingPlan,
        ProgressInvoicingChapter,
        ProgressInvoicingProduct,
    )

    session = DBSESSION()
    conn = get_bind()
    group_status_query = conn.execute(
        """
Select g.id, g.source_task_line_group_id, b.business_id
from progress_invoicing_group_status as g
join progress_invoicing_base_status as b on b.id=g.id
"""
    )
    group_status_to_chapter = {}
    line_status_to_product = {}
    for (
        id_,
        task_line_group_id,
        business_id,
    ) in group_status_query.fetchall():
        chapter = ProgressInvoicingChapterStatus(
            source_task_line_group_id=task_line_group_id,
            business_id=business_id,
        )
        session.add(chapter)
        session.flush()
        # On stocke la transition d'id
        group_status_to_chapter[id_] = chapter.id
        line_status_query = conn.execute(
            """
Select l.id, l.source_task_line_id, b.percent_to_invoice, b.percent_left
from progress_invoicing_line_status as l
join progress_invoicing_base_status as b on b.id=l.id
where l.group_status_id={}
""".format(
                id_
            )
        )
        for (
            id_,
            task_line_id,
            percent_to_invoice,
            percent_left,
        ) in line_status_query.fetchall():
            product = ProgressInvoicingProductStatus(
                chapter_status_id=chapter.id,
                source_task_line_id=task_line_id,
                percent_to_invoice=percent_to_invoice,
                percent_left=percent_left,
            )
            session.add(product)
            session.flush()
            line_status_to_product[id_] = product.id

    group_element_query = conn.execute(
        """
select g.id, g.task_line_group_id, b.base_status_id, b.created_at, b.updated_at, tl.task_id
from progress_invoicing_group as g
join progress_invoicing_base_element as b on b.id=g.id
left join task_line_group as tl on tl.id=g.task_line_group_id
    """
    )
    for (
        id_,
        task_line_group_id,
        base_status_id,
        created_at,
        updated_at,
        task_id,
    ) in group_element_query.fetchall():
        plan = ProgressInvoicingPlan.query().filter_by(task_id=task_id).first()
        if plan is None:
            business = conn.execute(
                f"""
select business_id from progress_invoicing_base_status where id={base_status_id}
"""
            ).first()
            plan = ProgressInvoicingPlan(task_id=task_id, business_id=business[0])
            session.add(plan)
            session.flush()
        chapter = ProgressInvoicingChapter(
            task_line_group_id=task_line_group_id,
            status_id=group_status_to_chapter[base_status_id],
            created_at=created_at,
            updated_at=updated_at,
            plan=plan,
        )
        session.add(chapter)
        session.flush()

        line_element_query = conn.execute(
            """
            select l.id, l.task_line_id, b.percentage, b.base_status_id, b.created_at, b.updated_at
            from progress_invoicing_line as l
            join progress_invoicing_base_element as b on l.id=b.id
            left join progress_invoicing_line_status as ls on
            ls.id=b.base_status_id
            where ls.group_status_id={}
            """.format(
                base_status_id
            )
        )
        for (
            id_,
            task_line_id,
            percentage,
            base_status_id,
            created_at,
            updated_at,
        ) in line_element_query.fetchall():
            product = ProgressInvoicingProduct(
                task_line_id=task_line_id,
                percentage=percentage,
                base_status_id=line_status_to_product[base_status_id],
                chapter_id=chapter.id,
                created_at=created_at,
                updated_at=updated_at,
            )
            already_invoiced = conn.execute(
                f"""
select sum(percentage) from progress_invoicing_base_element
where created_at < "{created_at}" and base_status_id={base_status_id}
"""
            ).scalar()
            if already_invoiced is None:
                already_invoiced = 0
            product.already_invoiced = already_invoiced
            session.add(product)
            session.flush()

    mark_changed(session)
    session.flush()


def upgrade():
    migrate_datas()


def downgrade():
    pass
