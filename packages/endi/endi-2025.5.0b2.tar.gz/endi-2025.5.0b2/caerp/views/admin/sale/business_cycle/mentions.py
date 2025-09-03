import os
import colander
import peppercorn
import logging

from pyramid.httpexceptions import HTTPFound
from caerp.consts.permissions import PERMISSIONS
from caerp.models.project.mentions import BusinessTypeTaskMention
from caerp.models.project.types import BusinessType
from caerp.models.task.mentions import TaskMention

from caerp.forms.admin.sale.business_cycle.mentions import (
    BusinessTypeMentionEntries,
)
from caerp.views import (
    BaseView,
    TreeMixin,
)
from caerp.views.admin.sale.business_cycle import (
    BUSINESS_URL,
    BusinessCycleIndexView,
)

logger = logging.getLogger(__name__)

BUSINESS_MENTION_URL = os.path.join(BUSINESS_URL, "business_type_task_mention")


class BusinessTypeTaskMentionView(BaseView, TreeMixin):
    route_name = BUSINESS_MENTION_URL
    title = "Mentions obligatoires/facultatives"
    description = (
        "Les mentions qui sont intégrées dans les documents étapes"
        " (devis/factures), par type d'affaire."
    )
    permission = PERMISSIONS["global.config_sale"]

    @property
    def help_message(self):
        from caerp.views.admin.sale.forms.mentions import TASK_MENTION_URL

        return """
    Configurer l'utilisation des mentions dans les différents documents.<br />
    Pour chaque <b>type d'affaire</b>, pour chaque <b>type de document</b> une
    mention peut être  :
        <ul>
        <li>
        <b>Facultative</b> : elle sera proposée à l'entrepreneur lors de
        l'édition de ses documents
        </li>
        <li>
        <b>Obligatoire</b> : elle sera
        automatiquement intégré dans les sorties PDF
        </li>
        </ul>
    NB : Les mentions sont configurables dans <a
    href="{0}">Configuration -> Module Ventes -> Mentions des devis et
    factures</a>
    """.format(
            self.request.route_path(TASK_MENTION_URL)
        )

    def _collect_items(self):
        res = {}
        for item in BusinessTypeTaskMention.query():
            res.setdefault(item.task_mention_id, {}).setdefault(
                item.business_type_id, {}
            )[item.doctype] = item.mandatory
        return res

    def __call__(self):
        self.populate_navigation()
        return dict(
            business_types=BusinessType.query().all(),
            mentions=TaskMention.query().all(),
            items=self._collect_items(),
            help_message=self.help_message,
        )


class BusinessTypeTaskMentionSetView(BaseView):
    schema = BusinessTypeMentionEntries
    permission = PERMISSIONS["global.config_sale"]

    def _find_item(self, appstruct, create=False):
        logger.debug(appstruct)
        mention_id = appstruct["task_mention_id"]
        btype_id = appstruct["business_type_id"]
        doctype = appstruct["doctype"]
        res = BusinessTypeTaskMention.get((mention_id, btype_id, doctype))
        if res is None and create:
            res = BusinessTypeTaskMention(
                task_mention_id=mention_id,
                business_type_id=btype_id,
                doctype=doctype,
            )
        return res

    def __call__(self):
        schema = BusinessTypeMentionEntries().bind(request=self.request)
        if "submit" in self.request.params:
            controls = list(self.request.params.items())
            values = peppercorn.parse(controls)
            logger.debug(values)
            try:
                appstruct = schema.deserialize(values)
            except colander.Invalid:
                logger.exception("Error while validating association datas")
                self.request.session.flash(
                    "Une erreur est survenue, veuillez "
                    "contacter votre administrateur",
                    "error",
                )
            else:
                for datas in appstruct["items"]:
                    mandatory = datas.get("mandatory")
                    if mandatory is not None:
                        # Facultatif ou obligatoire : on retrouve ou on crée
                        obj = self._find_item(datas, create=True)
                        obj.mandatory = mandatory == "true"
                        self.request.dbsession.merge(obj)
                    else:
                        # Non utilisé : on supprime l'éventuel existant
                        obj = self._find_item(datas)
                        if obj is not None:
                            self.request.dbsession.delete(obj)
                self.request.session.flash("Vos modifications ont été enregistrées")

        return HTTPFound(self.request.current_route_path())


def includeme(config):
    config.add_route(BUSINESS_MENTION_URL, BUSINESS_MENTION_URL)

    config.add_admin_view(
        BusinessTypeTaskMentionView,
        request_method="GET",
        parent=BusinessCycleIndexView,
        renderer="caerp:templates/admin/sale/business_type_task_mention.mako",
    )
    config.add_view(
        BusinessTypeTaskMentionSetView,
        route_name=BUSINESS_MENTION_URL,
        request_method="POST",
    )
