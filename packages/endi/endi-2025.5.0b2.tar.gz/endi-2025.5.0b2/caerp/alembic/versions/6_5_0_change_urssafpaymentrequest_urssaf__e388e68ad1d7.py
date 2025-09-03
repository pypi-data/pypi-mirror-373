"""6.5.0 Change URSSAFPaymentRequest.urssaf_status_code to String

Revision ID: e388e68ad1d7
Revises: 94cab0a6d38c
Create Date: 2022-11-17 10:58:04.427585

"""

# revision identifiers, used by Alembic.
revision = "e388e68ad1d7"
down_revision = "94cab0a6d38c"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    op.alter_column(
        "urssaf_payment_request",
        "urssaf_status_code",
        existing_type=sa.Integer(),
        type_=sa.String(length=4),
        nullable=False,
        existing_nullable=True,
    )


def upgrade():
    update_database_structure()


def downgrade():
    op.alter_column(
        "urssaf_payment_request",
        "urssaf_status_code",
        type_=sa.Integer(),
        existing_type=sa.String(length=4),
        existing_nullable=False,
        nullable=True,
    )
