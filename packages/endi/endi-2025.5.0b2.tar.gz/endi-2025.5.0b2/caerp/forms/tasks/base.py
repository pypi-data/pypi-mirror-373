"""
    Task form schemas (estimation, invoice ...)
    Note : since deform doesn't fit our form needs
            (estimation form is complicated and its structure
             is mixing many sqla tables)

    validation process:
        set all the line in the colander expected schema
        validate
        raise error on an adapted way
            build an error dict which is mako understandable

    merging process:
        get the datas
        build a factory
        merge estimation and task object
        commit
        merge all lines
        commit
        merge payment conditions
        commit

    formulaire :

    phase, displayUnits
    lignes de prestation descr, cout qtité, unité, tva
    lignes de remise descr, cout, tva (seulement les tvas utilisées dans
                                                    les lignes au-dessus)
    TOTAL HT
    for tva in used_tva:
        TOTAL TVA tva%
    TTC
    Frais de port
    TOTAL
"""
import functools
import logging

import colander
import deform
from sqlalchemy import or_

from caerp.consts.permissions import PERMISSIONS
from caerp.forms import customize_field, today_node
from caerp.forms.third_party.customer import customer_choice_node_factory
from caerp.models.company import Company
from caerp.models.config import Config
from caerp.models.form_options import FormFieldDefinition
from caerp.models.project import Project
from caerp.models.project.phase import Phase
from caerp.models.project.types import BusinessType
from caerp.models.task import Task, TaskLine, TaskLineGroup
from caerp.models.third_party.customer import Customer

logger = logging.getLogger(__name__)
DAYS = (
    ("NONE", "-"),
    ("HOUR", "Heure(s)"),
    ("DAY", "Jour(s)"),
    ("WEEK", "Semaine(s)"),
    ("MONTH", "Mois"),
    ("FEUIL", "Feuillet(s)"),
    ("PACK", "Forfait"),
)


MAIN_INFOS_GRID = (
    (
        ("date", 6),
        ("financial_year", 4),
    ),
    (("address", 6),),
    (("description", 12),),
    (
        ("workplace", 6),
        (("start_date", 6)),
    ),
    (("mention_ids", 12),),
    (("display_units", 12),),
    (("display_ttc", 12),),
)


# NEW TASK SCHEMA
# 1 - Project is current context : OK
# 2 - Duplication : Task is current context
# 3 - Customer is current context
# 4 - Company is current context
def _get_tasktype_from_request(request):
    route_name = request.matched_route.name
    try:
        result = request.context.type_
    except AttributeError:  # nontask context
        result = None
        pass  # fallback to the second method

    for predicate in ("estimation", "cancelinvoice", "invoice"):
        # Matches estimation and estimations
        if predicate in route_name:
            result = predicate
            break

    if result is None:
        raise ValueError("Cannot guess task type from request")
    return result


def get_task_type_from_factory(factory) -> str:
    """Find the task "type"


    :param factory: Child of Task class
    :type factory: class

    :raises Exception: when factory doesn't match any of the types
    :rtype: Literal["estimation", "invoice", "cancelinvoice"]
    """
    for name in ("estimation", "cancelinvoice", "invoice"):
        if name in factory.__tablename__:
            return name

    raise Exception("Unknown Task Type")


def get_task_type_label(task: Task) -> str:
    """
    Build the task type label (for example for permission check)
    """
    type_ = task.type_

    if type_ == "internalinvoice":
        type_ = "invoice"
    elif type_ == "internalcancelinvoice":
        type_ = "cancelinvoice"
    elif type_ == "internalestimation":
        type_ = "estimation"
    return type_


def _get_project_customers(project):
    """
    Return project customers

    :param obj project: The current project
    :returns: A list of Customer instances
    :rtype: list
    """
    query = Customer.label_query()
    customers = query.filter(Customer.projects.any(Project.id == project.id)).order_by(
        Customer.label
    )
    return customers


def _get_company_customers(context):
    """
    Return company customers

    :param obj context: The current Pyramid context
    :returns: A list of Customer instances
    :rtype: list
    """
    company_id = context.get_company_id()
    customers = Customer.label_query()
    if isinstance(context, Task):
        cid = context.customer_id
        customers = customers.filter(
            or_(Customer.archived == False, Customer.id == cid)  # noqa: E712
        )
    else:
        customers = customers.filter_by(archived=False)

    customers = customers.filter_by(company_id=company_id).all()

    if hasattr(context, "project_id"):
        # Si le contexte est attaché à un dossier, on s'assure que les
        # clients du dossier sont présentés en haut de la liste des
        # clients en utilisant une fonction de tri custom

        project_id = context.project_id

        def sort_pid_first(a, b):
            """
            Sort customers moving the customers belonging to the current
            project
            up in the list
            """
            if project_id in a.get_project_ids():
                return -1
            elif project_id in b.get_project_ids():
                return 1
            else:
                return 0

        customers = sorted(customers, key=functools.cmp_to_key(sort_pid_first))
    return customers


