"""2024.3.0 Supprime BaseQualiopiSaleProduct.free_1

Create Date: 2024-06-06 17:00:03.246699

"""
from caerp.alembic.utils import column_exists

# revision identifiers, used by Alembic.

# Revision ID:
revision = "00ceb1d68304"

# Revises (previous revision or revisions):
down_revision = "caf82c019a06"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    if column_exists("base_sale_product_qualiopi", "free_1"):
        # May or may not exist,
        # because automatic table creation is out of alembic revisions control.
        op.drop_column("base_sale_product_qualiopi", "free_1")


def upgrade():
    update_database_structure()


def downgrade():
    op.add_column(
        "base_sale_product_qualiopi", sa.Column("free_1", mysql.TEXT(), nullable=False)
    )
