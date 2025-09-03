"""6.0 Add start_date and validity_duration to tasks models

Revision ID: c521ac577082
Revises: 6fb9c80c6fe3
Create Date: 2019-12-03 11:24:16.491799

"""

# revision identifiers, used by Alembic.
revision = "c521ac577082"
down_revision = "0f7d98915d57"

from alembic import op
from alembic.context import get_bind
import sqlalchemy as sa
from caerp_base.models.base import DBSESSION
from zope.sqlalchemy import mark_changed


def update_database_structure():
    op.add_column("task", sa.Column("start_date", sa.Date()))
    op.add_column("estimation", sa.Column("validity_duration", sa.String(50)))


def migrate_datas():
    from caerp.models.task.task import stop_listening

    stop_listening()
    session = DBSESSION()
    conn = get_bind()
    from caerp.models.config import Config

    default_duration = Config.get_value(
        "estimation_validity_duration_default", "3 mois"
    )
    conn.execute(
        sa.text(
            """
          UPDATE estimation
          LEFT JOIN task ON estimation.id = task.id
          SET estimation.validity_duration=:default_duration
        """
        ),
        default_duration=default_duration,
    )
    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("task", "start_date")
    op.drop_column("estimation", "validity_duration")
