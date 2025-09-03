"""6.4.0 Migre ThirdParty.comments en StatusLogEntry

Revision ID: 7aa5d4ce2813
Revises: 299427a02576
Create Date: 2022-02-24 17:09:30.752544

"""

# revision identifiers, used by Alembic.
revision = "7aa5d4ce2813"
down_revision = "299427a02576"

from alembic import op
import sqlalchemy as sa


SQL_COPY_TO_STATUSLOGENTRY = """
INSERT INTO status_log_entry(
     node_id,
     state_manager_key,
     status,
     comment,
     datetime,
     user_id,
     label,
     visibility,
     pinned
 )
    SELECT
           third_party.id,
           '',
           '',
           third_party.comments,
           NOW(6),
           first_active_account_id,
           'Commentaires',
           'public',
           true
    FROM third_party
        JOIN company on third_party.company_id = company.id
        JOIN (
            SELECT MAX(login.user_id) first_active_account_id, company_id
            FROM login
                JOIN company_employee ON login.user_id = company_employee.account_id
            WHERE login.active
            GROUP BY company_id
        ) AS sample ON company.id = sample.company_id
    WHERE third_party.comments <> '' AND first_active_account_id;
"""


def update_database_structure():
    pass


def migrate_datas():
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    op.execute(SQL_COPY_TO_STATUSLOGENTRY)

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
