from sqlalchemy.orm import load_only
from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.models import files
from caerp.forms.files import get_userdata_file_upload_schema
from caerp.models.user.user import User
from caerp.resources import fileupload_js

from caerp.views import BaseView
from caerp.views.files.views import FileUploadView, FileEditView
from caerp.views.userdatas.userdatas import USERDATAS_MENU
from caerp.views.userdatas.routes import (
    USER_USERDATAS_FILE_URL,
    USER_USERDATAS_URL,
    USER_USERDATAS_FILELIST_URL,
    USER_USERDATAS_MYDOCUMENTS_URL,
)


USERDATAS_MENU.add_item(
    name="userdatas_filelist",
    label="Portefeuille de documents",
    route_name=USER_USERDATAS_FILELIST_URL,
    icon="folder",
    perm=PERMISSIONS["global.view_userdata_files"],
)


class UserUserDatasFileAddView(FileUploadView):
    title = "Attacher un fichier au portefeuille de l’entrepreneur"

    def get_schema(self):
        return get_userdata_file_upload_schema(self.request)

    def before(self, form):
        fileupload_js.need()
        come_from = self.request.referrer
        appstruct = {"come_from": come_from, "parent_id": self.context.userdatas.id}
        form.set_appstruct(appstruct)

    def save(self, appstruct):
        appstruct["parent_id"] = self.context.userdatas.id
        return super().save(appstruct)


class UserDatasFileEditView(FileEditView):
    """
    context is a File object
    """

    def get_schema(self):
        return get_userdata_file_upload_schema(self.request)

    def _get_form_initial_data(self):
        appstruct = super()._get_form_initial_data()
        from caerp.models.career_path import CareerPathFileRel

        q = CareerPathFileRel.query().filter(
            CareerPathFileRel.file_id == self.context.id
        )
        file_rel = q.first()
        if file_rel is not None:
            appstruct["career_path_id"] = file_rel.career_path_id
        return appstruct

    def redirect(self, come_from):
        if come_from not in (None, "None"):
            return HTTPFound(come_from)
        return HTTPFound(
            self.request.route_path(
                USER_USERDATAS_FILELIST_URL,
                id=self.context.parent.user_id,
            )
        )


class UserDatasFileList(BaseView):
    help_message = "Cette liste présente l’ensemble des documents "
    "déposés dans enDI ainsi que l’ensemble des documents générés "
    "depuis l’onglet Génération de documents. Ces documents sont "
    "visibles par l’entrepreneur."

    @property
    def current_userdatas(self):
        return self.context

    def __call__(self):
        query = files.File.query().options(
            load_only(
                "description",
                "name",
                "updated_at",
                "id",
            )
        )
        query = query.filter_by(parent_id=self.current_userdatas.id).order_by(
            files.File.updated_at.desc()
        )

        return dict(
            title="Portefeuille de documents",
            files=query,
            add_url=self.request.route_path(
                USER_USERDATAS_URL,
                id=self.current_userdatas.user_id,
                _query=dict(action="attach_file"),
            ),
            help_message=self.help_message,
        )


class UserUserDatasFileList(UserDatasFileList):
    @property
    def current_userdatas(self):
        return self.context.userdatas


def mydocuments_view(context, request):
    """
    View callable collecting datas for showing the social docs associated to the
    current user's account
    """
    if context.userdatas is not None:
        query = files.File.query()
        documents = (
            query.filter(files.File.parent_id == context.userdatas.id)
            .order_by(files.File.updated_at.desc())
            .all()
        )
    else:
        documents = []
    return dict(
        title="Mes documents",
        documents=documents,
    )


def includeme(config):
    config.add_view(
        UserUserDatasFileAddView,
        route_name=USER_USERDATAS_URL,
        request_param="action=attach_file",
        layout="default",
        renderer="caerp:templates/base/formpage.mako",
        context=User,
        permission=PERMISSIONS["global.view_userdata_files"],
    )
    config.add_view(
        UserDatasFileEditView,
        route_name=USER_USERDATAS_FILE_URL,
        renderer="caerp:templates/base/formpage.mako",
        context=files.File,
        permission=PERMISSIONS["context.edit_file"],
    )
    config.add_view(
        UserUserDatasFileList,
        route_name=USER_USERDATAS_FILELIST_URL,
        renderer="/userdatas/filelist.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["global.view_userdata_files"],
    )
    config.add_view(
        mydocuments_view,
        route_name=USER_USERDATAS_MYDOCUMENTS_URL,
        renderer="/mydocuments.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["context.view_userdata_files"],
    )

    def deferred_permission(menu, kw):
        return kw["request"].identity.has_userdatas()

    config.add_company_menu(
        parent="document",
        order=4,
        label="Mes documents",
        route_name=USER_USERDATAS_MYDOCUMENTS_URL,
        route_id_key="user_id",
        permission=deferred_permission,
    )
