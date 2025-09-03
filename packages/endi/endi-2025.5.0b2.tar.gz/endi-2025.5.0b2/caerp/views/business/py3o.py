import logging

from genshi.template.eval import UndefinedError
from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.export.utils import write_file_to_request
from caerp.models.project.business import Business
from caerp.views import (
    BaseView,
    TreeMixin,
)
from caerp.views.business.routes import BUSINESS_ITEM_PY3O_ROUTE
from caerp.views.business.controller import BusinessPy3oController
from caerp.views.project.project import ProjectEntryPointView

logger = logging.getLogger(__name__)


def get_error_msg_from_genshi_error(err):
    """
    Genshi raises an UndefinedError, but doesn't store the key name in the
    Exception object.
    We try to get the missing key from the resulting message and return
    a comprehensive error message for the user.
    """
    if " not defined" in err.msg:
        # Donnée non renseignée
        return "La clé '{}' n'est pas définie.".format(err.msg.split(" not defined")[0])
    elif "has no member" in err.msg:
        # Liste vide
        return """Un élément utilisé dans le modèle n'est pas présent 
        pour cette affaire (généralement un devis ou une facture)."""
    else:
        # Autre erreur
        return "Détail de l'erreur : '{}'".format(err.msg)


class BusinessFileGeneration(BaseView, TreeMixin):
    help_message = """
    Vous pouvez générer et télécharger des documents modèles définis
    par la coopérative qui seront pré-remplis avec vos coordonnées et
    celles du client."""

    def __init__(self, context, request=None):
        super().__init__(context, request)
        self.controller = BusinessPy3oController(context, request)

    @property
    def title(self):
        return "Génération de documents pour l'affaire {0}".format(self.context.name)

    @property
    def tree_url(self):
        return self.request.route_path(self.route_name, id=self.context.id)

    def default_context_task_id(self):
        """
        Return the last estimation's id as default context for template generation
        or the last invoice's id if there's no estimation
        """
        if len(self.context.estimations) > 0:
            return self.context.estimations[-1].id
        elif len(self.context.invoices) > 0:
            return self.context.invoices[-1].id
        else:
            return None

    def py3o_action_view(self, business_type_id, file_type_id, context_task_id):
        try:
            template, output_buffer = self.controller.compile_template(
                business_type_id,
                file_type_id,
                context_task_id or self.default_context_task_id(),
            )
            write_file_to_request(self.request, template.file.name, output_buffer)
            return self.request.response
        except UndefinedError as err:
            msg = get_error_msg_from_genshi_error(err)
            logger.exception(msg)
            self.session.flash(
                "<b>Erreur à la compilation du modèle</b><p>{}</p>".format(msg),
                "error",
            )
        except IOError:
            logger.exception("Le template n'existe pas sur le disque")
            self.session.flash(
                """<b>Erreur à la compilation du modèle</b><p>Le fichier 
                correspondant au modèle de ce document est manquant. Merci de 
                le recharger depuis la configuration.</p>""",
                "error",
            )
        except KeyError:
            logger.exception(
                "Le template n'existe pas (business_id={} ; file_type_id={})".format(
                    business_type_id, file_type_id
                )
            )
            self.session.flash(
                """<b>Erreur à la compilation du modèle</b><p>Ce modèle de document 
                n'existe pas.</p>""",
                "error",
            )
        except Exception:
            logger.exception(
                """Une erreur est survenue à la compilation du template 
                (business_id={} ; file_type_id={} ; context_task_id={})""".format(
                    business_type_id,
                    file_type_id,
                    context_task_id,
                )
            )
            self.session.flash(
                """<b>Erreur à la compilation du modèle</b><p>Merci de contacter 
                votre administrateur.</p>""",
                "error",
            )
        return HTTPFound(self.request.current_route_path(_query={}))

    def __call__(self):
        self.populate_navigation()
        business_type_id = self.context.business_type_id
        file_type_id = self.request.GET.get("file")
        context_task_id = self.request.GET.get("task")
        if file_type_id:
            return self.py3o_action_view(
                business_type_id, file_type_id, context_task_id
            )
        else:
            templates = self.controller.get_available_templates(business_type_id)
            return dict(
                title=self.title,
                help_message=self.help_message,
                templates=templates,
            )


def includeme(config):
    config.add_tree_view(
        BusinessFileGeneration,
        route_name=BUSINESS_ITEM_PY3O_ROUTE,
        parent=ProjectEntryPointView,
        permission=PERMISSIONS["context.py3o_template_business"],
        renderer="/business/py3o.mako",
        layout="business",
        context=Business,
    )
