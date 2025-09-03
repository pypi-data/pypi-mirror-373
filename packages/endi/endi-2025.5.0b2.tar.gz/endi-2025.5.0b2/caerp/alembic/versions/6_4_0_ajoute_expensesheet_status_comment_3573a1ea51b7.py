"""6.4.0 Ajoute ExpenseSheet.status_comment

Revision ID: 3573a1ea51b7
Revises: 768321dd6773
Create Date: 2022-02-28 15:49:07.018821

"""

# revision identifiers, used by Alembic.
revision = "3573a1ea51b7"
down_revision = "768321dd6773"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "expense_sheet", sa.Column("status_comment", sa.Text(), nullable=True)
    )


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("expense_sheet", "status_comment")