def _get_customers_options(request):
    """
    Retrieve customers that should be presented to the end user

    Regarding the context we return :

        company customers
        project customers
    """
    context = request.context

    if isinstance(context, Project):
        customers = _get_project_customers(context)
    else:
        customers = _get_company_customers(context)

    return customers


@colander.deferred
def deferred_default_customer(node, kw):
    """
    Return a default customer if there is one in the request GET params or if
    there is only one in the project
    """
    request = kw["request"]
    res = 0

    if isinstance(request.context, (Company, Project)):
        customers = request.context.customers
        if len(customers) == 1:
            res = customers[0].id
        elif "customer_id" in request.GET:
            cid = int(request.GET["customer_id"])
            if cid in [cust.id for cust in customers]:
                res = cid
    elif isinstance(request.context, Task):
        res = request.context.customer_id
    return res


def _get_project_choices(projects):
    """
    Format project list to select options

    :param list projects: Project instances
    :returns: A list of 2-uple (id, label)
    :rtype: list
    """
    return [(project.id, project.name) for project in projects]


@colander.deferred
def deferred_project_widget(node, kw):
    """
    return phase select widget
    """
    if isinstance(kw["request"].context, Project):
        wid = deform.widget.HiddenWidget()
    else:
        customer_id = deferred_default_customer(node, kw)

        if customer_id != 0:
            projects = Project.get_customer_projects(customer_id)
        else:
            projects = []

        choices = _get_project_choices(projects)
        wid = deform.widget.SelectWidget(values=choices)
    return wid


@colander.deferred
def deferred_default_project(node, kw):
    """
    Return the default project
    """
    res = None
    request = kw["request"]

    if isinstance(request.context, Company):
        if len(request.context.projects) == 1:
            res = request.context.projects[0].id
        else:
            res = colander.null
    elif request.context.type_ == "project":
        res = request.context.id
    elif isinstance(request.context, Task):
        res = request.context.project.id
    return res


def _get_phases_from_request(request):
    """
    Get the phases from the current project regarding request context
    """
    phases = []
    if isinstance(request.context, Project):
        phases = Phase.query_for_select(request.context.id).all()
    elif hasattr(request.context, "project_id"):
        # 'invoice', 'cancelinvoice', 'estimation'
        phases = Phase.query_for_select(request.context.project_id).all()
    return phases


@colander.deferred
def deferred_phases_widget(node, kw):
    """
    return phase select widget
    """
    request = kw["request"]
    choices = _get_phases_from_request(request)

    choices.insert(0, ("", "Ne pas ranger dans un sous-dossier"))
    wid = deform.widget.SelectWidget(values=choices)
    return wid


@colander.deferred
def deferred_default_phase(node, kw):
    """
    Return the default phase if one is present in the request arguments
    """
    request = kw["request"]
    phase_id = request.params.get("phase")
    if phase_id is not None:
        phases = _get_phases_from_request(request)
        if phase_id in [str(phase[0]) for phase in phases]:
            return int(phase_id)
        else:
            return colander.null
    elif hasattr(request.context, "phase_id"):
        return request.context.phase_id or colander.null
    else:
        return colander.null


def get_business_types_from_request(request):
    """
    Collect available business types allowed for the current user/context

    :param obj request: The current Pyramid request
    """
    context = request.context
    project = None

    if isinstance(context, Project):
        project = context
    elif hasattr(context, "project"):
        project = context.project

    result = []

    if project:
        if project.project_type.default_business_type:
            result.append(project.project_type.default_business_type)

        for business_type in project.business_types:
            if business_type != project.project_type.default_business_type:
                if business_type.allowed(request):
                    result.append(business_type)
    else:
        result = [i for i in BusinessType.query_for_select() if i.allowed(request)]

    # fix 1065
    if hasattr(context, "business_type") and context.business_type:
        if context.business_type not in result:
            result.append(context.business_type)
    return result


@colander.deferred
def business_type_id_validator(node, kw):
    allowed_ids = [i.id for i in get_business_types_from_request(kw["request"])]
    return colander.OneOf(allowed_ids)


@colander.deferred
def deferred_business_type_description(node, kw):
    request = kw["request"]
    business_types = get_business_types_from_request(request)
    if len(business_types) == 1:
        return ""
    else:
        return ("Type d'affaire",)


@colander.deferred
def deferred_business_type_widget(node, kw):
    """
    Collect the widget to display for business type selection

    :param node: The node we affect the widget to
    :param dict kw: The colander schema binding dict
    :returns: A SelectWidget or an hidden one
    """
    request = kw["request"]
    business_types = get_business_types_from_request(request)
    if len(business_types) == 0:
        return deform.widget.HiddenWidget()
    else:
        return deform.widget.SelectWidget(
            values=[
                (business_type.id, business_type.label)
                for business_type in business_types
            ]
        )


