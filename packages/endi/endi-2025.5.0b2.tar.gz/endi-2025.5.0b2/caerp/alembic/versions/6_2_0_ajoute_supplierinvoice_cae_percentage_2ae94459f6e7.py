"""6.2.0 Ajoute SupplierInvoice.cae_percentage

Revision ID: 2ae94459f6e7
Revises: c4b03f713cae
Create Date: 2021-05-11 12:33:51.357039

"""

# revision identifiers, used by Alembic.
revision = "2ae94459f6e7"
down_revision = "2d0297c64801"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "supplier_invoice", sa.Column("cae_percentage", sa.Integer(), nullable=True)
    )


def migrate_datas():
    """
    Sets the supplier_invoice.cae_percentage :

    - to the same percentage as linked orders (if any)
    - else to the default (100%)
    """
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    op.execute(
        """
        UPDATE supplier_invoice
        LEFT JOIN (
          SELECT max(cae_percentage) orders_cae_percentage, supplier_invoice_id
          FROM supplier_order
          GROUP BY supplier_invoice_id
        ) orders on supplier_invoice_id = supplier_invoice.id
        SET cae_percentage = IFNULL(orders_cae_percentage, 100)
        """
    )

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("supplier_invoice", "cae_percentage")
