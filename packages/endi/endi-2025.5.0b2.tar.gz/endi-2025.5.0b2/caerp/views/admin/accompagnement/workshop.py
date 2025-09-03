import os
from colanderalchemy.schema import SQLAlchemySchemaNode
from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import (
    AccompagnementConfigPDFSchema,
    WorkshopConfigActionSchema,
)
from caerp.models.workshop import (
    WorkshopAction,
    WorkshopTagOption,
)
from caerp.views.admin.accompagnement import (
    BaseAdminAccompagnementPDF,
    BaseAdminAccompagnementActions,
    AccompagnementIndexView,
    ACCOMPAGNEMENT_URL,
)
from caerp.views.admin.tools import (
    get_model_admin_view,
    BaseAdminIndexView,
)
from caerp.forms.admin import (
    get_sequence_model_admin,
)
import colander

WORKSHOP_URL = os.path.join(ACCOMPAGNEMENT_URL, "workshop")
WORKSHOP_PDF = os.path.join(WORKSHOP_URL, "pdf")
WORKSHOP_TAGS_URL = os.path.join(WORKSHOP_URL, "tags")
WORKSHOP_ACTIONS_URL = os.path.join(WORKSHOP_URL, "actions")

BaseWorkshopTagOptionView = get_model_admin_view(
    WorkshopTagOption,
    r_path=WORKSHOP_URL,
    permission=PERMISSIONS["global.config_workshop"],
)


class WorkshopTagOptionView(BaseWorkshopTagOptionView):
    """
    Workshop tags configuration
    """

    permission = PERMISSIONS["global.config_workshop"]

    def get_schema(self):
        return get_sequence_model_admin(
            WorkshopTagOption,
            excludes=("requirements",),
        )

    def customize_schema(self, schema):
        schema["datas"]["data"]["label"] = colander.SchemaNode(
            colander.String(),
            name="label",
            title="Libellé",
            missing=None,
            validator=None,
        )
        return schema

    def remove_label_duplicates(self, item, options):
        """
        Remove duplicates label in tags
        """
        for option in options:
            if item["label"] == option.label and item["id"] != option.id:
                item["label"] = [i.label for i in options if i.id == item["id"]]
        return item

    def submit_success(self, appstruct):
        """
        Handle successfull submission
        """

        options = WorkshopTagOption.query().all()

        appstruct_options_labels_with_id = [
            i["label"] for i in appstruct["datas"] if i["id"] is not None
        ]
        options_validated = []

        for i in appstruct["datas"]:
            if i["id"] is not None:
                item = self.remove_label_duplicates(i, options)
                options_validated.append(item)
            elif (
                i["label"] is not None
                and i["label"] not in appstruct_options_labels_with_id
            ):
                options_validated.append(i)

        appstruct["datas"] = options_validated

        self._disable_or_remove_elements(appstruct)

        for index, datas in enumerate(appstruct.get("datas", [])):
            self._add_or_edit(index, datas)

        self.request.session.flash(self.validation_msg)
        return HTTPFound(self.request.route_path(self.redirect_route_name))


class AdminWorkshopActionView(BaseAdminAccompagnementActions):
    """
    Vue pour les liste d'actions/sous actions
    """

    title = "Actions des ateliers"
    route_name = WORKSHOP_ACTIONS_URL
    permission = PERMISSIONS["global.config_workshop"]

    def get_schema(self):
        return WorkshopConfigActionSchema(title="Actions des ateliers")

    def before(self, form):
        query = WorkshopAction.query()
        query = query.filter_by(parent_id=None)
        actions = query.filter_by(active=True)

        appstruct = {
            "actions": self._recursive_action_appstruct(actions),
        }
        form.set_appstruct(appstruct)

    def submit_success(self, appstruct):
        """
        Handle successfull activity configuration
        """
        # We delete the elements that are no longer in the appstruct
        self.disable_actions(appstruct, WorkshopAction)
        self.dbsession.flush()

        self.add_actions(appstruct, "actions", WorkshopAction)

        self.request.session.flash(self.validation_msg)
        return HTTPFound(self.request.route_path(self.parent_view.route_name))


class AdminWorkshopView(BaseAdminAccompagnementPDF):
    """
    Workshops administration views
    """

    title = "Sorties PDF"
    route_name = WORKSHOP_PDF
    permission = PERMISSIONS["global.config_workshop"]

    def get_schema(self):
        return AccompagnementConfigPDFSchema(title="")

    def before(self, form):
        """
        Add appstruct to the current form object
        """
        appstruct = {
            "footer": self.request.config.get("workshop_footer", ""),
        }
        self._add_pdf_img_to_appstruct("workshop", appstruct)

        form.set_appstruct(appstruct)

    def submit_success(self, appstruct):
        """
        Handle successfull workshop configuration
        """
        self.store_pdf_conf(appstruct, "workshop")
        self.dbsession.flush()

        self.request.session.flash(self.validation_msg)
        return HTTPFound(self.request.route_path(self.parent_view.route_name))


class WorkshopIndexView(BaseAdminIndexView):
    title = "Ateliers"
    description = "Configuration du module Ateliers"
    route_name = WORKSHOP_URL
    permission = PERMISSIONS["global.config_workshop"]


def includeme(config):
    config.add_route(WORKSHOP_URL, WORKSHOP_URL)
    config.add_admin_view(
        WorkshopIndexView,
        parent=AccompagnementIndexView,
    )

    for view in (
        WorkshopTagOptionView,
        AdminWorkshopActionView,
        AdminWorkshopView,
    ):
        config.add_route(view.route_name, view.route_name)
        config.add_admin_view(
            view,
            parent=WorkshopIndexView,
        )
