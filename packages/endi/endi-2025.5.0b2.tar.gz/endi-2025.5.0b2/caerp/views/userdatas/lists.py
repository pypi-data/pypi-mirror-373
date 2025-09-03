import logging
import colander

from caerp.consts.permissions import PERMISSIONS
from sqlalchemy import (
    or_,
    distinct,
)

from caerp_celery.models import FileGenerationJob
from caerp_celery.tasks.export import export_to_file

from caerp.forms.user.userdatas import get_list_schema
from caerp.models.user import User
from caerp.models.user.userdatas import (
    AntenneOption,
    CaeSituationOption,
    UserDatas,
    CompanyDatas,
)
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.views import AsyncJobMixin, BaseListView
from caerp.views.userdatas.routes import (
    USERDATAS_URL,
    USERDATAS_XLS_URL,
    USERDATAS_CSV_URL,
    USERDATAS_ODS_URL,
    USER_USERDATAS_URL,
)


logger = logging.getLogger(__name__)


class UserDatasListClass:
    title = "Liste des informations sociales"
    schema = get_list_schema()
    sort_columns = dict(
        lastname=UserDatas.coordonnees_lastname,
        antenna=AntenneOption.label,
        situation=CaeSituationOption.label,
        follower=User.lastname,
        updated_at=UserDatas.updated_at,
    )
    default_sort = "lastname"

    def query(self):
        return (
            UserDatas.query()
            .outerjoin(
                AntenneOption, UserDatas.situation_antenne_id == AntenneOption.id
            )
            .outerjoin(
                CaeSituationOption,
                UserDatas.situation_situation_id == CaeSituationOption.id,
            )
            .outerjoin(User, UserDatas.situation_follower_id == User.id)
            .with_entities(UserDatas)
        )

    def filter_search(self, query, appstruct):
        search = appstruct.get("search")
        if search not in (None, "", colander.null):
            filter_ = "%" + search + "%"
            query = query.filter(
                or_(
                    UserDatas.coordonnees_firstname.like(filter_),
                    UserDatas.coordonnees_lastname.like(filter_),
                    UserDatas.activity_companydatas.any(
                        CompanyDatas.name.like(filter_)
                    ),
                    UserDatas.activity_companydatas.any(
                        CompanyDatas.title.like(filter_)
                    ),
                )
            )
        return query

    def filter_situation_situation(self, query, appstruct):
        situation = appstruct.get("situation_situation")
        if situation not in (None, "", colander.null):
            query = query.filter(UserDatas.situation_situation_id == situation)
        return query

    def filter_situation_follower_id(self, query, appstruct):
        follower_id = appstruct.get("situation_follower_id")
        if follower_id not in (None, -1, colander.null):
            query = query.filter(UserDatas.situation_follower_id == follower_id)
        return query

    def filter_situation_antenne_id(self, query, appstruct):
        antenne_id = appstruct.get("situation_antenne_id")
        if antenne_id not in (None, -1, colander.null):
            query = query.filter(UserDatas.situation_antenne_id == antenne_id)
        return query


class UserDatasListView(UserDatasListClass, BaseListView):
    add_template_vars = (
        "stream_actions",
        "is_multi_antenna_server",
        "get_edit_url",
    )

    @property
    def is_multi_antenna_server(self):
        return AntenneOption.query().count() > 1

    def get_edit_url(self, item: UserDatas):
        return self.request.route_path(USER_USERDATAS_URL, id=item.user_id)

    def stream_actions(self, item: UserDatas):
        yield Link(
            self.get_edit_url(item),
            "Voir",
            title="Voir / Modifier les données de gestion sociale",
            icon="pen",
            css="icon",
        )
        if self.request.has_permission(PERMISSIONS["global.view_userdata"]):
            yield POSTButton(
                self.request.route_path(
                    USER_USERDATAS_URL, id=item.user_id, _query={"action": "delete"}
                ),
                "Supprimer",
                title="Supprimer la fiche de gestion sociale",
                icon="trash-alt",
                css="icon negative",
                confirm="En supprimant cette fiche de "
                "gestion sociale, vous supprimerez également \n"
                "les données associées (documents sociaux, "
                "parcours, historiques…). \n\nContinuer ?",
            )


class UserDatasXlsView(
    AsyncJobMixin,
    UserDatasListClass,
    BaseListView,
):
    model = UserDatas
    file_format = "xlsx"
    filename = "gestion_sociale_"

    def query(self):
        return self.request.dbsession.query(distinct(UserDatas.id))

    def _build_return_value(self, schema, appstruct, query):
        all_ids = [elem[0] for elem in query]
        if not all_ids:
            msg = "Il n'y a aucun élément à exporter"
            return self.show_error(msg)

        celery_error_resp = self.is_celery_alive()
        if celery_error_resp:
            return celery_error_resp

        job_result = self.initialize_job_result(FileGenerationJob)
        celery_job = export_to_file.delay(
            job_result.id, "userdatas", all_ids, self.filename, self.file_format
        )
        return self.redirect_to_job_watch(celery_job, job_result)


class UserDatasOdsView(UserDatasXlsView):
    file_format = "ods"


class UserDatasCsvView(UserDatasXlsView):
    file_format = "csv"


def includeme(config):
    config.add_view(
        UserDatasListView,
        route_name=USERDATAS_URL,
        renderer="/userdatas/list.mako",
        permission=PERMISSIONS["global.view_userdata"],
    )
    config.add_view(
        UserDatasXlsView,
        route_name=USERDATAS_XLS_URL,
        permission=PERMISSIONS["global.view_userdata_details"],
    )
    config.add_view(
        UserDatasOdsView,
        route_name=USERDATAS_ODS_URL,
        permission=PERMISSIONS["global.view_userdata_details"],
    )
    config.add_view(
        UserDatasCsvView,
        route_name=USERDATAS_CSV_URL,
        permission=PERMISSIONS["global.view_userdata_details"],
    )

    config.add_admin_menu(
        parent="userdata", order=0, label="Consulter", href="/userdatas"
    )
