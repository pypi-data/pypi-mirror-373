"""6.1.0 initialize supplierinvoice_number_template

Revision ID: 35e9bfc2ae2c
Revises: 6373d1701a81
Create Date: 2021-01-20 17:55:06.103608

"""

# revision identifiers, used by Alembic.
revision = "35e9bfc2ae2c"
down_revision = "6373d1701a81"

from alembic import op
import sqlalchemy as sa


def migrate_datas():
    from caerp_base.models.base import DBSESSION
    from caerp.models.config import Config

    session = DBSESSION()

    Config.query().filter_by(name="supplierinvoice_number_template").delete()

    default_format = Config(name="supplierinvoice_number_template", value="{SEQGLOBAL}")


def upgrade():
    migrate_datas()


def downgrade():
    pass
