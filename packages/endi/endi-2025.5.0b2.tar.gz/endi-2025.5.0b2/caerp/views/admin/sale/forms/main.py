import logging
import os

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.models.task import (
    WorkUnit,
    PaymentConditions,
)
from caerp.views.admin.tools import (
    get_model_admin_view,
    BaseConfigView,
)

from . import FORMS_URL, FormsIndexView


logger = logging.getLogger(__name__)


FORM_CONFIG_URL = os.path.join(FORMS_URL, "config")


class SaleFormAdminView(BaseConfigView):
    title = "Options de formulaire"
    description = (
        "Activation du mode TTC, valeur par défaut limite de validité des devis"
    )
    route_name = FORM_CONFIG_URL
    validation_msg = "Les informations ont bien été enregistrées"

    keys = (
        "task_display_units_default",
        "task_display_ttc_default",
        "estimation_validity_duration_default",
        "estimation_payment_display_default",
    )
    schema = get_config_schema(keys)
    permission = PERMISSIONS["global.config_sale"]


WorkUnitAdminView = get_model_admin_view(WorkUnit, r_path=FORMS_URL, can_disable=False)

PaymentConditionsAdminView = get_model_admin_view(PaymentConditions, r_path=FORMS_URL)


def includeme(config):
    for view in (
        SaleFormAdminView,
        WorkUnitAdminView,
        PaymentConditionsAdminView,
    ):
        config.add_route(view.route_name, view.route_name)
        config.add_admin_view(
            view,
            parent=FormsIndexView,
        )
