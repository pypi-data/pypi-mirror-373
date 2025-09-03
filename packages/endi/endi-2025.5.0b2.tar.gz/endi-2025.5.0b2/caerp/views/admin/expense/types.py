import os
import datetime
from sqlalchemy import distinct
from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.compute.math_utils import convert_to_int
from caerp.models.expense.types import (
    ExpenseType,
    ExpenseKmType,
    ExpenseTelType,
)

from caerp.resources import admin_expense_types_js
from caerp.utils.widgets import (
    Link,
    POSTButton,
)

from caerp.views import (
    BaseView,
    TreeMixin,
)
from caerp.forms.admin.expense_type import (
    get_expense_type_schema,
    get_expense_kmtype_schema,
    get_expense_teltype_schema,
)
from caerp.views.admin.expense import (
    ExpenseIndexView,
    EXPENSE_URL,
)
from caerp.views.admin.tools import (
    AdminCrudListView,
    BaseAdminDisableView,
    BaseAdminAddView,
    BaseAdminEditView,
)


EXPENSE_BASETYPE_URL = os.path.join(EXPENSE_URL, "expense")
EXPENSE_BASETYPE_ITEM_URL = os.path.join(EXPENSE_BASETYPE_URL, "{id}")
EXPENSE_TEL_URL = os.path.join(EXPENSE_URL, "expensetel")
EXPENSE_TEL_ITEM_URL = os.path.join(EXPENSE_TEL_URL, "{id}")
EXPENSE_KM_INDEX_URL = os.path.join(EXPENSE_URL, "expensekm")
EXPENSE_KM_URL = os.path.join(EXPENSE_KM_INDEX_URL, "{year}")
EXPENSE_KM_ITEM_URL = os.path.join(EXPENSE_KM_URL, "{id}")


def _get_year_from_request(request):
    """
    Retrieve the current year from the request
    Usefull for ExpenseKmType edition

    :param obj request: The Pyramid request object
    :returns: A year
    :rtype: int
    """
    return convert_to_int(request.matchdict["year"], datetime.date.today().year)


class ExpenseTypeJSMixin:
    def before(self, form):
        super().before(form)
        admin_expense_types_js.need()


class ExpenseKmTypesIndexView(BaseView, TreeMixin):
    """
    Entry point to the km expense types configuration
    """

    title = "Types de dépenses kilométriques"
    description = "Configurer les types de dépenses kilométriques par année"
    route_name = EXPENSE_KM_INDEX_URL
    permission = PERMISSIONS["global.config_accounting"]

    def _get_year_options(self):
        """
        Return the year selection options to be provided
        """
        years = [
            a[0]
            for a in self.request.dbsession.query(distinct(ExpenseKmType.year))
            if a[0]
        ]
        today = datetime.date.today()
        years.append(today.year)
        years.append(today.year + 1)

        years = list(set(years))
        years.sort()
        return years

    def __call__(self):
        self.populate_navigation()
        return dict(
            title=self.title,
            years=self._get_year_options(),
            admin_path=EXPENSE_KM_URL,
        )


