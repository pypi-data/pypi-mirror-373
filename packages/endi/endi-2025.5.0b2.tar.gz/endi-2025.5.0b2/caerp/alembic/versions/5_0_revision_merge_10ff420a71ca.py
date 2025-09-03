"""5.0 Revision merge

Revision ID: 10ff420a71ca
Revises: ('1242fa563c83', '414d467360af')
Create Date: 2019-05-06 10:20:34.228020

"""

# revision identifiers, used by Alembic.
revision = "10ff420a71ca"
down_revision = ("1242fa563c83", "414d467360af")

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
