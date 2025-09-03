"""6.1.0 Add expense_sheet.official_number

Revision ID: 60e32edeb921
Revises: 9d9ab48e488c
Create Date: 2021-01-19 22:13:53.717149

"""

# revision identifiers, used by Alembic.
revision = "60e32edeb921"
down_revision = "9d9ab48e488c"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "expense_sheet",
        sa.Column("official_number", sa.String(length=255), nullable=True),
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
    op.drop_column("expense_sheet", "official_number")
