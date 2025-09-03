"""5.0 Add Company.internal field

Revision ID: 1242fa563c83
Revises: 3fa5e47992bf
Create Date: 2019-04-09 10:46:50.379361

"""

# revision identifiers, used by Alembic.
revision = "1242fa563c83"
down_revision = "3fa5e47992bf"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("company", sa.Column("internal", sa.Boolean(), nullable=False))


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("company", "internal")
