import logging

from caerp.consts.permissions import PERMISSIONS
from pyramid.csrf import get_csrf_token

from caerp.statistics import (
    STATISTIC_FILTER_OPTIONS,
    get_inspector,
)

from caerp.models.statistics import (
    StatisticSheet,
    StatisticEntry,
    StatisticCriterion,
)
from caerp.forms.statistics import (
    get_criterion_add_edit_schema,
    get_entry_add_edit_schema,
    get_sheet_add_edit_schema,
)
from caerp.views import BaseRestView

from .routes import (
    get_sheet_url,
    API_ITEM_ROUTE,
    API_ENTRIES_ROUTE,
    API_ENTRY_ITEM_ROUTE,
    API_CRITERIA_ROUTE,
    API_CRITERION_ITEM_ROUTE,
)


logger = logging.getLogger(__name__)


class RestStatisticSheet(BaseRestView):
    """
    Json rest api for statistic sheet handling
    """

    schema = get_sheet_add_edit_schema()

    def collection_get(self):
        return StatisticSheet.query().all()

    def load_manytoone(self, inspector, res=None):
        """
        Return the opt rel options
        """
        if res is None:
            res = {}

        for key, column in inspector.columns.items():
            if column["type"] == "manytoone":
                rel_class = column["related_class"]
                formatter = column.get("formatter")
                if formatter is None:
                    related_key = column.get("related_key", "label")

                    def formatter(option):
                        return getattr(option, related_key, "Inconnu")

                related_key = column.get("related_key", "label")
                res[key] = [
                    {
                        "label": formatter(option),
                        "id": option.id,
                        "value": str(option.id),
                    }
                    for option in rel_class.query()
                ]
            elif column["type"] == "onetomany":
                self.load_manytoone(column["inspector"], res)
        return res

    def load_static_options(self, inspector, res=None):
        """
        Return the options for static selectable elements
        """
        if res is None:
            res = {}
        for key, column in list(inspector.columns.items()):
            if column["type"] == "static_opt" and "options" in column:
                # It's a string column
                res[key] = [
                    {
                        "label": option[1],
                        "value": option[0],
                    }
                    for option in column["options"]
                ]
            elif column["type"] == "onetomany":
                self.load_static_options(column["inspector"], res)
        return res

    def _collect_form_actions(self):
        """
        collect the 'more' actions we want to display to the end
        user (csv, duplicate)
        """
        result = []
        url = get_sheet_url(self.request, _query={"action": "edit"})
        result.append(
            {
                "widget": "anchor",
                "option": {
                    "url": url,
                    "title": "Renommer cette feuille de statistiques",
                    "css": "btn icon only",
                    "icon": "pen",
                },
            }
        )

        url = get_sheet_url(self.request, suffix=".csv")
        result.append(
            {
                "widget": "anchor",
                "option": {
                    "url": url,
                    "title": "Extraire les données au format CSV",
                    "css": "btn icon only",
                    "icon": "file-csv",
                    "popup": True,
                },
            }
        )
        url = get_sheet_url(self.request, _query={"action": "duplicate"})
        result.append(
            {
                "widget": "POSTButton",
                "option": {
                    "url": url,
                    "title": "Dupliquer cette feuille de statistiques",
                    "css": "btn icon only",
                    "icon": "copy",
                },
            }
        )
        return {
            "more": result,
        }

    def load_sheet_list(self):
        query = StatisticSheet.query()
        query = query.filter(StatisticSheet.active == True)  # noqa:E712
        query = query.filter(StatisticSheet.id != self.context.id)
        result = query.all()
        result.insert(0, self.context)
        return result

    def _collect_form_options(self):
        """
        Collect form data options
        """
        inspector = get_inspector()
        json_repr = inspector.__json__(self.request)
        return dict(
            columns=json_repr,
            manytoone_options=self.load_manytoone(inspector),
            static_opt_options=self.load_static_options(inspector),
            methods=STATISTIC_FILTER_OPTIONS,
            csrf_token=get_csrf_token(self.request),
            sheet_list=self.load_sheet_list(),
        )

    def form_config(self):
        return dict(
            options=self._collect_form_options(),
            actions=self._collect_form_actions(),
        )


