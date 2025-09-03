"""2024.5.0 Fix label role predefinis

Create Date: 2024-12-11 09:24:27.922723

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "1ee600382694"

# Revises (previous revision or revisions):
down_revision = "280eff27a43f"


def update_database_structure():
    pass


def migrate_datas():
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION
    from caerp.consts.users import PREDEFINED_GROUPS
    from caerp.models.user.group import Group

    session = DBSESSION()
    for group_def in PREDEFINED_GROUPS:
        if group_def["account_type"] == "equipe_appui":
            continue
        group = Group._find_one(group_def["name"])
        if group:
            group.label = group_def["label"]
            session.merge(group)
    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
