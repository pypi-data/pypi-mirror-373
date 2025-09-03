import os
import colander
import peppercorn
import logging

from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.models.project.file_types import (
    BusinessTypeFileType,
    BusinessTypeFileTypeTemplate,
)
from caerp.models.project.types import BusinessType
from caerp.models.files import FileType
from caerp.models.node import Node

from caerp.forms.admin.sale.business_cycle.file_types import (
    BusinessTypeFileTypeEntries,
)
from caerp.forms.files import get_businesstype_filetype_template_upload_schema
from caerp.views import (
    BaseView,
    BaseFormView,
    TreeMixin,
)
from caerp.views.admin.sale.business_cycle import (
    BUSINESS_URL,
    BusinessCycleIndexView,
)
from caerp.resources import fileupload_js
from caerp.views.files.controller import FileController

logger = logging.getLogger(__name__)


BUSINESS_FILETYPE_URL = os.path.join(BUSINESS_URL, "business_type_file_type")
BUSINESS_FILETYPE_ADD_TEMPLATE_URL = os.path.join(BUSINESS_FILETYPE_URL, "addtemplate")


class BusinessTypeFileTypeView(BaseView, TreeMixin):
    route_name = BUSINESS_FILETYPE_URL
    title = "Fichiers obligatoires/facultatifs"
    description = "Les fichiers qui doivent être déposés pour valider une \
affaire ou des documents étapes (devis/factures…)"
    permission = PERMISSIONS["global.config_sale"]

    @property
    def help_message(self):
        from caerp.views.admin.main.file_types import FILE_TYPE_ROUTE

        return """
        Configurer les obligations documentaires pour les différents types de
        documents.<br/><br/>
        <p>Pour chaque <b>type d'affaire</b>, pour chaque <b>type de
        document</b> un type de fichier peut être :
        <ul>
            <li><b>Globalement requis</b> : Au moins un fichier de ce type doit
            être fourni dans l'affaire pour pouvoir valider le document</li>
            <li><b>Requis</b> : Pour chaque document (devis/facture), un
            fichier de ce type est requis pour la validation</li>
            <li><b>Recommandé</b> : Un avertissement non bloquant sera indiqué
            si aucun fichier de ce type n'a été fourni</li>
            <li><b>Facultatif</b> : Ce type de fichier sera proposé à
            l'utilisateur lors du dépôt de fichier</li>
        </ul></p><br/>
        <p>Pour le paramétrage des modèles de fusion veuillez vous reporter à 
        <a href='https://doc.endi.coop/'>la documentation d'enDI</a>.</p><br/>
        <p><b>NB :</b> Les types de fichiers sont configurables dans
        <a href="{0}">Configuration -> Configuratrion générale ->
        Type de fichiers déposables dans enDI</a></p>
        """.format(
            self.request.route_path(FILE_TYPE_ROUTE)
        )

    def _collect_items(self):
        res = {}
        for item in BusinessTypeFileType.query():
            res.setdefault(item.file_type_id, {}).setdefault(item.business_type_id, {})[
                item.doctype
            ] = {
                "requirement_type": item.requirement_type,
                "validation": item.validation,
            }
        return res

    def _collect_templates(self):
        res = {}
        for template in BusinessTypeFileTypeTemplate.query():
            res.setdefault(template.file_type_id, {})[template.business_type_id] = {
                "file_id": template.file_id,
                "file_name": template.file.description,
            }
        return res

    def __call__(self):
        self.populate_navigation()
        business_filter = None
        file_filter = None
        business_query_all = BusinessType.query().order_by(BusinessType.label)
        file_query_all = FileType.query().order_by(FileType.label)
        business_query = business_query_all
        file_query = file_query_all
        for param in self.request.params.items():
            if param[0] == "business" and int(param[1]) > 0:
                business_query = business_query.filter(BusinessType.id == param[1])
                business_filter = int(param[1])
            if param[0] == "file" and int(param[1]) > 0:
                file_query = file_query.filter(FileType.id == param[1])
                file_filter = int(param[1])
        return dict(
            business_types_all=business_query_all.all(),
            business_types=business_query.all(),
            file_types_all=file_query_all.all(),
            file_types=file_query.all(),
            business_filter=business_filter,
            file_filter=file_filter,
            items=self._collect_items(),
            templates=self._collect_templates(),
            help_message=self.help_message,
            add_template_url=BUSINESS_FILETYPE_ADD_TEMPLATE_URL,
        )


