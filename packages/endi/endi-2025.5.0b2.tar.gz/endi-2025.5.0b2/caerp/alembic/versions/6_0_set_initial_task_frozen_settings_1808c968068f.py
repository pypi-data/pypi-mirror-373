"""6.0 Set initial Task.frozen_settings

Revision ID: 1808c968068f
Revises: 2fa7840218f2
Create Date: 2020-11-08 14:50:51.688425

"""

# revision identifiers, used by Alembic.
revision = "1808c968068f"
down_revision = "2fa7840218f2"

from alembic import op
import sqlalchemy as sa
from zope.sqlalchemy import mark_changed


def update_database_structure():
    pass


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()

    # We freeze everything to same value
    # Logic is to preserve the historic documents named as before
    initial_json = '{"label_overrides": {"label_overrides": {"estimation": "Devis", "invoice": "Facture", "cancelinvoice": "Avoir", "signed_agreement": "Bon pour accord"}}}'

    op.execute(f"UPDATE task SET frozen_settings = '{initial_json}'")
    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
