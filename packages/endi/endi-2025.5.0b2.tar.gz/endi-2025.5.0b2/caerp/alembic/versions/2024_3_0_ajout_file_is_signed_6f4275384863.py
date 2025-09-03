"""2024.3.0 Ajout de file.is_signed

Revision ID: 6f4275384863
Revises: 7c3bc9b26029
Create Date: 2024-04-19 12:08:13.342506

"""

# revision identifiers, used by Alembic.
revision = "6f4275384863"
down_revision = "12a5d42d5158"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    op.add_column("file", sa.Column("is_signed", sa.Boolean(), default=False))


def migrate_datas():
    pass


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("file", "is_signed")