@colander.deferred
def deferred_business_type_default(node, kw):
    """
    Collect the default value to present to the end user
    """
    request = kw["request"]
    context = request.context
    if isinstance(context, Project):
        project = context
    elif hasattr(context, "business_type_id"):
        return context.business_type_id
    elif hasattr(context, "project"):
        project = context.project
    elif context.__name__ == "company":
        project = None
    else:
        raise KeyError(
            "No project could be found starting from current : %s" % (context,)
        )

    if project and project.project_type.default_business_type:
        return project.project_type.default_business_type.id
    else:
        return get_business_types_from_request(request)[0].id


@colander.deferred
def deferred_customer_project_widget(node, kw):
    request = kw["request"]
    projects = request.context.customer.projects
    logger.debug("### Getting the projects")
    choices = _get_project_choices(projects)
    wid = deform.widget.SelectWidget(values=choices)
    return wid


def change_metadatas_fields_after_bind(schema, kw):
    """
    Alter metadatas fields after binding the metadatas modification schema
    """
    context = kw["request"].context
    clean = False
    if context.type_ == "estimation":
        if context.business and not context.business.is_void():
            clean = True
    else:
        if context.type_ == "invoice":
            if context.invoicing_mode == context.PROGRESS_MODE:
                clean = True

    if clean:
        del schema["customer_id"]
        del schema["project_id"]
        del schema["phase_id"]
        schema.validator = None


def get_task_metadatas_edit_schema():
    """
    Return the schema for editing tasks metadatas

    :returns: The schema
    """
    schema = DuplicateSchema().clone()
    schema["customer_id"].widget = deform.widget.HiddenWidget()
    schema["project_id"].widget = deferred_customer_project_widget
    schema["project_id"].title = "Dossier vers lequel déplacer ce document"
    schema["phase_id"].title = "Sous-dossier dans lequel déplacer ce document"
    del schema["business_type_id"]
    schema.after_bind = change_metadatas_fields_after_bind
    return schema


@colander.deferred
def deferred_duplicate_name(node, kw):
    """
    Return a default name for the duplicated document
    current context is a Task
    """
    request = kw["request"]
    return "{} (Copie)".format(request.context.name)


class DuplicateSchema(colander.Schema):
    """
    schema used to duplicate a task
    """

    def validator(self, form, value):
        """
        Validate that customer project and phase are linked

        :param obj form: The form object
        :param dict value: The submitted values
        """
        customer_id = value.get("customer_id")
        project_id = value.get("project_id")
        phase_id = value.get("phase_id")

        if phase_id and not Project.check_phase_id(project_id, phase_id):
            exc = colander.Invalid(form, "Sous-dossier et dossier ne correspondent pas")
            exc["phase_id"] = "Ne correspond pas au dossier ci-dessus"
            raise exc
        if project_id and not Customer.check_project_id(customer_id, project_id):
            exc = colander.Invalid(form, "Client et dossier ne correspondent pas")
            exc["project_id"] = "Ne correspond pas au client ci-dessus"
            raise exc

    name = colander.SchemaNode(
        colander.String(),
        title="Nom du document",
        description="Ce nom n’apparaît pas dans le document final",
        validator=colander.Length(max=255),
        default=deferred_duplicate_name,
    )
    customer_id = customer_choice_node_factory(
        query_func=_get_customers_options,
        default=deferred_default_customer,
    )
    project_id = colander.SchemaNode(
        colander.Integer(),
        title="Dossier dans lequel insérer le document",
        widget=deferred_project_widget,
        default=deferred_default_project,
    )
    phase_id = colander.SchemaNode(
        colander.Integer(),
        title="Sous-dossier dans lequel insérer le document",
        widget=deferred_phases_widget,
        default=deferred_default_phase,
        missing=colander.drop,
    )
    business_type_id = colander.SchemaNode(
        colander.Integer(),
        title="Type d'affaire",
        widget=deferred_business_type_widget,
        default=deferred_business_type_default,
    )


def get_duplicate_schema():
    """
    Return the schema for task duplication

    :returns: The schema
    """
    return DuplicateSchema()


def _field_def_to_colander_params(field_def: FormFieldDefinition) -> dict:
    """
    Build colander SchemaNode parameters from a Field Definition
    """
    res = {"title": field_def.title, "missing": None}
    if field_def.required:
        res["missing"] = colander.required
    return res


def _customize_custom_fields(customize, schema):
    """
    Customize schema nodes for fields than can be customized through the
     FormFieldDefinition models
    """
    for field in (
        "workplace",
        "insurance_id",
        "start_date",
        "end_date",
        "first_visit",
        "validity_duration",
    ):
        if field in schema:
            field_def = FormFieldDefinition.get_definition(field, "task")
            if field_def is None or not field_def.visible:
                del schema[field]
            else:
                params = _field_def_to_colander_params(field_def)
                customize(field, **params)
    return schema


def task_after_bind(schema, kw):
    """
    After bind methods passed to the task schema

    Remove fields not allowed for edition

    :param obj schema: The SchemaNode concerning the Task
    :param dict kw: The bind arguments
    """
    customize = functools.partial(customize_field, schema)
    _customize_custom_fields(customize, schema)
