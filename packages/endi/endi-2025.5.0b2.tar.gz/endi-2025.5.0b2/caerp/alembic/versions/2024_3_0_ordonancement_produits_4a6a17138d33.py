"""2024.3.0 ordonancement produits

Revision ID: 4a6a17138d33
Revises: 9cb9b960cd52
Create Date: 2024-05-14 18:34:41.806790

"""

# revision identifiers, used by Alembic.
revision = "4a6a17138d33"
down_revision = "9cb9b960cd52"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "product", sa.Column("order", sa.Integer(), nullable=False, default=0)
    )


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    conn.execute(
        """
        update product
        set product.order = product.id
        """
    )

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("product", "order")
