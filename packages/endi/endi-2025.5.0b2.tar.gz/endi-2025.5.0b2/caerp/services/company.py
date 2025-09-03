from sqlalchemy import select
from caerp.models.company import Company
from caerp.models.project import Project
from . import get_model_by_id


def find_company_id_from_model(request, model):
    """
    Retrieve the id of the company linked to the given model.
    """
    if isinstance(model, Company):
        return model.id

    elif hasattr(model, "company_id"):
        return model.company_id

    elif hasattr(model, "get_company_id"):
        return model.get_company_id()

    elif hasattr(model, "project_id"):

        return request.dbsession.execute(
            select(Project.company_id).filter(Project.id == model.project_id)
        ).scalar_one()
    else:
        return None


def get_company_by_id(request, company_id):
    return get_model_by_id(request, Company, company_id)
