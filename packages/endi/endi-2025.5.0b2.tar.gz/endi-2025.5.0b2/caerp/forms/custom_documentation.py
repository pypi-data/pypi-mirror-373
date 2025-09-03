import colander
import deform_extensions
from caerp.forms import (
    files,
    merge_session_with_post,
)
from caerp.models.files import File

from pyramid.authorization import (
    Allow,
    Authenticated,
)


class CustomDocumentationSchema(colander.Schema):
    title = colander.SchemaNode(
        colander.String(),
        title="Titre du document",
    )

    # RadioChoiceToggleWidget to select between a link or a file. Used
    # in validator/dictify/objectify and not stored into the model.
    _type = colander.SchemaNode(
        colander.String(),
        title="Vous souhaitez ajouter",
        widget=deform_extensions.RadioChoiceToggleWidget(
            values=(
                (
                    "document",
                    "Un fichier",
                    "document",
                ),
                (
                    "uri",
                    "Un lien",
                    "uri",
                ),
            ),
        ),
    )

    document = files.FileNode(
        title="Document",
        missing=colander.drop,
    )

    uri = colander.SchemaNode(
        colander.String(),
        title="Lien",
        missing=colander.drop,
        validator=colander.url,
    )

    @colander.deferred
    def validator(node, kw):
        context = kw["request"].context

        def valid_type_func(node, cstruct):
            _type = cstruct["_type"]
            if _type not in cstruct.keys() and not getattr(context, _type, None):
                raise colander.Invalid(node, f"Vous devez remplir le champs {_type}")

        return valid_type_func

    def dictify(self, model):
        """Return a dictified version of obj using schema information."""

        d = {
            "title": model.title,
            "uri": str(model.uri or ""),
            "_type": "uri",
        }

        if model.document:
            d["document"] = {
                "filename": model.document.name,
                "uid": model.document.id,
                "description": model.document.description,
                "file_type_id": model.document.file_type_id,
            }
            d["_type"] = "document"

        return d

    def objectify(self, appstruct, model):
        """Return an object representing value using schema information."""

        if appstruct["_type"] == "uri":
            appstruct.pop("document", None)  # remove useless document
        elif appstruct["_type"] == "document":
            appstruct.pop("uri", None)  # remove useless uri

        filestruct = appstruct.pop("document", None)

        for key, value in appstruct.items():
            setattr(model, key, value)

        if appstruct["_type"] == "uri":
            model.document = None

        if filestruct:
            f = model.document
            filedata = filestruct.pop("fp")
            if f is None:
                f = File(
                    name=filestruct["filename"],
                    description=appstruct["title"],
                    _acl=[(Allow, Authenticated, ("context.view_file"))],
                )
            else:
                f.name = filestruct["filename"]
                f.description = appstruct["title"]
                f.mimetype = filestruct["mimetype"]
                f.data = filedata
            f.mimetype = filestruct["mimetype"]
            f.size = filestruct["size"]
            f.data = filedata
            model.document = f

        return model
