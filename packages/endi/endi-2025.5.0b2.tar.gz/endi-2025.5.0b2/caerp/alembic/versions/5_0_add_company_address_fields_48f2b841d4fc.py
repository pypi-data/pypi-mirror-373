"""5.0 Add Company address fields

Revision ID: 48f2b841d4fc
Revises: 226992705175
Create Date: 2019-03-27 23:18:14.873094

"""

# revision identifiers, used by Alembic.
revision = "48f2b841d4fc"
down_revision = "226992705175"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("company", sa.Column("address", sa.String(length=255), nullable=True))
    op.add_column("company", sa.Column("city", sa.String(length=255), nullable=True))
    op.add_column("company", sa.Column("country", sa.String(length=150), nullable=True))
    op.add_column("company", sa.Column("zip_code", sa.String(length=20), nullable=True))


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("company", "zip_code")
    op.drop_column("company", "country")
    op.drop_column("company", "city")
    op.drop_column("company", "address")
