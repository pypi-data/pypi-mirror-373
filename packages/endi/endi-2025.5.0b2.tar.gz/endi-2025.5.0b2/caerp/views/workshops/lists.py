import colander
import logging
from caerp.consts.permissions import PERMISSIONS
from sqlalchemy import (
    or_,
    and_,
    func,
    distinct,
    not_,
)

from caerp_base.models.base import DBSESSION

from caerp.models.user.user import User
from caerp.models.activity import Attendance
from caerp.models.company import Company
from caerp.models.workshop import (
    WorkshopAction,
    Workshop,
    Timeslot,
    WorkshopTagOption,
)
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.forms.workshop import get_list_schema
from caerp.views import BaseListView

logger = logging.getLogger(__name__)

NAVIGATION_KEY = "/workshops"


class WorkshopListTools:
    """
    Tools for listing workshops
    """

    title = "Liste des ateliers"

    sort_columns = dict(datetime=Workshop.datetime)
    default_sort = "datetime"
    default_direction = "asc"

    def get_schema(self):
        return get_list_schema()

    def query(self):
        query = Workshop.query()
        return query

    def filter_participant(self, query, appstruct):
        participant_id = appstruct.get("participant_id")
        if participant_id not in (None, colander.null):
            logger.debug("Filtering by participant")
            query = query.filter(
                Workshop.attendances.any(Attendance.account_id == participant_id)
            )
        return query

    def filter_info_1_id(self, query, appstruct):
        info_1_id = appstruct.get("info_1_id")
        if info_1_id not in (None, colander.null):
            logger.debug("Filtering by info_1_id")
            query = query.filter(Workshop.info1.has(WorkshopAction.id == info_1_id))
        return query

    def filter_trainer(self, query, appstruct):
        trainer_id = appstruct.get("trainer_id")
        if trainer_id:
            logger.debug("Filtering by trainer")
            query = query.join(Workshop.trainers).filter(
                User.id == trainer_id,
            )
        return query

    def filter_search(self, query, appstruct):
        search = appstruct["search"]
        if search not in (None, colander.null, ""):
            logger.debug("Filtering by search word")
            query = query.filter(Workshop.name.like("%{}%".format(search)))
        return query

    def filter_year(self, query, appstruct):
        year = appstruct.get("year")
        if year not in (None, colander.null, -1):
            logger.debug("Filtering by year")
            query = query.filter(
                Workshop.timeslots.any(
                    func.extract("YEAR", Timeslot.start_time) == year
                )
            )
        return query

    def filter_period(self, query, appstruct):
        date_range = appstruct.get("date_range")
        date_range_start = date_range.get("start")
        date_range_end = date_range.get("end")
        if date_range_start not in (None, colander.null) and date_range_end not in (
            None,
            colander.null,
        ):
            logger.debug("Filtering by date range")
            query = query.filter(
                Workshop.timeslots.any(
                    and_(
                        func.date(Timeslot.start_time) >= date_range_start,
                        func.date(Timeslot.end_time) <= date_range_end,
                    )
                )
            )
        elif date_range_start not in (None, colander.null):
            logger.debug("Filtering by date range start")
            query = query.filter(
                Workshop.timeslots.any(
                    func.date(Timeslot.start_time) >= date_range_start
                )
            )
        elif date_range_end not in (None, colander.null):
            logger.debug("Filtering by date range end")
            query = query.filter(
                Workshop.timeslots.any(func.date(Timeslot.end_time) <= date_range_end)
            )
        return query

    def filter_tags(self, query, appstruct):
        tags = appstruct.get("tags")
        if tags not in (None, colander.null, set()):
            logger.debug("Filtering by tag")
            query = query.filter(Workshop.tags.any(WorkshopTagOption.id.in_(tags)))
        return query

    def filter_notfilled(self, query, appstruct):
        """
        Filter the workshops for which timeslots have not been filled
        """
        notfilled = appstruct.get("notfilled")
        if notfilled not in (None, colander.null, False, "false"):
            logger.debug("Filtering the workshop that where not filled")
            attendance_query = DBSESSION().query(distinct(Attendance.event_id))
            attendance_query = attendance_query.filter(
                Attendance.status != "registered"
            )

            timeslot_ids = [item[0] for item in attendance_query]

            query = query.filter(
                not_(Workshop.timeslots.any(Timeslot.id.in_(timeslot_ids)))
            )
        return query

    def filter_company_manager_or_cae(self, query, appstruct):
        """
        Show all workshops or only CAE workshops (workshops wihtout company
        name)
        """
        company_manager = appstruct.get("company_manager")

        if company_manager not in (colander.null, None):
            if company_manager in (-1, "-1"):
                logger.debug("Company manager is -1")
                query = query.outerjoin(Workshop.company_manager).filter(
                    or_(
                        Workshop.company_manager_id == None,  # noqa: E711
                        Company.internal == True,  # noqa: E712
                    )
                )
            else:
                logger.debug("Company manager is {}".format(company_manager))
                query = query.filter(
                    Workshop.company_manager_id == int(company_manager)
                )
        logger.debug("Company manager is -1")
        return query

    def __call__(self):
        logger.debug("# Calling the list view #")
        logger.debug(" + Collecting the appstruct from submitted datas")
        schema, appstruct = self._collect_appstruct()
        self.appstruct = appstruct
        logger.debug(appstruct)
        logger.debug(" + Launching query")
        query = self.query()
        if query is not None:
            logger.debug(" + Filtering query")
            query = self._filter(query, appstruct)
            logger.debug(query)
            logger.debug(" + Sorting query")
            query = self._sort(query, appstruct)

        logger.debug(" + Getting the current route_name")
        logger.debug(" + Building the return values")
        return self._build_return_value(schema, appstruct, query)


