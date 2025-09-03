"""
Career stages administration tools
"""
import os
from caerp.consts.permissions import PERMISSIONS
from caerp.models.career_stage import CareerStage, STAGE_TYPE_OPTIONS
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.forms.admin.career_stage import get_career_stage_schema
from caerp.views.admin.tools import (
    AdminCrudListView,
    BaseAdminEditView,
    BaseAdminAddView,
    BaseAdminDisableView,
)
from caerp.views.admin.userdatas import (
    USERDATAS_URL,
    UserDatasIndexView,
)

CAREER_STAGE_URL = os.path.join(USERDATAS_URL, "career_stage")
CAREER_STAGE_ITEM_URL = os.path.join(CAREER_STAGE_URL, "{id}")


class CareerStageListView(AdminCrudListView):
    """
    List of career stages entries
    """

    title = "Étapes de parcours"
    description = ""
    route_name = CAREER_STAGE_URL
    columns = ["Libellé", "Nouvelle situation CAE", "Nature"]

    item_route_name = CAREER_STAGE_ITEM_URL
    permission = PERMISSIONS["global.config_userdatas"]

    def stream_columns(self, career_stage):
        """
        Stream the table datas for the given item
        :param obj career_stage: The CareerStage object to stream
        :returns: List of labels
        """
        situation_label = "<small class='text-muted'>Aucune</small>"
        if career_stage.cae_situation is not None:
            situation_label = career_stage.cae_situation.label
        stage_type_label = "<small class='text-muted'>Autre</small>"
        if career_stage.stage_type is not None:
            stage_type_label = dict(STAGE_TYPE_OPTIONS)[career_stage.stage_type]
        return (
            career_stage.name,
            situation_label,
            stage_type_label,
        )

    def stream_actions(self, career_stage):
        """
        Stream the actions available for the given career_stage object
        :param obj career_stage: CareerStage instance
        :returns: List of 5-uples (url, label, title, icon, disable)
        """
        yield Link(
            self._get_item_url(career_stage), "Voir/Modifier", icon="pen", css="icon"
        )
        if career_stage.active:
            yield POSTButton(
                self._get_item_url(career_stage, action="disable"),
                label="Désactiver",
                title="L'étape n'apparaitra plus dans l'interface",
                icon="lock",
                css="icon",
            )
        else:
            yield POSTButton(
                self._get_item_url(career_stage, action="disable"),
                "Activer",
                title="L'étape apparaitra dans l'interface",
                icon="lock-open",
                css="icon",
            )

    def load_items(self):
        return (
            CareerStage.query(include_inactive=True)
            # Clear existing ordering, then display disabled items last
            .order_by(None)
            .order_by(CareerStage.active.desc(), CareerStage.name)
            .all()
        )

    def more_template_vars(self, result):
        result["nodata_msg"] = "Aucune étape de parcours n'a été configurée"
        return result


class CareerStageDisableView(BaseAdminDisableView):
    """
    Disable view
    """

    route_name = CAREER_STAGE_ITEM_URL
    disable_msg = "L'étape de parcours a bien été désactivée"
    enable_msg = "L'étape de parcours a bien été activée"
    permission = PERMISSIONS["global.config_userdatas"]


class CareerStageEditView(BaseAdminEditView):
    """
    Edit view
    """

    route_name = CAREER_STAGE_ITEM_URL
    schema = get_career_stage_schema()
    factory = CareerStage
    title = "Modifier une étape de parcours"
    permission = PERMISSIONS["global.config_userdatas"]


class CareerStageAddView(BaseAdminAddView):
    """
    Add view
    """

    route_name = CAREER_STAGE_URL
    schema = get_career_stage_schema()
    factory = CareerStage
    title = "Ajouter une étape de parcours"

    permission = PERMISSIONS["global.config_userdatas"]


def includeme(config):
    """
    Add routes and views
    """
    config.add_route(CAREER_STAGE_URL, CAREER_STAGE_URL)
    config.add_route(
        CAREER_STAGE_ITEM_URL, CAREER_STAGE_ITEM_URL, traverse="/career_stages/{id}"
    )

    config.add_admin_view(
        CareerStageListView,
        parent=UserDatasIndexView,
        renderer="admin/crud_list.mako",
    )
    config.add_admin_view(
        CareerStageDisableView,
        parent=CareerStageListView,
        request_param="action=disable",
        require_csrf=True,
        request_method="POST",
        permission=PERMISSIONS["global.config_userdatas"],
    )
    config.add_admin_view(
        CareerStageAddView,
        parent=CareerStageListView,
        request_param="action=add",
        renderer="admin/crud_add_edit.mako",
        permission=PERMISSIONS["global.config_userdatas"],
    )
    config.add_admin_view(
        CareerStageEditView,
        parent=CareerStageListView,
        renderer="admin/crud_add_edit.mako",
        permission=PERMISSIONS["global.config_userdatas"],
    )
