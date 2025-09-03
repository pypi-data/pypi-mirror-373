"""2024.3.0 Supprime SaleProductTraining.price

Revision ID: 6a40660273fa
Revises: 381b37ecd573
Create Date: 2024-04-27 18:41:17.652150

"""

# revision identifiers, used by Alembic.
revision = "6a40660273fa"
down_revision = "381b37ecd573"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.drop_column("sale_product_training", "price")


def upgrade():
    update_database_structure()


def downgrade():
    op.add_column(
        "sale_product_training", sa.Column("price", mysql.TEXT(), nullable=False)
    )
