"""
Le code wsgi renvoie un fichier sous la forme d'un cgi.FieldStorage


Cas 1 : Dans le cas d'un formulaire classique: 
    
    le widget deform le deserialize en dict et le stocke dans un tempstore 
    pour le retrouver en cas d'erreur de validation

Cas 2 : Dans le cas de l'api rest, pas de deform donc on a le fichier sous la forme de cgi.FieldStorage

Niveau Wsgi et Rest api :

    {
        'upload': <FieldStorage>
    }
FieldStorage a les propriétés suivantes
    file : le fichier
    filename : le nom du fichier (à formatter dans le cas d'IE)
    type : le mimetype 
    length : la taille du fichier

sorti de deform il a les attributs suivant

    {
        'upload': {
            filename: nom du fichier
            mimetype: mimetype
            size: taille
            fp: pointer to file
            uid: uid
        }
    }

    
Le modèle File attend les données suivantes lors de l'initialisation

name : str  <- filename
description : str <- description ou filename
mimetype : str <- type
size : int
file_type_id : int

Puis dans un deuxième temps :

data : binary blob ou FieldStorage
"""

from io import BytesIO
import logging

from cgi import FieldStorage
from typing import Optional
from dataclasses import dataclass

from caerp.consts.permissions import PERMISSIONS
from caerp.forms import merge_session_with_post
from caerp.interfaces import ISignPDFService
from caerp.models.files import File
from caerp.models.indicators import SaleFileRequirement
from caerp.models.node import Node

from caerp.utils.controller import BaseAddEditController
from caerp.events.files import FileAdded, FileDeleted, FileUpdated
from caerp.views.files.routes import FILE_ITEM

logger = logging.getLogger(__name__)


@dataclass
class FileData:
    name: str
    data: BytesIO
    mimetype: Optional[str] = None
    size: Optional[int] = None
    is_signed: bool = False


def get_filedata_from_file_object_and_stream(
    file_object: File, file_data_stream: BytesIO
) -> FileData:
    """
    Create a FileData object from a File object (file description) and a stream (file data)
    """
    return FileData(
        name=file_object.name,
        data=file_data_stream,
        mimetype=file_object.mimetype,
        size=file_object.size,
        is_signed=file_object.is_signed,
    )


def get_file_object_from_filedata(filedata_object: FileData) -> File:
    """
    Create a File object from a FileData object
    """
    filedata_object.data.seek(0)
    file_datas = filedata_object.data.read()
    filedata_object.data.seek(0)
    return File(
        name=filedata_object.name,
        data=file_datas,
        mimetype=filedata_object.mimetype,
        size=filedata_object.size,
        is_signed=filedata_object.is_signed,
    )


def ensure_filename(name: str) -> str:
    """
    Handle the case when the browser (IE) returns an absolute path
    """
    return name[name.rfind("\\") + 1 :].strip()


