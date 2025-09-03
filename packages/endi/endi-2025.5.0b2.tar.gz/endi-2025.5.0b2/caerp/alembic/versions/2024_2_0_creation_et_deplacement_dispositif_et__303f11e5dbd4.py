"""2024.2.0 Création et déplacement dispositif et administratif

Revision ID: 303f11e5dbd4
Revises: e032a4187413
Create Date: 2024-05-13 16:32:17.966040

"""

# revision identifiers, used by Alembic.
revision = "303f11e5dbd4"
down_revision = "e032a4187413"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from caerp.models.user.utils import get_active_custom_fields
from caerp.models.config import Config


def update_database_structure():
    op.alter_column(
        "user_datas_custom_fields",
        column_name="agri__dispositif_region",
        new_column_name="loca__dispositif_region",
        existing_type=sa.Boolean(),
    )
    # If agri__dispositif_region is active, we activate loca__dispositif_region
    for fields in get_active_custom_fields():
        if fields == "agri__dispositif_region":
            config = Config.get_value("userdatas_active_custom_fields", "[]")
            config = config.replace(
                "agri__dispositif_region", "loca__dispositif_region"
            )
            Config.set("userdatas_active_custom_fields", config)

    op.add_column(
        "user_datas_custom_fields",
        sa.Column("loca__debut_dispositif_region", sa.Date(), nullable=True),
    )
    op.add_column(
        "user_datas_custom_fields",
        sa.Column("loca__fin_dispositif_region", sa.Date(), nullable=True),
    )
    op.add_column(
        "user_datas_custom_fields",
        sa.Column("admin__num_carte_depot", sa.Text(), nullable=True),
    )
    op.add_column(
        "user_datas_custom_fields",
        sa.Column("admin__date_fin_carte_depot", sa.Date(), nullable=True),
    )


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("user_datas_custom_fields", "admin__date_fin_carte_depot")
    op.drop_column("user_datas_custom_fields", "admin__num_carte_depot")
    op.drop_column("user_datas_custom_fields", "loca__fin_dispositif_region")
    op.drop_column("user_datas_custom_fields", "loca__debut_dispositif_region")
    op.alter_column(
        "user_datas_custom_fields",
        column_name="loca__dispositif_region",
        new_column_name="agri__dispositif_region",
        existing_type=sa.Boolean(),
    )
