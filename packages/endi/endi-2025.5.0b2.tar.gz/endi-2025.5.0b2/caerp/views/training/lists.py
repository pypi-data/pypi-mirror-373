import logging

from caerp.consts.permissions import PERMISSIONS
from caerp.models.user.user import User
from caerp.forms.training.trainer import get_list_schema

from caerp.views.user.lists import BaseUserListView
from caerp.views.training.routes import TRAINER_LIST_URL


logger = logging.getLogger(__name__)


class TrainerListView(BaseUserListView):
    """
    View listing Trainers
    """

    title = "Liste des formateurs de la CAE (qui ont une fiche formateur)"

    def get_schema(self):
        return get_list_schema()

    def filter_trainer(self, query, appstruct):
        query = query.join(User.trainerdatas)
        return query


def includeme(config):
    config.add_view(
        TrainerListView,
        route_name=TRAINER_LIST_URL,
        renderer="/training/list_trainers.mako",
        permission=PERMISSIONS["global.authenticated"],
    )
