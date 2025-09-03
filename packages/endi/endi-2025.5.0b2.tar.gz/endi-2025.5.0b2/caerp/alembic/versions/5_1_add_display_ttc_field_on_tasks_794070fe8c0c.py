"""5.1 Add display_ttc field on tasks

Revision ID: 794070fe8c0c
Revises: b987d23091a0
Create Date: 2019-10-25 18:28:07.282085

"""

# revision identifiers, used by Alembic.
revision = "794070fe8c0c"
down_revision = "b987d23091a0"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    op.add_column("task", sa.Column("display_ttc", sa.Integer()))


def migrate_datas():
    op.execute("UPDATE task SET display_ttc=0")


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("task", "display_ttc")
