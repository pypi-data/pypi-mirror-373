"""2024.5.0 Supprime les _acl des Task

Create Date: 2024-11-21 15:37:50.248443

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "86b7c129d8a9"

# Revises (previous revision or revisions):
down_revision = "2eb7be665f50"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()
    conn.execute(
        "update node set _acl=NULL where type_ in ('invoice', 'internalinvoice', 'estimation', 'internalestimation', 'cancelinvoice', 'internalcancelinvoice')"
    )
    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
