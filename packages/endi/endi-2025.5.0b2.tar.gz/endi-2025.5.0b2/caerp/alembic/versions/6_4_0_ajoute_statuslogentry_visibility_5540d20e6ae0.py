"""6.4.0 Ajoute StatusLogEntry.visibility

Revision ID: 5540d20e6ae0
Revises: 27e3d45bfea3
Create Date: 2022-02-09 15:38:50.359219

"""

# revision identifiers, used by Alembic.
revision = "5540d20e6ae0"
down_revision = "27e3d45bfea3"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "status_log_entry",
        sa.Column("visibility", sa.String(length=50), nullable=False),
    )


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    op.execute("UPDATE status_log_entry SET visibility = 'public'")

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("status_log_entry", "visibility")