class RestStatisticEntry(BaseRestView):
    """
    Json rest api for statistic entries handling
    """

    schema = get_entry_add_edit_schema()

    def collection_get(self):
        """
        Return the list of entries
        context is the parent sheet
        """
        logger.debug("# Getting the entries ")
        logger.debug(self.context)
        logger.debug(self.context.entries)
        return self.context.entries

    def post_format(self, entry, edit, attributes):
        if not edit:
            entry.sheet = self.context
            entry.criteria.append(StatisticCriterion(type="and"))
        return entry

    def duplicate_view(self):
        assert "sheet_id" in self.request.json_body
        sheet_id = self.request.json_body["sheet_id"]
        sheet = StatisticSheet.get(sheet_id)

        # On s'assure de ne pas avoir des entrées en double
        title = self.context.title
        index = 1
        while sheet.has_entry(title):
            title = "{} ({})".format(self.context.title, index)
            index += 1

        new_entry = self.context.duplicate(sheet_id=sheet.id)
        new_entry.title = title
        self.dbsession.add(new_entry)
        self.dbsession.flush()
        return new_entry


class RestStatisticCriterion(BaseRestView):
    """
    Api rest pour la gestion des critères statistiques
    """

    def get_schema(self, submitted):
        logger.debug("Looking for a schema : %s" % submitted)
        if "type" in submitted:
            model_type = submitted["type"]
        elif isinstance(self.context, StatisticCriterion):
            model_type = self.context.type

        schema = get_criterion_add_edit_schema(model_type)
        return schema

    def collection_get(self):
        """
        Return the list of top level criteria (not those combined in Or or And
        clauses
        context is the current entry
        """
        return self.context.criteria

    def pre_format(self, values, edit=False):
        """
        Since when serializing a multi select on the client side, we get a list
        OR a string, we need to enforce getting a string
        """
        logger.debug("pre_format")
        if "searches" in values:
            searches = values.get("searches")
            if not hasattr(searches, "__iter__"):
                values["searches"] = [searches]

        values = self._complete_one_to_many(values, edit)

        return values

    def _ensure_parent_is_multiple(self, criterion, related, attributes):
        """
        Ensure the parent of the criterion is a complex one
        """
        logger.debug("ensure parent is multiple ?")
        logger.debug(criterion)
        logger.debug(related)
        if related and not related.complex:
            logger.debug(
                "We ensure the parent is a complex criterion " "(clause or related)"
            )
            clause_criterion = StatisticCriterion(
                type="and",
                entry_id=self.context.id,
            )

            if related.parent:
                # create a and clause above both crit and its parent
                clause_criterion.parent = related.parent
            self.dbsession.add(clause_criterion)
            self.dbsession.flush()
            criterion.parent = clause_criterion
            related.parent = clause_criterion
            self.dbsession.merge(criterion)
            self.dbsession.merge(related)
        return criterion

    def _complete_one_to_many(self, values, edit=False):
        relationship = values.pop("relationship", None)
        # On récupère la définition de la relationship
        #   On crée une instance de StatisticCriterion avec pour parent
        #   le parent courant
        #
        #   Cette instance devrait devenir le parent
        if relationship:
            logger.debug("We set up a relationship criterion")
            rel_criterion = StatisticCriterion(
                type="onetomany",
                key=relationship,
                entry_id=self.context.id,
                parent_id=values.get("parent_id"),
            )
            self.dbsession.add(rel_criterion)
            self.dbsession.flush()
            related = rel_criterion.parent
            self._ensure_parent_is_multiple(rel_criterion, related, values)
            values["parent_id"] = rel_criterion.id
        return values

    def post_format(self, criterion, edit, attributes):
        """
        Handle clause insertion inside the criterion tree if needed
        """
        if not edit:
            criterion.entry = self.context
        return criterion

    def after_flush(self, criterion, edit, attributes):
        if not edit:
            logger.debug("Criterion {} was added".format(criterion))
            # Si le parent du nouveau critère n'est pas une clause (ou/et,
            # table reliée) On va vouloir insérer une clause ET regroupant le
            # nouveau critère et son parent
            related = criterion.parent
            logger.debug(related)
            logger.debug("Parent id %s" % criterion.parent_id)
            self._ensure_parent_is_multiple(criterion, related, attributes)
        return criterion

    def pre_delete(self):
        # On stocke le parent de l'élément qu'on supprimer pour nettoyer
        # d'éventuel noeuds "complexes" vides après coup
        self.current_parent = self.context.parent

    def on_delete(self):
        """
        On delete we clean the tree to avoid void nodes

        We delete the and/or/onetomany clauses if there are no children left
        except for the root node
        """
        logger.debug("After the criteria is deleted we clean the tree")
        logger.debug("Current parent ")
        logger.debug(self.current_parent)
        while self.current_parent:
            if not self.current_parent.root and self.current_parent.complex:
                logger.debug("Current is not root and complex")
                current = self.current_parent
                parent = self.current_parent = current.parent

                if len(current.children) == 0:
                    logger.debug("We delete a criterion {}".format(current))
                    self.dbsession.delete(current)
                    self.dbsession.flush()
                elif current.type in ("and", "or") and len(current.children) == 1:
                    logger.debug("  + We delete a criterion {}".format(current.id))
                    # On supprime la clause or/and et on déplace l'enfant un
                    # cran plus haut
                    child = current.children[0]
                    child.parent = parent
                    self.dbsession.merge(child)
                    self.dbsession.flush()
                    self.dbsession.delete(current)
                    self.dbsession.flush()
            else:
                self.current_parent = None


