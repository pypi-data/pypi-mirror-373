"""2024.3.0 Nouvelle nomenclature de produits formation

Revision ID: 58c1c52190b3
Revises: 6a40660273fa
Create Date: 2024-04-29 18:27:56.860284

"""

# revision identifiers, used by Alembic.
revision = "58c1c52190b3"
down_revision = "6a40660273fa"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def update_database_structure():
    op.drop_table("training_type_sale_product_training_rel")
    op.drop_table("training_type_options")

    op.add_column(
        "sale_product_training",
        sa.Column("rncp_rs_code", sa.String(length=20), nullable=False),
    )
    op.add_column(
        "sale_product_training",
        sa.Column("certification_name", sa.String(length=100), nullable=False),
    )
    op.add_column(
        "sale_product_training",
        sa.Column("certificator_name", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "sale_product_training",
        sa.Column("certification_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "sale_product_training",
        sa.Column("gateways", sa.String(length=20), nullable=False),
    )

    op.drop_constraint(
        "fk_sale_product_training_id", "sale_product_training", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_sale_product_training_id"),
        "sale_product_training",
        "base_sale_product_qualiopi_knowledge",
        ["id"],
        ["id"],
        ondelete="cascade",
    )

    op.drop_column("sale_product_training", "goals")
    op.drop_column("sale_product_training", "free_3")
    op.drop_column("sale_product_training", "free_2")
    op.drop_column("sale_product_training", "duration")
    op.drop_column("sale_product_training", "date")
    op.drop_column("sale_product_training", "for_who")
    op.drop_column("sale_product_training", "evaluation")
    op.drop_column("sale_product_training", "teaching_method")
    op.drop_column("sale_product_training", "free_1")
    op.drop_column("sale_product_training", "content")
    op.drop_column("sale_product_training", "place")
    op.drop_column("sale_product_training", "more_stuff")
    op.drop_column("sale_product_training", "logistics_means")


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    op.execute(
        """
        INSERT INTO base_sale_product_qualiopi
        (
         id,
         teaching_method,
         content,
        
        
         access_delay,
         accessibility,
         group_size,
         results,
         trainer,
         presence_modality
         )
        SELECT
            id,
            teaching_method,
            content,
        
            '',
            '',
            '',
            '',
            '',
            ''
        
        
        FROM sale_product_training
    """
    )

    op.execute(
        """
        INSERT INTO base_sale_product_qualiopi_knowledge
        (
         id,
         goals,
         for_who,
         evaluation,
         place
         )
        SELECT
            id,
            goals,
            for_who,
            evaluation,
            place
        FROM sale_product_training"""
    )
    session = DBSESSION()
    conn = get_bind()

    mark_changed(session)
    session.flush()


def upgrade():
    migrate_datas()
    update_database_structure()


def downgrade():
    op.add_column(
        "sale_product_training",
        sa.Column("logistics_means", mysql.TEXT(), nullable=False),
    )
    op.add_column(
        "sale_product_training", sa.Column("more_stuff", mysql.TEXT(), nullable=False)
    )
    op.add_column(
        "sale_product_training", sa.Column("place", mysql.TEXT(), nullable=False)
    )
    op.add_column(
        "sale_product_training", sa.Column("content", mysql.TEXT(), nullable=False)
    )
    op.add_column(
        "sale_product_training", sa.Column("free_1", mysql.TEXT(), nullable=False)
    )
    op.add_column(
        "sale_product_training",
        sa.Column("teaching_method", mysql.TEXT(), nullable=False),
    )
    op.add_column(
        "sale_product_training", sa.Column("evaluation", mysql.TEXT(), nullable=False)
    )
    op.add_column(
        "sale_product_training", sa.Column("for_who", mysql.TEXT(), nullable=False)
    )
    op.add_column(
        "sale_product_training", sa.Column("date", mysql.TEXT(), nullable=False)
    )
    op.add_column(
        "sale_product_training", sa.Column("duration", mysql.TEXT(), nullable=False)
    )
    op.add_column(
        "sale_product_training", sa.Column("free_2", mysql.TEXT(), nullable=False)
    )
    op.add_column(
        "sale_product_training", sa.Column("free_3", mysql.TEXT(), nullable=False)
    )
    op.add_column(
        "sale_product_training", sa.Column("goals", mysql.TEXT(), nullable=False)
    )
    op.drop_constraint(
        op.f("fk_sale_product_training_id"), "sale_product_training", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_sale_product_training_id",
        "sale_product_training",
        "sale_product_work",
        ["id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_column("sale_product_training", "gateways")
    op.drop_column("sale_product_training", "certification_date")
    op.drop_column("sale_product_training", "certificator_name")
    op.drop_column("sale_product_training", "certification_name")
    op.drop_column("sale_product_training", "rncp_rs_code")

    op.create_table(
        "training_type_sale_product_training_rel",
        sa.Column(
            "training_type_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "sale_product_training_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["sale_product_training_id"],
            ["sale_product_training.id"],
            name="fk_training_type_rel_sale_product_training_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["training_type_id"],
            ["training_type_options.id"],
            name="fk_training_type_sale_product_training_rel_training_type_id",
            ondelete="CASCADE",
        ),
        mysql_collate="utf8mb4_unicode_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    op.create_table(
        "training_type_options",
        sa.Column(
            "id", mysql.INTEGER(display_width=11), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["id"], ["configurable_option.id"], name="fk_training_type_options_id"
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_unicode_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