class BaseWorkshopListView(WorkshopListTools, BaseListView):
    add_template_vars = (
        "is_edit_view",
        "stream_actions",
        "current_user_id",
        "stream_main_actions",
        "stream_more_actions",
        "route_name",
    )
    is_edit_view = True
    signup_label = "M'inscrire"
    signout_label = "Me désincrire"
    route_name = None

    def __init__(self, *args, **kwargs):
        super(BaseWorkshopListView, self).__init__(*args, **kwargs)

    @property
    def current_user_id(self):
        return self.request.identity.id

    def _signup_buttons(self, workshop):
        if self.request.has_permission(
            PERMISSIONS["context.signup_workshop"], workshop
        ):
            if workshop.is_participant(self.current_user_id):
                yield POSTButton(
                    self.request.route_path(
                        "workshop",
                        id=workshop.id,
                        _query=dict(action="signout", user_id=self.current_user_id),
                    ),
                    self.signout_label,
                    "{} de cet atelier".format(self.signout_label),
                    icon="times",
                    css="icon negative",
                )
            else:
                yield POSTButton(
                    self.request.route_path(
                        "workshop",
                        id=workshop.id,
                        _query=dict(action="signup", user_id=self.current_user_id),
                    ),
                    self.signup_label,
                    "{} à cet atelier".format(self.signup_label),
                    icon="calendar-alt",
                    css="btn-primary icon",
                )

    def _edit_buttons(self, workshop):
        if self.request.has_permission(PERMISSIONS["context.edit_workshop"], workshop):
            yield Link(
                self.request.route_path(
                    "workshop", id=workshop.id, _query=dict(action="edit")
                ),
                label="Voir/éditer",
                title="Voir / Éditer l'atelier",
                icon="pen",
            )
            yield POSTButton(
                self.request.route_path(
                    "workshop",
                    id=workshop.id,
                    _query=dict(action="delete"),
                ),
                label="Supprimer",
                title="Supprimer définitivement cet atelier",
                confirm="Êtes vous sûr de vouloir supprimer cet atelier ?",
                icon="trash-alt",
                css="icon negative",
            )

    def _view_button(self, workshop):
        if self.request.has_permission(PERMISSIONS["context.view_workshop"], workshop):
            yield Link(
                self.request.route_path("workshop", id=workshop.id),
                label="Voir",
                title="Voir l'atelier",
                icon="arrow-right",
                css="icon",
            )

    def stream_actions(self, workshop):
        yield from self._signup_buttons(workshop)
        yield from self._edit_buttons(workshop)
        if not self.request.has_permission(
            PERMISSIONS["context.edit_workshop"], workshop
        ):
            yield from self._view_button(workshop)

    def stream_main_actions(self):
        if self.request.has_permission(PERMISSIONS["global.manage_workshop"]):
            yield Link(
                self.request.route_path("workshops", _query=dict(action="new")),
                label="Nouvel atelier",
                title="Ajouter un atelier",
                icon="plus",
                css="btn-primary icon",
            )

    def _get_export_url(self, file_format):
        return self.request.route_path(
            self.route_name,
            file_format=file_format,
            _query=self.request.GET,
        )

    def stream_more_actions(self):
        if self.route_name is not None:
            yield Link(
                url=self._get_export_url(".csv"),
                label="Exporter vers CSV",
                title="Exporter vers CSV",
                icon="file-csv",
                css="btn icon_only_mobile",
            )
            yield Link(
                url=self._get_export_url(".xlsx"),
                label="Exporter vers Excel",
                title="Exporter vers Excel",
                icon="file-excel",
                css="btn icon_only_mobile",
            )
            yield Link(
                url=self._get_export_url(".ods"),
                label="Exporter vers ODS",
                title="Exporter vers ODS",
                icon="file-spreadsheet",
                css="btn icon_only_mobile",
            )


