import os
from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import (
    AccompagnementConfigPDFSchema,
    ActivityConfigActionSchema,
)
from caerp.models.activity import (
    ActivityType,
    ActivityMode,
    ActivityAction,
)
from caerp.views.admin.accompagnement import (
    BaseAdminAccompagnementPDF,
    BaseAdminAccompagnementActions,
    AccompagnementIndexView,
    ACCOMPAGNEMENT_URL,
)
from caerp.views.admin.tools import (
    BaseAdminIndexView,
    get_model_admin_view,
)


ACTIVITY_URL = os.path.join(ACCOMPAGNEMENT_URL, "activity")
ACTIVITY_PDF_URL = os.path.join(ACTIVITY_URL, "pdfconfig")
ACTIVITY_ACTIONS_URL = os.path.join(ACTIVITY_URL, "actions")


class AdminActivitiesIndex(BaseAdminIndexView):
    route_name = ACTIVITY_URL
    title = "Rendez-vous"
    description = "Configuration des rendez-vous"
    permission = PERMISSIONS["global.config_activity"]


class AdminActivitiesActionView(BaseAdminAccompagnementActions):
    """
    Vue pour les liste d'actions/sous actions
    """

    title = "Actions des rendez-vous"
    route_name = ACTIVITY_ACTIONS_URL
    permission = PERMISSIONS["global.config_activity"]

    def get_schema(self):
        return ActivityConfigActionSchema(title="Actions des rendez-vous")

    def before(self, form):
        query = ActivityAction.query()
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
        self.disable_actions(appstruct, ActivityAction)
        self.dbsession.flush()

        self.add_actions(appstruct, "actions", ActivityAction)

        self.request.session.flash(self.validation_msg)
        return HTTPFound(self.request.route_path(self.parent_view.route_name))


class AdminActivitiesPDFView(BaseAdminAccompagnementPDF):
    """
    Activities Admin PDF config view
    """

    title = "Sorties PDF"
    route_name = ACTIVITY_PDF_URL
    permission = PERMISSIONS["global.config_activity"]

    def get_schema(self):
        return AccompagnementConfigPDFSchema(title="")

    def before(self, form):
        appstruct = {
            "footer": self.request.config.get("activity_footer", ""),
        }
        self._add_pdf_img_to_appstruct("activity", appstruct)
        form.set_appstruct(appstruct)

    def submit_success(self, appstruct):
        """
        Handle successfull activity configuration
        """
        self.store_pdf_conf(appstruct, "activity")
        self.dbsession.flush()
        self.request.session.flash(self.validation_msg)
        return HTTPFound(self.request.route_path(self.parent_view.route_name))


def includeme(config):
    config.add_route(ACTIVITY_URL, ACTIVITY_URL)
    config.add_admin_view(
        AdminActivitiesIndex,
        parent=AccompagnementIndexView,
    )

    config.add_route(ACTIVITY_ACTIONS_URL, ACTIVITY_ACTIONS_URL)
    config.add_admin_view(
        AdminActivitiesActionView,
        parent=AdminActivitiesIndex,
    )

    for model in (ActivityMode,):
        view = get_model_admin_view(model, r_path=ACTIVITY_URL)
        config.add_route(view.route_name, view.route_name)
        config.add_admin_view(
            view,
            parent=AdminActivitiesIndex,
        )

    for model in (ActivityType,):
        view = get_model_admin_view(model, only_active=True, r_path=ACTIVITY_URL)
        config.add_route(view.route_name, view.route_name)
        config.add_admin_view(
            view,
            parent=AdminActivitiesIndex,
        )

    config.add_route(ACTIVITY_PDF_URL, ACTIVITY_PDF_URL)
    config.add_admin_view(
        AdminActivitiesPDFView,
        parent=AdminActivitiesIndex,
    )
