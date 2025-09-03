"""6.4.0 Transforme ExpenseSheet.status_date en datetime

Revision ID: 783c9072821f
Revises: 5540d20e6ae0
Create Date: 2022-02-17 10:50:31.196967

"""

# revision identifiers, used by Alembic.
revision = "783c9072821f"
down_revision = "5540d20e6ae0"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.alter_column(
        "expense_sheet",
        "status_date",
        existing_type=sa.DATE(),
        type_=mysql.DATETIME(fsp=6),
        existing_nullable=True,
    )


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()
    op.execute(
        """
        UPDATE expense_sheet 
        JOIN (
            SELECT node_id, MAX(datetime) AS latest_datetime 
            FROM status_log_entry
            WHERE state_manager_key = 'status'
            GROUP BY node_id
        ) AS latest_status ON latest_status.node_id = expense_sheet.id
        SET status_date = latest_status.latest_datetime
        """
    )

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.alter_column(
        "expense_sheet",
        "status_date",
        existing_type=mysql.DATETIME(fsp=6),
        type_=sa.DATE(),
        existing_nullable=True,
    )