class TrainingWorkshopListView(BaseWorkshopListView):
    """
    Vue EA : Liste des formations de la CAE (Ateliers organisés par des enseignes)

    Menu : Formations -> Ateliers
    """

    title = "Tous les ateliers"
    route_name = "workshops{file_format}"


class CaeWorkshopListView(BaseWorkshopListView):
    """
    Vue EA : Liste des ateliers internes de la CAE

    Accompagnement -> Ateliers
    """

    title = "Tous les ateliers de la CAE"
    route_name = "cae_workshops{file_format}"

    def get_schema(self):
        return get_list_schema(company=False, default_company_value=-1, training=False)


class CompanyWorkshopTrainingListView(BaseWorkshopListView):
    """
    Vue ES : Liste des formations organisées au sein d'une enseigne

    Outils métiers -> Organisation d'ateliers
    """

    add_template_vars = BaseWorkshopListView.add_template_vars + (
        "current_users",
        "company_id",
    )
    title = "Organisation d'ateliers"
    route_name = "company_workshops{file_format}"

    def get_schema(self):
        return get_list_schema(company=True)

    def stream_actions(self, workshop):
        yield from self._edit_buttons(workshop)
        if not self.request.has_permission(
            PERMISSIONS["context.edit_workshop"], workshop
        ):
            yield from self._edit_buttons(workshop)

    @property
    def current_user_id(self):
        return None

    @property
    def current_users(self):
        return self.context.employees

    @property
    def company_id(self):
        return self.context.id

    def filter_company_manager_or_cae(self, query, appstruct):
        company = self.context
        employee_ids = company.get_employee_ids()
        query = query.filter(
            or_(
                Workshop.company_manager_id == company.id,
                Workshop.trainers.any(User.id.in_(employee_ids)),
            )
        )
        return query

    def _get_export_url(self, file_format):
        return self.request.route_path(
            self.route_name,
            id=self.company_id,
            file_format=file_format,
            _query=self.request.GET,
        )

    def stream_main_actions(self):
        if self.request.has_permission(PERMISSIONS["context.add_training"]):
            yield Link(
                self.request.route_path(
                    "company_workshops",
                    id=self.company_id,
                    _query=dict(action="new"),
                ),
                label="Nouvel atelier",
                title="Ajouter un atelier",
                icon="plus",
                css="btn-primary icon",
            )


class CompanyWorkshopSubscribedListView(BaseWorkshopListView):
    """
    Liste des ateliers auxquels les membres d'une enseigne sont inscrits

    Gestion -> Mes inscriptions
    """

    add_template_vars = BaseWorkshopListView.add_template_vars + ("current_users",)
    title = "Ateliers auxquels un des membres de l'enseigne est inscrit"
    is_edit_view = False

    def get_schema(self):
        return get_list_schema(company=True)

    @property
    def current_users(self):
        return self.context.employees

    @property
    def current_user_id(self):
        return None

    def stream_actions(self, workshop):
        yield from self._edit_buttons(workshop)
        if not self.request.has_permission(
            PERMISSIONS["context.edit_workshop"], workshop
        ):
            yield from self._view_button(workshop)

    def filter_participant(self, query, appstruct):
        company = self.context
        employees_id = company.get_employee_ids()
        query = query.filter(Workshop.participants.any(User.id.in_(employees_id)))
        return query


