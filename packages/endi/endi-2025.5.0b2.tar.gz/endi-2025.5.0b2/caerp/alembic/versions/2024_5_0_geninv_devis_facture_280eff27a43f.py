"""2024.5.0 Corrige le statut 'Factures générées' des devis

Create Date: 2024-12-06 14:25:44.222782

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "280eff27a43f"

# Revises (previous revision or revisions):
down_revision = "a30c7a922ec5"

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
        "update estimation set geninv=1 where id in (select distinct(estimation_id) from invoice) and geninv=0"
    )

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
