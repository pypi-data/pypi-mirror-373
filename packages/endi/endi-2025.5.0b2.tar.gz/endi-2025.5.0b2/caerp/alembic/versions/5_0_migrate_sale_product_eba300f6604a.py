"""5.0 clean sale product

Revision ID: eba300f6604a
Revises: 6a67ebd21c93
Create Date: 2019-06-06 09:54:19.625186

"""

# revision identifiers, used by Alembic.
revision = "eba300f6604a"
down_revision = "6a67ebd21c93"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from caerp.alembic.utils import enable_constraints, disable_constraints, column_exists


def set_company_id_on_product_groups():
    op.add_column(
        "sale_product_group", sa.Column("company_id", sa.Integer(), nullable=True)
    )
    op.execute(
        "update sale_product_group set company_id=(select company_id from sale_product_category where sale_product_category.id=sale_product_group.category_id);"
    )


def migrate_datas_before():
    from caerp_base.models.base import DBSESSION
    from zope.sqlalchemy import mark_changed

    session = DBSESSION()
    mark_changed(session)
    from alembic.context import get_bind

    conn = get_bind()

    group_helper = sa.Table(
        "sale_product_group",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("label", sa.String(255)),
        sa.Column("ref", sa.String(255)),
        sa.Column("title", sa.String(255)),
        sa.Column("description", sa.Text()),
        sa.Column("category_id", sa.Integer),
        sa.Column("type_", sa.String(255)),
        sa.Column("company_id", sa.Integer),
    )
    group_product_rel_helper = sa.Table(
        "product_product_group_rel",
        sa.MetaData(),
        sa.Column("sale_product_id", sa.Integer),
        sa.Column("sale_product_group_id", sa.Integer),
    )
    product_helper = sa.Table(
        "sale_product",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("label", sa.String(255)),
        sa.Column("ref", sa.String(255)),
        sa.Column("description", sa.Text()),
        sa.Column("tva", sa.Integer),
        sa.Column("value", sa.Float),
        sa.Column("unity", sa.String(100)),
        sa.Column("category_id", sa.Integer),
        sa.Column("product_id", sa.Integer),
        sa.Column("company_id", sa.Integer),
    )
    training_helper = sa.Table(
        "sale_training_group",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("goals", sa.String(255)),
        sa.Column("prerequisites", sa.String(255)),
        sa.Column("for_who", sa.String(255)),
        sa.Column("duration", sa.String(255)),
        sa.Column("content", sa.String(255)),
        sa.Column("teaching_method", sa.String(255)),
        sa.Column("logistics_means", sa.String(255)),
        sa.Column("more_stuff", sa.String(255)),
        sa.Column("evaluation", sa.String(255)),
        sa.Column("place", sa.String(255)),
        sa.Column("modality_one", sa.Boolean()),
        sa.Column("modality_two", sa.Boolean()),
        sa.Column("date", sa.String(255)),
        sa.Column("price", sa.String(255)),
        sa.Column("free_1", sa.String(255)),
        sa.Column("free_2", sa.String(255)),
        sa.Column("free_3", sa.String(255)),
    )

    from caerp.models.sale_product.sale_product import SaleProductServiceDelivery
    from caerp.models.sale_product.training import SaleProductTraining
    from caerp.models.sale_product.work import SaleProductWork
    from caerp.models.sale_product.work_item import (
        WorkItem,
    )
    from caerp.models.tva import Tva

    product_id_dict = {}

    for product in conn.execute(
        product_helper.select().where(product_helper.c.company_id != None)
    ):
        if product.tva:
            tva_id = session.query(Tva.id).filter_by(value=product.tva).scalar()
        else:
            tva_id = None

        new_product = SaleProductServiceDelivery(
            label=product.label,
            ref=product.ref,
            description=product.description,
            ht=product.value * 10**5,
            tva_id=tva_id,
            product_id=product.product_id,
            company_id=product.company_id,
            category_id=product.category_id,
        )
        session.add(new_product)
        session.flush()
        product_id_dict[product.id] = new_product

    group_id_dict = {}
    training_id_dict = {}
    for product in conn.execute(
        group_helper.select()
        .where(group_helper.c.type_ == "base")
        .where(group_helper.c.company_id != None)
    ):
        new_product = SaleProductWork(
            title=product.title,
            description=product.description,
            ref=product.ref,
            label=product.label,
            category_id=product.category_id,
            company_id=product.company_id,
        )
        session.add(new_product)
        session.flush()
        group_id_dict[product.id] = new_product

    for product in conn.execute(
        group_helper.select()
        .where(group_helper.c.type_ == "training")
        .where(group_helper.c.company_id != None)
    ):
        new_product = SaleProductTraining(
            title=product.title,
            description=product.description,
            ref=product.ref,
            label=product.label,
            category_id=product.category_id,
            company_id=product.company_id,
        )
        session.add(new_product)
        session.flush()
        group_id_dict[product.id] = new_product
        training_id_dict[product.id] = new_product

    for product in conn.execute(training_helper.select()):
        if product.id in training_id_dict:
            training = training_id_dict[product.id]

            for key in (
                "goals",
                "prerequisites",
                "for_who",
                "duration",
                "content",
                "teaching_method",
                "logistics_means",
                "more_stuff",
                "evaluation",
                "place",
                "modality_one",
                "modality_two",
                "date",
                "price",
                "free_1",
                "free_2",
                "free_3",
            ):
                value = getattr(product, key, None)
                if value is not None:
                    setattr(training, key, value)
            session.merge(training)
            session.flush()

    for rel in conn.execute(group_product_rel_helper.select()):
        group = group_id_dict.get(rel.sale_product_group_id)
        product = product_id_dict.get(rel.sale_product_id)

        if group is not None and product is not None:
            workitem = WorkItem.from_base_sale_product(product)

            workitem.sale_product_work_id = group.id
            session.add(workitem)
            session.flush()

    for product in SaleProductServiceDelivery.query():
        product.sync_amounts()

    for work_item in WorkItem.query():
        work_item.sync_amounts()


def update_database_structure():
    # ### commands auto generated by Alembic - please adjust! ###
    disable_constraints()
    op.drop_table("sale_product_group")
    op.drop_table("product_product_group_rel")
    op.drop_table("sale_product")
    op.drop_table("sale_training_group")
    op.drop_table("training_type_sale_training_group_rel")
    op.add_column(
        "company",
        sa.Column(
            "general_overhead",
            sa.Numeric(6, 5),
            nullable=True,
        ),
    )
    op.add_column(
        "company",
        sa.Column(
            "margin_rate",
            sa.Numeric(6, 5),
            nullable=True,
        ),
    )
    if column_exists("company", "old_active"):
        op.drop_column("company", "old_active")
    # ### end Alembic commands ###
    enable_constraints()


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    from alembic.context import get_bind

    conn = get_bind()
    conn.execute("update company set margin_rate=0")
    conn.execute("update company set general_overhead=0")


def upgrade():
    set_company_id_on_product_groups()
    migrate_datas_before()
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
