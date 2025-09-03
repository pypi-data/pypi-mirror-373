"""6.0 Add Task.frozen_settings

Revision ID: 2fa7840218f2
Revises: b4120ace97c3
Create Date: 2020-11-06 15:02:28.205293

"""

# revision identifiers, used by Alembic.
revision = "2fa7840218f2"
down_revision = "b4120ace97c3"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("task", sa.Column("frozen_settings", sa.JSON(), nullable=True))


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("task", "frozen_settings")
