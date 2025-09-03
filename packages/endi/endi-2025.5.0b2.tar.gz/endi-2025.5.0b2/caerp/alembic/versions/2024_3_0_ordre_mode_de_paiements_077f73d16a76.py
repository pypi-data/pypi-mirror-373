"""2024.3.0 ordre mode de paiements

Revision ID: 077f73d16a76
Revises: 303f11e5dbd4
Create Date: 2024-05-16 17:15:13.596680

"""

# revision identifiers, used by Alembic.
revision = "077f73d16a76"
down_revision = "4a6a17138d33"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("paymentmode", sa.Column("order", sa.Integer(), nullable=False))


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
    op.drop_column("paymentmode", "order")
