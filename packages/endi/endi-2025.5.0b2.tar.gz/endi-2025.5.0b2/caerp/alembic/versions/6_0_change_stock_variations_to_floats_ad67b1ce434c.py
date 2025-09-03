"""6.0 Change stock variations to floats

Revision ID: ad67b1ce434c
Revises: 000c62b7ac2a
Create Date: 2020-09-28 15:55:24.506095

"""

# revision identifiers, used by Alembic.
revision = "ad67b1ce434c"
down_revision = "000c62b7ac2a"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.alter_column(
        "sale_product_stock_operation",
        "stock_variation",
        existing_type=mysql.INTEGER(display_width=11),
        type_=sa.Float(precision=4),
        existing_nullable=True,
    )


def migrate_datas():
    pass


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.alter_column(
        "sale_product_stock_operation",
        "stock_variation",
        existing_type=sa.Float(precision=4),
        type_=mysql.INTEGER(display_width=11),
        existing_nullable=True,
    )
