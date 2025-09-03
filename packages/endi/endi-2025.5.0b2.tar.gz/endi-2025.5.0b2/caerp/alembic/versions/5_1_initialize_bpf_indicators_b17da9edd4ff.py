"""5.1 Initialize BPF indicators

Revision ID: b17da9edd4ff
Revises: e4151c91ccfb
Create Date: 2019-09-10 16:41:44.459131

"""

# revision identifiers, used by Alembic.
revision = "b17da9edd4ff"
down_revision = "e4151c91ccfb"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()
    from caerp.models.project.business import Business
    from caerp.models.project.types import BusinessType
    from caerp.models.services.business_status import BusinessStatusService

    query = Business.query().join(BusinessType)
    query = query.filter(BusinessType.name == "training")

    for business in query:
        indicator = BusinessStatusService.update_bpf_indicator(business)
        session.add(indicator)


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
