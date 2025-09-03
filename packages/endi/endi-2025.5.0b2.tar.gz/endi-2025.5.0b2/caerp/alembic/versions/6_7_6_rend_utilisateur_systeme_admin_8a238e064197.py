"""6.7.6 Rend l'utilisateur système admin si besoin

Revision ID: 8a238e064197
Revises: 8366109f74a3
Create Date: 2024-01-09 17:12:39.324881

"""

# revision identifiers, used by Alembic.
revision = "8a238e064197"
down_revision = "8366109f74a3"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()
    from caerp.models.user import Login

    user = Login.get(0)
    if user:
        if user.primary_group != "admin":
            user.groups.append("admin")
            session.merge(user)

        mark_changed(session)
        session.flush()


def upgrade():
    migrate_datas()


def downgrade():
    pass
