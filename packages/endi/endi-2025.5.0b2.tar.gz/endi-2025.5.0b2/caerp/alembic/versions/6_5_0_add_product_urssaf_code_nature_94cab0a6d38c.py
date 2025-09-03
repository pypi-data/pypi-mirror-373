"""6.5.0 Add Product.urssaf_code_nature

Revision ID: 94cab0a6d38c
Revises: 0d277ad21613
Create Date: 2022-11-01 21:32:15.823297

"""

# revision identifiers, used by Alembic.
revision = "94cab0a6d38c"
down_revision = "0d277ad21613"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "product", sa.Column("urssaf_code_nature", sa.String(length=10), nullable=False)
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
    op.drop_column("product", "urssaf_code_nature")
