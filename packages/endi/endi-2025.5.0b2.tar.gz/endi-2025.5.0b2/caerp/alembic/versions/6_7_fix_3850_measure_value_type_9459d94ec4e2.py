"""6.7.0 Fix 3850 measure value type

Revision ID: 9459d94ec4e2
Revises: 9ff2b756eb0b
Create Date: 2023-09-28 17:25:19.407468

"""

# revision identifiers, used by Alembic.
revision = "9459d94ec4e2"
down_revision = "9ff2b756eb0b"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.alter_column(
        "base_accounting_measure",
        "value",
        existing_type=mysql.FLOAT(),
        type_=sa.Numeric(precision=9, scale=2, asdecimal=False),
        existing_nullable=True,
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
    op.alter_column(
        "base_accounting_measure",
        "value",
        existing_type=sa.Numeric(precision=9, scale=2, asdecimal=False),
        type_=mysql.FLOAT(),
        existing_nullable=True,
    )