class ExpenseTypeListView(AdminCrudListView):
    title = "Types de dépenses"
    route_name = EXPENSE_BASETYPE_URL
    columns = [
        "Catégorie",
        "Libellé",
        "Compte de charge",
        "TVA sur marge",
        "Code TVA",
        "Compte de TVA déductible",
        "Contribution",
        "Facturation Interne",
    ]
    factory = ExpenseType
    item_route = EXPENSE_BASETYPE_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]

    def stream_columns(self, expense_type):
        """
        Stream a column object (called from within the template)

        :param obj expense_type: The object to display
        :returns: A generator of labels representing the different columns of
        our list
        :rtype: generator
        """
        if expense_type.category == "1":
            yield "Frais"
        elif expense_type.category == "2":
            yield "Achats"
        else:
            yield "Frais + Achats"

        yield expense_type.label or "Non renseigné"
        yield expense_type.code or "Aucun"
        if expense_type.tva_on_margin:
            yield "Oui"
        else:
            yield "Non"
        yield expense_type.code_tva or "Aucun"
        yield expense_type.compte_tva or "Aucun"
        if expense_type.contribution:
            yield "Oui"
        else:
            yield "Non"
        if expense_type.internal:
            yield "Oui"
        else:
            yield "Non"

    @classmethod
    def get_type(cls):
        return cls.factory.__mapper_args__["polymorphic_identity"]

    def _get_item_url(self, expense_type, action=None):
        """
        shortcut for route_path calls
        """
        query = dict(self.request.GET)
        if action is not None:
            query["action"] = action

        return self.request.route_path(
            self.item_route, id=expense_type.id, _query=query, **self.request.matchdict
        )

    def stream_actions(self, expense_type):
        """
        Stream the actions available for the given expense_type object
        :param obj expense_type: ExpenseType instance
        :returns: List of 4-uples (url, label, title, icon,)
        """
        yield Link(
            self._get_item_url(expense_type), "Voir/Modifier", icon="pen", css="icon"
        )
        move_url = self._get_item_url(expense_type, action="move")
        if expense_type.active:
            if expense_type.order > 0:
                yield POSTButton(
                    move_url + "&direction=up",
                    "Remonter",
                    title="Remonter dans l'ordre de présentation",
                    icon="arrow-up",
                    css="icon",
                )
            if expense_type.order < self.max_order:
                yield POSTButton(
                    move_url + "&direction=down",
                    "Redescendre",
                    title="Redescendre dans l'ordre de présenation",
                    icon="arrow-down",
                    css="icon",
                )

            yield POSTButton(
                self._get_item_url(expense_type, action="disable"),
                "Désactiver",
                title="Le type de dépense n’apparaitra plus dans l’interface",
                icon="lock",
                css="icon",
            )
        else:
            yield POSTButton(
                self._get_item_url(expense_type, action="disable"),
                "Activer",
                title="Le type de dépense apparaitra dans l’interface",
                icon="lock-open",
                css="icon",
            )

    def load_items(self, year=None):
        """
        Return the sqlalchemy models representing current queried elements
        :rtype: SQLAlchemy.Query object
        """
        items = (
            self.factory.query()
            .filter(self.factory.type == self.get_type())
            .order_by(self.factory.active.desc())
            .order_by(self.factory.order.asc())
        )
        self.max_order = self.factory.get_next_order() - 1
        return items

    def get_addurl(self):
        """
        Return the url for the add view

        :returns: The url to access the add form
        :rtype: str
        """
        query = dict(self.request.GET)
        query["action"] = "add"

        return self.request.current_route_path(_query=query, **self.request.matchdict)


def move_view(context, request):
    """
    Reorder the current context moving it up in the category's hierarchy

    :param obj context: The given ExpenseType  instance
    """
    action = request.params["direction"]
    if action == "up":
        context.move_up()
    else:
        context.move_down()

    if type(context) is ExpenseKmType:
        return HTTPFound(
            request.route_path(EXPENSE_KM_URL, year=_get_year_from_request(request))
        )
    elif type(context) is ExpenseTelType:
        return HTTPFound(EXPENSE_TEL_URL)
    return HTTPFound(request.route_path(EXPENSE_BASETYPE_URL))


