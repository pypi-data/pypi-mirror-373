"""6.4.0 Fait hériter Company de Node

Revision ID: 914fba36e9ce
Revises: 33de05381b82
Create Date: 2022-03-03 11:45:58.658977

"""

# revision identifiers, used by Alembic.
revision = "914fba36e9ce"
down_revision = "33de05381b82"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.create_foreign_key(op.f("fk_company_id"), "company", "node", ["id"], ["id"])
    op.drop_column("company", "name")
    op.drop_column("company", "created_at")
    op.drop_column("company", "updated_at")


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
    op.add_column("company", sa.Column("updated_at", sa.DATE(), nullable=False))
    op.add_column("company", sa.Column("created_at", sa.DATE(), nullable=True))
    op.add_column(
        "company", sa.Column("name", mysql.VARCHAR(length=150), nullable=False)
    )
    op.drop_constraint(op.f("fk_company_id"), "company", type_="foreignkey")
