import logging
import operator

from caerp.consts.permissions import PERMISSIONS
from caerp.models.services.user import UserPrefsService
from caerp.views import BaseView


logger = logging.getLogger(__name__)


class DataQueryListView(BaseView):
    """
    Liste des requêtes statistiques
    """

    title = "Requêtes statistiques"

    def is_favorite(self, query_name):
        favorites = UserPrefsService.get(self.request, "dataqueries_favorite")
        if favorites:
            return query_name in favorites
        else:
            return False

    def set_favorite_state(self, query_name, state):
        favorites = UserPrefsService.get(self.request, "dataqueries_favorite")
        if favorites:
            if state == "1" and query_name not in favorites:
                favorites.append(query_name)
            if state == "0" and query_name in favorites:
                favorites.remove(query_name)
        elif state == "1":
            favorites = [
                query_name,
            ]
        UserPrefsService.set(self.request, "dataqueries_favorite", favorites)
        return True

    def is_hidden(self, query_name):
        hidden = UserPrefsService.get(self.request, "dataqueries_hidden")
        if hidden:
            return query_name in hidden
        else:
            return False

    def set_hidden_state(self, query_name, state):
        hidden = UserPrefsService.get(self.request, "dataqueries_hidden")
        if hidden:
            if state == "1" and query_name not in hidden:
                hidden.append(query_name)
            if state == "0" and query_name in hidden:
                hidden.remove(query_name)
        elif state == "1":
            hidden = [
                query_name,
            ]
        UserPrefsService.set(self.request, "dataqueries_hidden", hidden)
        return True

    def get_dataqueries(self):
        queries = []
        for query in self.request.get_dataqueries():
            queries.append(
                dict(
                    name=query.name,
                    label=query.label,
                    descr=query.description,
                    favorite=self.is_favorite(query.name),
                    hidden=self.is_hidden(query.name),
                )
            )
        queries.sort(key=operator.itemgetter("label"))
        return queries

    def __call__(self):
        if "query" in self.request.GET:
            if "favorite" in self.request.GET:
                self.set_favorite_state(
                    self.request.GET["query"],
                    self.request.GET["favorite"],
                )
            if "hidden" in self.request.GET:
                self.set_hidden_state(
                    self.request.GET["query"], self.request.GET["hidden"]
                )

        dataqueries = self.get_dataqueries()

        return dict(
            title=self.title,
            queries=dataqueries,
        )


def includeme(config):
    config.add_route("dataqueries", "dataqueries")
    config.add_view(
        DataQueryListView,
        route_name="dataqueries",
        renderer="dataqueries/queries_list.mako",
        permission=PERMISSIONS["global.view_dataquery"],
    )
