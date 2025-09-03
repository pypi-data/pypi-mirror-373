"""6.1.0 Set ProjectType booleans non-nullables

Revision ID: d11959327f54
Revises: a5c2c70e6942
Create Date: 2021-02-26 19:30:05.705906

"""

# revision identifiers, used by Alembic.
revision = "d11959327f54"
down_revision = "a5c2c70e6942"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()
    op.execute(
        "UPDATE project_type SET with_business = 0 " "WHERE with_business IS NULL"
    )

    op.execute(
        "UPDATE project_type SET include_price_study = 0 "
        "WHERE include_price_study IS NULL"
    )
    op.execute("UPDATE project_type SET `default` = 0 " "WHERE `default` IS NULL")

    mark_changed(session)
    session.flush()


def upgrade():
    migrate_datas()
    op.alter_column(
        "project_type",
        "with_business",
        existing_type=mysql.TINYINT(display_width=1),
        existing_nullable=True,
        nullable=False,
    )
    op.alter_column(
        "project_type",
        "include_price_study",
        existing_type=mysql.TINYINT(display_width=1),
        existing_nullable=True,
        nullable=False,
    )
    op.alter_column(
        "project_type",
        "default",
        existing_type=mysql.TINYINT(display_width=1),
        existing_nullable=True,
        nullable=False,
    )


def downgrade():
    op.alter_column(
        "project_type",
        "with_business",
        existing_type=mysql.TINYINT(display_width=1),
        existing_nullable=False,
        nullable=True,
    )
    op.alter_column(
        "project_type",
        "include_price_study",
        existing_type=mysql.TINYINT(display_width=1),
        existing_nullable=False,
        nullable=True,
    )
    op.alter_column(
        "project_type",
        "default",
        existing_type=mysql.TINYINT(display_width=1),
        existing_nullable=False,
        nullable=True,
    )
