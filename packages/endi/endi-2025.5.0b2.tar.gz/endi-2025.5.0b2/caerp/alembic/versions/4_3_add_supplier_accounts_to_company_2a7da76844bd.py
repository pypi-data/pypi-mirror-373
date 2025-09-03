"""4.3 Add supplier accounts to company

Revision ID: 2a7da76844bd
Revises: 434b21bf4934
Create Date: 2019-02-22 17:53:39.165100

"""

# revision identifiers, used by Alembic.
revision = "2a7da76844bd"
down_revision = "434b21bf4934"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    op.add_column(
        "company",
        sa.Column("general_supplier_account", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "company",
        sa.Column("third_party_supplier_account", sa.String(length=255), nullable=True),
    )


def migrate_datas():
    pass


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("company", "third_party_supplier_account")
    op.drop_column("company", "general_supplier_account")
