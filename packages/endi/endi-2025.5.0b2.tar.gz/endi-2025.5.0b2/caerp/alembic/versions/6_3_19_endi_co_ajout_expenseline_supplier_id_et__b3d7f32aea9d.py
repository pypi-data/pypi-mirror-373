"""6.3.19 Caerp co Ajout ExpenseLine.supplier_id et ExpenseLine.invoice_number

Revision ID: b3d7f32aea9d
Revises: 48cbb45ca42d
Create Date: 2021-11-12 16:07:37.918151

"""

# revision identifiers, used by Alembic.
revision = "b3d7f32aea9d"
down_revision = "48cbb45ca42d"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("expense_line", sa.Column("supplier_id", sa.Integer(), nullable=True))
    op.add_column(
        "expense_line",
        sa.Column("invoice_number", sa.String(length=255), nullable=False),
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
    op.drop_constraint(
        op.f("fk_expense_line_supplier_id"), "expense_line", type_="foreignkey"
    )
    op.drop_column("expense_line", "invoice_number")
    op.drop_column("expense_line", "supplier_id")
