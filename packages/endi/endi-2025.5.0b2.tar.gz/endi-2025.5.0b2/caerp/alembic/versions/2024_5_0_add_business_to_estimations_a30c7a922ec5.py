"""2024.5.0 Créé une affaire pour les devis qui n'en ont pas

Create Date: 2024-11-14 17:29:31.691120

"""

# revision identifiers, used by Alembic.

# Revision ID:
revision = "a30c7a922ec5"

# Revises (previous revision or revisions):
down_revision = "86b7c129d8a9"

from alembic import op
import sqlalchemy as sa
import logging

logger = logging.getLogger(__name__)


class Dummy:
    def __init__(self, **kwargs):
        for key, value in list(kwargs.items()):
            setattr(self, key, value)


def update_database_structure():
    pass


def migrate_datas():
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION
    from caerp.models.task import Task

    session = DBSESSION()
    request = Dummy(dbsession=session)
    query_count = session.execute(
        sa.select(sa.func.count(Task.id)).filter(Task.business_id == None)
    ).scalar_one()
    print(f"Updating business data for {query_count} tasks on ...")
    for task in session.execute(
        sa.select(Task).filter(Task.business_id == None)
    ).scalars():
        task._caerp_service._set_business_data(request, task)
        if task.status == "valid":
            task.business.populate_deadlines()

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