class UserWorkshopSubscriptionsListView(BaseWorkshopListView):
    """
    Liste des ateliers auxquels un utilisateur est inscrit ou peut s'inscrire

    List :
        * user's workshops
        * open workshops

    Ateliers
    """

    add_template_vars = BaseWorkshopListView.add_template_vars + ("current_users",)
    is_edit_view = False
    title = "Inscription aux ateliers de la CAE"

    def get_schema(self):
        return get_list_schema(
            company=False, user=True, include_open=True, is_current_user=True
        )

    @property
    def current_users(self):
        return [self.context]

    @property
    def current_user_id(self):
        return self.context.id

    def filter_participant(self, query, appstruct):
        user_id = self.context.id
        onlysubscribed = appstruct.get("onlysubscribed", True)
        # Initial display of this view
        if onlysubscribed == "false":
            onlysubscribed = False

        # Par défaut on veut que les ateliers inscrits si on n'est
        # pas le user courant
        if onlysubscribed:
            query = query.filter(
                Workshop.attendances.any(Attendance.account_id == user_id),
            )
        else:
            logger.debug("Workshops where user is a participant or open")
            query = query.filter(
                or_(
                    Workshop.attendances.any(Attendance.account_id == user_id),
                    Workshop.signup_mode == "open",
                )
            )
        return query


class UserDatasWorkshopSubscribedListView(UserWorkshopSubscriptionsListView):
    """
    View for listing user's workshops as participant dedicated to EA role

    Gestion sociale -> Accompagnement -> Ateliers
    """

    signup_label = "Inscrire l'utilisateur"
    signout_label = "Désinscrire l'utilisateur"

    def get_schema(self):
        return get_list_schema(
            company=False, user=True, include_open=True, is_current_user=False
        )

    @property
    def title(self):
        return "Ateliers auxquels {} assiste".format(self.context.label)

    def stream_actions(self, workshop):
        yield from self._view_button(workshop)
        yield from self._signup_buttons(workshop)

    def filter_participant(self, query, appstruct):
        user_id = self.context.id
        onlysubscribed = appstruct.get("onlysubscribed", True)
        if onlysubscribed:
            query = query.filter(
                Workshop.attendances.any(Attendance.account_id == user_id),
            )
        else:
            query = super().filter_participant(query, appstruct)
        return query


def includeme(config):
    # Vue EA
    config.add_view(
        CaeWorkshopListView,
        route_name="cae_workshops",
        permission=PERMISSIONS["global.manage_workshop"],
        renderer="/workshops/workshops.mako",
    )

    config.add_view(
        TrainingWorkshopListView,
        route_name="workshops",
        renderer="/workshops/workshops.mako",
        permission=PERMISSIONS["global.manage_workshop"],
    )

    config.add_view(
        CompanyWorkshopSubscribedListView,
        route_name="company_workshops_subscribed",
        renderer="/workshops/workshops.mako",
        context=Company,
        permission=PERMISSIONS["global.manage_workshop"],
    )
    config.add_view(
        UserDatasWorkshopSubscribedListView,
        route_name="user_workshops_subscribed",
        renderer="/workshops/user_workshops.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["global.manage_workshop"],
    )

    # Vue ES
    config.add_view(
        UserWorkshopSubscriptionsListView,
        route_name="user_workshop_subscriptions",
        renderer="/workshops/workshops.mako",
        context=User,
        permission=PERMISSIONS["context.view_user"],
    )

    # Vue ES Formateur
    config.add_view(
        CompanyWorkshopTrainingListView,
        route_name="company_workshops",
        renderer="/workshops/workshops.mako",
        context=Company,
        permission=PERMISSIONS["context.view_training"],
    )
