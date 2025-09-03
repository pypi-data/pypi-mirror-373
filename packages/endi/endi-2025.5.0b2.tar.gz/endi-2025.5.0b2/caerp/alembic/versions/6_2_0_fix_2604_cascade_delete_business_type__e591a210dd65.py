"""6.2.0 Fix #2604: cascade delete business_type label_override

Revision ID: e591a210dd65
Revises: c4b03f713cae
Create Date: 2021-05-04 15:39:49.446035

"""

# revision identifiers, used by Alembic.
revision = "e591a210dd65"
down_revision = "35a5b1ceaa31"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.drop_constraint(
        op.f("fk_label_override_business_type_id"), "label_override", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_label_override_business_type_id"),
        "label_override",
        "business_type",
        ["business_type_id"],
        ["id"],
        ondelete="CASCADE",
    )


def upgrade():
    update_database_structure()
