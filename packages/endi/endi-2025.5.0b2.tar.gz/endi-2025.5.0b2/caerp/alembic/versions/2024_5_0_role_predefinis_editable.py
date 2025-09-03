"""2024.5.0 Rend les roles predefinis editable

Create Date: 2024-12-11 15:34:01.218930

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "820a37d9c692"

# Revises (previous revision or revisions):
down_revision = "1ee600382694"


def update_database_structure():
    pass


def migrate_datas():

    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION
    from caerp.models.user.group import Group

    session = DBSESSION()
    for group_name in ("trainer", "constructor"):
        group = Group._find_one(group_name)
        group.editable = True
        session.merge(group)

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
