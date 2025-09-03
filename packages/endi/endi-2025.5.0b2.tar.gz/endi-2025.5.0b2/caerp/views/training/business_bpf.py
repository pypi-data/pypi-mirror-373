from caerp.consts.permissions import PERMISSIONS
from colanderalchemy import SQLAlchemySchemaNode
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
)

from caerp.forms.training.bpf import (
    get_cerfa_spec,
    get_year_from_request,
)
from caerp.models.services.bpf import BPFService
from caerp.models.task.invoice import (
    get_invoice_years,
)
from caerp.resources import bpf_js
from caerp.utils.colanderalchemy import patched_objectify
from caerp.utils.widgets import (
    ButtonDropDownMenu,
    ViewLink,
)
from caerp.events.business import BpfDataModified
from caerp.utils.datetimes import get_current_year
from caerp.views.training.routes import (
    BUSINESS_BPF_DATA_FORM_URL,
    BUSINESS_BPF_DATA_DELETE_URL,
    BUSINESS_BPF_DATA_LIST_URL,
)
from caerp.views.business.business import BusinessOverviewView
from caerp.views import (
    BaseEditView,
    BaseView,
    DeleteView,
    TreeMixin,
)


class BusinessBPFMixin:
    @property
    def bpf_datas(self):
        return self.current_business.bpf_datas

    @property
    def current_business(self):
        return self.context

    @property
    def new_bpf_years(self):
        """
        The financial years eligible for new bpf data (with no existing bpf)

        :yield: <year>, <bpf year url>
        """
        existing_bpf_years = set(i.financial_year for i in self.bpf_datas)
        for year in get_invoice_years():
            if year not in existing_bpf_years:
                yield year

    @property
    def new_bpfdata_menu(self):
        menu = ButtonDropDownMenu()
        menu.name = "Ajouter une année"
        menu.icon = "plus"

        for year in self.new_bpf_years:
            link = ViewLink(
                year,
                css="btn",
                path=BUSINESS_BPF_DATA_FORM_URL,
                id=self.current_business.id,
                year=year,
            )
            menu.add(link)
        return menu


class BusinessBPFDataListView(TreeMixin, BusinessBPFMixin, BaseView):
    route_name = BUSINESS_BPF_DATA_LIST_URL
    title = "Données BPF"

    @property
    def tree_url(self):
        return self.request.route_path(
            self.route_name,
            id=self.current_business.id,
        )

    @property
    def bpf_datas_links(self):
        for bpf_data in self.bpf_datas:
            form_link = self.request.route_path(
                BUSINESS_BPF_DATA_FORM_URL,
                id=self.current_business.id,
                year=bpf_data.financial_year,
            )
            delete_link = self.request.route_path(
                BUSINESS_BPF_DATA_DELETE_URL,
                id=self.current_business.id,
                year=bpf_data.financial_year,
            )
            yield [bpf_data, form_link, delete_link]

    def __call__(self):
        self.populate_navigation()

        # More than 1 bpf data : offer choice
        if len(self.bpf_datas) > 1:
            return dict(
                current_business=self.current_business,
                bpf_datas=self.bpf_datas,
                bpf_datas_links=self.bpf_datas_links,
                title=self.title,
                new_bpfdata_menu=self.new_bpfdata_menu,
            )
        else:
            try:
                year = self.bpf_datas[0].financial_year
            except IndexError:
                year = get_current_year()

            return HTTPFound(
                self.request.route_path(
                    BUSINESS_BPF_DATA_FORM_URL,
                    id=self.current_business.id,
                    year=year,
                )
            )


