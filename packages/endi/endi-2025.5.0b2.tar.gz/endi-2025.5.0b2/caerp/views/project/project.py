"""
Project views
Context could be either

Company
- add view
- list view

Project
- view
- add_phase
- edit
"""
import logging

from colanderalchemy.schema import SQLAlchemySchemaNode
from deform import Form
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.models.company import Company
from caerp.models.project import Project
from caerp.models.task import Task, Estimation, Invoice, CancelInvoice
from caerp.utils.colors import COLORS_SET
from caerp.forms.project import (
    get_add_project_schema,
    get_add_step2_project_schema,
    get_edit_project_schema,
    PhaseSchema,
)
from caerp.views import (
    BaseView,
    BaseAddView,
    BaseEditView,
    submit_btn,
    TreeMixin,
)
from caerp.views.project.routes import (
    COMPANY_PROJECTS_ROUTE,
    PROJECT_ITEM_ROUTE,
    PROJECT_ITEM_GENERAL_ROUTE,
    PROJECT_ITEM_PHASE_ROUTE,
    PROJECT_ITEM_BUSINESS_ROUTE,
    PROJECT_ITEM_ESTIMATION_ROUTE,
    PROJECT_ITEM_INVOICE_ROUTE,
)
from caerp.views.project.lists import (
    redirect_to_customerslist,
    ProjectListView,
)

log = logger = logging.getLogger(__name__)

ADD_STEP1_FORM_GRID = (
    (("name", 12),),
    (("project_type_id", 12),),
    (("customers", 12),),
)
ADD_STEP2_FORM_GRID = (
    (
        ("description", 6),
        ("code", 6),
    ),
    (
        ("starting_date", 6),
        ("ending_date", 6),
    ),
    (("definition", 12),),
    (("business_types", 12),),
    (("mode", 12),),
)
EDIT_FORM_GRID = (
    (("name", 12),),
    (("project_type_id", 12),),
    (("customers", 12),),
    (
        ("description", 8),
        ("code", 4),
    ),
    (
        ("starting_date", 6),
        ("ending_date", 6),
    ),
    (("definition", 12),),
    (("business_types", 12),),
    (("mode", 12),),
)


class ProjectEntryPointView(BaseView, TreeMixin):
    route_name = PROJECT_ITEM_ROUTE

    @property
    def title(self):
        return "Dossier {}".format(self.current().name)

    def current(self):
        if hasattr(self.context, "project_id"):
            return self.context.project
        elif hasattr(self.context, "task"):
            return self.context.task.project
        else:
            return self.context

    @property
    def tree_url(self):
        return self.request.route_path(self.route_name, id=self.current().id)

    def __call__(self):
        """
        Project entry point view only redirects to the most appropriate page
        """
        if (
            self.request.has_permission(PERMISSIONS["context.list_businesses"])
            and self.context.businesses
        ):
            last = self.request.route_path(
                PROJECT_ITEM_BUSINESS_ROUTE, id=self.context.id
            )
        elif self.context.invoices:
            last = self.request.route_path(
                PROJECT_ITEM_INVOICE_ROUTE, id=self.context.id
            )
        else:
            last = self.request.route_path(
                PROJECT_ITEM_ESTIMATION_ROUTE, id=self.context.id
            )
        return HTTPFound(last)


