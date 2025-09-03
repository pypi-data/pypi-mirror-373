"""2024.2.0 Ajout du compte client sur les TVA

Revision ID: e032a4187413
Revises: a389d617354b
Create Date: 2024-03-13 16:03:41.806729

"""

# revision identifiers, used by Alembic.
revision = "e032a4187413"
down_revision = "a389d617354b"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    op.add_column("tva", sa.Column("compte_client", sa.String(125), nullable=True))


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    conn.execute("UPDATE tva SET compte_client=''")

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("tva", "compte_client")
