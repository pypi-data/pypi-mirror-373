"""2024.3.1 Ajoute sequence_number.key et force l'unicité

Create Date: 2024-07-04 10:31:52.798468

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "e22f7bc4b1ca"

# Revises (previous revision or revisions):
down_revision = "6f4275384863"

import logging
from alembic import op
import sqlalchemy as sa


logger = logging.getLogger(__name__)


def update_database_structure():
    op.add_column(
        "sequence_number", sa.Column("key", sa.String(length=100), nullable=False)
    )


def update_database_constraints():
    op.create_unique_constraint(
        op.f("uq_sequence_number_sequence"),
        "sequence_number",
        ["sequence", "index", "key"],
    )


def populate_datas():
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION
    from caerp.models.sequence_number import SequenceNumber

    used_keys = []
    session = DBSESSION()
    sequences = set(session.execute(sa.select(SequenceNumber)).scalars().all())
    for seq in sequences:
        key = ""
        if "_month_company" in seq.sequence:
            key = "{}-{}-{}".format(
                seq.node.date.year,
                seq.node.date.month,
                seq.node.company.id,
            )
        elif "_month" in seq.sequence:
            key = "{}-{}".format(
                seq.node.date.year,
                seq.node.date.month,
            )
        elif "_year" in seq.sequence:
            key = seq.node.date.year

        while f"{seq.sequence}/{seq.index}/{key}" in used_keys:
            logger.warning(
                f"DUPLICATE CONSTRAINT KEY : {seq.sequence}/{seq.index}/{key}"
            )
            key = f"{key}+"

        logger.debug(
            f"Sequence '{seq.sequence}' for node {seq.node.id} (date {seq.node.date}, company {seq.node.company.id}) => key is '{key}'"
        )

        used_keys.append(f"{seq.sequence}/{seq.index}/{key}")
        seq.key = key
        session.merge(seq)

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    populate_datas()
    update_database_constraints()


def downgrade():
    op.drop_constraint(
        op.f("uq_sequence_number_sequence"), "sequence_number", type_="unique"
    )
    op.drop_column("sequence_number", "key")
