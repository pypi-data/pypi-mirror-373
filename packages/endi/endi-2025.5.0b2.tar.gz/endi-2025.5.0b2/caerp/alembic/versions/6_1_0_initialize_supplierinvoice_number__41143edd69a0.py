"""6.1.0 initialize supplierinvoice_number_template

Revision ID: 41143edd69a0
Revises: 6be1efa57217
Create Date: 2021-01-21 12:02:23.616579

"""

# revision identifiers, used by Alembic.
revision = "41143edd69a0"
down_revision = "6be1efa57217"

from alembic import op
import sqlalchemy as sa


def migrate_datas():
    from caerp_base.models.base import DBSESSION
    from caerp.models.config import Config

    session = DBSESSION()

    Config.query().filter_by(name="supplierinvoice_number_template").delete()

    default_format = Config(name="supplierinvoice_number_template", value="{SEQGLOBAL}")

    session.add(default_format)
    session.flush()


def upgrade():
    migrate_datas()


def downgrade():
    pass
