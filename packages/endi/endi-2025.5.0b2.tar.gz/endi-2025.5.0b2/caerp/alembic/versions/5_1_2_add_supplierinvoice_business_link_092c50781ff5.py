"""5.1.2 add SupplierInvoice business link

Revision ID: 092c50781ff5
Revises: 6de07846fbc8
Create Date: 2019-11-12 18:05:38.012536

"""

# revision identifiers, used by Alembic.
revision = "092c50781ff5"
down_revision = "fbfe14ea2b55"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "supplier_invoice_line", sa.Column("business_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "supplier_invoice_line", sa.Column("customer_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "supplier_invoice_line", sa.Column("project_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        op.f("fk_supplier_invoice_line_customer_id"),
        "supplier_invoice_line",
        "customer",
        ["customer_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_supplier_invoice_line_business_id"),
        "supplier_invoice_line",
        "business",
        ["business_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_supplier_invoice_line_project_id"),
        "supplier_invoice_line",
        "project",
        ["project_id"],
        ["id"],
        ondelete="SET NULL",
    )


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_constraint(
        op.f("fk_supplier_invoice_line_project_id"),
        "supplier_invoice_line",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_supplier_invoice_line_business_id"),
        "supplier_invoice_line",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_supplier_invoice_line_customer_id"),
        "supplier_invoice_line",
        type_="foreignkey",
    )
    op.drop_column("supplier_invoice_line", "project_id")
    op.drop_column("supplier_invoice_line", "customer_id")
    op.drop_column("supplier_invoice_line", "business_id")