class ExpenseKmTypeListView(ExpenseTypeListView):
    columns = [
        "Catégorie",
        "Libellé",
        "Compte de charge",
        "Indemnité kilométrique",
        "TVA sur marge",
        "Code TVA",
        "Compte de TVA déductible",
        "Contribution",
        "Facturation Interne",
    ]
    route_name = EXPENSE_KM_URL

    factory = ExpenseKmType
    item_route = EXPENSE_KM_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]

    @property
    def title(self):
        title = (
            "Configuration des types de dépenses kilométriques pour "
            "l'année {0}".format(_get_year_from_request(self.request))
        )
        return title

    @property
    def tree_url(self):
        return self.request.route_path(
            EXPENSE_KM_URL, year=_get_year_from_request(self.request)
        )

    def load_items(self, year=None):
        """
        Load the items we will display

        :returns: A SQLAlchemy query
        """
        query = ExpenseTypeListView.load_items(self)
        if year is None:
            year = _get_year_from_request(self.request)
        query = query.filter_by(year=year).order_by(self.factory.active.desc())
        return query

    def stream_columns(self, expense_type):
        if expense_type.category == "1":
            yield "Frais"
        elif expense_type.category == "2":
            yield "Achats"
        else:
            yield "Frais + Achats"

        yield expense_type.label or "Non renseigné"
        yield expense_type.code or "Aucun"
        yield "%s €/km" % (expense_type.amount or 0)
        if expense_type.tva_on_margin:
            yield "Oui"
        else:
            yield "Non"
        yield expense_type.code_tva or "Aucun"
        yield expense_type.compte_tva or "Aucun"
        if expense_type.contribution:
            yield "Oui"
        else:
            yield "Non"
        if expense_type.internal:
            yield "Oui"
        else:
            yield "Non"

    def stream_actions(self, expense_type):
        """
        Stream the actions available for the given expense_type object
        :param obj expense_type: ExpenseType instance
        :returns: List of 4-uples (url, label, title, icon,)
        """
        yield Link(
            self._get_item_url(expense_type), "Voir/Modifier", icon="pen", css="icon"
        )
        if expense_type.active:
            yield POSTButton(
                self._get_item_url(expense_type, action="disable"),
                "Désactiver",
                title="La TVA n’apparaitra plus dans l’interface",
                icon="lock",
                css="icon",
            )
        else:
            yield POSTButton(
                self._get_item_url(expense_type, action="disable"),
                "Activer",
                title="La TVA apparaitra dans l’interface",
                icon="lock-open",
                css="icon",
            )

    def _get_duplicate_url(self):
        """
        Return the duplication url
        """
        return self.request.current_route_path(_query={"action": "duplicate"})

    def _get_duplicate_from_previous_url(self):
        """
        Return the duplicate from previous url
        """
        return self.request.current_route_path(
            _query={"action": "duplicate", "from_previous": "1"}
        )

    def get_actions(self, items):
        """
        Return the description of additionnal main actions buttons

        :rtype: generator
        """
        current_year = datetime.date.today().year
        year = _get_year_from_request(self.request)

        # if we've got datas and we're not in the last year
        if len(items) > 0 and year != current_year + 1:
            if self.load_items(year + 1).count() > 0:
                confirm = (
                    "Tous les types de dépense présentés ici seront "
                    "copiés vers l'année {}. Des frais sont déjà configurés "
                    "sur cette année."
                    " Voulez-vous continuer ?".format(year + 1)
                )
            else:
                confirm = None
            yield POSTButton(
                self._get_duplicate_url(),
                label="Dupliquer vers l’année suivante " "(%s)" % (year + 1),
                title="Dupliquer cette grille vers l’année suivante",
                icon="copy",
                css="btn",
                confirm=confirm,
            )

        # If previous year there were some datas configured
        if self.load_items(year - 1).count() > 0:
            yield POSTButton(
                self._get_duplicate_from_previous_url(),
                label="Recopier l’année précédente " "(%s)" % (year - 1),
                title="Recopier la grille de l’année précédente ici",
                icon="copy",
                css="btn",
                confirm="Tous les types de dépense de l’année précédente seront "
                "recopiés ici. Voulez-vous continuer ?",
            )


