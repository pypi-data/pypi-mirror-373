"""6.4.1 Ajout colonnes ProjectType.{ttc,ht}_compute_mode_allowed

Revision ID: 14fb928359ce
Revises: 6b661cafa4e2
Create Date: 2022-06-17 11:50:38.334462

"""

# revision identifiers, used by Alembic.
revision = "14fb928359ce"
down_revision = "6b661cafa4e2"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "project_type",
        sa.Column("ht_compute_mode_allowed", sa.Boolean(), nullable=False),
    )
    op.add_column(
        "project_type",
        sa.Column("ttc_compute_mode_allowed", sa.Boolean(), nullable=False),
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
    op.drop_column("project_type", "ttc_compute_mode_allowed")
    op.drop_column("project_type", "ht_compute_mode_allowed")
