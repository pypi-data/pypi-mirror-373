""" 6.0 Migrate to Cerfa 10443*16

Because of the lack of early support of 10443*16 in enDi, some trainings from
2020 have mistakenly be filled with a 10443*15 form.

Let's try to migrate them to 10443*16

Revision ID: ae9a26b79ac0
Revises: 5000b3d46b77
Create Date: 2020-10-27 21:46:00.923865
"""

import logging

logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision = "ae9a26b79ac0"
down_revision = "5000b3d46b77"

import sqlalchemy as sa
from alembic import op


def update_database_structure():
    pass


def migrate_datas():
    from caerp.models.training.bpf import BusinessBPFData
    from caerp.models.services.bpf import BusinesssBPFDataMigrator_15to16

    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()

    query = BusinessBPFData.query().filter_by(
        financial_year=2020, cerfa_version="10443*15"
    )
    for bpf_data in query:
        logger.info(
            f"Migrating BusinessBPFData#{bpf_data.id} ({bpf_data.business.name})"
            "from Cerfa 10443*15 to 10443*16"
        )
        BusinesssBPFDataMigrator_15to16.migrate(bpf_data)


def upgrade():
    migrate_datas()


def downgrade():
    pass