class ExpenseTelTypeListView(ExpenseTypeListView):
    title = "Types de dépenses téléphoniques"
    description = "Configurer des types spécifiques donnant lieu à un \
remboursement en pourcentage de la dépense déclarée"
    route_name = EXPENSE_TEL_URL
    columns = [
        "Catégorie",
        "Libellé",
        "Compte de charge",
        "Pourcentage indemnisé",
        "TVA sur marge",
        "Code TVA",
        "Compte de TVA déductible",
        "Contribution",
        "Facturation Interne",
    ]

    factory = ExpenseTelType
    item_route = EXPENSE_TEL_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]

    def stream_columns(self, expense_type):
        if expense_type.category == "1":
            yield "Frais"
        elif expense_type.category == "2":
            yield "Achats"
        else:
            yield "Frais + Achats"

        yield expense_type.label or "Non renseigné"
        yield expense_type.code or "Aucun"
        yield "%s %%" % (expense_type.percentage or 0)
        if expense_type.tva_on_margin:
            yield "Oui"
        else:
            yield "Non"
        yield expense_type.code_tva or "Aucun"
        yield expense_type.compte_tva or "Aucun"
        if expense_type.contribution:
            yield "Oui"
        else:
            yield "Non"
        if expense_type.internal:
            yield "Oui"
        else:
            yield "Non"


class ExpenseTypeDisableView(BaseAdminDisableView):
    disable_msg = "L'élément a bien été désactivé"
    enable_msg = "L'élément a bien été activé"
    factory = ExpenseType
    route_name = EXPENSE_BASETYPE_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]

    @classmethod
    def get_type(cls):
        return cls.factory.__mapper_args__["polymorphic_identity"]


class ExpenseKmTypeDisableView(ExpenseTypeDisableView):
    factory = ExpenseKmType
    route_name = EXPENSE_KM_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]


class ExpenseTelTypeDisableView(ExpenseTypeDisableView):
    factory = ExpenseTelType
    route_name = EXPENSE_TEL_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]


class ExpenseTypeAddView(ExpenseTypeJSMixin, BaseAdminAddView):
    title = "Ajouter"
    factory = ExpenseType
    schema = get_expense_type_schema()
    route_name = EXPENSE_BASETYPE_URL
    permission = PERMISSIONS["global.config_accounting"]

    @classmethod
    def get_type(cls):
        return cls.factory.__mapper_args__["polymorphic_identity"]


class ExpenseKmTypeAddView(ExpenseTypeAddView):
    """
    View used to add Expense Km types
    Custom methods are added here to keep the year param in the url and in the
    form
    """

    factory = ExpenseKmType
    schema = get_expense_kmtype_schema()
    route_name = EXPENSE_KM_URL
    permission = PERMISSIONS["global.config_accounting"]

    def before(self, form):
        super().before(form)
        form.set_appstruct({"year": _get_year_from_request(self.request)})


class ExpenseTelTypeAddView(ExpenseTypeAddView):
    factory = ExpenseTelType
    schema = get_expense_teltype_schema()
    route_name = EXPENSE_TEL_URL
    permission = PERMISSIONS["global.config_accounting"]


class ExpenseTypeEditView(ExpenseTypeJSMixin, BaseAdminEditView):
    title = "Modifier"
    schema = get_expense_type_schema()
    factory = ExpenseType
    route_name = EXPENSE_BASETYPE_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]

    @classmethod
    def get_type(cls):
        return cls.factory.__mapper_args__["polymorphic_identity"]


class ExpenseKmTypeEditView(ExpenseTypeEditView):
    factory = ExpenseKmType
    schema = get_expense_kmtype_schema()
    route_name = EXPENSE_KM_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]


class ExpenseTelTypeEditView(ExpenseTypeEditView):
    factory = ExpenseTelType
    schema = get_expense_teltype_schema()
    route_name = EXPENSE_TEL_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]


