"""6.3.0 Migre la config receipts_group_by_remittance ➡ receipts_grouping_strategy

Revision ID: 48cbb45ca42d
Revises: a9bb2ebf988d
Create Date: 2021-10-15 14:40:52.888987

"""

# revision identifiers, used by Alembic.
revision = "48cbb45ca42d"
down_revision = "a9bb2ebf988d"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


OLD_CONFIG_KEY = "receipts_group_by_remittance"
NEW_CONFIG_KEY = "receipts_grouping_strategy"


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()

    from caerp.models.config import Config

    legacy_entry = Config.get(OLD_CONFIG_KEY)

    if legacy_entry:
        if legacy_entry.value == "1":
            new_setting_value = "remittance_id"
        else:
            new_setting_value = ""

        Config.set(NEW_CONFIG_KEY, new_setting_value)

        session.delete(legacy_entry)

        mark_changed(session)
        session.flush()


def unmigrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    from caerp.models.config import Config

    new_entry = Config.get(NEW_CONFIG_KEY)
    if new_entry and new_entry.value.startswith("remittance_id"):
        old_setting_value = "1"
    else:
        old_setting_value = "0"

    Config.set(OLD_CONFIG_KEY, old_setting_value)

    session.delete(new_entry)

    mark_changed(session)
    session.flush()


def upgrade():
    migrate_datas()


def downgrade():
    unmigrate_datas()
