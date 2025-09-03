"""5.1 Add 'issuer' field on invoice payments

Revision ID: 69e690478b6c
Revises: 3024401478db
Create Date: 2019-09-26 15:40:36.901233

"""

# revision identifiers, used by Alembic.
revision = "69e690478b6c"
down_revision = "3024401478db"

from alembic import op
import sqlalchemy as sa
from caerp_base.models.base import DBSESSION
from zope.sqlalchemy import mark_changed
from alembic.context import get_bind


def update_database_structure():
    op.add_column("payment", sa.Column("issuer", sa.String(255)))


def migrate_datas():
    session = DBSESSION()
    conn = get_bind()
    payments = conn.execute(
        "SELECT payment.id, third_party.label \
        FROM payment, task, third_party WHERE payment.task_id=task.id \
        AND task.customer_id=third_party.id ORDER BY payment.id"
    )
    for p in payments:
        conn.execute(
            sa.text("UPDATE payment SET issuer=:issuer WHERE id=:id"),
            issuer=p.label,
            id=p.id,
        )
    mark_changed(session)


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("payment", "issuer")