class ExpenseKmTypesDuplicateView(BaseView):
    """
    Expense km list Duplication view

    Allows to duplicate :
        to next (default)

        from previous (if 'from_previous' is set in the GET params
    """

    route_name = EXPENSE_KM_URL
    permission = PERMISSIONS["global.config_accounting"]

    def load_items(self, year):
        query = ExpenseKmType.query().filter_by(active=True)
        return query.filter_by(year=year)

    def __call__(self):
        if "from_previous" in self.request.GET:
            new_year = _get_year_from_request(self.request)
            year = new_year - 1
            msg = "Les données ont bien été réprises"
        else:
            year = _get_year_from_request(self.request)
            new_year = year + 1
            msg = "Vous avez été redirigé vers la grille des frais de " "l'année %s" % (
                new_year,
            )

        for item in self.load_items(year):
            new_item = item.duplicate(new_year)
            self.request.dbsession.merge(new_item)
        self.request.session.flash(msg)
        return HTTPFound(self.request.current_route_path(_query={}, year=new_year))


def add_routes(config):
    """
    Add the routes related to the current module
    """
    config.add_route(EXPENSE_BASETYPE_URL, EXPENSE_BASETYPE_URL)
    config.add_route(
        EXPENSE_BASETYPE_ITEM_URL,
        EXPENSE_BASETYPE_ITEM_URL,
        traverse="/expense_types/{id}",
    )
    config.add_route(EXPENSE_TEL_URL, EXPENSE_TEL_URL)
    config.add_route(
        EXPENSE_TEL_ITEM_URL,
        EXPENSE_TEL_ITEM_URL,
        traverse="/expense_types/{id}",
    )

    config.add_route(EXPENSE_KM_INDEX_URL, EXPENSE_KM_INDEX_URL)
    config.add_route(EXPENSE_KM_URL, EXPENSE_KM_URL)
    config.add_route(
        EXPENSE_KM_ITEM_URL,
        EXPENSE_KM_ITEM_URL,
        traverse="/expense_types/{id}",
    )


def includeme(config):
    add_routes(config)
    # BASE TYPES
    config.add_admin_view(
        ExpenseTypeListView,
        parent=ExpenseIndexView,
        renderer="admin/crud_list.mako",
    )
    config.add_admin_view(
        ExpenseTypeAddView,
        parent=ExpenseTypeListView,
        request_param="action=add",
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        ExpenseTypeEditView,
        parent=ExpenseTypeListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        ExpenseTypeDisableView,
        parent=ExpenseTypeListView,
        request_param="action=disable",
        request_method="POST",
        require_csrf=True,
    )
    config.add_admin_view(
        move_view,
        route_name=EXPENSE_BASETYPE_ITEM_URL,
        request_param="action=move",
        request_method="POST",
        require_csrf=True,
    )

    # TEL TYPES
    config.add_admin_view(
        ExpenseTelTypeListView,
        parent=ExpenseIndexView,
        renderer="admin/crud_list.mako",
    )
    config.add_admin_view(
        ExpenseTelTypeAddView,
        parent=ExpenseTelTypeListView,
        request_param="action=add",
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        ExpenseTelTypeEditView,
        parent=ExpenseTelTypeListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        ExpenseTelTypeDisableView,
        parent=ExpenseTelTypeListView,
        request_param="action=disable",
        request_method="POST",
        require_csrf=True,
    )
    config.add_admin_view(
        move_view,
        route_name=EXPENSE_TEL_ITEM_URL,
        request_param="action=move",
        request_method="POST",
        require_csrf=True,
    )

    # KMTYPES
    config.add_admin_view(
        ExpenseKmTypesIndexView,
        parent=ExpenseIndexView,
        renderer="admin/expense_km_index.mako",
    )

    config.add_admin_view(
        ExpenseKmTypesDuplicateView,
        request_param="action=duplicate",
        request_method="POST",
        require_csrf=True,
    )
    config.add_admin_view(
        ExpenseKmTypeListView,
        parent=ExpenseKmTypesIndexView,
        renderer="admin/crud_list.mako",
    )
    config.add_admin_view(
        ExpenseKmTypeAddView,
        parent=ExpenseKmTypeListView,
        request_param="action=add",
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        ExpenseKmTypeEditView,
        parent=ExpenseKmTypeListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        ExpenseKmTypeDisableView,
        parent=ExpenseKmTypeListView,
        request_param="action=disable",
        request_method="POST",
        require_csrf=True,
    )