class FileController(BaseAddEditController):
    """
    Controller used to manipulate file objects

        - build a schema
        - add a file to the database
        - edit an existing file
        - delete an existing file

    >>> controller = FileController(self.request, self.context)
    >>> schema = controller.get_schema()
    >>> data = schema.deserialize(submitted_data)
    >>> controller.add(data, parent_node)
    """

    def __init__(self, request, edit=False, factory=File):
        super().__init__(request, edit)
        self.factory = factory

    def _get_size(self, file_pointer) -> int:
        file_pointer.seek(0)
        value = len(file_pointer.read())
        file_pointer.seek(0)
        return value

    def _get_context_id(self) -> Optional[int]:
        return self.context.id if hasattr(self.context, "id") else None

    def file_to_appstruct(self, file_object: File) -> dict:
        """
        Format a file_object as a dict matching the upload schema for deform.Form
        initialization
        """
        file_dict = {
            "name": file_object.name,
            "description": file_object.description,
            "file_type_id": file_object.file_type_id,
        }
        file_dict["upload"] = {
            "filename": file_dict["name"],
            "uid": str(file_object.id),
            "preview_url": self.request.route_path(
                FILE_ITEM, id=file_object.id, _query={"action": "download"}
            ),
        }
        return file_dict

    def set_upload_data(self, file_object: File, upload):

        # 1- On transforme les données de formulaire en FileData
        if isinstance(upload, dict):
            file_data: Optional[FileData] = self.file_data_from_dict(upload)
        elif isinstance(upload, FieldStorage):
            file_data: Optional[FileData] = self.file_data_from_fieldstorage(upload)
        else:
            return None
        if file_data is None:
            return None

        # 2- On signe le fichier si nécessaire
        try:
            pdf_sign_service = self.request.find_service(ISignPDFService)
        except:
            logger.info("No PDF signing service (ISignPDFService) configured")
            pdf_sign_service = None
        if pdf_sign_service:
            file_data.is_signed = pdf_sign_service.sign(
                file_data,
                node_id=self._get_context_id(),
                with_stamp=False,  # Désactivé pour l'instant, cf #4199
            )

        # 3- On applique les données FileData sur le modèle File
        self.set_file_data_on_file_object(file_object, file_data)

        return file_object

    def file_data_from_dict(self, upload: dict) -> Optional[FileData]:
        """
        Get formatted data from upload in dict format (coming from deform)
        """
        if upload and "fp" in upload:
            file_data = FileData(
                name=upload["filename"],
                data=upload["fp"],
                mimetype=upload["mimetype"],
                size=upload.get("size", self._get_size(upload["fp"])),
            )
        else:
            file_data = None
        return file_data

    def file_data_from_fieldstorage(self, upload: FieldStorage) -> FileData:
        """
        Get formatted data from upload in fieldstorage format (coming from JS components)
        """
        if upload is not None:
            file_data = FileData(
                name=ensure_filename(upload.filename),
                data=upload.file,
                mimetype=upload.type,
                size=self._get_size(upload.file),
            )
        else:
            file_data = None
        return file_data

    def set_file_data_on_file_object(
        self, file_object: File, file_data: Optional[FileData]
    ) -> File:
        """
        Attach the formatted file data to the given file object
        """
        if file_data is not None:
            file_object.name = file_data.name
            file_object.size = file_data.size
            file_object.data = file_data.data
            file_object.mimetype = file_data.mimetype
            file_object.is_signed = file_data.is_signed
        return file_object

    def _find_associated_indicator(
        self, default_parent: Node, attributes: dict
    ) -> Optional[SaleFileRequirement]:
        """
        Try to retrieve the indicator from the submitted data and concerning
        default_parent
        """
        indicator = None
        if "indicator_id" in attributes:
            indicator = SaleFileRequirement.get(attributes["indicator_id"])

        if indicator is None:
            # On tente de retrouver un requirement avec le même type de fichier
            if "file_type_id" in attributes and hasattr(
                default_parent, "get_file_requirements"
            ):
                file_type_id = attributes["file_type_id"]
                # On retrouve un file_requirement qui concerne le Node par défaut et qui a ce type
                indicators = default_parent.get_file_requirements(
                    file_type_id=file_type_id, scoped=False
                )

                if len(indicators) >= 1:
                    return indicators[0]

        return indicator

    def _get_parent(self, attributes: dict, default_parent: Node) -> Node:
        """
        Retrieve the parent the submitted file should be attached to
        """
        if "parent_id" in attributes:
            parent_id = attributes["parent_id"]
            node: Node = Node.get(parent_id)
            if node is not None and self.request.has_permission(
                PERMISSIONS["context.add_file"], node
            ):
                default_parent = node

        indicator = self._find_associated_indicator(default_parent, attributes)

        if indicator is None or not self.request.has_permission(
            PERMISSIONS["context.add_file"], indicator.node
        ):
            return default_parent

        return indicator.node

    def _add(self, attributes: dict, parent: Optional[Node] = None) -> File:
        """
        Add a file object

        **Attributes/Arguments**

        attributes

            Attributes passed through the schema validation

            {
                'come_from': 'http://example.com',
                'popup': 0,
                'upload': FieldStorage or {'fp', 'size' ...},
                'description': "Ma description",
                'file_type_id': 5
            }
            UPLOAD_DATA could be either a dict or an object (FieldStorage)
            (dict if coming from the deform widget)

        parent

            The parent object to which we attach the file
        """
        logger.debug("Adding a file")
        file_object = self.factory()
        upload = attributes.pop("upload", {})
        self.set_upload_data(file_object, upload)

        if file_object.name is None:
            raise Exception("Missing file data ?")

        if parent:
            default_parent = parent
        elif isinstance(self.context, Node):
            default_parent = self.context
        else:
            default_parent = None
        # Magic #3925 : déplacement auto des fichiers de ventes au niveau où ils sont
        # requis
        file_object.parent = self._get_parent(attributes, default_parent)
        # Merge other attributes
        merge_session_with_post(file_object, attributes)
        self.request.dbsession.add(file_object)
        self.request.dbsession.flush()

        self.request.registry.notify(FileAdded(self.request, file_object, attributes))
        return file_object

    def _edit(self, attributes) -> File:
        file_object: File = self.context
        upload = attributes.pop("upload", None)
        self.set_upload_data(file_object, upload)
        # Merge other attributes
        merge_session_with_post(file_object, attributes)

        # Magic #3925 : déplacement auto des fichiers de ventes au niveau où ils sont
        # requis
        parent = self._get_parent(attributes, file_object.parent)
        if parent != file_object.parent:
            file_object = self.move(attributes, parent)
        else:
            self.request.dbsession.merge(file_object)
            self.request.dbsession.flush()
            self.request.registry.notify(
                FileUpdated(self.request, file_object, attributes)
            )
        return file_object

    def save(self, attributes: dict, parent: Optional[Node] = None) -> File:
        if self.edit:
            return self._edit(attributes)
        else:
            return self._add(attributes, parent)

    def move(self, attributes: dict, parent: Node) -> File:
        file_object: File = self.context
        self.request.registry.notify(FileDeleted(self.request, file_object))

        file_object.parent = parent
        self.request.dbsession.merge(file_object)
        self.request.dbsession.flush()
        self.request.registry.notify(FileAdded(self.request, file_object, attributes))
        return file_object

    def delete(self):
        logger.info(
            "# {} deletes a {} with id {}".format(
                self.request.identity,
                str(self.context.__class__.__name__),
                self.context.id,
            )
        )
        self.request.registry.notify(FileDeleted(self.request, self.context))
        self.request.dbsession.delete(self.context)
