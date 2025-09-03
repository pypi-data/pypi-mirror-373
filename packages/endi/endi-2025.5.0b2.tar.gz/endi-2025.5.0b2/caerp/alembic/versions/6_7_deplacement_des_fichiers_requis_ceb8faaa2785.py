"""6.7.0 Deplacement des fichiers requis

Revision ID: ceb8faaa2785
Revises: 790f171aa01f
Create Date: 2023-09-28 13:54:17.476978

"""

# revision identifiers, used by Alembic.
revision = "ceb8faaa2785"
down_revision = "790f171aa01f"

from alembic import op
import sqlalchemy as sa


def update_database_structure():
    pass


def duplicate_sale_file_requirement(requirement, business_id):
    from caerp.models.indicators import SaleFileRequirement

    result = SaleFileRequirement(
        validation_status=requirement.validation_status,
        forced=requirement.forced,
        file_type_id=requirement.file_type_id,
        doctype=requirement.doctype,
        requirement_type=requirement.requirement_type,
        validation=requirement.validation,
        file_id=requirement.file_id,
        node_id=business_id,
    )
    return result


def move_file(session, requirement, destination_node_id):
    if requirement.file_id is not None:
        if requirement.file_object.parent_id != destination_node_id:
            requirement.file_object.parent_id = destination_node_id
            session.merge(requirement.file_object)


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION
    from caerp.models.files import File
    from caerp.models.node import Node
    from caerp.models.indicators import SaleFileRequirement

    session = DBSESSION()
    conn = get_bind()
    query = SaleFileRequirement.query().join(
        Node, SaleFileRequirement.node_id == Node.id
    )
    business_requirements = query.filter(
        SaleFileRequirement.requirement_type == "business_mandatory"
    ).filter(
        Node.type_.in_(
            [
                "task",
                "invoice",
                "estimation",
                "internalestimation",
                "internalinvoice",
                "cancelinvoice",
            ]
        )
    )

    project_requirements = query.filter(
        SaleFileRequirement.requirement_type == "project_mandatory"
    ).filter(
        Node.type_.in_(
            [
                "task",
                "invoice",
                "estimation",
                "internalestimation",
                "internalinvoice",
                "cancelinvoice",
                "business",
            ]
        )
    )

    # On a un requirement par Task, on veut un seul requirement pour le Business
    # Donc on identifie ceux qu'on a déjà traité
    cache = {}
    for requirement in business_requirements:
        node = requirement.node
        if node.business_id:
            if node.business_id not in cache:
                new_requirement = duplicate_sale_file_requirement(
                    requirement, node.business_id
                )
                session.add(new_requirement)
                session.flush()
                move_file(session, requirement, node.business_id)
                cache[node.business_id] = new_requirement
            elif requirement.file_id and cache[node.business_id].file_id is None:
                cache[node.business_id].set_file(
                    requirement.file_id, validated=requirement.validated
                )
                session.merge(cache[node.business_id])
                session.flush()
            session.delete(requirement)

    for requirement in project_requirements:
        node = requirement.node
        if node.project_id not in cache:
            new_requirement = duplicate_sale_file_requirement(
                requirement, node.project_id
            )
            session.add(new_requirement)
            session.flush()
            move_file(session, requirement, node.project_id)
            cache[node.project_id] = new_requirement
        elif requirement.file_id and cache[node.project_id].file_id is None:
            cache[node.project_id].set_file(
                requirement.file_id, validated=requirement.validated
            )
            session.merge(cache[node.project_id])
            session.flush()
        session.delete(requirement)

    mark_changed(session)
    session.flush()


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    pass
