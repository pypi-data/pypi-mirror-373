"""5.0 Add paid_status_* fields to ExpenseSheet

Revision ID: 15f720735537
Revises: eba300f6604a
Create Date: 2019-06-19 20:01:58.898267

"""

# revision identifiers, used by Alembic.
revision = "15f720735537"
down_revision = "eba300f6604a"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():

    op.add_column(
        "expense_sheet", sa.Column("paid_status_comment", sa.Text(), nullable=True)
    )
    op.add_column(
        "expense_sheet",
        sa.Column("paid_status_date", mysql.DATETIME(fsp=6), nullable=True),
    )
    op.add_column(
        "expense_sheet", sa.Column("paid_status_user_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        op.f("fk_expense_sheet_paid_status_user_id"),
        "expense_sheet",
        "accounts",
        ["paid_status_user_id"],
        ["id"],
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
        op.f("fk_expense_sheet_paid_status_user_id"),
        "expense_sheet",
        type_="foreignkey",
    )
    op.drop_column("expense_sheet", "paid_status_user_id")
    op.drop_column("expense_sheet", "paid_status_date")
    op.drop_column("expense_sheet", "paid_status_comment")
