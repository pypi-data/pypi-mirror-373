"""
Customer handling forms schemas and related widgets
"""

import functools
import logging

import colander
import deform
from caerp_base.consts import CIVILITE_OPTIONS as ORIG_CIVILITE_OPTIONS
from colanderalchemy import SQLAlchemySchemaNode
from sqlalchemy import asc, distinct, not_, select
from sqlalchemy.orm import contains_eager

from caerp import forms
from caerp.compute.math_utils import convert_to_int
from caerp.forms.company import company_choice_node
from caerp.forms.lists import BaseListsSchema
from caerp.forms.project import project_node_factory
from caerp.forms.third_party.base import (
    build_admin_third_party_options,
    build_third_party_values,
    customize_third_party_schema,
    third_party_after_bind,
)
from caerp.models.company import Company
from caerp.models.project import Project
from caerp.models.task import Task
from caerp.models.third_party.customer import Customer

logger = logging.getLogger(__name__)


# For customers we also want 'Mr et Mme'
CIVILITE_OPTIONS = ORIG_CIVILITE_OPTIONS + (
    ("M. et Mme", "Monsieur et Madame"),
    ("M. ou Mme", "Monsieur ou Madame"),
    ("M. et M.", "Monsieur et Monsieur"),
    ("M. ou M.", "Monsieur ou Monsieur"),
    ("Mme et Mme", "Madame et Madame"),
    ("Mme ou Mme", "Madame ou Madame"),
)


def get_company_customers_from_request(request):
    """
    Extract a customers list from the request object

    :param obj request: The pyramid request object
    :returns: A list of customers
    :rtype: list
    """
    exclude_internal = False
    if isinstance(request.context, Project):
        company_id = request.context.company.id
        if request.context.mode == "ttc":
            # Pas de client interne pour les projets TTC
            exclude_internal = True
    elif isinstance(request.context, Company):
        company_id = request.context.id
    else:
        return []

    customers = Customer.label_query()
    customers = customers.filter_by(company_id=company_id)
    customers = customers.filter_by(archived=False)
    if exclude_internal:
        customers = customers.filter(Customer.type != "internal")
    return customers.order_by(Customer.label).all()


def _get_customers_for_filters_from_request(
    request, is_global=False, with_invoice=False, with_estimation=False
):
    """
    Extract a customers list from the request object in order to build up a
    customer filter

    :param obj request: The Pyramid request object
    :param bool is_global: Do we request all CAE customers ?
    :param bool with_invoice: Only invoiced customers ?
    :param bool with_estimation: Only customers with estimations ?

    :returns: A SQLAlchemy query
    """
    context = request.context
    query = Customer.label_query()
    # Clients d'une enseigne
    if isinstance(context, Company):
        query = query.filter_by(company_id=context.id)
    # Clients d'une enseigne (mais depuis une fiche client)
    elif isinstance(context, Customer):
        query = query.filter_by(company_id=context.company.id)
    # Clients d'un dossier
    elif isinstance(context, Project):
        query = query.outerjoin(Customer.projects)
        query = query.filter(Customer.projects.any(Project.id == context.id))
    # Clients de la CAE
    elif is_global:
        query = query.join(Customer.company)
        query = query.options(contains_eager(Customer.company).load_only("name"))
    else:
        raise Exception(
            "Unsupported context {} (not Company nor Project)".format(context)
        )

    if with_invoice:
        query = query.filter(
            Customer.id.in_(
                request.dbsession.query(distinct(Task.customer_id)).filter(
                    Task.type_.in_(Task.invoice_types)
                )
            )
        )
    elif with_estimation:
        query = query.filter(
            Customer.id.in_(
                request.dbsession.query(distinct(Task.customer_id)).filter(
                    Task.type_.in_(Task.estimation_types)
                )
            )
        )
    query = query.order_by(asc(Customer.label))
    return query


