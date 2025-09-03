"""2024.3.0 Ajout d'une option 'is_provision' aux modules de contribution

Create Date: 2024-06-05 17:35:07.852605

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "bc80db375bde"

# Revises (previous revision or revisions):
down_revision = "f5d6f4b6c984"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column(
        "custom_invoice_book_entry_module",
        sa.Column("is_provision", sa.Boolean(), nullable=False, default=False),
    )


def upgrade():
    update_database_structure()


def downgrade():
    op.drop_column("custom_invoice_book_entry_module", "is_provision")
