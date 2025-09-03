"""
    Regouping all models imports is necessary
    to allow the metadata.create_all function to work well
"""
# flake8: noqa: E401
from caerp_base.models.base import DBBASE, DBSESSION


from . import (
    activity,
    career_path,
    career_stage,
    commercial,
    company,
    competence,
    config,
    files,
    form_options,
    holiday,
    indicators,
    node,
    notification,
    options,
    payments,
    progress_invoicing,
    project,
    sepa,
    smtp,
    statistics,
    supply,
    task,
    third_party,
    tva,
    workshop,
)
from .accounting import (
    accounting_closures,
    balance_sheet_measures,
    bookeeping,
    general_ledger_account_wordings,
    income_statement_measures,
    operations,
    treasury_measures,
)
from .expense import payment, sheet, types

# Évite les conflits de chemin lors d'import depuis pshell
from .price_study import chapter, discount
from .price_study import price_study as p
from .price_study import product, work, work_item

# Évite les conflits de chemin lors d'import depuis pshell
from .sale_product import base, category
from .sale_product import sale_product as s
from .sale_product import training, work, work_item

# from .sale_product import price_study_work
from .training import bpf, trainer

# Évite les conflits de chemin lors d'import depuis pshell
from .user import group, login
from .user import user as u
from .user import userdatas

from caerp_celery import models

# Importe systématiquement les modèles des plugins
# Même si ils sont inutilisés
from caerp.plugins.sap.models import sap
from caerp.plugins.sap_urssaf3p import models


def adjust_for_engine(engine):
    """
    Ajust the models definitions to fit the current database engine
    :param obj engine: The current engine to be used
    """
    if engine.dialect.name == "mysql":
        # Mysql does case unsensitive comparison by default
        login.Login.__table__.c.login.type.collation = "utf8mb4_bin"