def get_current_customer_id_from_request(request):
    """
    Return the current customer from the request object

    :param obj request: The current pyramid request object
    """
    result = None
    if "customer" in request.params:
        result = convert_to_int(request.params.get("customer"))
    return result


def get_deferred_customer_select(
    query_func=get_company_customers_from_request,
    item_builder=build_third_party_values,
    default_option=None,
    **widget_options,
):
    """
    Dynamically build a deferred customer select with (or without) a void
    default value

    :param function query_func: The query builder to get the customers (gets
    request as argument)
    :param function item_builder: a function user
    :param 2-uple default_option: A default option to insert in the select
    options

    :returns: A deferred customer Select2Widget
    """

    @colander.deferred
    def deferred_customer_select(node, kw):
        """
        Collecting customer select datas from the given request's context

        :param dict kw: Binding dict containing a request key
        :returns: A deform.widget.Select2Widget
        """
        request = kw["request"]
        customers = query_func(request)
        values = list(item_builder(customers))
        if default_option is not None:
            # Use of placeholder arg is mandatory with Select2 ; otherwise, the
            # clear button crashes. https://github.com/select2/select2/issues/5725
            # Cleaner fix would be to replace `default_option` 2-uple arg with
            # a `placeholder` str arg, as in JS code.
            widget_options["placeholder"] = default_option[1]
            values.insert(0, default_option)

        return deform.widget.Select2Widget(values=values, **widget_options)

    return deferred_customer_select


def get_deferred_default_customer(query_func):
    @colander.deferred
    def deferred_default_customer(node, kw):
        """
        Collect the default customer value from a request's context

        :param dict kw: Binding dict containing a request key
        :returns: The current customer or colander.null
        """
        request = kw["request"]
        customer_id = get_current_customer_id_from_request(request)
        result = colander.null
        if customer_id is not None:
            # On checke pour éviter de se faire avoir si le customer est passé
            # en paramètre
            customers = query_func(request)
            if customer_id in [c.id for c in customers]:
                result = customer_id
        return result

    return deferred_default_customer


def get_deferred_customer_select_validator(
    query_func=get_company_customers_from_request, multiple=False
):
    @colander.deferred
    def _deferred_customer_validator(node, kw):
        """
        Build a customer option validator based on the request's context

        :param dict kw: Binding dict containing a request key
        :returns: A colander validator
        """
        request = kw["request"]
        customers = query_func(request)

        if multiple:
            # Ici le type est Set, les valeurs sont des strings
            customer_ids = [str(customer.id) for customer in customers]
            result = colander.ContainsOnly(customer_ids)
        else:
            # En mode multiple on a un type Set, ici le type est Integer, la
            # value est déjà transformée en int
            customer_ids = [customer.id for customer in customers]
            result = colander.OneOf(customer_ids)

        return result

    return _deferred_customer_validator


def _base_customer_choice_node_factory(multiple=False, **kw):
    """
    Shortcut used to build a colander schema node

    all arguments are optionnal

    Allow following options :

        any key under kw

            colander.SchemaNode options :

                * title,
                * description,
                * default,
                * missing
                * ...

        widget_options

            deform.widget.Select2Widget options as a dict

        query_func

            A callable expecting the request parameter and returning
            the current customer that should be selected

    e.g:

        >>> get_company_customers_from_request(
            title="Client",
            query_func=get_customers_list,
            default=get_current_customer,
            widget_options={}
        )


    """
    title = kw.pop("title", "")
    query_func = kw.pop("query_func", get_company_customers_from_request)
    default = kw.pop("default", get_deferred_default_customer(query_func))
    widget_options = kw.pop("widget_options", {})

    # On ajoute une fonction pour cleaner les informations "incorrectes"
    # renvoyées par l'interface (chaine vide, doublon ...) dans le cas d'un
    # select multiple
    if multiple and "preparer" not in kw:
        kw["preparer"] = forms.uniq_entries_preparer

    return colander.SchemaNode(
        colander.Set() if multiple else colander.Integer(),
        title=title,
        default=default,
        widget=get_deferred_customer_select(query_func=query_func, **widget_options),
        validator=get_deferred_customer_select_validator(query_func, multiple),
        **kw,
    )


