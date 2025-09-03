"""5.1 IncomeSource.invoice_id-cascade-delete

Revision ID: d824a2ca7973
Revises: 794070fe8c0c
Create Date: 2019-11-09 18:22:07.495348

"""

# revision identifiers, used by Alembic.
revision = "d824a2ca7973"
down_revision = "794070fe8c0c"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.drop_constraint(
        "fk_business_bpf_data_income_source_invoice_id",
        "business_bpf_data_income_source",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_business_bpf_data_income_source_invoice_id"),
        "business_bpf_data_income_source",
        "invoice",
        ["invoice_id"],
        ["id"],
        ondelete="CASCADE",
    )


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_constraint(
        op.f("fk_business_bpf_data_income_source_invoice_id"),
        "business_bpf_data_income_source",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_business_bpf_data_income_source_invoice_id",
        "business_bpf_data_income_source",
        "invoice",
        ["invoice_id"],
        ["id"],
    )
