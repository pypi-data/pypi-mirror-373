import os

from sqlalchemy import asc, desc
from sqlalchemy.orm import load_only
from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.models.task.insurance import (
    TaskInsuranceOption,
)
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.forms.admin.sale.insurance import (
    get_admin_task_insurance_schema,
)
from caerp.views.admin.tools import (
    AdminCrudListView,
    BaseAdminDisableView,
    BaseAdminDeleteView,
    BaseAdminEditView,
    BaseAdminAddView,
)
from . import FORMS_URL, FormsIndexView

from caerp.utils.strings import format_float

COLLECTION_URL = os.path.join(FORMS_URL, "task_insurances")
ITEM_URL = os.path.join(COLLECTION_URL, "{id}")


class TaskInsuranceListView(AdminCrudListView):
    title = "Taux d'assurance des devis factures"
    description = (
        "Configurer les taux d'assurance à utiliser dans les devis et factures"
    )

    route_name = COLLECTION_URL
    item_route_name = ITEM_URL
    columns = ["Libellé", "Taux", "Est utilisé ?"]
    factory = TaskInsuranceOption
    permission = PERMISSIONS["global.config_sale"]

    def __init__(self, *args, **kwargs):
        AdminCrudListView.__init__(self, *args, **kwargs)
        self.max_order = TaskInsuranceOption.get_next_order() - 1

    @property
    def help_msg(self):
        from caerp.views.admin.sale.accounting.invoice import (
            MODULE_COLLECTION_URL,
        )

        return """
    Configurez les taux d'assurance à utiliser dans les devis et factures.
    <br />
    Ils pourront ensuite être sélectionnés dans les documents.<br />
    Une fois ces taux configurés, ils seront utilisés dans les calculs des
     écritures du module de contribution d'assurance, celui-ci est configurable
      dans <br />
    <a target='_blank' href='{}' title='Cette page s’ouvrira dans une nouvelle fenêtre' aria-label='Cette page s’ouvrira dans une nouvelle fenêtre'>Modules ventes -> Comptabilité : Écritures de
     ventes -> Factures -> Modules de contribution"</a>
    """.format(
            self.request.route_path(MODULE_COLLECTION_URL)
        )

    def stream_columns(self, item):
        yield item.label
        yield "{} %".format(format_float(item.rate))
        if item.is_used:
            yield self.get_icon("check")
        else:
            yield ""

    def stream_actions(self, item):
        yield Link(self._get_item_url(item), "Voir/Modifier", icon="pen", css="icon")
        move_url = self._get_item_url(item, action="move")
        if item.active:
            if item.order > 0:
                yield POSTButton(
                    move_url + "&direction=up",
                    "Remonter",
                    title="Remonter dans l'ordre de présentation",
                    icon="arrow-up",
                    css="icon",
                )
            if item.order < self.max_order:
                yield POSTButton(
                    move_url + "&direction=down",
                    "Redescendre",
                    title="Redescendre dans l'ordre de présenation",
                    icon="arrow-down",
                    css="icon",
                )
            yield POSTButton(
                self._get_item_url(item, action="disable"),
                "Désactiver",
                title=(
                    "Ce taux d'assurance ne sera plus proposé dans les" " documents"
                ),
                icon="lock",
                css="icon",
            )
        else:
            yield POSTButton(
                self._get_item_url(item, action="disable"),
                "Activer",
                title="Ce taux d'assurance sera proposé dans les documents",
                icon="lock-open",
                css="icon",
            )

        if not item.is_used:
            yield POSTButton(
                self._get_item_url(item, action="delete"),
                "Supprimer",
                icon="trash-alt",
                css="icon negative",
            )

    def load_items(self):
        """
        Return the sqlalchemy models representing current queried elements
        :rtype: SQLAlchemy.Query object
        """
        items = self.request.dbsession.query(TaskInsuranceOption).options(
            load_only(
                "label",
            )
        )
        items = items.order_by(desc(self.factory.active))
        items = items.order_by(asc(self.factory.order))
        return items

    def more_template_vars(self, result):
        result["help_msg"] = self.help_msg
        return result


class TaskInsuranceAddView(BaseAdminAddView):
    route_name = COLLECTION_URL
    factory = TaskInsuranceOption
    schema = get_admin_task_insurance_schema()

    def before(self, form):
        """
        Launched before the form is used

        :param obj form: The form object
        """
        pre_filled = {"order": self.factory.get_next_order()}
        form.set_appstruct(pre_filled)


class TaskInsuranceEditView(BaseAdminEditView):
    route_name = ITEM_URL
    factory = TaskInsuranceOption
    schema = get_admin_task_insurance_schema()

    help_msg = TaskInsuranceListView.help_msg

    @property
    def title(self):
        return "Modifier le taux d'assurance '{0}'".format(self.context.label)


class TaskInsuranceDisableView(BaseAdminDisableView):
    """
    View for TaskInsuranceOption disable/enable
    """

    route_name = ITEM_URL

    def on_enable(self):
        """
        on enable we set order to the last one
        """
        order = TaskInsuranceOption.get_next_order()
        self.context.order = order
        self.request.dbsession.merge(self.context)


class TaskInsuranceDeleteView(BaseAdminDeleteView):
    """
    TaskInsuranceOption deletion view
    """

    route_name = ITEM_URL


def move_view(context, request):
    """
    Reorder the current context moving it up in the category's hierarchy

    :param obj context: The given IncomeStatementMeasureType instance
    """
    action = request.params["direction"]
    if action == "up":
        context.move_up()
    else:
        context.move_down()
    return HTTPFound(request.route_path(COLLECTION_URL))


def includeme(config):
    config.add_route(COLLECTION_URL, COLLECTION_URL)
    config.add_route(
        ITEM_URL,
        ITEM_URL,
        traverse="/task_insurance_options/{id}",
    )
    config.add_admin_view(
        TaskInsuranceListView,
        parent=FormsIndexView,
        renderer="admin/crud_list.mako",
    )
    config.add_admin_view(
        TaskInsuranceAddView,
        parent=TaskInsuranceListView,
        renderer="admin/crud_add_edit.mako",
        request_param="action=add",
    )
    config.add_admin_view(
        TaskInsuranceEditView,
        parent=TaskInsuranceListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        TaskInsuranceDisableView,
        parent=TaskInsuranceListView,
        request_param="action=disable",
        request_method="POST",
        require_csrf=True,
    )
    config.add_admin_view(
        TaskInsuranceDeleteView,
        parent=TaskInsuranceListView,
        request_param="action=delete",
        request_method="POST",
        require_csrf=True,
    )
    config.add_admin_view(
        move_view,
        route_name=ITEM_URL,
        request_param="action=move",
        request_method="POST",
        require_csrf=True,
    )
