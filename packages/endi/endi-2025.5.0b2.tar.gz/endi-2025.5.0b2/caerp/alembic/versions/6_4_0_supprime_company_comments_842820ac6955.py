"""6.4.0 Supprime company.comments

Revision ID: 842820ac6955
Revises: a9ac168053d4
Create Date: 2022-03-03 14:51:39.182940

"""

# revision identifiers, used by Alembic.
revision = "842820ac6955"
down_revision = "a9ac168053d4"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.drop_column("company", "comments")


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
    op.add_column("company", sa.Column("comments", mysql.TEXT(), nullable=True))