class ProjectPhaseListView(BaseView, TreeMixin):
    route_name = PROJECT_ITEM_PHASE_ROUTE

    def current_id(self):
        if hasattr(self.context, "project_id"):
            return self.context.project_id
        else:
            return self.context.id

    @property
    def tree_url(self):
        return self.request.route_path(self.route_name, id=self.current_id())

    @property
    def title(self):
        return "Dossier : {0}".format(self.context.name)

    def _get_phase_add_form(self):
        """
        Return a form object for phase add
        :param obj request: The pyramid request object
        :returns: A form
        :rtype: class:`deform.Form`
        """
        schema = PhaseSchema().bind(request=self.request)
        form = Form(
            schema,
            buttons=(submit_btn,),
            action=self.request.route_path(
                PROJECT_ITEM_ROUTE, id=self.context.id, _query={"action": "addphase"}
            ),
        )
        return form

    def _get_latest_phase_id(self, tasks_by_phase):
        """
        Return the phase where we can identify the last modification

        :param list tasks_by_phase: The dict of tasks
        """
        result = 0
        if "phase" in self.request.GET:
            result = int(self.request.GET["phase"])

        else:
            # We get the latest used task and so we get the latest used phase
            all_tasks = []
            for phase_id, tasks in list(tasks_by_phase.items()):
                all_tasks.extend(tasks["estimations"])
                all_tasks.extend(tasks["invoices"])
            all_tasks.sort(key=lambda task: task.status_date, reverse=True)

            if all_tasks:
                result = all_tasks[0].phase_id

        return result

    def _get_color(self, index):
        """
        return the color for the given index (uses modulo to avoid index errors
        """
        return COLORS_SET[index % len(COLORS_SET)]

    def _set_estimation_colors(self, estimations):
        """
        Set colors on the estimations

        :param list estimations: Estimations
        """
        color_index = 0
        for estimation in estimations:
            estimation.color = self._get_color(color_index)
            color_index += 1

    def _set_invoice_colors(self, invoices):
        """
        Set colors on invoices

        :param list invoices: List of invoices
        """
        color_index = 0
        for invoice in invoices:
            if invoice.estimation and hasattr(invoice.estimation, "color"):
                invoice.color = invoice.estimation.color
            else:
                invoice.color = self._get_color(color_index)
                color_index += 1

    def _set_cancelinvoice_colors(self, invoices):
        """
        Set colors on cancelinvoices

        :param list invoices: List of cancelinvoices
        """
        color_index = 0
        for invoice in invoices:
            if invoice.invoice and hasattr(invoice.invoice, "color"):
                invoice.color = invoice.invoice.color
            else:
                invoice.color = self._get_color(color_index)
                color_index += 1

    def _collect_documents_by_phase(self, phases):
        """
        Collect all documents (estimations, invoices, cancelinvoices)
        and store them by phase

        :param phases: All the phases attached to this project
        :returns: A dict {phase_id: {'estimations': [], 'invoices': {}}}
        :rtype: dict
        """
        estimations = (
            self.request.dbsession.query(Estimation)
            .filter_by(project_id=self.context.id)
            .order_by(Estimation.date)
            .all()
        )

        query = self.request.dbsession.query(Task)
        query = query.with_polymorphic([Invoice, CancelInvoice])
        query = query.filter(Task.type_.in_(Task.invoice_types))
        query = query.filter_by(project_id=self.context.id)
        invoices = query.order_by(Task.date).all()

        self._set_estimation_colors(estimations)
        self._set_invoice_colors(
            [i for i in invoices if i.type_ in ("internalinvoice", "invoice")]
        )
        self._set_cancelinvoice_colors(
            [
                i
                for i in invoices
                if i.type_ in ("cancelinvoice", "internalcancelinvoice")
            ]
        )

        result = {}
        for phase in phases:
            result[phase.id] = {"estimations": [], "invoices": []}
        for estimation in estimations:
            logger.debug("We've got an estimation : %s" % estimation.phase_id)
            phase_dict = result.setdefault(
                estimation.phase_id, {"estimations": [], "invoices": []}
            )
            phase_dict["estimations"].append(estimation)

        for invoice in invoices:
            phase_dict = result.setdefault(
                invoice.phase_id, {"estimations": [], "invoices": []}
            )
            phase_dict["invoices"].append(invoice)
        logger.debug("Returning %s" % result)
        return result

    def __call__(self):
        self.populate_navigation()
        phases = self.context.phases
        tasks_by_phase = self._collect_documents_by_phase(phases)

        tasks_without_phases = tasks_by_phase.pop(None, None) or dict(
            estimations=[],
            invoices=[],
        )

        return dict(
            project=self.context,
            latest_phase_id=self._get_latest_phase_id(tasks_by_phase),
            phase_form=self._get_phase_add_form(),
            tasks_by_phase=tasks_by_phase,
            tasks_without_phases=tasks_without_phases,
            phases=phases,
            title=self.title,
        )


class ProjectGeneralView(BaseView, TreeMixin):
    route_name = PROJECT_ITEM_GENERAL_ROUTE

    @property
    def tree_url(self):
        return self.request.route_path(self.route_name, id=self.context.id)

    @property
    def title(self):
        return "Dossier : {0}".format(self.context.name)

    def __call__(self):
        """
        Return datas for displaying one project
        """
        self.populate_navigation()
        return dict(
            title=self.title,
            project=self.context,
            company=self.context.company,
        )


class ProjectAddView(BaseAddView, TreeMixin):
    title = "Ajout d'un nouveau dossier"
    msg = "Le dossier a été ajouté avec succès"
    named_form_grid = ADD_STEP1_FORM_GRID
    factory = Project
    route_name = COMPANY_PROJECTS_ROUTE

    def get_schema(self) -> SQLAlchemySchemaNode:
        return get_add_project_schema(self.request)

    def before(self, form):
        BaseAddView.before(self, form)
        self.populate_navigation()
        # If there's no customer, redirect to customer view
        if len(self.request.context.customers) == 0:
            redirect_to_customerslist(self.request, self.request.context)

    def redirect(self, appstruct, new_model):
        return HTTPFound(
            self.request.route_path(
                PROJECT_ITEM_ROUTE,
                id=new_model.id,
                _query={"action": "addstep2"},
            )
        )

    def on_add(self, new_model: Project, appstruct):
        new_model.company = self.context

        # Set compute mode if there is no choice to be made about it
        # Else step2 will offer the user the choice.
        compute_mode = self._guess_compute_mode(new_model)
        if compute_mode is not None:
            new_model.mode = compute_mode

    @staticmethod
    def _guess_compute_mode(new_model: Project):
        from caerp.models.project import ProjectType

        # Not relying on new_model.project_type because new_model has not been saved yet
        # (at this stage, new_model.project_type is None, despite
        # new_model.project_type_id being set)
        project_type = ProjectType.get(new_model.project_type_id)

        ht_allowed = project_type.ht_compute_mode_allowed
        ttc_allowed = project_type.ttc_compute_mode_allowed

        if ht_allowed and not ttc_allowed:
            return "ht"
        elif ttc_allowed and not ht_allowed:
            return "ttc"
        else:
            return None


