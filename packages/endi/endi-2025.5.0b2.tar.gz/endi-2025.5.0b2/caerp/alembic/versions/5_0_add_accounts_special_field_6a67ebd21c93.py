"""5.0 Add accounts.special field

Revision ID: 6a67ebd21c93
Revises: 10ff420a71ca
Create Date: 2019-06-03 17:15:42.542011

"""

# revision identifiers, used by Alembic.
revision = "6a67ebd21c93"
down_revision = "10ff420a71ca"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    op.add_column(
        "accounts", sa.Column("special", sa.Boolean(), nullable=False, default=False)
    )


def upgrade():
    update_database_structure()


def downgrade():
    op.drop_column("accounts", "special")
