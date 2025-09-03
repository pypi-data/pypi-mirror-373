"""6.4.0 Renomme Task.status_person_id -> Task.status_user_id

Revision ID: cf3b3f9cfc11
Revises: 3db408759e73
Create Date: 2022-02-28 18:18:35.122766

"""

# revision identifiers, used by Alembic.
revision = "cf3b3f9cfc11"
down_revision = "3db408759e73"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from caerp.alembic.utils import (
    drop_foreign_key_if_exists,
    drop_index_if_exists,
)


def update_database_structure():
    # Recreate FK / index with right field name and constraint naming convention
    drop_foreign_key_if_exists("task", "fk_task_status_person_id")
    drop_index_if_exists("task", "fk_task_statusPerson_accounts")

    op.alter_column(
        "task",
        column_name="status_person_id",
        new_column_name="status_user_id",
        existing_type=mysql.INTEGER(display_width=11),
    )

    op.create_foreign_key(
        op.f("fk_task_status_user_id"),
        "task",
        "accounts",
        ["status_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("fk_task_status_user_id", "task", ["status_user_id"], unique=False)


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
    op.alter_column(
        "task",
        column_name="status_user_id",
        new_column_name="status_person_id",
        existing_type=mysql.INTEGER(display_width=11),
    )