class ProjectAddStep2View(BaseEditView, TreeMixin):
    named_form_grid = ADD_STEP2_FORM_GRID
    add_template_vars = ("title", "project_codes")
    route_name = PROJECT_ITEM_ROUTE

    def get_schema(self) -> SQLAlchemySchemaNode:
        return get_add_step2_project_schema(self.request, self.context)

    @property
    def project_codes(self):
        return Project.get_code_list_with_labels(self.context.company_id)

    @reify
    def title(self):
        return "Création du dossier : {0}, étape 2".format(self.context.name)

    def redirect(self, appstruct):
        return HTTPFound(
            self.request.route_path(
                PROJECT_ITEM_ROUTE,
                id=self.context.id,
            )
        )


class ProjectEditView(BaseEditView, TreeMixin):
    add_template_vars = (
        "project",
        "project_codes",
    )
    named_form_grid = EDIT_FORM_GRID
    route_name = PROJECT_ITEM_ROUTE

    def get_schema(self):
        return get_edit_project_schema(self.request, self.context)

    def before(self, form):
        BaseEditView.before(self, form)
        self.populate_navigation()

    @property
    def title(self):
        return "Modification du dossier : {0}".format(self.request.context.name)

    @property
    def project(self):
        return self.context

    @property
    def project_codes(self):
        return Project.get_code_list_with_labels(self.context.company_id)

    def redirect(self, appstruct):
        return HTTPFound(
            self.request.route_path(PROJECT_ITEM_ROUTE, id=self.context.id)
        )


def project_archive(request):
    """
    Archive the current project
    """
    project = request.context
    if not project.archived:
        request.session.flash("Le dossier '{0}' a été archivé".format(project.name))
        project.archived = True
    else:
        project.archived = False
        request.session.flash("Le dossier '{0}' a été désarchivé".format(project.name))
    request.dbsession.merge(project)
    if request.referer is not None:
        return HTTPFound(request.referer)
    else:
        return HTTPFound(
            request.route_path(COMPANY_PROJECTS_ROUTE, id=request.context.company_id)
        )


def project_delete(request):
    """
    Delete the current project
    """
    project = request.context
    cid = project.company_id
    log.info("Project {0} deleted".format(project))
    request.dbsession.delete(project)
    request.session.flash("Le dossier '{0}' a bien été supprimé".format(project.name))
    if request.referer is not None:
        return HTTPFound(request.referer)
    else:
        return HTTPFound(request.route_path(COMPANY_PROJECTS_ROUTE, id=cid))


def includeme(config):
    config.add_tree_view(
        ProjectEntryPointView,
        parent=ProjectListView,
        context=Project,
        permission=PERMISSIONS["company.view"],
    )
    config.add_tree_view(
        ProjectPhaseListView,
        parent=ProjectListView,
        renderer="project/phases.mako",
        layout="project",
        context=Project,
        permission=PERMISSIONS["company.view"],
    )
    config.add_tree_view(
        ProjectGeneralView,
        parent=ProjectListView,
        renderer="project/general.mako",
        layout="project",
        context=Project,
        permission=PERMISSIONS["company.view"],
    )
    config.add_tree_view(
        ProjectAddView,
        parent=ProjectListView,
        renderer="caerp:templates/base/formpage.mako",
        request_param="action=add",
        layout="default",
        context=Company,
        permission=PERMISSIONS["context.add_project"],
    )
    config.add_tree_view(
        ProjectAddStep2View,
        parent=ProjectListView,
        renderer="project/edit.mako",
        request_param="action=addstep2",
        layout="default",
        context=Project,
        permission=PERMISSIONS["context.edit_project"],
    )
    config.add_tree_view(
        ProjectEditView,
        parent=ProjectGeneralView,
        renderer="project/edit.mako",
        request_param="action=edit",
        layout="project",
        context=Project,
        permission=PERMISSIONS["context.edit_project"],
    )
    config.add_view(
        project_delete,
        route_name=PROJECT_ITEM_ROUTE,
        request_param="action=delete",
        require_csrf=True,
        request_method="POST",
        context=Project,
        permission=PERMISSIONS["context.edit_project"],
    )
    config.add_view(
        project_archive,
        route_name=PROJECT_ITEM_ROUTE,
        request_param="action=archive",
        require_csrf=True,
        request_method="POST",
        context=Project,
        permission=PERMISSIONS["context.edit_project"],
    )
