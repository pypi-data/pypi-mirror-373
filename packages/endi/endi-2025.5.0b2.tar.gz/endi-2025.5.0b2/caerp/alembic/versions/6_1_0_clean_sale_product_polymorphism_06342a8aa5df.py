"""6.1.0 clean sale_product polymorphism

Revision ID: 06342a8aa5df
Revises: 8316776402ee
Create Date: 2021-01-21 14:26:49.435214

"""

# revision identifiers, used by Alembic.
revision = "06342a8aa5df"
down_revision = "8316776402ee"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()
    from zope.sqlalchemy import mark_changed

    subtables = (
        "sale_product_work_force",
        "sale_product_service_delivery",
        "sale_product_product",
        "sale_product_material",
    )
    for table in subtables:
        query = """select id from base_sale_product as b where
        type_='{0}' and id not in (select id from {0})""".format(
            table
        )
        conn.execute(query)
        for item in conn.execute(query):
            insert_query = "insert into {} ( `id` ) values ({})".format(
                table, item["id"]
            )
            conn.execute(insert_query)

            for other_table in subtables:
                if other_table != table:
                    query = """select count(id) from {0}
                    where id ={1}""".format(
                        other_table, item["id"]
                    )

                    if conn.execute(query).rowcount > 0:
                        delete_query = "delete from {} where id={}".format(
                            other_table, item["id"]
                        )
                        conn.execute(delete_query)

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
