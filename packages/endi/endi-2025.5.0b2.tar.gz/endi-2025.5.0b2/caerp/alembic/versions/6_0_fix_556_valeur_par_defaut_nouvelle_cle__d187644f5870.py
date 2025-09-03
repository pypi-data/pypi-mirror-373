"""6.0 Fix #556: Valeur par défaut nouvelle clé de config ungroup_expenses_ndf

Revision ID: d187644f5870
Revises: 6000812cf022
Create Date: 2020-11-02 11:34:25.204429

"""

# revision identifiers, used by Alembic.
revision = "d187644f5870"
down_revision = "6000812cf022"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def insert_new_config_key():
    op.execute(
        "INSERT INTO config (name, value) VALUES\
        ('ungroup_expenses_ndf', '0')\
        ON DUPLICATE KEY UPDATE name = 'ungroup_expenses_ndf';"
    )
    # The line above allows the upgrade not to crash if
    # config key already exists


def upgrade():
    insert_new_config_key()