def _base_customer_filter_node_factory(
    is_global=False,
    widget_options=None,
    with_invoice=False,
    with_estimation=False,
    **kwargs,
):
    """
    return a customer selection node

        is_global

            is the associated view restricted to company's invoices
    """
    widget_options = widget_options or {}
    default_option = widget_options.pop("default_option", None)

    # On pré-remplie la fonction _get_customers_for_filters_from_request
    query_func = functools.partial(
        _get_customers_for_filters_from_request,
        is_global=is_global,
        with_invoice=with_invoice,
        with_estimation=with_estimation,
    )

    if is_global:
        deferred_customer_validator = None
        item_builder = build_admin_third_party_options
    else:
        deferred_customer_validator = get_deferred_customer_select_validator(query_func)
        item_builder = build_third_party_values

    return colander.SchemaNode(
        colander.Integer(),
        widget=get_deferred_customer_select(
            query_func=query_func,
            item_builder=item_builder,
            default_option=default_option,
        ),
        validator=deferred_customer_validator,
        **kwargs,
    )


# Customer choice node : utilisé dans les formulaires:
# Dossier
# Facturation (Task)
# Liste des clients :
# 1- Tous ceux de l'enseigne avec ceux du dossier courant en premier
# 2- Tous ceux de l'enseigne
customer_choice_node_factory = forms.mk_choice_node_factory(
    _base_customer_choice_node_factory,
    title="Choix du client",
    resource_name="un client",
)

# Customer filter node : utilisé dans les listview
# 1- Tous les clients
# 2- Tous les clients d'un dossier
# 3- Tous les clients d'une enseigne
customer_filter_node_factory = forms.mk_filter_node_factory(
    _base_customer_filter_node_factory,
    title="Client",
    empty_filter_msg="Tous",
)


def get_list_schema():
    """
    Return the schema for the customer search list
    """
    schema = BaseListsSchema().clone()
    schema["search"].title = "Entreprise ou contact principal"
    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="archived",
            label="Inclure les clients archivés",
            title="",
            default=False,
            missing=False,
        )
    )
    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="internal",
            label="Inclure les enseignes internes",
            title="",
            default=True,
            missing=True,
        )
    )
    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="individual",
            label="Inclure les particuliers",
            title="",
            default=True,
            missing=True,
        )
    )
    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="company",
            label="Inclure les personnes morales",
            title="",
            default=True,
            missing=True,
        )
    )
    return schema


def _customize_schema(schema):
    """
    Add common widgets configuration for the customer forms schema

    :param obj schema: The Customer form schema
    """
    schema = customize_third_party_schema(schema)
    # Override default civilite
    schema["civilite"].widget = forms.get_select(
        CIVILITE_OPTIONS,
    )
    schema["civilite"].validator = colander.OneOf([a[0] for a in CIVILITE_OPTIONS])
    return schema


def get_company_customer_schema():
    """
    return the schema for user add/edit regarding the current user's role
    """
    excludes = "name"
    schema = SQLAlchemySchemaNode(Customer, excludes=excludes)
    schema = _customize_schema(schema)
    schema["company_name"].missing = colander.required
    schema["registration"].description = (
        "SIRET, SIREN, RCS, RNA… "
        "<strong>Obligatoire pour pouvoir facturer ce client</strong>"
    )
    schema["registration"].missing = colander.required
    schema.after_bind = third_party_after_bind
    return schema


def get_individual_customer_schema() -> SQLAlchemySchemaNode:
    """
    Build an individual customer form schema

    :return: The schema
    """
    excludes = [
        "name",
        "company_name",
        "tva_intracomm",
        "function",
        "registration",
    ]

    schema = SQLAlchemySchemaNode(Customer, excludes=excludes)
    schema = _customize_schema(schema)
    schema["firstname"].title = "Prénom"
    schema["lastname"].title = "Nom"
    schema["lastname"].missing = colander.required
    schema.after_bind = third_party_after_bind
    return schema


