import logging
from caerp.consts.permissions import PERMISSIONS
from typing import Dict

from sqlalchemy import desc
from pyramid.httpexceptions import (
    HTTPFound,
)
from sqla_inspect import csv

from caerp.resources import statistic_resources
from caerp.models.user.userdatas import UserDatas
from caerp.models.statistics import (
    StatisticEntry,
    StatisticSheet,
)
from caerp.statistics import (
    EntryQueryFactory,
    SheetQueryFactory,
    get_inspector,
)
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.utils import ascii
from caerp.forms.statistics import get_sheet_add_edit_schema
from caerp.views import (
    BaseView,
    DisableView,
    DeleteView,
    DuplicateView,
    BaseAddView,
    BaseEditView,
    TreeMixin,
    JsAppViewMixin,
)
from caerp.views.userdatas.lists import UserDatasCsvView
from caerp.export.utils import write_file_to_request

from .routes import (
    get_sheet_url,
    STATISTICS_ROUTE,
    STATISTIC_ITEM_ROUTE,
    STATISTIC_ITEM_CSV_ROUTE,
    ENTRY_ITEM_CSV_ROUTE,
    API_ENTRIES_ROUTE,
)


logger = logging.getLogger(__name__)


class SheetListView(BaseView, TreeMixin):
    """
    Listview of statistic sheets
    """

    title = "Feuilles de statistiques (obsolète)"
    route_name = STATISTICS_ROUTE

    def stream_actions(self, sheet):
        """
        Collect action button definitions for the given sheet
        """
        yield Link(
            get_sheet_url(self.request, sheet),
            "Voir / Modifier",
            "Voir cette feuille de statistiques",
            icon="pen",
        )
        yield POSTButton(
            get_sheet_url(self.request, sheet, _query={"action": "duplicate"}),
            "Dupliquer",
            "Dupliquer cette feuille de statistiques",
            icon="copy",
        )
        if sheet.active:
            label = "Désactiver"
            title = "Désactiver cette feuille de statistiques"
            icon = "lock"
        else:
            label = "Activer"
            title = "Activer cette feuille de statistiques"
            icon = "lock-open"

        yield POSTButton(
            get_sheet_url(self.request, sheet, _query={"action": "disable"}),
            label,
            title=title,
            icon=icon,
        )
        if not sheet.active:
            yield POSTButton(
                get_sheet_url(self.request, sheet, _query={"action": "delete"}),
                "Supprimer",
                title="Supprimer définitivement",
                icon="trash-alt",
                css="negative",
            )

    def _get_links(self):
        return [
            Link(
                self.request.route_path(
                    STATISTICS_ROUTE,
                    _query=dict(action="add"),
                ),
                "Ajouter",
                "Ajouter une nouvelle feuille de statistiques",
                icon="plus",
            )
        ]

    def __call__(self):
        sheets = StatisticSheet.query()
        sheets = sheets.order_by(desc(StatisticSheet.active)).all()

        return dict(
            title=self.title,
            sheets=sheets,
            links=self._get_links(),
            stream_actions=self.stream_actions,
        )


class SheetAddView(BaseAddView, TreeMixin):
    title = "Ajouter une feuille de statistiques"
    schema = get_sheet_add_edit_schema()
    msg = "La feuille a été ajoutée avec succès"
    factory = StatisticSheet
    route_name = STATISTICS_ROUTE

    def before(self, form):
        BaseAddView.before(self, form)
        self.populate_navigation()

    def redirect(self, appstruct, new_model):
        return HTTPFound(self.request.route_path(STATISTIC_ITEM_ROUTE, id=new_model.id))


class SheetEditView(BaseEditView, TreeMixin):
    title = "Modifier une feuille de statistiques"
    schema = get_sheet_add_edit_schema()
    msg = "La feuille a bien été modifiée"
    route_name = STATISTIC_ITEM_ROUTE

    @property
    def tree_url(self):
        return get_sheet_url(self.request, _query={"action": "edit"})

    def before(self, form):
        BaseEditView.before(self, form)
        self.populate_navigation()

    def redirect(self, appstruct):
        return HTTPFound(
            self.request.route_path(STATISTIC_ITEM_ROUTE, id=self.context.id)
        )


class SheetView(BaseView, TreeMixin, JsAppViewMixin):
    """
    Statistic sheet view
    """

    route_name = STATISTIC_ITEM_ROUTE

    @property
    def title(self):
        return f"{self.context.title}"

    def context_url(self, _query: Dict[str, str] = {}):
        return get_sheet_url(self.request, api=True, _query=_query)

    def more_js_app_options(self):
        return {
            "entries_url": self.request.route_path(
                API_ENTRIES_ROUTE, id=self.context.id
            ),
        }

    def __call__(self):
        self.populate_navigation()
        statistic_resources.need()

        return dict(
            title=self.title,
            js_app_options=self.get_js_app_options(),
        )


