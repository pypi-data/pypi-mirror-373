"""5.1 Add IBAN and BIC to Bank Accounts

Revision ID: 3024401478db
Revises: 783d20753ba0
Create Date: 2019-09-25 13:51:05.276144

"""

# revision identifiers, used by Alembic.
revision = "3024401478db"
down_revision = "783d20753ba0"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    op.add_column("bank_account", sa.Column("iban", sa.String(35), nullable=True))
    op.add_column("bank_account", sa.Column("bic", sa.String(15), nullable=True))


def migrate_datas():
    pass


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("bank_account", "iban")
    op.drop_column("bank_account", "bic")
