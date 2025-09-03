"""6.4.0 Change File.Description to Text

Revision ID: c685fd419967
Revises: 2409eb7e97a4
Create Date: 2022-03-08 12:11:20.778056

"""

# revision identifiers, used by Alembic.
revision = "c685fd419967"
down_revision = "2409eb7e97a4"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.alter_column(
        "file",
        "description",
        existing_type=mysql.VARCHAR(length=100),
        type_=sa.Text(),
        existing_nullable=True,
    )


def upgrade():
    update_database_structure()


def downgrade():
    op.alter_column(
        "file",
        "description",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=100),
        existing_nullable=True,
    )
