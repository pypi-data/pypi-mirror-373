"""4.3 Transform task.status_date date → datetime(6)

Revision ID: 37cae75cb90
Revises: 14d28a95ac46
Create Date: 2018-12-19 19:43:30.886258

"""

# revision identifiers, used by Alembic.
revision = "37cae75cb90"
down_revision = "14d28a95ac46"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from zope.sqlalchemy import mark_changed


def update_database_structure():
    op.alter_column(
        "task",
        "status_date",
        existing_type=sa.DATE(),
        type_=mysql.DATETIME(fsp=6),
        existing_nullable=True,
    )


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()

    # Use a temporary table to store ordering index of tasks
    session.execute("DROP TABLE IF EXISTS ordered_task")
    session.execute(
        """
CREATE TEMPORARY TABLE `ordered_task` (
  `id` int(11) NOT NULL DEFAULT '0',
  `rowindex` MEDIUMINT NOT NULL AUTO_INCREMENT,
   UNIQUE KEY rowindex (rowindex)
)
"""
    )

    # Order tasks using both their status_date and sequence numbers.
    #
    # Note that as status_date as validation date is only reliable since
    # sept. 2017,
    #
    # Before that date, ordering via status_date may be wrong for some rows.
    session.execute(
        """
INSERT INTO ordered_task(id)
SELECT task.id
FROM task
LEFT JOIN task_sequence_number tsn_invoice_global
     ON (
        tsn_invoice_global.task_id = task.id
        AND
        tsn_invoice_global.sequence = 'invoice_year'
     )

LEFT JOIN task_sequence_number tsn_invoice_year
     ON (
        tsn_invoice_year.task_id = task.id
        AND
        tsn_invoice_year.sequence = 'invoice_year'
     )

LEFT JOIN task_sequence_number tsn_invoice_month
     ON (
       tsn_invoice_month.task_id = task.id
       AND
       tsn_invoice_month.sequence = 'invoice_month'
     )

LEFT JOIN task_sequence_number tsn_invoice_month_company
     ON (
       tsn_invoice_month_company.task_id = task.id
       AND
       tsn_invoice_month_company.sequence = 'invoice_month_company'
     )
ORDER BY
  status_date,
  tsn_invoice_global.index,
  tsn_invoice_year.index,
  tsn_invoice_month.index,
  tsn_invoice_month_company.index
"""
    )

    # Use the rowindex ordering index we built to fill the fractional part
    # (microseconds) of status_date DATETIME(6).
    # It allows chronological ordering of same-day tasks.
    #
    # NB: as this field was a DATE before this revision, same-day tasks
    # were not distinguishable on status_date.
    session.execute(
        """
UPDATE task
LEFT JOIN ordered_task
     ON ordered_task.id = task.id
SET task.status_date = ADDTIME(
  task.status_date,
  CONCAT('.',LPAD((ordered_task.rowindex), 6, '0'))
)
WHERE task.status_date IS NOT NULL;
    """
    )
    mark_changed(session)


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.alter_column(
        "task",
        "status_date",
        existing_type=mysql.DATETIME(fsp=6),
        type_=sa.DATE(),
        existing_nullable=True,
    )
