"""6.4.0 Ajout du montant HT sur les ExpenseKmLines

Revision ID: 7d2c6cb2724f
Revises: a9ac168053d4
Create Date: 2022-03-10 00:29:27.874662

"""

# revision identifiers, used by Alembic.
revision = "7d2c6cb2724f"
down_revision = "61d0d891d3c2"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.add_column("expensekm_line", sa.Column("ht", sa.Integer(), nullable=True))


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    UPD_QUERY = """
    UPDATE expensekm_line
    INNER JOIN ( 
        SELECT expensekm_line.id, CAST(km*amount as UNSIGNED) AS ht 
        FROM expensekm_line 
        JOIN baseexpense_line ON expensekm_line.id=baseexpense_line.id
        JOIN expensekm_type ON baseexpense_line.type_id=expensekm_type.id
    ) AS compute ON expensekm_line.id = compute.id
    SET expensekm_line.ht = compute.ht
    """
    conn.execute(UPD_QUERY)

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("expensekm_line", "ht")
