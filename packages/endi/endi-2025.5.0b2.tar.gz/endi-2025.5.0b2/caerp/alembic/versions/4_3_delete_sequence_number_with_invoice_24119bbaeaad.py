"""4.3 delete sequence number with invoice

Revision ID: 24119bbaeaad
Revises: 14d28a95ac46
Create Date: 2019-01-08 17:08:43.632121

"""

# revision identifiers, used by Alembic.
revision = "24119bbaeaad"
down_revision = "37cae75cb90"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.drop_constraint(
        "fk_task_sequence_number_task_id", "task_sequence_number", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_task_sequence_number_task_id"),
        "task_sequence_number",
        "task",
        ["task_id"],
        ["id"],
        ondelete="cascade",
    )


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_constraint(
        op.f("fk_task_sequence_number_task_id"),
        "task_sequence_number",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_task_sequence_number_task_id",
        "task_sequence_number",
        "task",
        ["task_id"],
        ["id"],
    )