class BusinessBPFDataEditView(BusinessBPFMixin, TreeMixin, BaseEditView):
    """Create+Edit view for BusinessBPFData Model

    As there is maximum one BusinessBPFData per Business, this is a single
    view, with a « create or update » logic.
    """

    route_name = BUSINESS_BPF_DATA_FORM_URL
    add_template_vars = [
        "new_bpfdata_menu",
        "bpf_datas_tuples",
        "is_creation_form",
        "context_model",
    ]

    def get_schema(self) -> SQLAlchemySchemaNode:
        is_subcontract_data = self.request.POST.get("is_subcontract", "false")
        is_subcontract = is_subcontract_data == "true"
        return get_cerfa_spec(self.request).get_colander_schema(
            is_subcontract=is_subcontract
        )

    @property
    def title(self):
        return get_year_from_request(self.request)

    @property
    def is_creation_form(self):
        return self.get_context_model().id is None

    @property
    def bpf_datas_tuples(self):
        tuples = []
        for bpf_data in self.bpf_datas:
            edit_link = self.request.route_path(
                BUSINESS_BPF_DATA_FORM_URL,
                id=bpf_data.business.id,
                year=bpf_data.financial_year,
            )
            delete_link = self.request.route_path(
                BUSINESS_BPF_DATA_DELETE_URL,
                id=bpf_data.business.id,
                year=bpf_data.financial_year,
            )
            tuples.append([bpf_data, edit_link, delete_link])
        return tuples

    @property
    def context_model(self):
        return self.get_context_model()

    def get_context_model(self):
        try:
            return self.bpf_data  # cached
        except AttributeError:
            self.bpf_data = BPFService.get_or_create(
                self.context.id,
                get_year_from_request(self.request),
            )
            # We do not want to save anything now.
            if self.bpf_data.id is None:
                self.dbsession.expunge(self.bpf_data)
        return self.bpf_data

    def before(self, form):
        self.populate_navigation()
        bpf_js.need()
        return BaseEditView.before(self, form)

    def merge_appstruct(self, appstruct, model):
        # Workaround ColanderAlchemy bug #101 (FlushError)
        # https://github.com/stefanofontanelli/ColanderAlchemy/issues/101
        # A PR is ongoing, if merged/released, that workaround should be removed
        # https://github.com/stefanofontanelli/ColanderAlchemy/pull/103
        model = patched_objectify(self.schema, appstruct, model)
        return model

    def submit_success(self, appstruct):
        if "trainee_types" in appstruct and len(appstruct["trainee_types"]) == 1:
            appstruct["trainee_types"][0]["headcount"] = appstruct["headcount"]
            appstruct["trainee_types"][0]["total_hours"] = appstruct["total_hours"]

        # Forces some values if is_subcontract is on
        if appstruct["is_subcontract"]:
            for income_source in appstruct["income_sources"]:
                # 31 = « Contrats conclus avec d’autres organismes de formation (y compris CFA) »
                income_source["income_category_id"] = 31
            appstruct["training_goal_id"] = None
            appstruct["training_speciality_id"] = None

        return super(BusinessBPFDataEditView, self).submit_success(appstruct)

    def on_edit(self, appstruct, model):
        self.request.registry.notify(BpfDataModified(self.request, model.business_id))

    def redirect(self, redirect):
        return HTTPFound(
            self.request.route_path(
                BUSINESS_BPF_DATA_LIST_URL,
                id=self.get_context_model().business.id,
            )
        )


class BusinessBPFDeleteView(DeleteView):
    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                BUSINESS_BPF_DATA_LIST_URL,
                id=self._business.id,
            )
        )

    def on_before_delete(self):
        # The context is Business, which is not what we want to delete…
        year = get_year_from_request(self.request)
        self._bpf_data = BPFService.get(
            business_id=self.context.id, financial_year=year
        )
        if self._bpf_data is None:
            raise HTTPNotFound()
        else:
            self._business = self.context
            self.context = self._bpf_data
            self.delete_msg = f"Les données BPF pour l'année {year} ont été supprimées"

    def on_delete(self):
        # Restore context
        self.context = self._business
        self.request.registry.notify(BpfDataModified(self.request, self._business.id))


def includeme(config):
    config.add_view(
        BusinessBPFDeleteView,
        route_name=BUSINESS_BPF_DATA_DELETE_URL,
        permission=PERMISSIONS["context.edit_bpf"],
        request_method="POST",
        require_csrf=True,
    )

    config.add_tree_view(
        BusinessBPFDataEditView,
        parent=BusinessBPFDataListView,
        renderer="caerp:templates/training/bpf/business_bpf_data_form.mako",
        permission=PERMISSIONS["context.edit_bpf"],
        layout="business",
    )

    config.add_tree_view(
        BusinessBPFDataListView,
        parent=BusinessOverviewView,
        renderer="caerp:templates/training/bpf/business_bpf_data_list.mako",
        permission=PERMISSIONS["context.edit_bpf"],
        layout="business",
    )