class StatisticDisableView(DisableView):
    """
    Sheet Disable view
    """

    enable_msg = "La feuille de statistiques a été activée"
    disable_msg = "La feuille de statistiques a été désactivée"
    redirect_route = STATISTICS_ROUTE


class StatisticDuplicateView(DuplicateView):
    """
    Sheet Duplication view
    """

    message = "Vous avez été redirigé vers la nouvelle feuille de statistique"
    route_name = STATISTIC_ITEM_ROUTE

    def redirect(self, item):
        """
        Default redirect implementation

        :param obj item: The newly created element (flushed)
        :returns: The url to redirect to
        :rtype: str
        """
        return HTTPFound(
            self.request.route_path(
                self.route_name, id=item.id, _query={"action": "edit"}
            )
        )


class StatisticDeleteView(DeleteView):
    """
    Sheet Deletion view
    """

    delete_msg = "La feuille de statistiques a bien été supprimée"
    redirect_route = STATISTICS_ROUTE


class CsvEntryView(UserDatasCsvView):
    """
    The view used to stream a the items matching a statistic entry
    """

    model = UserDatas

    def query(self):
        inspector = get_inspector()
        try:
            query_factory = EntryQueryFactory(UserDatas, self.context, inspector)
            query = query_factory.query()
        except KeyError as exc:
            logger.exception("Error in csv entry view")
            query = None
            self.current_exception = exc
        return query

    @property
    def filename(self):
        filename = "{0}.csv".format(ascii.force_ascii(self.context.title))
        return filename

    def show_error(self, msg: str, show_refresh_button=False) -> dict:
        return {"info_msg": msg}

    def _build_return_value(self, schema, appstruct, query):
        if query is None:
            return {"info_msg": str(self.current_exception)}
        else:
            return UserDatasCsvView._build_return_value(self, schema, appstruct, query)


class CsvSheetView(BaseView):
    """
    Return a csv sheet as a csv response
    """

    @property
    def filename(self):
        return "{0}.csv".format(ascii.force_ascii(self.context.title))

    def __call__(self):
        try:
            query_factory = SheetQueryFactory(UserDatas, self.context, get_inspector())

            writer = csv.CsvExporter()
            writer.set_headers(query_factory.headers)
            for row in query_factory.rows:
                writer.add_row(row)

            write_file_to_request(self.request, self.filename, writer.render())
            return self.request.response
        except KeyError as exc:
            return {"info_msg": str(exc)}


def includeme(config):
    """
    Include views in the app's configuration
    """
    config.add_tree_view(
        SheetListView,
        renderer="statistics/list.mako",
        permission=PERMISSIONS["global.view_userdata_details"],
    )

    config.add_tree_view(
        SheetAddView,
        parent=SheetListView,
        request_param="action=add",
        renderer="caerp:templates/base/formpage.mako",
        layout="default",
        permission=PERMISSIONS["global.view_userdata_details"],
    )
    config.add_tree_view(
        SheetEditView,
        parent=SheetListView,
        request_param="action=edit",
        renderer="caerp:templates/base/formpage.mako",
        layout="default",
        context=StatisticSheet,
        permission=PERMISSIONS["global.view_userdata_details"],
    )

    config.add_tree_view(
        SheetView,
        parent=SheetListView,
        renderer="statistics/edit.mako",
        layout="opa",
        context=StatisticSheet,
        permission=PERMISSIONS["global.view_userdata_details"],
    )

    config.add_view(
        StatisticDisableView,
        route_name=STATISTIC_ITEM_ROUTE,
        request_param="action=disable",
        request_method="POST",
        require_csrf=True,
        context=StatisticSheet,
        permission=PERMISSIONS["global.view_userdata_details"],
    )
    config.add_view(
        StatisticDeleteView,
        route_name=STATISTIC_ITEM_ROUTE,
        request_param="action=delete",
        request_method="POST",
        require_csrf=True,
        context=StatisticSheet,
        permission=PERMISSIONS["global.view_userdata_details"],
    )

    config.add_view(
        StatisticDuplicateView,
        route_name=STATISTIC_ITEM_ROUTE,
        request_param="action=duplicate",
        request_method="POST",
        require_csrf=True,
        context=StatisticSheet,
        permission=PERMISSIONS["global.view_userdata_details"],
    )

    # Csv export views
    config.add_view(
        CsvEntryView,
        route_name=ENTRY_ITEM_CSV_ROUTE,
        renderer="statistics/info.mako",
        context=StatisticEntry,
        permission=PERMISSIONS["global.view_userdata_details"],
    )

    config.add_view(
        CsvSheetView,
        route_name=STATISTIC_ITEM_CSV_ROUTE,
        renderer="statistics/info.mako",
        context=StatisticSheet,
        permission=PERMISSIONS["global.view_userdata_details"],
    )
    config.add_admin_menu(
        parent="userdata",
        order=1,
        label="Statistiques (obsolète)",
        href="/statistics",
        permission=PERMISSIONS["global.view_userdata_details"],
    )
