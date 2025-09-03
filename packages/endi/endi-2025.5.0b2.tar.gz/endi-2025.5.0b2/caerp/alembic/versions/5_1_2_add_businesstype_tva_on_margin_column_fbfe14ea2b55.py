"""5.1.2 Add BusinessType.tva_on_margin column

Revision ID: fbfe14ea2b55
Revises: 794070fe8c0c
Create Date: 2019-11-19 16:01:21.692782

"""

# revision identifiers, used by Alembic.
revision = "fbfe14ea2b55"
down_revision = "6de07846fbc8"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "business_type", sa.Column("tva_on_margin", sa.Boolean(), nullable=False)
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
    op.drop_column("business_type", "tva_on_margin")
