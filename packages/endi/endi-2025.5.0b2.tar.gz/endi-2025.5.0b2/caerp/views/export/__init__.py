from caerp.utils.compat import Iterable
import logging
from typing import Iterator, Optional, Tuple

from deform.exception import ValidationFailure

from caerp.interfaces import ITreasuryWriter
from caerp.views import BaseListView
from caerp.compute.sage import MissingData
from caerp.views.export.utils import HELPMSG_CONFIG
from caerp.export.utils import (
    write_file_to_request,
    store_export_file,
)


logger = logging.getLogger(__name__)


def get_value_from_writer(writer: ITreasuryWriter, operation_line) -> Iterator[tuple]:
    """
    Compute values that will be written to the end file

    Used by preview
    """
    data = writer.format_row(operation_line)
    for index, header in enumerate(writer.headers):
        if isinstance(data, dict):
            label = header["label"]
            yield header, data.get(label, "")
        else:
            if len(data) > index:
                yield header, data[index]
            else:
                yield header, ""


class BaseExportView(BaseListView):
    """
    Base export view
    Provide skeleton for export view development

    - Return forms
    - Validate form datas
    - Check elements can be exported
    - Return error messages
    - Return the generated file
    """

    admin_route_name = "/admin"
    help_message = None
    writer_interface = None
    schema = None

    def before(self):
        """
        Launched before anything is done
        """
        pass

    def get_forms(self):
        """
        :returns: the forms to be rendered in the form
            {formname: {'title': A title, 'form': 'The form object'}}
        :rtype: dict or OrderedDict
        """
        return {}

    def validate_form(self, forms) -> Tuple[Optional[str], Optional[dict]]:
        """
        Validate a submitted form if needed
        """
        form_name = appstruct = None
        if "submit" in self.request.params or "preview" in self.request.params:
            form_name = self.request.POST["__formid__"]
            form = forms[form_name]["form"]

            post_items = list(self.request.POST.items())

            logger.debug("Form %s was submitted", form_name)
            try:
                appstruct = form.validate(post_items)
                logger.debug("Validation successfull")
            except ValidationFailure as validation_error:
                logger.exception("There was an error on form validation")
                logger.exception(post_items)
                # Replace the form, it now contains errors
                # - will be displayed again
                forms[form_name]["form"] = validation_error
        return form_name, appstruct

    def query(self, appstruct, form_name):
        """
        :param dict appstruct: The validated form datas
        :param str form_name: The name of the form that was submitted
        :returns: a Sqlalchemy query collecting items to be exported
        """
        raise NotImplementedError()

    def check(self, items):
        """
        Check items are valid for export

        :param obj items: A Sqlalchemy query
        :returns: a 2-uple (valid, messages_dict) where messages_dict is in the
            form {'title': A message block title, "errors": [error messages]}
        """
        return True, {}

    def record_exported(self, items, form_name, appstruct):
        """
        Record exported elements in the database

        :param list items: the items to render
        :param str form_name: The name of the form that was submitted
        :param dict appstruct: The validated datas
        """
        pass

    def record_export(self, items, form_name, appstruct, file_obj):
        """
        Record in the log the export that has just been done

        :param list items: the items to render
        :param str form_name: The name of the form that was submitted
        :param dict appstruct: The validated datas
        :returns: A response object
        """
        raise NotImplementedError()

    def produce_file_and_record(self, items, form_name, appstruct):
        """
        Fonction en charge de produire le fichier de sortie

        Par défaut, on enregistre également l'historique et
        on enregistre le statut "exporté"
        """
        # Let's process and return successfully the csvfile
        logger.debug("  + Producing file")
        # Ici on efectue la requête car les infos vont changer et
        # la requête ne donnera plus le même résultat d'un appel à
        # l'autre
        if hasattr(items, "all"):
            items = items.all()
        file_obj, result = self.write_file(items, form_name, appstruct)
        logger.debug("  + Record exported items")
        self.record_exported(items, form_name, appstruct)
        logger.debug("  + Record export in the logs")
        self.record_export(items, form_name, appstruct, file_obj)
        logger.info("-> Done")
        return result

    def get_writer(self):
        if self.writer_interface is None:
            raise NotImplementedError(
                "Il manque la configuration de l'interface de la classe du Writer"
            )
        return self.request.find_service(self.writer_interface)

    def get_filename(self, writer):
        raise NotImplementedError()

    def _collect_export_data(
        self, models: Iterable[object], appstruct: dict = None
    ) -> Iterable[dict]:
        raise NotImplementedError()

    def get_preview_items(self, items, form_name, appstruct=None):
        """
        Return all the elements to be previewed

        :param list items: the items to render
        :param str form_name: The name of the form that was submitted
        :param dict appstruct: The validated datas
        :returns: A response object
        """
        return self._collect_export_data(items.all(), appstruct)

    def write_file(
        self, models: Iterable[object], form_name: str, appstruct: dict
    ) -> Tuple[object, object]:
        """
        Add a file to the request.response

        :param models: the items to render
        :param form_name: The name of the form that was submitted
        :param appstruct: The validated datas
        :returns: A tuple [file, response object]
        """
        writer = self.get_writer()
        data = self._collect_export_data(models, appstruct)
        writer.set_datas(data)
        export_file = writer.render()
        export_filename = self.get_filename(writer)

        encoding = writer.encoding
        write_file_to_request(
            self.request,
            export_filename,
            export_file,
            writer.mimetype,
            encoding=encoding,
        )

        # Store the actual file in the database and file depot
        file_obj = store_export_file(
            self.context,
            self.request,
            export_file,
            export_filename,
            writer.mimetype,
            encoding=encoding,
        )

        return file_obj, self.request.response

    def __call__(self):
        """
        Main view entry

        1- Collect forms
        2- if submission :
            validate datas
            query
            check elements can be exported
            write the file
        3- return forms and messages
        """
        logger.debug("Calling for accounting operations generation")
        check_messages = None
        preview_items = None
        writer = None
        self.before()
        forms = self.get_forms()

        form_name, appstruct = self.validate_form(forms)
        logger.debug("    + Selected filters {}".format(appstruct))

        if appstruct is not None:
            is_preview = "preview" in self.request.POST

            logger.debug("  + Querying export items")
            items = self.query(appstruct, form_name)
            logger.debug("  + Checking for data integrity")
            is_ok, check_messages = self.check(items)

            if is_ok:
                logger.debug("  + Data are ok")
                if is_preview:  # Actually print the item to the screen
                    logger.debug("Displaying preview items")
                    writer = self.get_writer()
                    preview_items = self.get_preview_items(items, form_name, appstruct)

                else:  # Actually write the file
                    try:
                        return self.produce_file_and_record(items, form_name, appstruct)
                    except (MissingData, KeyError):
                        logger.exception("Exception occured while writing file")
                        config_help_msg = HELPMSG_CONFIG.format(
                            self.request.route_url(self.admin_route_name)
                        )
                        check_messages["errors"] = [config_help_msg]

        # We are either
        # * reporting an error
        # * or doing the initial display of forms.

        # rendered forms
        for key in forms:
            forms[key]["form"] = forms[key]["form"].render()

        return {
            "title": self.title,
            "help_message": self.help_message,
            "check_messages": check_messages,
            "preview_items": preview_items,
            "get_value_from_writer": get_value_from_writer,
            "writer": writer,
            "forms": forms,
        }