def company_query_for_internal_customer(request):
    """
    Build a query to collect the company ids that we propose in the internal
    customer form

    excludes already used company ids and current's company id

    :returns: a Sqlalchemy Query
    """
    company = request.context

    # Collecte des enseignes dont on ne veut pas dans le formulaire
    company_ids = [company.id]
    company_id_query = select(Customer.source_company_id).where(
        Customer.company_id == company.id,
        Customer.source_company_id != None,  # noqa: E711
    )
    company_ids.extend(request.dbsession.execute(company_id_query).scalars().all())

    query = (
        select(Company.id, Company.name)
        .where(Company.active == True, not_(Company.id.in_(company_ids)))
        .order_by(asc(Company.name))
    )
    return request.dbsession.execute(query)


@colander.deferred
def default_current_context_id(node, kw):
    """
    Return the default current context id as company_id
    """
    return kw["request"].context.id


def company_employees_validator(node, company_id):
    company = Company.get(company_id)
    if not company:
        raise colander.Invalid(node, "Enseigne introuvable")
    if len(company.get_active_employees()) == 0:
        raise colander.Invalid(node, "Cette enseigne n'est associée à aucun compte")


def get_internal_customer_addschema():
    """
    Build a schema to add an internal customer
    """
    schema = colander.Schema()
    schema.add(
        colander.SchemaNode(
            name="type",
            typ=colander.String(),
            default="internal",
            missing=colander.required,
        )
    )
    schema.add(
        company_choice_node(
            name="source_company_id",
            title="Enseigne",
            widget_options={"query": company_query_for_internal_customer},
            validator=company_employees_validator,
        )
    )
    schema.add(
        colander.SchemaNode(
            name="company_id",
            typ=colander.Integer(),
            widget=deform.widget.HiddenWidget(),
            missing=default_current_context_id,
        )
    )

    def create_customer_from_company_id(appstruct, model=None):
        if model is None:
            company_id = appstruct.pop("source_company_id")
            owner_company_id = appstruct.pop("company_id")
            if company_id == owner_company_id:
                raise colander.Invalid("Erreur : on ne peut se facturer à soi-même")
            company = Company.get(company_id)
            owner_company = Company.get(owner_company_id)
            model = Customer.from_company(company, owner_company)
        else:
            appstruct.pop("company_id", None)
        forms.merge_session_with_post(model, appstruct)
        return model

    schema["source_company_id"].missing = colander.required
    schema.objectify = create_customer_from_company_id
    return schema


def get_internal_customer_editschema():
    excludes = (
        "name",
        "tva_intracomm",
        "registration",
    )
    schema = SQLAlchemySchemaNode(Customer, excludes=excludes)
    schema = _customize_schema(schema)
    schema["company_name"].missing = colander.required
    schema.after_bind = third_party_after_bind
    return schema


def get_internal_customer_schema(edit=False):
    if not edit:
        return get_internal_customer_addschema()
    else:
        return get_internal_customer_editschema()


def get_add_edit_customer_schema(excludes=None, includes=None):
    """
    Build a generic add edit customer schema
    """
    if includes is not None:
        excludes = None
    elif excludes is None:
        excludes = ("company_id",)

    schema = SQLAlchemySchemaNode(Customer, excludes=excludes, includes=includes)
    return schema


project_choice_node_factory = forms.mk_choice_node_factory(
    project_node_factory,
    title="Rattacher à un dossier",
    resource_name="un dossier",
    description="Rattacher ce client à un dossier existant",
)


class CustomerAddToProjectSchema(colander.MappingSchema):
    """
    Schema for project
    """

    customer_id_node = project_choice_node_factory(
        name="project_id",
    )
