from caerp.consts.permissions import PERMISSIONS
from caerp.models.company import Company
from caerp.utils.widgets import Link
from caerp.utils.strings import format_account

from caerp.models.project.business import Business
from caerp.models.project.project import Project
from caerp.forms.training.training import get_training_list_schema
from caerp.models.project.types import BusinessType

from caerp.views.business.lists import GlobalBusinessListView
from .routes import (
    TRAINING_DASHBOARD_URL,
    USER_TRAINER_EDIT_URL,
)


class TrainingDashboardView(GlobalBusinessListView):
    """
    Dashboard view allowing an employee to have an overview of its training
    activity

    Context : Company instance
    """

    is_admin = False
    schema = get_training_list_schema(is_global=False)
    title = "Mon activité de formation"

    def query(self):
        query = super(GlobalBusinessListView, self).query()
        query = query.join(Business.project)
        query = query.join(Business.business_type)
        query = query.filter(
            BusinessType.bpf_related == True,  # noqa: E712
            Project.company_id == self.context.id,
        )
        return query

    def _trainer_datas_links(self):
        result = []
        for user in self.context.employees:
            if user.trainerdatas:
                if not self.request.has_permission(
                    PERMISSIONS["global.view_training"], user
                ):
                    # Je ne peux pas éditer les infos formateurs de mes
                    # collègues
                    continue

                if user.id == self.request.identity.id:
                    label = "Voir/Modifier ma fiche formateur"
                else:
                    label = "Voir/Modifier la fiche formateur de {}".format(
                        format_account(user)
                    )
                result.append(
                    Link(
                        self.request.route_path(USER_TRAINER_EDIT_URL, id=user.id),
                        label,
                        icon="search",
                        popup=True,
                        css="btn",
                    )
                )
        return result

    def more_template_vars(self, result):
        result = GlobalBusinessListView.more_template_vars(self, result)
        result["trainer_datas_links"] = self._trainer_datas_links()
        return result


def includeme(config):
    config.add_view(
        TrainingDashboardView,
        route_name=TRAINING_DASHBOARD_URL,
        renderer="caerp:/templates/training/dashboard.mako",
        context=Company,
        permission=PERMISSIONS["context.view_training"],
    )

    def deferred_permission(menu, kw):
        return kw["request"].has_permission(
            PERMISSIONS["context.view_training"], kw["company"]
        )

    config.add_company_menu(
        parent="worktools",
        order=0,
        label="Formation",
        route_name=TRAINING_DASHBOARD_URL,
        route_id_key="company_id",
        permission=deferred_permission,
    )