def includeme(config):
    config.add_rest_service(
        RestStatisticSheet,
        API_ITEM_ROUTE,
        context=StatisticSheet,
        view_rights=PERMISSIONS["global.view_userdata_details"],
        edit_rights=PERMISSIONS["global.view_userdata_details"],
    )
    config.add_view(
        RestStatisticSheet,
        attr="form_config",
        route_name=API_ITEM_ROUTE,
        request_param="form_config=1",
        request_method="GET",
        renderer="json",
        context=StatisticSheet,
        permission=PERMISSIONS["global.view_userdata_details"],
    )

    config.add_rest_service(
        RestStatisticEntry,
        API_ENTRY_ITEM_ROUTE,
        collection_route_name=API_ENTRIES_ROUTE,
        collection_context=StatisticSheet,
        context=StatisticEntry,
        add_rights=PERMISSIONS["global.view_userdata_details"],
        edit_rights=PERMISSIONS["global.view_userdata_details"],
        view_rights=PERMISSIONS["global.view_userdata_details"],
        delete_rights=PERMISSIONS["global.view_userdata_details"],
    )
    config.add_view(
        RestStatisticEntry,
        attr="duplicate_view",
        route_name=API_ENTRY_ITEM_ROUTE,
        request_param="action=duplicate",
        request_method="POST",
        renderer="json",
        context=StatisticSheet,
        permission=PERMISSIONS["global.view_userdata_details"],
    )
    config.add_rest_service(
        RestStatisticCriterion,
        API_CRITERION_ITEM_ROUTE,
        collection_route_name=API_CRITERIA_ROUTE,
        collection_context=StatisticEntry,
        context=StatisticCriterion,
        add_rights=PERMISSIONS["global.view_userdata_details"],
        edit_rights=PERMISSIONS["global.view_userdata_details"],
        view_rights=PERMISSIONS["global.view_userdata_details"],
        delete_rights=PERMISSIONS["global.view_userdata_details"],
    )
