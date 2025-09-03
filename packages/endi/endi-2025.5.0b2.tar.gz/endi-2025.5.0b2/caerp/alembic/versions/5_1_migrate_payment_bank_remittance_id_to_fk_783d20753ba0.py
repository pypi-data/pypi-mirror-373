"""5.1 Migrate payment.bank_remittance_id to FK

Revision ID: 783d20753ba0
Revises: b17da9edd4ff
Create Date: 2019-09-19 15:28:16.783923

"""

# revision identifiers, used by Alembic.
revision = "783d20753ba0"
down_revision = "b17da9edd4ff"

import datetime
from alembic import op
import sqlalchemy as sa
from caerp_base.models.base import DBSESSION
from zope.sqlalchemy import mark_changed
from caerp.alembic.utils import (
    disable_constraints,
    enable_constraints,
)


def update_database_structure():
    op.create_foreign_key(
        op.f("fk_payment_bank_remittance"),
        "payment",
        "bank_remittance",
        ["bank_remittance_id"],
        ["id"],
    )


def migrate_datas():
    from caerp.models.task.payment import BankRemittance

    session = DBSESSION()
    conn = op.get_bind()
    disable_constraints()
    # On s'assure que le champ 'bank_remittance_id' soit nullable
    op.execute("ALTER TABLE payment MODIFY bank_remittance_id VARCHAR(255) NULL")
    # Suppression des donnees inutiles dans l'identifiant de remise (correspondant au montant)
    op.execute(
        "UPDATE payment SET bank_remittance_id=NULL WHERE bank_remittance_id LIKE '%.%' OR bank_remittance_id LIKE '%,%'"
    )
    # Modification des bank_remittance_id qui sont sur plusieurs modes ou banques
    payments = conn.execute(
        "SELECT bank_remittance_id, COUNT(*) AS nb FROM ( \
        SELECT DISTINCT bank_remittance_id, mode, bank_id FROM payment WHERE bank_remittance_id IS NOT NULL \
    ) as remittances GROUP BY bank_remittance_id  HAVING nb > 1"
    )
    for p in payments:
        i = 1
        payments2 = conn.execute(
            "SELECT id FROM payment WHERE bank_remittance_id='{}'".format(
                p.bank_remittance_id
            )
        )
        for p2 in payments2:
            op.execute(
                "UPDATE payment SET bank_remittance_id='{0} ({1})' WHERE id='{2}'".format(
                    p.bank_remittance_id,
                    i,
                    p2.id,
                )
            )
            i = i + 1
    mark_changed(session)
    session.flush()
    # Creation des remises en banque existantes
    payments = conn.execute(
        "SELECT DISTINCT bank_remittance_id, mode, bank_id FROM payment WHERE bank_remittance_id IS NOT NULL"
    )
    for p in payments:
        session.add(
            BankRemittance(
                id=p.bank_remittance_id,
                payment_mode=p.mode,
                bank_id=p.bank_id,
                remittance_date=datetime.date.today(),
                closed=1,
            )
        )
    mark_changed(session)
    session.flush()
    enable_constraints()


def upgrade():
    migrate_datas()
    update_database_structure()


def downgrade():
    try:
        op.drop_constraint(
            "fk_payment_bank_remittance_id", "payment", type_="foreignkey"
        )
    except:
        pass