class BusinessTypeFileTypeSetView(BaseView):
    schema = BusinessTypeFileTypeEntries
    permission = PERMISSIONS["global.config_sale"]

    def _find_item(self, appstruct, create=False):
        logger.debug(appstruct)
        file_type_id = appstruct["file_type_id"]
        btype_id = appstruct["business_type_id"]
        doctype = appstruct["doctype"]
        res = BusinessTypeFileType.get((file_type_id, btype_id, doctype))
        if res is None and create:
            res = BusinessTypeFileType(
                file_type_id=file_type_id, business_type_id=btype_id, doctype=doctype
            )
        return res

    def __call__(self):
        schema = self.schema().bind(request=self.request)
        if "del_template" in self.request.params:
            del_params = self.request.params["del_template"].split("__")
            query = self.request.dbsession.query(BusinessTypeFileTypeTemplate)
            query = query.filter(
                BusinessTypeFileTypeTemplate.business_type_id == del_params[0]
            ).filter(BusinessTypeFileTypeTemplate.file_type_id == del_params[1])
            template = query.first()
            if template:
                query = self.request.dbsession.query(Node)
                query = query.filter(Node.id == template.file_id)
                file = query.first()
                template_name = file.description
                self.request.dbsession.delete(template)
                self.request.dbsession.delete(file)
                self.request.session.flash(
                    "Le modèle <b>{}</b> a été supprimé".format(template_name)
                )
            else:
                logger.exception(
                    "No template found for deleting \
                    on business_type {} and file_type {}".format(
                        del_params[0], del_params[1]
                    )
                )
                self.request.session.flash(
                    "Impossible de supprimer le modèle : document non trouvé",
                    "error",
                )
        if "submit" in self.request.params:
            controls = list(self.request.params.items())
            values = peppercorn.parse(controls)
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
                    requirement_type = datas.get("requirement_type")
                    if requirement_type is not None:
                        # Facultatif ou obligatoire : on retrouve ou on crée
                        obj = self._find_item(datas, create=True)
                        obj.requirement_type = requirement_type
                        validation = datas.get("validation")
                        obj.validation = validation == "on"
                        self.request.dbsession.merge(obj)
                    else:
                        # Non utilisé : on supprime l'éventuel existant
                        obj = self._find_item(datas)
                        if obj is not None:
                            self.request.dbsession.delete(obj)
                self.request.session.flash("Vos modifications ont été enregistrées")
        return HTTPFound(self.request.current_route_path())


class BusinessTypeFileTypeTemplateAddView(BaseFormView):
    title = "Téléverser un modèle de document"
    schema = get_businesstype_filetype_template_upload_schema()
    permission = PERMISSIONS["global.config_sale"]

    def before(self, form):
        fileupload_js.need()
        appstruct = {}
        appstruct["come_from"] = self.request.referrer
        appstruct["business_type_id"] = self.request.params["business"]
        appstruct["file_type_id"] = self.request.params["file"]
        form.set_appstruct(appstruct)

    def submit_success(self, appstruct):
        controller = FileController(self.request)
        # Upload du fichier
        file_object = controller.save(appstruct)
        # Ajout du modèle
        template = BusinessTypeFileTypeTemplate()
        template.business_type_id = appstruct["business_type_id"]
        template.file_type_id = appstruct["file_type_id"]
        template.file_id = file_object.id
        self.dbsession.add(template)
        self.dbsession.flush()
        self.request.session.pop("substanced.tempstore")
        self.request.session.changed()
        self.add_popup_response()
        return self.request.response


def includeme(config):
    config.add_route(BUSINESS_FILETYPE_URL, BUSINESS_FILETYPE_URL)
    config.add_route(
        BUSINESS_FILETYPE_ADD_TEMPLATE_URL, BUSINESS_FILETYPE_ADD_TEMPLATE_URL
    )

    config.add_admin_view(
        BusinessTypeFileTypeTemplateAddView,
        route_name=BUSINESS_FILETYPE_ADD_TEMPLATE_URL,
        layout="default",
        parent=BusinessTypeFileTypeView,
        renderer="caerp:templates/base/formpage.mako",
    )
    config.add_admin_view(
        BusinessTypeFileTypeView,
        request_method="GET",
        parent=BusinessCycleIndexView,
        renderer="caerp:templates/admin/sale/business_type_file_type.mako",
    )
    config.add_view(
        BusinessTypeFileTypeSetView,
        route_name=BUSINESS_FILETYPE_URL,
        request_method="POST",
    )
